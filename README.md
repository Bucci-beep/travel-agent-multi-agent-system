# ✈️ Safiri: Multi-Agent AI Travel Concierge

An asynchronous, multi-agent travel planning application built with Python, Streamlit, and Llama 3 (via Groq). 

Safiri goes beyond standard LLM wrappers by orchestrating multiple specialized AI agents concurrently. It researches destinations, fetches live weather data, extracts cultural nuances, and calculates visa/flight budgets based on user nationality—compiling it all into a clean UI and an offline-ready PDF.


## 🧠 Engineering Highlights & Architecture

Building robust GenAI applications requires treating LLMs as volatile components within a strict software architecture. This project highlights several production-minded engineering patterns:

* **Asynchronous Orchestration:** Utilized `asyncio` and `httpx` to execute independent agent tasks (Research, Culture, Live Weather API) in parallel, drastically reducing latency compared to sequential generation.
* **Edge-Case Resilience:** Engineered defensive fallback logic within the agent class to gracefully handle silent `None` type returns and hallucinated tool-calls from the LLM, preventing application crashes.
* **Dynamic Context Injection:** Developed a dynamic prompting pipeline that routes the user's specific passport/nationality to a dedicated Budget Agent for highly accurate visa requirement calculations.
* **Custom Unicode Document Generation:** Implemented a sanitization and custom font-rendering pipeline using `fpdf2` (DejaVu Sans) to securely parse unpredictable LLM text (including phonetic spellings and foreign characters) into downloadable PDFs without triggering encoding exceptions.

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python 3.10+
* **LLM Engine:** Groq API (Llama-3.1-8b-instant for fast parallel research, Llama-3.3-70b-versatile for complex final synthesis)
* **APIs:** OpenWeatherMap API
* **Document Generation:** `fpdf2`

## ⚙️ Local Setup & Installation

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/safiri-ai-travel.git](https://github.com/yourusername/safiri-ai-travel.git)
cd safiri-ai-travel
**2. Create a virtual environment**
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

**3. Install dependencies**
pip install -r requirements.txt

**4. Configure Environment variables**
GROQ_API_KEY="your_groq_api_key"
WEATHER_API_KEY="your_openweathermap_api_key"

**5. Add the unicode Font**
Ensure DejaVuSans.ttf is present in the root directory for PDF generation to work correctly.

**6. Run the application**
streamlit run app.py

🔄 Agentic Workflow
Phase 1 (Parallel): * Research Agent: Scours for hidden gems and specific hotel recommendations.
Culture Agent: Extracts phonetic greetings and local customs.
Weather API: Fetches deterministic live weather data.
Phase 2 (Sequential): * Activity Agent: Ingests Phase 1 data to build a day-by-day itinerary constrained by the live weather.
Budget Agent: Calculates costs, flights, and visa fees based on the departure city and user nationality.
Phase 3 (Synthesis): * Final Assistant: Compiles the raw data pipeline into a highly readable, 700-word markdown structure.
