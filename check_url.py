# Check URL for 404
# RUN: streamlit run check_url.py

import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import sys

st.title('URL CHECKER')

# Set limit for URLs to process
LIMIT = 6

# Function to check URL status using curl
def check_url_status(url):
    try:
        # Remove everything after the ? in the URL
        base_url = url.split('?')[0]

        # Force HTTPS by replacing http:// with https://
        if base_url.startswith('http://'):
            base_url = base_url.replace('http://', 'https://')
        elif not base_url.startswith('https://'):
            # If no protocol is specified, add https://
            base_url = 'https://' + base_url

        # Run curl command with -I (head request) and capture output
        # The -H flags add headers to prevent caching
        cmd = [
            'curl', '-I',
            '-H', 'Cache-Control: no-cache, no-store, must-revalidate',
            '-H', 'Pragma: no-cache',
            '-H', 'Expires: 0',
            base_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Check if '404' appears in the response
        is_404 = '404' in result.stdout
        
        # Display URL with emoji indicator
        if is_404:
            st.markdown(f"{base_url} :x:", unsafe_allow_html=True)
        else:
            st.markdown(f"{base_url} :white_check_mark:", unsafe_allow_html=True)

        return is_404
    except:
        # If any error occurs, treat as failed URL and show red cross
        st.markdown(f"{base_url} :x:", unsafe_allow_html=True)
        return True

# Load URLs from CSV at startup
try:
    # Read URLs from CSV (assuming URLs are in first column)
    df = pd.read_csv('urls.csv')
    urls = df.iloc[:, 0].tolist()  # Get first column as list
    
    # Display total number of URLs found in CSV
    st.text(f"Total URLs found in CSV: {len(urls)}")
    
    # Limit the number of URLs to process
    urls = urls[:LIMIT]
    st.text(f"Number of URLs that will be processed (LIMIT): {len(urls)}")

    # Create a button to start the process
    if st.button('Start URL Check'):
        # List to store URLs with 404 status
        broken_urls = []
        
        # Progress bar
        progress_bar = st.progress(0)
        
        # Process each URL
        for index, url in enumerate(urls):
            if check_url_status(url):
                broken_urls.append(url)
            
            # Update progress bar
            progress_bar.progress((index + 1) / len(urls))
        
        # Display results
        st.text(f"Total URLs checked: {len(urls)}")
        st.text(f"Number of 404 errors found: {len(broken_urls)}")
        
        # if broken_urls:
        #     st.text("URLs returning 404:")
        #     for url in broken_urls:
        #         st.text(url)
    else:
        st.text("Click the button above to start checking URLs")

except FileNotFoundError:
    st.error("Error: urls.csv file not found")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
