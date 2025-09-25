import streamlit as st
from router_logic import route_query
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Dynamic LLM Router",
    page_icon=":traffic_light:",
    layout="wide"
)

# --- Custom CSS (NEW STYLES) ---
st.markdown("""
<style>
    /* Style for the main containers in dark mode */
    .st-emotion-cache-1r4qj8v {
        border: 1px solid #31333f; /* A subtle border for dark mode */
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    /* Style for the submit button */
    .stButton>button {
        background-color: #6c5ce7; /* A modern, vibrant purple */
        color: white;
        border-radius: 10px; /* More rounded corners */
        padding: 10px 20px;
        border: none;
        width: 100%;
        font-weight: bold;
        transition: background-color 0.3s ease; /* Smooth hover effect */
    }
    .stButton>button:hover {
        background-color: #5948d6; /* A slightly darker shade for hover */
    }
</style>
""", unsafe_allow_html=True)


# --- State Initialization ---
if 'query_text' not in st.session_state:
    st.session_state.query_text = ""
if 'query_cache' not in st.session_state:
    st.session_state.query_cache = {}
if 'submitted_query' not in st.session_state:
    st.session_state.submitted_query = ""

# --- Helper Function for Buttons ---
def run_example_query(example_text):
    """Sets the query text in the input box and also triggers a run."""
    st.session_state.query_text = example_text
    st.session_state.submitted_query = example_text

# --- Sidebar ---
with st.sidebar:
    st.title("Dynamic LLM Router")
    st.info(
        "This app intelligently routes your query to the most suitable "
        "Language Model (LLM) based on its complexity."
    )
    st.divider()
    st.subheader(":rocket: Try These Examples")
    
    st.button("Simple: Translation", on_click=run_example_query, args=["Translate 'Good morning' to Arabic"])
    st.button("Medium: Explanation", on_click=run_example_query, args=["Explain in a paragraph how a car engine works"])
    st.button("Advanced: Coding", on_click=run_example_query, args=["Write a Python script to scrape a website and save the headlines to a CSV file"])
    
    st.divider()
    st.caption("Powered by Youssef Mustafa")

# --- Main Page ---
st.title(":traffic_light: Dynamic LLM Router")
st.markdown("Ask any question, and the router will intelligently select the best expert to answer it!")

# The text area now gets its value from session state
user_query_input = st.text_area(
    "Enter your question here:", 
    value=st.session_state.query_text, 
    height=150, 
    key="query_input"
)

if st.button("Get Answer"):
    if user_query_input:
        st.session_state.submitted_query = user_query_input
    else:
        st.error("Please enter a question first.")

if st.session_state.submitted_query:
    query_to_run = st.session_state.submitted_query
    
    with st.spinner("⏳ Analyzing query and routing to the best expert..."):
        start_time = time.time()
        final_answer, logs = route_query(query_to_run, st.session_state.query_cache)
        end_time = time.time()
        processing_time = end_time - start_time

    st.session_state.submitted_query = ""

    classification = "N/A"
    if logs:
        for line in logs.split('\n'):
            if "Query classified as:" in line:
                classification = line.split(': ')[1].strip()
                break

    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.container(border=True):
            st.subheader(":white_check_mark: Final Answer")
            st.markdown(final_answer)

    with col2:
        with st.container(border=True):
            st.subheader(":brain: Router's Decision")
            
            if classification == "Simple":
                st.success(f"**Classification:** {classification}")
            elif classification == "Medium":
                st.warning(f"**Classification:** {classification}")
            elif classification == "Advanced":
                st.info(f"**Classification:** {classification}")
            
            st.metric(label=":timer_clock: Response Time", value=f"{processing_time:.2f} seconds")

            with st.expander(":mag: View Details (Logs)"):
                st.text_area("Execution Logs", logs, height=250, disabled=True)

