import streamlit as st
import asyncio
from fpdf import FPDF
from main import run_travel_workflow

def create_pdf_bytes(itinerary_text: str):
    """Converts the itinerary text into a PDF byte stream for downloading."""
    pdf = FPDF()
    pdf.add_page()

    # fpdf2 has built-in fonts, we'll use standard Helvetica
    pdf.add_font("DejaVu", style="", fname="DejaVuSans.ttf")
    pdf.set_font("DejaVu", size=12)
    # Clean up some markdown artifacts (like asterisks) so it looks cleaner in PDF
    clean_text = itinerary_text.replace("**", "").replace("*", "-")

    # Write the text to the PDF
    # multi_cell automatically handles line breaks
    pdf.multi_cell(0, 8, txt=clean_text)

    # Return the raw PDF bytes
    return bytes(pdf.output())

# --- UI Configuration ---
st.set_page_config(page_title="AI Travel Assistant", page_icon="✈️", layout="centered")

st.title("Welcome to Safiri | Your AI travel planner")
st.write("Stop planning, start exploring.")

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("Trip parameters")

    starting_location = st.text_input("Flying From", placeholder="e.g., London")
    nationality = st.text_input("Your Nationality / Passport", placeholder="e.g., Kenyan")
    destination = st.text_input("Destination City", placeholder="e.g., Madrid")

    days = st.number_input("Duration (Days)", min_value=1, max_value=30, value=5)
    travelers = st.number_input("Travelers", min_value=1, max_value=10, value=2)
    budget = st.selectbox("Budget Tier", ["Low", "Medium", "High"])
    interests = st.text_area("Passions / Interests", placeholder="Museums, food, live music...")

    submit_btn = st.button("Generate your Itinerary", type="primary", use_container_width=True)

if submit_btn:
    if not destination.strip():
        st.error("Please provide a destination city!")
    else:
        # Visual loading statuses representing our multi-layered engineering workflow
        with st.status("Orchestrating AI Agents...", expanded=True) as status:

            st.write(
                "⚡ [PHASE 1] Executing concurrent network requests (Weather API + Research Agent + Culture Agent)...")
            # We wrap our async call inside asyncio.run() to bridge it into Streamlit
            final_output = asyncio.run(
                run_travel_workflow(starting_location, nationality, destination, days, travelers, budget, interests)
            )

            status.update(label="Compilation Engine Finished successfully!", state="complete", expanded=False)

        st.success(f"Here is your tailored plan for {destination}!")
        st.markdown(final_output)

        # --- NEW: PDF Export Feature ---
        st.divider()  # Adds a nice visual line
        st.subheader("Take it offline")
        st.write("Download this itinerary as a PDF to view it on your flight.")

        # Only create the PDF if final_output actually has text
        if final_output:
            pdf_data = create_pdf_bytes(final_output)

            st.download_button(
                label="Download Itinerary as PDF",
                data=pdf_data,
                file_name=f"Safiri_{destination}_Travel_Plan.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.error("Warning: The final output was empty. PDF generation failed.")
