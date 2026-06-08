import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def run(self, task):

        print(f"{self.name} is working...")

        response = client.chat.completions.create(
            model = "qwen/qwen3-32b",

            messages=[

            {
                "role": "system",
                "content": self.role
            },

            {
                "role": "user",
                "content": task
            }
        ],
        max_tokens= 1200

        )

        return response.choices[0].message.content

research_agent = Agent(
    "Research Agent",
    """
    You are an expert travel researcher.
    Your job:
    - Find popular attractions
    - Find hidden gems
    - Suggest local experiences
    - Recommend best places
    """
)

activity_agent = Agent(
    "Activity Planner Agent",
    """
    You are a professional travel planner.
    Your job:
    - Create daily activities
    - Plan sightseeing
    - Recommend food experiences
    - Organize activities logically
    """
)

budget_agent = Agent(
    "Budget Agent",
    """
    You are a travel budget expert.
    Calculate:
    - Estimated flight cost
    - Visa requirements
    - Visa fees if needed
    - Hotel cost
    - Food expenses
    - Transport cost
    - Activity costs
    Create an approximate total trip budget.
    Keep response short.
    """
)

final_agent = Agent(
    "Final Travel Assistant",
    """
    You are a professional travel planner.
    Create the final itinerary.
    Include:
    1. Short trip overview
    2. Visa information
    3. Estimated flight cost
    4. Day-wise plan
    5. Food suggestions
    6. Total estimated budget
    Keep everything under 700 words.
    """
)


#Get User Travel Details

starting_location = input(
    "Where are you flying from? "
)

destination = input(
    "Where do you want to travel? "
)

days = input(
    "How many days is your trip? "
)

travelers = input(
    "How many travelers? "
)

budget = input(
    "What is your budget? (low/medium/high) "
)


interests = input(
    "What are your interests? "
)


# Create request for AI agents

user_request = f"""

Create a travel plan with these details:

Flying From:
{starting_location}

Destination:
{destination}

Trip Duration:
{days} days

Number of Travelers:
{travelers}

Budget Level:
{budget}

Interests:
{interests}

Include:
- Visa requirements
- Estimated flight cost
- Places to visit
- Activities
- Food recommendations
- Total estimated budget

"""

print("\nCreating your AI travel plan...\n")


#Multi-Agent Workflow

#Agent 1 researches destination
research = research_agent.run(
    user_request
)
print("\n--- Research Completed ---")

#Agent 2 creates activities
activities = activity_agent.run(
    research
)
print("\n--- Activities Planned ---")

#Agent 3 calculates budget
budget = budget_agent.run(
    activities
)
print("\n--- Budget Created ---")

#Agent 4 creates final itinerary
final_plan = final_agent.run(
    f"""
    Research:
    {research}

    Activities:
    {activities}

    Budget:
    {budget}

    Create final travel plan.
    """
)

print("\n==========================")
print(" FINAL TRAVEL PLAN")
print("==========================\n")

print(final_plan)