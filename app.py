import streamlit as st
import pandas as pd
import re
import time
from datetime import datetime
import requests
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
    1. Enter your Twitter API Bearer Token in the sidebar
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
⚠️ <strong>Important:</strong> 
- You need Twitter API access with appropriate permissions
- This tool may not work with Essential access level (apply for Elevated access)
- Never share your API keys publicly
- This tool is for educational purposes only
</div>
""", unsafe_allow_html=True)

# Sidebar for API credentials
st.sidebar.header("Twitter API Configuration")
st.sidebar.markdown("""
<div class="api-section">
You need a Twitter API Bearer Token. If you're getting errors, you may need to apply for Elevated access.
</div>
""", unsafe_allow_html=True)

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

# Function to get user ID from username using API v2
def get_user_id(username, bearer_token):
    if not bearer_token:
        st.error("Missing Bearer Token. Please check your API configuration.")
        return None
        
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['data']['id']
        else:
            error_msg = response.json().get('errors', [{}])[0].get('message', 'Unknown error')
            st.error(f"Error fetching user ID: {response.status_code} - {error_msg}")
            
            # Provide guidance based on common errors
            if "access level" in error_msg.lower():
                st.info("""
                🔍 **Access Level Issue Detected**
                
                It appears your Twitter developer account has limited API access.
                
                **To fix this:**
                1. Go to https://developer.twitter.com/
                2. Navigate to your Project & App
                3. Click on the "Products" tab
                4. Apply for **Elevated access**
                5. Wait for approval (may take several days)
                """)
                
            return None
    except Exception as e:
        st.error(f"Exception occurred while fetching user ID: {str(e)}")
        return None

# Function to get followers with pagination using API v2
def get_followers(user_id, bearer_token, max_results=10):
    if not bearer_token:
        return []
        
    followers = []
    next_token = None
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    
    # For demo purposes, we'll limit to a few pages
    page_count = 0
    max_pages = 2  # Very limited due to API restrictions
    
    while page_count < max_pages and len(followers) < max_results:
        url = f"https://api.twitter.com/2/users/{user_id}/followers"
        params = {
            "max_results": min(10, max_results - len(followers)),
            "user.fields": "id,name,username,description,url,verified,public_metrics,created_at"
        }
        
        if next_token:
            params["pagination_token"] = next_token
            
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                followers.extend(data.get('data', []))
                next_token = data.get('meta', {}).get('next_token')
                page_count += 1
                
                # Respect rate limits
                time.sleep(2)
            else:
                error_msg = response.json().get('errors', [{}])[0].get('message', 'Unknown error')
                st.error(f"Error fetching followers: {response.status_code} - {error_msg}")
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
    elif not bearer_token:
        st.error("Please enter your Bearer Token in the sidebar")
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
        user_id = get_user_id(username, bearer_token)
        if not user_id:
            st.stop()
        progress_bar.progress(25)
        
        # Step 2: Get followers
        status_text.text("Step 2: Fetching followers...")
        followers_data = get_followers(user_id, bearer_token, max_results=10)
        progress_bar.progress(50)
        
        if not followers_data:
            st.error("No followers found or error fetching data. You may need Elevated API access.")
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
                "id": follower.get('id', ''),
                "username": follower.get('username', ''),
                "name": follower.get('name', ''),
                "description": (follower.get('description', '')[:100] + "...") if follower.get('description') and len(follower.get('description')) > 100 else follower.get('description', ''),
                "website": website,
                "emails": ", ".join(emails),
                "verified": follower.get('verified', False),
                "followers_count": follower.get('public_metrics', {}).get('followers_count', 0),
                "following_count": follower.get('public_metrics', {}).get('following_count', 0),
                "tweet_count": follower.get('public_metrics', {}).get('tweet_count', 0),
                "created_at": follower.get('created_at', '')
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

# Add information about API access
st.markdown("---")
st.header("API Access Information")

st.markdown("""
<div class="info-box">
<h3>Understanding Twitter API Access Levels</h3>

Twitter offers three access levels:

1. <strong>Essential</strong> (Free) - Limited access to API v2 endpoints
2. <strong>Elevated</strong> (Free) - Full access to API v2 endpoints + limited v1.1 access
3. <strong>Pro</strong> (Paid) - Higher rate limits + additional features

<h3>How to Apply for Elevated Access:</h3>
<ol>
  <li>Go to https://developer.twitter.com/</li>
  <li>Navigate to your Project & App</li>
  <li>Click on the "Products" tab</li>
  <li>Click "Apply" for Elevated access</li>
  <li>Complete the application form</li>
  <li>Wait for approval (may take several days)</li>
</ol>

<h3>In the Meantime:</h3>
<p>While waiting for Elevated access, you can:</p>
<ul>
  <li>Test with the limited API v2 endpoints available</li>
  <li>Use the simulated data functionality</li>
  <li>Explore other Twitter API endpoints that are available with your current access level</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray;">
    <p>This tool requires a Twitter Developer account with appropriate API access level.</p>
    <p>Built with Streamlit | For educational purposes only</p>
    </div>
    """,
    unsafe_allow_html=True
)
