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
    
    Breakout price is latest close price crossing 52 Week High price and name is stock name.
    
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




# import streamlit as st
# import pandas as pd
# from supabase import create_client
# import google.generativeai as genai

# # 1. Setup Connection
# url = "https://vgicevfkzjdfwziwoubo.supabase.co"
# key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZnaWNldmZrempkZnd6aXdvdWJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc0MjYzMDgsImV4cCI6MjA4MzAwMjMwOH0.GOyGvHTyYBNqsamPt6_N9OJN4Yv_HXZP6tnTTkOeGdk"
# supabase = create_client(url, key)

# # Fetch data
# response = supabase.table("daily_scans_test").select("*").execute()

# # Convert to Pandas DataFrame
# df_supabase = pd.DataFrame(response.data)


# st.write(df_supabase)


# genai.configure(api_key="AIzaSyAWUxpAfyQEllH_Jt_vVZrtposZXybbj7U")
# model = genai.GenerativeModel("gemini-2.5-flash")


# # 3. Helper function to ask questions
# def ask_dataframe(query, dataframe):
#     # We pass the dataframe as a string (CSV format is token-efficient)
#     prompt = f"""
#     Basis this data:
#     {dataframe}
    
#     Breakout price is lastest close price crossing 52 Week High price and name is stock name.
    
#     Question: {query}.
    
#     Give short crisp to the point answer.
    
#     """
#     response = model.generate_content(prompt)
#     return response.text

# # 4. Example usage
# answer = ask_dataframe("Why is Reliance industries not in this list", df_supabase)



