import streamlit as st
import pandas as pd
from supabase import create_client
import google.generativeai as genai
from streamlit_option_menu import option_menu


# 1. Initialize "Memory" (Session State)
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "df_results" not in st.session_state:
    st.session_state.df_results = pd.DataFrame()

# --- TOP NAVIGATION MENU ---
st.set_page_config(page_title="TraDatAnalytix", layout="wide")

# --- TOP NAVIGATION MENU ---
# This creates a clean, horizontal bar at the top
choice = option_menu(
    menu_title=None,  # Hide the menu title
    options=["Swing Momentum", "Stock Analysis", "Settings"], # Menu options
    icons=["house", "graph-up-arrow", "gear"], # Bootstrap icons
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
)



# Supabase Setup
url = "https://vgicevfkzjdfwziwoubo.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZnaWNldmZrempkZnd6aXdvdWJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc0MjYzMDgsImV4cCI6MjA4MzAwMjMwOH0.GOyGvHTyYBNqsamPt6_N9OJN4Yv_HXZP6tnTTkOeGdk"
supabase = create_client(url, key)

# Gemini Setup
genai.configure(api_key="AIzaSyAWUxpAfyQEllH_Jt_vVZrtposZXybbj7U")
model = genai.GenerativeModel("gemini-2.5-flash") # Note: Adjusted to currently available flash model



def fetch_all_supabase_data(table_name, batch_size=1000):
    """
    Fetches all rows from a Supabase table by paginating through records.
    """
    all_rows = []
    start_index = 0
    
    while True:
        # Fetch a chunk of data
        response = (
            supabase.table(table_name)
            .select("*")
            .range(start_index, start_index + batch_size - 1)
            .execute()
        )
        
        chunk = response.data
        all_rows.extend(chunk)
        
        # If we got fewer rows than requested, we've reached the end
        if len(chunk) < batch_size:
            break
            
        start_index += batch_size
        
    return pd.DataFrame(all_rows)

# Usage:
df = fetch_all_supabase_data("daily_scans_test")
df['date_column'] = pd.to_datetime(df['created_at'])


# Get unique dates for the slider/picker range (optional but helpful)
min_date = df['date_column'].min().date()
max_date = df['date_column'].max().date()





if choice == "Swing Momentum":
    
    # 1. Initialize Session State (at the top of the choice)
    if "df_results" not in st.session_state:
        st.session_state.df_results = None
    if "last_date" not in st.session_state:
        st.session_state.last_date = None

    with st.container(border=False):
        with st.form("data_filter_form"):
            col1, col2 = st.columns([5, 1])
            with col1:
                selected_date = st.date_input(
                    "Select a date to view scans:",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date
                )
            with col2:
                st.write(" ") 
                submit_button = st.form_submit_button(label="🚀 Refresh Data")

    # 2. DATA PROCESSING (Only runs on button click)
    if submit_button:
        mask = df['date_column'].dt.date == selected_date
        # Save to session state so it survives the row-click rerun
        st.session_state.df_results = df[mask].copy()
        st.session_state.last_date = selected_date

    # 3. DISPLAY LOGIC (Always runs if data exists in session state)
    if st.session_state.df_results is not None:
        res_df = st.session_state.df_results
        
        if not res_df.empty:
            # Metrics
            a, b = st.columns([3, 3], gap="medium")
            a.metric(f"Stocks for {st.session_state.last_date}", len(res_df), border=True)

            left_col, right_col = st.columns([2, 3], gap="medium")

            with a:
                # Prepare columns for display
                display_df = res_df[['name', 'Breakout_price', 'Relative Strength (vs Nifty 50)', 'Days since consolidation']].rename(
                    columns={'name': 'Stock Name', 'Breakout_price': 'Price'}
                )

                # Dataframe Selection
                event = st.dataframe(
                    display_df,
                    key="stock_table",
                    on_select="rerun",
                    selection_mode="single-row",
                    use_container_width=True,
                    hide_index=True
                )

            with b:
                # 4. Detailed Analysis (Survives reruns because it's outside the submit block)
                selected_indices = event.selection.get("rows", [])

                if selected_indices:
                    selected_name = display_df.iloc[selected_indices[0]]['Stock Name']
                    # st.write("---")
                    st.subheader(f"🎯 Analysis for {selected_name}")
                    st.info(f"Detailed view for **{selected_name}** is Coming Soon!")
                    top_left_cell = st.container(
                        border=True, height="stretch", vertical_alignment="center"
                    )

                    with top_left_cell:
                        horizon_map = {
                        "1 Months": "1mo",
                        "3 Months": "3mo",
                        "6 Months": "6mo",
                        "1 Year": "1y",
                        "5 Years": "5y",
                        "10 Years": "10y",
                        "20 Years": "20y",
                    }
                        # Buttons for picking time horizon
                        horizon = st.pills(
                            "Time horizon",
                            options=list(horizon_map.keys()),
                            default="6 Months",
                        )


                    # Add your charts or more stats here!
                else:
                    st.write("💡 *Click a row in the table above to view details.*")
        else:
            st.warning("Click Refresh Data")











































