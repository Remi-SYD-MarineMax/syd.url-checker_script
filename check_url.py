# Check URL for 404
# RUN: streamlit run check_url.py

import streamlit as st
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import subprocess
import sys
from datetime import datetime

# Make the app full width
st.set_page_config(
    page_title="URL CHECKER",
    layout="wide",
    initial_sidebar_state="auto"
)

st.title('URL CHECKER')

# Add this function to handle the recheck button click
def recheck_url(url):
    base_url, raw_status, status_code, status_label = check_url_status(url)
    # Update the results in session state
    for result in st.session_state.scan_results:
        if result["URL"] == url:
            result["Status Code"] = raw_status
            result["Display Status"] = status_code
            result["Status"] = status_label
            result["Last Checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.rerun()



def load_csv_from_file():
    # Open file dialog to select CSV file
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if file_path:
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return None
    return None


def check_url_status(url):
    try:
        base_url = url.split('?')[0]
        if base_url.startswith('http://'):
            base_url = base_url.replace('http://', 'https://')
        elif not base_url.startswith('https://'):
            base_url = 'https://' + base_url

        cmd = [
            'curl', '-I',
            '-H', 'Cache-Control: no-cache, no-store, must-revalidate',
            '-H', 'Pragma: no-cache',
            '-H', 'Expires: 0',
            base_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Extract status code and determine status label
        status_code = None
        status_label = "Unknown"
        status_icon = "❌"  # Default icon
        
        for line in result.stdout.splitlines():
            if line.startswith('HTTP/'):
                status_code = line.split()[1]
                if status_code == "200":
                    status_label = "OK"
                    status_icon = "✅"
                elif status_code.startswith('3'):
                    status_label = "Redirect"
                    status_icon = "⚠️"
                elif status_code.startswith('4'):
                    status_label = "Client Error"
                    status_icon = "❌"
                elif status_code.startswith('5'):
                    status_label = "Server Error"
                    status_icon = "❌"
                break
        
        return base_url, status_code, f"{status_icon} {status_code}", status_label

    except Exception as e:
        return base_url, "Error", "❌ Error", "Connection Error"

# Initialize session state to store scan results if not already present
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = []


# Function to determine row style based on status
def highlight_rows(row):
    if '✅' in row['Status Code']:
        return ['background-color: #e6ffe6'] * len(row)  # Light green
    elif '⚠️' in row['Status Code']:
        return ['background-color: #fff3e6'] * len(row)  # Light yellow
    elif '❌' in row['Status Code']:
        return ['background-color: #ffe6e6'] * len(row)  # Light red
    return [''] * len(row)





try:
    # Add file loading options
    st.markdown("### Choose CSV File Source")
    col1, col2 = st.columns(2)

    with col1:
        if st.button('Use Default File (urls.csv)'):
            try:
                df = pd.read_csv('urls.csv')
                urls = df.iloc[:, 0].tolist()
                total_urls = len(urls)
                st.session_state['urls'] = urls
                st.session_state['total_urls'] = total_urls
                st.success(f"Successfully loaded {total_urls} URLs from default file")
            except FileNotFoundError:
                st.error("Error: urls.csv file not found. Please ensure the file exists in the same directory as this script.")
                st.stop()

    with col2:
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                urls = df.iloc[:, 0].tolist()
                total_urls = len(urls)
                st.session_state['urls'] = urls
                st.session_state['total_urls'] = total_urls
                st.success(f"Successfully loaded {total_urls} URLs from uploaded file")
            except Exception as e:
                st.error(f"Error loading CSV file: {e}")
                st.stop()

    # Check if URLs are loaded
    if 'urls' not in st.session_state:
        st.info("Please select a file source to begin")
        st.stop()

    # Continue with your existing code
    urls = st.session_state['urls']
    total_urls = st.session_state['total_urls']
    
    # # Apply the styling
    # styled_df = df.style.apply(style_row, axis=1)
    
    # # Continue with your existing processing...

    # # Read URLs from CSV (assuming URLs are in first column)
    # df = pd.read_csv('urls.csv')
    # urls = df.iloc[:, 0].tolist()  # Get first column as list
    
    # total_urls = len(urls)
    # st.text(f"Total URLs found in CSV: {total_urls}")

    # # Check if URLs are loaded
    # if 'urls' not in st.session_state:
    #     st.info("Please select a file source to begin")
    #     st.stop()

    # # Continue with your existing code, but replace the initial URL loading with:
    # urls = st.session_state['urls']
    # total_urls = st.session_state['total_urls']

    # Then continue with your existing code for displaying total URLs and processing
    st.text(f"Total URLs found in CSV: {total_urls}")

    # Add explanation message
    st.markdown("""
    ### Range Selection
    Use the fields below to specify which portion of the URL list you want to check.
    Leave both fields empty to process the entire file.
    Note: Indexing starts at 0 (first URL = index 0)
    """)

    # Add input fields with columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        start_index = st.number_input(
            "Start checking from index:",
            min_value=0,
            max_value=total_urls - 1,
            value=None,
            help="Enter the index you want to start with (0 = first URL)"
        )

    with col2:
        end_index = st.number_input(
            "End checking at index:",
            min_value=0,
            max_value=total_urls - 1,
            value=None,
            help="Enter the index you want to end with"
        )

    # Add checkboxes for status codes
    st.markdown("### Select Status Codes to Display")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_200 = st.checkbox('2xx (Success)', value=True)
    with col2:
        show_300 = st.checkbox('3xx (Redirect)', value=True)
    with col3:
        show_400 = st.checkbox('4xx (Client Error)', value=True)
    with col4:
        show_500 = st.checkbox('5xx (Server Error)', value=True)

    # Handle empty inputs
    if start_index is None:
        start_index = 0
    if end_index is None:
        end_index = total_urls - 1

    # Validate input
    if start_index > end_index:
        st.error("Start index cannot be greater than end index!")
    else:
        urls_to_check = urls[start_index:end_index + 1]
        st.text(f"Number of URLs that will be processed: {len(urls_to_check)}")

        # Create a button to start the scan
        if st.button('Start URL Check'):
            # Clear previous results
            st.session_state.scan_results = []
            
            # Progress bar
            progress_bar = st.progress(0)
            
            # Process each URL
            for index, url in enumerate(urls_to_check):
                base_url, raw_status, status_code, status_label = check_url_status(url)
                
                # Store all results
                st.session_state.scan_results.append({
                    "URL": base_url,
                    "Status Code": raw_status,
                    "Display Status": status_code,
                    "Status": status_label,
                    "Last Checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Update progress bar
                progress_bar.progress((index + 1) / len(urls_to_check))

        # Display filtered results if we have any
        # Update the results display section:
        if st.session_state.scan_results:
            # Filter results based on checkbox selection
            filtered_results = []
            for result in st.session_state.scan_results:
                status_code = result["Display Status"]
                show_result = (
                    ('✅' in status_code and show_200) or
                    ('⚠️' in status_code and show_300) or
                    ('❌' in status_code and (
                        (result["Status Code"].startswith('4') and show_400) or
                        (result["Status Code"].startswith('5') and show_500) or
                        (result["Status Code"] == "Error" and show_400)
                    ))
                )
                if show_result:
                    filtered_results.append({
                        "URL": result["URL"],
                        "Status Code": result["Display Status"],
                        "Status": result["Status"],
                        # "Recheck": result["URL"]  # Pass URL to the button
                    })

            if filtered_results:
                results_df = pd.DataFrame(filtered_results)

                # Create the CSS for row colors
                css = """
                <style>
                    .row-success {
                        background-color: #90EE90;
                    }
                    .row-warning {
                        background-color: #FFE5B4;
                    }
                    .row-error {
                        background-color: #FFB6C1;
                    }
                </style>
                """
                st.markdown(css, unsafe_allow_html=True)

                # Style the dataframe
                styled_df = results_df.style.apply(highlight_rows, axis=1)
                
                # Display results in a table
                st.dataframe(
                    styled_df,
                    column_config={
                        "URL": st.column_config.LinkColumn(
                            "URL",
                            width=600,
                            help="Click to open URL in new tab"
                        ),
                        "Status Code": st.column_config.TextColumn(
                            "Status Code",
                            width=150
                        ),
                        "Status": st.column_config.TextColumn(
                            "Status",
                            width=200
                        ),
                        # "Recheck": st.column_config.LinkColumn(
                        #     "Recheck",
                        #     help="Click to recheck this URL",
                        #     width=100,
                        #     on_click=recheck_url
                        # )
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No results to display for the selected status codes.")
            
            # Display summary
            st.text(f"Total URLs checked: {len(st.session_state.scan_results)}")
            error_count = len([r for r in st.session_state.scan_results if '❌' in r['Display Status']])
            st.text(f"Number of errors found: {error_count}")

except FileNotFoundError:
    st.error("Error: urls.csv file not found. Please ensure the file exists in the same directory as this script.")
