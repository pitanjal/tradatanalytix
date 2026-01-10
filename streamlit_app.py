import streamlit as st
import pandas as pd
from supabase import create_client
import google.generativeai as genai

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="Stock Data Assistant", layout="wide")
st.title("📈 Stock Data Chatbot")

# Supabase Setup
url = "https://vgicevfkzjdfwziwoubo.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZnaWNldmZrempkZnd6aXdvdWJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc0MjYzMDgsImV4cCI6MjA4MzAwMjMwOH0.GOyGvHTyYBNqsamPt6_N9OJN4Yv_HXZP6tnTTkOeGdk"
supabase = create_client(url, key)

# Gemini Setup
genai.configure(api_key="AIzaSyAWUxpAfyQEllH_Jt_vVZrtposZXybbj7U")
model = genai.GenerativeModel("gemini-2.5-flash") # Note: Adjusted to currently available flash model

# --- 2. DATA FETCHING ---
@st.cache_data(ttl=600) # Cache data for 10 minutes
def get_data():
    response = supabase.table("daily_scans_test").select("*").execute()
    return pd.DataFrame(response.data)

df_supabase = get_data()

# Optional: Show data in a sidebar toggle
with st.sidebar:
    if st.checkbox("Show Raw Data"):
        st.write(df_supabase)

# --- 3. CHATBOT LOGIC ---

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about breakout stocks..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare context for the AI
    # We convert dataframe to markdown/CSV for the prompt
    # df_context = df_supabase.to_markdown() 
    
    full_prompt = f"""
    Basis this data:
    {df_supabase}
    
    Column "name" is stock name and most important parameter for this chatbot response. 
    'id' is not important to the user. 'created_at' is the date when scan ran and picked the stock names.
    Any query relating to days consolidation, the column of reference is 'Days since consolidation', which shows number of days after which the stock is breaking out and the 'Breakout price' is the current price at which the breakout is happening. 
    Column 'Relative Strength (vs Nifty 50)' indicates the relative strength of the stock against Nifty 50, a value greater than 0, indicates out-performance and a good stock, higher the value means higher the out-performance and vice-versa.
    Question: {prompt}.
    
    Give short crisp to the point answer.
    """

    try:
        # Generate Response
        with st.chat_message("assistant"):
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    
    except Exception as e:
        st.error(f"Error generating response: {e}")