# if choice == "Swing Momentum":
        
#         with st.container(border=False):
#             # st.subheader("🛠️ Data Controls")
#             # Using a form so the app only refreshes on 'Submit'
#             with st.form("data_filter_form"):
#                 col1, col2 = st.columns([5, 1])
                
#                 with col1:
#                     selected_date = st.date_input(
#                             "Select a date to view scans:",
#                             value=max_date, # Default to the most recent date
#                             min_value=min_date,
#                             max_value=max_date
#                         )

#                 with col2:
#                     st.write(" ") # Spacer for alignment
#                     submit_button = st.form_submit_button(label="🚀 Refresh Data")

#         if submit_button:

#             a, b, c = st.columns(3)

#             # 4. Filter the dataframe
#             # We compare the .dt.date version of the column to the selected_date
#             mask = df['date_column'].dt.date == selected_date
#             filtered_df = df[mask]

#             st.session_state.df_results = filtered_df.copy()
#             st.session_state.data_loaded = True

#             if st.session_state.data_loaded and not st.session_state.df_results.empty:
    
#                 display_df = filtered_df[['name', 'Breakout_price','Relative Strength (vs Nifty 50)', 'Days since consolidation']].rename(
#                 columns={
#                         'name': 'Stock Name',
#                         'Breakout_price': 'Price',
#                         'Relative Strength (vs Nifty 50)': 'Relative Strength (vs Nifty 50)',
#                             'Days since consolidation' : 'Days since consolidation'
#                     })

#                 # 5. Display results
#                 st.write(f"### Results for {selected_date}")
#                 a.metric(f"### # Stocks for {selected_date}", len(filtered_df), border = True)

#                 if not filtered_df.empty:
#                     # st.table(filtered_df, border="horizontal")
#                     # 3. Create the interactive dataframe
#                     event = st.dataframe(
#                         display_df,
#                         key="stock_table",
#                         on_select="rerun",
#                         selection_mode="single-row", # Simplified for row selection
#                         use_container_width=True,
#                         hide_index=True
#                     )

#                     # 4. Logic to display the selected Stock Name
#                     selected_indices = event.selection["rows"]

#                     if selected_indices:
#                         # Get the names based on the selected row indices
#                         selected_names = display_df.iloc[selected_indices]['Stock Name'].tolist()
                        
#                         st.write("---")
#                         st.subheader("🎯 Selected Stocks for Analysis")
                        
#                         # Display them nicely
#                         for name in selected_names:
#                             st.info(f"Viewing detailed analysis for: **{name}**")
#                     else:
#                         st.write("💡 *Click a row in the table above to view details.*")

#                 # st.dataframe(display_df, hide_index=True, use_container_width=True)
 
                
                
#             else:
#                 st.warning("No data found for the selected date.")

