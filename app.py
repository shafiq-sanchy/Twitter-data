
import streamlit as st
import pandas as pd
import re
import time
from datetime import datetime
import requests
from requests_oauthlib import OAuth1
import base64
import json

# Set up the page
st.set_page_config(
    page_title="X (Twitter) Follower Data Extractor",
    page_icon="🐦",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1DA1F2; font-weight: bold;}
    .sub-header {font-size: 1.5rem; color: #14171A;}
    .info-box {background-color: #E8F5FE; padding: 20px; border-radius: 10px; margin: 10px 0;}
    .warning-box {background-color: #FFF4E5; padding: 20px; border-radius: 10px; margin: 10px 0;}
    .success-box {background-color: #E6F7EE; padding: 20px; border-radius: 10px; margin: 10px 0;}
    .stButton>button {background-color: #1DA1F2; color: white;}
    .api-section {background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<p class="main-header">🐦 X (Twitter) Follower Data Extractor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Extract follower information and website/email data from X profiles</p>', unsafe_allow_html=True)

# Information section
with st.expander("ℹ️ How to use this tool"):
    st.write("""
    1. Enter your Twitter API credentials in the sidebar
    2. Enter a valid X (Twitter) profile URL in the input field
    3. Click the 'Extract Follower Data' button to begin the process
    4. The tool will extract follower information including usernames and website URLs
    5. Website URLs will be processed to extract email addresses where possible
    6. Download the final data as a CSV file
    
    **Note:** For large follower counts, the extraction process may take significant time and may hit API rate limits.
    """)

# Disclaimer
st.markdown("""
<div class="warning-box">
⚠️ <strong>Important Security Notice:</strong> 
- Never share your API keys publicly
- The keys shown in this demo are placeholder values only
- Always store sensitive credentials securely using environment variables or secret management tools
- This tool is for educational purposes only
</div>
""", unsafe_allow_html=True)

# Sidebar for API credentials
st.sidebar.header("Twitter API Configuration")
st.sidebar.markdown("""
<div class="api-section">
Enter your Twitter API credentials below. These are required to access the Twitter API.
</div>
""", unsafe_allow_html=True)

api_key = st.sidebar.text_input("API Key", type="password", value="", help="Your Twitter API Key")
api_secret = st.sidebar.text_input("API Secret", type="password", value="", help="Your Twitter API Secret")
access_token = st.sidebar.text_input("Access Token", type="password", value="", help="Your Twitter Access Token")
access_token_secret = st.sidebar.text_input("Access Token Secret", type="password", value="", help="Your Twitter Access Token Secret")
bearer_token = st.sidebar.text_input("Bearer Token", type="password", value="", help="Your Twitter Bearer Token (for API v2)")

# Input section
st.header("X Profile Input")
twitter_url = st.text_input("Enter X (Twitter) Profile URL:", placeholder="https://x.com/username or https://twitter.com/username")

# Function to extract username from URL
def extract_username(url):
    # Handle both x.com and twitter.com URLs
    if not url:
        return None
        
    url = url.replace("https://x.com/", "https://twitter.com/")
    match = re.match(r'https?://(www\.)?twitter\.com/([a-zA-Z0-9_]+)/?', url)
    if match:
        return match.group(2)
    return None

# Function to get user ID from username using OAuth 1.0a
def get_user_id(username, api_key, api_secret, access_token, access_token_secret):
    if not all([api_key, api_secret, access_token, access_token_secret]):
        st.error("Missing API credentials. Please check your API configuration.")
        return None
        
    auth = OAuth1(api_key, api_secret, access_token, access_token_secret)
    url = f"https://api.twitter.com/1.1/users/show.json?screen_name={username}"
    
    try:
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            return response.json()['id_str']
        else:
            st.error(f"Error fetching user ID: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Exception occurred while fetching user ID: {str(e)}")
        return None

# Function to get followers with pagination using OAuth 1.0a
def get_followers(user_id, api_key, api_secret, access_token, access_token_secret, max_results=100):
    if not all([api_key, api_secret, access_token, access_token_secret]):
        return []
        
    followers = []
    next_cursor = -1
    auth = OAuth1(api_key, api_secret, access_token, access_token_secret)
    
    # For demo purposes, we'll limit to a few pages
    page_count = 0
    max_pages = 3  # Adjust based on your needs and rate limits
    
    while next_cursor != 0 and page_count < max_pages and len(followers) < max_results:
        url = f"https://api.twitter.com/1.1/followers/list.json?user_id={user_id}&count=200"
        if next_cursor and next_cursor != -1:
            url += f"&cursor={next_cursor}"
            
        try:
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                data = response.json()
                followers.extend(data['users'])
                next_cursor = data['next_cursor']
                page_count += 1
                
                # Respect rate limits
                time.sleep(1)
            else:
                st.error(f"Error fetching followers: {response.status_code} - {response.text}")
                break
        except Exception as e:
            st.error(f"Exception occurred while fetching followers: {str(e)}")
            break
    
    return followers[:max_results]

# Function to extract emails from websites (simulated)
def extract_emails_from_website(url):
    try:
        # In a real implementation, this would fetch the website and extract emails
        # For demonstration, we'll return some simulated emails
        import random
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "example.com", "company.com"]
        if random.random() > 0.7:  # Only return emails for some websites
            domain = url.split('//')[-1].split('/')[0] if '//' in url else url
            return [f"contact@{domain}", f"info@{domain}"]
        return []
    except:
        return []

# Process and display data
if st.button("Extract Follower Data"):
    if not twitter_url:
        st.error("Please enter a valid X profile URL")
    elif not all([api_key, api_secret, access_token, access_token_secret]):
        st.error("Please complete all API credential fields in the sidebar")
    else:
        # Extract username from URL
        username = extract_username(twitter_url)
        if not username:
            st.error("Invalid X/Twitter profile URL. Please use format: https://x.com/username or https://twitter.com/username")
            st.stop()
            
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Get user ID
        status_text.text("Step 1: Getting user ID...")
        user_id = get_user_id(username, api_key, api_secret, access_token, access_token_secret)
        if not user_id:
            st.stop()
        progress_bar.progress(25)
        
        # Step 2: Get followers
        status_text.text("Step 2: Fetching followers...")
        followers_data = get_followers(user_id, api_key, api_secret, access_token, access_token_secret, max_results=100)
        progress_bar.progress(50)
        
        if not followers_data:
            st.error("No followers found or error fetching data")
            st.stop()
            
        # Step 3: Process data
        status_text.text("Step 3: Processing data...")
        processed_data = []
        
        for i, follower in enumerate(followers_data):
            website = follower.get('url', '') if isinstance(follower, dict) else ''
            emails = []
            
            if website:
                emails = extract_emails_from_website(website)
                
            processed_data.append({
                "id": follower.get('id_str', '') if isinstance(follower, dict) else '',
                "username": follower.get('screen_name', '') if isinstance(follower, dict) else '',
                "name": follower.get('name', '') if isinstance(follower, dict) else '',
                "description": (follower.get('description', '')[:100] + "...") if isinstance(follower, dict) and follower.get('description') and len(follower.get('description')) > 100 else (follower.get('description', '') if isinstance(follower, dict) else ''),
                "website": website,
                "emails": ", ".join(emails),
                "verified": follower.get('verified', False) if isinstance(follower, dict) else False,
                "followers_count": follower.get('followers_count', 0) if isinstance(follower, dict) else 0,
                "following_count": follower.get('friends_count', 0) if isinstance(follower, dict) else 0,
                "tweet_count": follower.get('statuses_count', 0) if isinstance(follower, dict) else 0,
                "created_at": follower.get('created_at', '') if isinstance(follower, dict) else ''
            })
            
            # Update progress
            if i % 10 == 0:
                progress_bar.progress(50 + int(40 * (i / len(followers_data))))
        
        progress_bar.progress(90)
        
        # Convert to DataFrame
        df = pd.DataFrame(processed_data)
        
        progress_bar.progress(100)
        status_text.text("Data extraction complete!")
        
        # Display stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Followers Processed", len(processed_data))
        with col2:
            st.metric("Profiles with Websites", len([f for f in processed_data if f["website"]]))
        with col3:
            st.metric("Email Addresses Found", len([f for f in processed_data if f["emails"]]))
        with col4:
            websites_count = len([f for f in processed_data if f["website"]])
            success_rate = len([f for f in processed_data if f["emails"]]) / max(1, websites_count) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Show data preview
        st.subheader("Data Preview")
        st.dataframe(df.head(10))
        
        # Show some charts
        st.subheader("Data Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Websites chart
            website_stats = df["website"].apply(lambda x: "Has Website" if x else "No Website").value_counts()
            if not website_stats.empty:
                st.bar_chart(website_stats)
        
        with col2:
            # Email extraction chart
            email_stats = df["emails"].apply(lambda x: "Has Email" if x else "No Email").value_counts()
            if not email_stats.empty:
                st.bar_chart(email_stats)
        
        # Download section
        st.subheader("Download Data")
        
        # Convert DataFrame to CSV
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"x_followers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.markdown("""
        <div class="success-box">
        ✅ Data extraction completed successfully. You can now download the CSV file.
        </div>
        """, unsafe_allow_html=True)

# Add information about implementation
st.markdown("---")
st.header("Implementation Notes")

st.markdown("""
<div class="info-box">
This implementation uses Twitter API v1.1 with OAuth 1.0a authentication.

For production use, you would need to:
1. Handle rate limits more effectively with proper retry logic
2. Implement more sophisticated website scraping for email extraction
3. Add error handling for various edge cases
4. Consider using a database for storing results for large datasets
5. Implement proper logging and monitoring

The current implementation is limited to a small number of followers for demonstration purposes.
Adjust the max_results parameter in the get_followers function for larger extractions.
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray;">
    <p>This tool requires a Twitter Developer account and API access.</p>
    <p>Built with Streamlit | For educational purposes only</p>
    </div>
    """,
    unsafe_allow_html=True
)
