# X (Twitter) Follower Data Extractor

A Streamlit application that extracts follower data from X (Twitter) profiles and attempts to find email addresses from their websites.

## Important Security Notice

Never commit actual API keys to version control. Use environment variables or Streamlit secrets for production.

## Setup

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Set up your Twitter API credentials:
   - Create a developer account at https://developer.twitter.com/
   - Create a new app and generate API keys
4. Run the app: `streamlit run app.py`

## Usage

1. Enter your Twitter API credentials in the sidebar
2. Enter a valid X (Twitter) profile URL
3. Click "Extract Follower Data"
4. Preview and download the results as CSV

## Deployment

For deployment on Streamlit Cloud:
1. Connect your GitHub repository
2. Add your API credentials as secrets in Streamlit Cloud
3. Deploy the application

## Important Notes

- This tool is for educational purposes only
- Respect Twitter's API terms of service
- Be mindful of rate limits when extracting data
- Email extraction is simulated in this version
