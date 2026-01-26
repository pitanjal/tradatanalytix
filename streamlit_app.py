import streamlit as st
import pandas as pd
from supabase import create_client
import google.generativeai as genai
from streamlit_option_menu import option_menu
from streamlit_echarts import st_echarts
from candlestick_chart import candlestick_chart_display
from stock_data_fun import getHistData

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

# Upstox Master
fileUrl ='https://assets.upstox.com/market-quote/instruments/exchange/complete.csv.gz'
symboldf = pd.read_csv(fileUrl)
bse_full_stocks = symboldf[symboldf['exchange'].str.contains('BSE', case=False, na=False) & symboldf['instrument_type'].str.contains('EQ', case=False, na=False) &
                           symboldf['last_price'] > 0]
symboldf2 = bse_full_stocks[['instrument_key', 'name']]
# st.dataframe(symboldf2)



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

            

            with a:
                
                left_col, right_col = st.columns([2, 3], gap="small")
                left_col.metric(f"Stocks for {st.session_state.last_date}", len(res_df), border=True)
                right_col.metric(f"Stock Market Sentiment", "Bullish", border=True)
                

                # Prepare columns for display -- 'Relative Strength (vs Nifty 50)',
                display_df = res_df[['name', 'Breakout_price', 'Days since consolidation']].rename(
                    columns={'name': 'Stock Name', 'Breakout_price': 'Price', 'Days since consolidation' : 'Range Days'}
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
                
                selected_indices = event.selection.get("rows", [])

                if selected_indices:
                    selected_name = display_df.iloc[selected_indices[0]]['Stock Name']
                    match = symboldf2[symboldf2['name'] == selected_name]
                    if not match.empty:
                        # 2. Extract the key safely
                        instrument_key = match['instrument_key'].iloc[0]
                        df_stock = getHistData(instrument_key)
                        # st.write(f"The key for {selected_name} is: {instrument_key}")
                    else:
                        st.error(f"Symbol '{selected_name}' not found in the list.")
                    top_left_cell = st.container(
                        border=True, height="stretch", vertical_alignment="center"
                    )

                    with top_left_cell:
                        st.subheader(f"{selected_name}")


                        # 1. Ensure the date column is datetime-ready
                        df_stock['date'] = pd.to_datetime(df_stock['date'])

                        # 2. Extract values
                        dfohlc = df_stock[["close", "open", "low", "high"]]

                        # 3. Convert to JSON-serializable lists
                        datelist = df_stock['date'].dt.strftime('%Y-%m-%d').tolist()
                        ohlclist = dfohlc.to_numpy().tolist()

                        # 4. Pass to chart
                        printcandlechart = candlestick_chart_display(datelist, ohlclist)

                        st_echarts(options=printcandlechart, height="400px")

                else:
                    st.write("💡 *Click a row in the table above to view details.*")
        else:
            st.warning("Click Refresh Data")

