import streamlit as st
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os
import time
def create_table_html(df, start_idx, end_idx):
    table_html = """
    <style>
        table {
       
        border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            padding: 0.25rem 0.375rem;
            text-align: left;
            vertical-align: middle;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
   <table>
        <tr>""" + "".join(f"<th>{col}</th>" for col in df.columns)

    # Iterate through the rows and add the download buttons
    for idx, row in df.iloc[start_idx:end_idx].iterrows():
        table_html += "<tr>"
        for value in row:
            table_html += f"<td>{value}</td>"       
        table_html += "</tr>"
    
    table_html += "</table>"
    return table_html

def app():
    st.header("Exception Details")
    with open("style.css") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        
    load_dotenv()

    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')


    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    with st.spinner('Loading data...'):
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        query = 'SELECT * FROM [dbo].[Exception]'  # Replace with your actual query
        
        # Fetch data using pandas read_sql
        df = pd.read_sql(query, conn)
        df["From Email"] = df["FromEmail"]
        df.drop(columns=["FromEmail"], inplace=True)
        if 'CreatedDate' in df.columns:
     # Rename column and format the date in one step
          df['Created Date'] = pd.to_datetime(df['CreatedDate']).dt.strftime('%Y-%m-%d')  # Format as YYYY-MM-DD
          df.drop(columns=['CreatedDate'], inplace=True)  # Drop the old column

        df_filtered = df.drop(columns=["ExceptionId"])
        df_filtered.index += 1
        # Close the connection

        conn.close()
        csv = None
        # Convert the DataFrame to CSV for download
        if not df_filtered.empty:
          csv = df_filtered.to_csv(index=False).encode('utf-8')

        if csv:  
         st.download_button(
        label="⬇️ Download",
        data=csv,
        file_name="Exception_details.csv",
        mime="text/csv",
        key="download_csv"
    )
 
    toast_message = st.empty() 
    toast_message.success('Exception Details loaded successfully!')
    # st.dataframe(df)
    time.sleep(1)
    toast_message.empty()  
    if df_filtered.empty:
                st.warning("No exception records available.")
                return

    rows_per_page = 5

    # Calculate total pages
    total_pages = (len(df_filtered) // rows_per_page) + (1 if len(df_filtered) % rows_per_page > 0 else 0)

    # Initialize session state for page number
    if "page_number" not in st.session_state:
        st.session_state.page_number = 0

    # Show data for the current page
    start_idx = st.session_state.page_number * rows_per_page
    end_idx = start_idx + rows_per_page
    # st.table(df_filtered.iloc[start_idx:end_idx])
    table_html = create_table_html(df_filtered, start_idx, end_idx)
    
    st.markdown(table_html, unsafe_allow_html=True)
    # Pagination Buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Previous", disabled=(st.session_state.page_number == 0)):
            st.session_state.page_number -= 1
            st.rerun()

    with col3:
        if st.button("Next ➡️", disabled=(st.session_state.page_number >= total_pages - 1)):
            st.session_state.page_number += 1
            st.rerun()

    # Show current page number
    st.write(f"**Page {st.session_state.page_number + 1} of {total_pages}**")