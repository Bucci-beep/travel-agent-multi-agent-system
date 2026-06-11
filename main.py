import os
import httpx
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

# initialize the asynchronous Groq client
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

class AsyncAgent:
    def __init__(self, name, role, model):
        self.name = name
        self.role = role
        self.model = model # we introduce this so that we can introduce right-sizing
        # (each agent can run an appropriate tailor-sized model)

    async def run(self, task):
        # we use await so this agent yields control while waiting for the network response
        response = await client.chat.completions.create(
            model = self.model,
            messages=[
            { "role": "system", "content": self.role},
            {"role": "user", "content": task}
            ],
            max_tokens= 1200
        )
        content = response.choices[0].message.content

        if content is None:
            return f"Error: The {self.name} failed to generate text (Content was None)."

        return content

# deterministic API helper
async def get_live_weather(destination: str) -> str:
    """Fetches real-time weather data from OpenweatherMapvAPi asynchronously."""
    if not WEATHER_API_KEY:
        return "Weather  data unavailable (Missing API Key)."

    url = f"https://api.openweathermap.org/data/2.5/weather?q={destination}&appid={WEATHER_API_KEY}&units=metric"

    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.get(url)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"Currently {temp}°C with {desc}."
            return f"Could not find weather data for '{destination}'."
        except Exception:
            return "Weather network request failed."

# defining our optimized agents
FAST_MODEL = "llama-3.1-8b-instant"
HEAVY_MODEL = "llama-3.3-70b-versatile"

research_agent = AsyncAgent(
    "Research Agent",
    """
    You are an expert travel researcher.
    Your job:
    - Find popular attractions
    - Find hidden gems
    - Suggest local experiences
    - Recommend best places
    - Recommend 2 to 3 specific hotel names to stay at in the destination city that align with the user's specified budget tier.
    """,
    model=FAST_MODEL # Fast, lightweight
)

culture_agent = AsyncAgent(
    "Culture & Language Agent",
    """
    You are a local cultural ambassador. 
    Your job:
    - Provide 3 vital local greetings, phonetics, and 1 important cultural custom.
    """,
    model=FAST_MODEL # Fast, lightweight
)
activity_agent = AsyncAgent(
    "Activity Planner Agent",
    """
    You are a professional travel planner.
    Your job:
    - Create daily activities
    - Plan sightseeing
    - Recommend food experiences
    - Organize activities logically
    """,
    model=FAST_MODEL
)

budget_agent = AsyncAgent(
    "Budget Agent",
    """
    You are a travel budget expert.
    Calculate:
    - Estimated flight cost based on the departure country
    - Specific Visa requirements and visa fees based on the traveler's nationality passport
    - Extract the specific hotel names recommended by the researcher and estimate their total cost for the duration of the trip.
    - Food expenses
    - Transport cost
    - Activity costs
    Create an approximate total trip budget.
    Keep response short.
    """,
    model=FAST_MODEL
)

final_agent = AsyncAgent(
    "Final Assistant",
    """You are a premium travel concierge. Compile all provided data into a beautiful, highly detailed markdown travel itinerary.

    You MUST extract data from the provided context and include the following sections in your final output:
    - Trip Overview
    - Current Local Weather
    - Culture & Local Greetings (Include the phonetic pronunciations)
    - Visa Requirements & Flight Costs
    - Recommended Accommodation (Include specific hotel names and estimated costs)
    - Day-by-Day Itinerary
    - Food & Dining Suggestions
    - Total Estimated Budget

    Ensure the formatting is clean, professional, and easy to read offline with not more than 700 words.""",
    model=HEAVY_MODEL
)

# Orchestration engine
async def run_travel_workflow(starting_location,nationality, destination, days, travelers, budget, interests):
    user_request = f"Flying from {starting_location}, Nationality: {nationality}, Destination: {destination}, Days: {days}, Travelers: {travelers}, Budget: {budget}, Interests: {interests}"
    """
    This function orchestrates the multi-agent workflow.
    It takes inputs from Streamlit and returns the final itinerary.
    """

    # PHASE 1: Parallel Execution
    # Research, Culture, and Weather API all execute at the EXACT same time (introduces parallelization)
    research_task = research_agent.run(user_request)
    culture_task = culture_agent.run(f"Provide local greetings and customs for: {destination}")
    weather_task = get_live_weather(destination)

    # Wait for all three concurrent requests to finish
    research_data, culture_data, weather_data = await asyncio.gather(research_task, culture_task, weather_task)

    # 2. Run dependent tasks sequentially
    print("Planning activities based on research...")
    activity_context = f"Context:\n{research_data}\nLive Weather Constraints: {weather_data}"
    activities_data = await activity_agent.run(activity_context)

    print("Calculating budget...")
    budget_prompt = (
        f"Calculate travel expenses for {travelers} travelers. "
        f"Departure location: {starting_location}. "
        f"Traveler Passport/Nationality: {nationality}. "
        f"Destination: {destination}. "
        f"Planned Activities: {activities_data}."
    )
    budget_data = await budget_agent.run(budget_prompt)

    print("Compiling final itinerary...")
    final_prompt = (
        f"Synthesize this master itinerary:\n\n"
        f"--- DESTINATION WEATHER ---\n{weather_data}\n\n"
        f"--- CULTURAL INSIGHTS ---\n{culture_data}\n\n"
        f"--- CURATED ACTIVITIES ---\n{activities_data}\n\n"
        f"--- BUDGET BREAKDOWN (Including Visas & Flights) ---\n{budget_data}"
    )

    final_itinerary_text = await final_agent.run(final_prompt)

    return final_itinerary_text

if __name__ == "__main__":
    print("Testing agents locally...")
    # Hardcode some test variables
    test_result = asyncio.run(
        run_travel_workflow("Tokyo", "Japanese", "Thailand", 4, travelers=2, budget="Medium", interests="Food, History")
    )
    print(test_result)