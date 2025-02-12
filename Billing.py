import base64
import streamlit as st
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Function to generate a PDF
def generate_pdf(row):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(100, 750, "Billing Details")
    
    y = 720
    for key, value in row.items():
        pdf.drawString(100, y, f"{key}: {value}")
        y -= 20
    
    pdf.save()
    buffer.seek(0)
    return buffer


# Function to create an HTML table with buttons
def create_table_html(df, start_idx, end_idx):
    # Start creating the HTML table
    table_html = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            margin-right: 0;
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
        .hidden-column {
            display: none;
        }
        .tooltip {
            position: relative;
            display: inline-block;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 400px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 5px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Position above the tooltip */
            left: 50%;
            margin-left: -100px; /* Center the tooltip */
            opacity: 0;
            transition: opacity 0.3s;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
    </style>
    <table>
        <tr>""" + "".join(f"<th>{col}</th>" for col in df.columns if col != "FilePath") + "<th>Download</th></tr>"

    # Iterate through the rows of the DataFrame
    for idx, row in df.iloc[start_idx:end_idx].iterrows():
        table_html += "<tr>"
        
        # Add each column value to the table (excluding FilePath)
        for col, value in row.items():
            if col == "FilePath":
                continue  # Skip rendering the FilePath column
            elif col == "Remark":  
                truncated_text = value[:50] + "..." if len(value) > 50 else value
                tooltip = f"""
                <div class="tooltip">
                    {truncated_text}
                    <span class="tooltiptext">{value}</span>
                </div>
                """
                table_html += f"<td>{tooltip}</td>"
            else:
                table_html += f"<td>{value}</td>"

        # Handle the FilePath for the download button
        file_path = row.get('FilePath', '#') 
        file_name = f"Billing_{idx + 1}.pdf"  
        table_html += f'<td><a href="{file_path}" download="{file_name}">⬇️</a></td>'
        table_html += "</tr>"
    
    table_html += "</table>"
    return table_html


def app():
    st.header("Billing Details")
    with open("style.css") as f:
        css = f.read()

    # Inject the CSS
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    load_dotenv()

    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')

    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    with st.spinner('Loading data...'):
        conn = pyodbc.connect(conn_str)
        query = 'SELECT * FROM [dbo].[bill]'  
        
        df = pd.read_sql(query, conn)
        df["Bill No"] = df["BillNo"]
        df.drop(columns=["BillNo"], inplace=True)
        df["Customer Name"] = df["CustomerName"]
        df.drop(columns=["CustomerName"], inplace=True)
        df["Total Amount"] = df["TotalAmount"]
        df.drop(columns=["TotalAmount"], inplace=True)
        df["Bill Date"] = df["BillDate"]
        df.drop(columns=["BillDate"], inplace=True)
        df_filtered = df.drop(columns=["BillId"])
        df_filtered.index += 1
        conn.close()
    
    toast_message = st.empty() 
    toast_message.success('Billing Details loaded successfully!')
    time.sleep(1)
    toast_message.empty()  
    if df_filtered.empty:
                st.warning("No billing records available.")
                return
    rows_per_page = 5
    total_pages = (len(df_filtered) // rows_per_page) + (1 if len(df_filtered) % rows_per_page > 0 else 0)

    if "page_number" not in st.session_state:
        st.session_state.page_number = 0

    start_idx = st.session_state.page_number * rows_per_page
    end_idx = start_idx + rows_per_page

    # Display styled table
    table_html = create_table_html(df_filtered, start_idx, end_idx)
    st.markdown(table_html, unsafe_allow_html=True)

    # Pagination
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Previous", disabled=(st.session_state.page_number == 0)):
            st.session_state.page_number -= 1
            st.rerun()

    with col3:
        if st.button("Next ➡️", disabled=(st.session_state.page_number >= total_pages - 1)):
            st.session_state.page_number += 1
            st.rerun()

    st.write(f"**Page {st.session_state.page_number + 1} of {total_pages}**")
 
       