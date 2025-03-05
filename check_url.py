# Check URL for 404
# RUN: streamlit run check_url.py

import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import sys

st.title('URL CHECKER')


# Function to check URL status using curl (keeping your existing function unchanged)
def check_url_status(url, show_successful):
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
        is_404 = '404' in result.stdout
        
        if is_404:
            st.markdown(f"{base_url} :x:", unsafe_allow_html=True)
        elif show_successful:
            st.markdown(f"{base_url} :white_check_mark:", unsafe_allow_html=True)

        return is_404
    except:
        st.markdown(f"{base_url} :x:", unsafe_allow_html=True)
        return True

# Load URLs from CSV at startup
try:
    # Read URLs from CSV (assuming URLs are in first column)
    df = pd.read_csv('urls.csv')
    urls = df.iloc[:, 0].tolist()  # Get first column as list
    
    # Display total number of URLs found in CSV
    total_urls = len(urls)
    st.text(f"Total URLs found in CSV: {total_urls}")

    # Add explanation message
    st.markdown("""
    ### Range Selection
    Use the fields below to specify which portion of the URL list you want to check.
    Leave both fields empty to process the entire file.
    """)

    # Add input fields with columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        start_index = st.number_input(
            "Start checking from URL number:",
            min_value=1,
            max_value=total_urls,
            value=None,
            help="Enter the number of the URL you want to start with (1 = first URL)"
        )

    with col2:
        end_index = st.number_input(
            "End checking at URL number:",
            min_value=1,
            max_value=total_urls,
            value=None,
            help="Enter the number of the URL you want to end with"
        )

    # Add checkbox for displaying successful URLs
    show_successful = st.checkbox('Show successful URLs', value=True, 
                                help="When checked, both successful and failed URLs will be displayed. When unchecked, only failed URLs are shown.")

    # Handle empty inputs
    if start_index is None:
        start_index = 1
    if end_index is None:
        end_index = total_urls

    # Validate input
    if start_index > end_index:
        st.error("Start number cannot be greater than end number!")
    else:
        # Adjust indices for 0-based indexing
        urls_to_check = urls[start_index-1:end_index]
        st.text(f"Number of URLs that will be processed: {len(urls_to_check)}")

        # Create a button to start the process
        if st.button('Start URL Check'):
            # List to store URLs with 404 status
            broken_urls = []
            
            # Progress bar
            progress_bar = st.progress(0)
            
            # Process each URL
            for index, url in enumerate(urls_to_check):
                if check_url_status(url, show_successful):
                    broken_urls.append(url)
                
                # Update progress bar
                progress_bar.progress((index + 1) / len(urls_to_check))
            
            # Display results
            st.text(f"Total URLs checked: {len(urls_to_check)}")
            st.text(f"Number of 404 errors found: {len(broken_urls)}")
        else:
            st.text("Click the button above to start checking URLs")

except FileNotFoundError:
    st.error("Error: urls.csv file not found")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
