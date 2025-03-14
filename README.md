# url_checker
Check 404 error from a list of URL within a csv file.

# Requirements
You need to have the following packages install to run the app
- Python
- Streamlit (https://streamlit.io/#install)

# Create a simple EXE file
nativefier --name '<you .exe name>' '<your streamlit sharing website url>' --platform <'windows' or 'mac' or 'linux'>

nativefier --name 'check_url' 'http://localhost:8502/' --platform 'mac'


# Run
```
streamlit run check_url.py
```

# TO EDIT
- Edit the CSV file to include your list of URL to check
- Edit the LIMIT variable to specify how many URLs you want to check.

# Screenshots

![URL Checker Interface](/screenshots/screenshot1.png "User Interface")