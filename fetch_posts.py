import requests
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment variables
ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
BASE_URL = "https://api.linkedin.com/rest/memberChangeLogs"

# Headers required for the API
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'LinkedIn-Version': '202312'
}

# Calculate timestamp for 24 hours ago
start_time = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)

# Parameters for the API request
params = {
    'q': 'memberAndApplication',
    'count': 50,
    'startTime': start_time
}

def fetch_last_linkedin_post():
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        print(f"API Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            posts = []
            
            for element in data.get('elements', []):
                if (element.get('resourceName') == 'ugcPosts' and 
                    element.get('method') == 'CREATE'):
                    
                    activity = element.get('activity', {})
                    content = (activity.get('specificContent', {})
                             .get('com.linkedin.ugc.ShareContent', {}))
                    
                    post_urn = element.get('resourceId', '')
                    timestamp = element.get('capturedAt', 0)
                    
                    # Print each post's date for debugging
                    post_date = datetime.fromtimestamp(timestamp/1000)
                    print(f"Found post from: {post_date}")
                    
                    posts.append({
                        'content': content.get('shareCommentary', {}).get('text', ''),
                        'url': f"https://www.linkedin.com/feed/update/{post_urn}",
                        'published_at': datetime.fromtimestamp(timestamp/1000).isoformat(),
                        'timestamp': timestamp
                    })
            
            if posts:
                # Sort posts by timestamp and get the most recent one
                posts.sort(key=lambda x: x['timestamp'], reverse=True)
                latest_post = posts[0]
                
                # Remove the timestamp from the final output
                del latest_post['timestamp']
                
                # Save to JSON file
                with open('last_linkedin_post.json', 'w', encoding='utf-8') as f:
                    json.dump(latest_post, f, ensure_ascii=False, indent=2)
                
                print("\nMost recent post has been saved to 'last_linkedin_post.json'")
                print("\nPost data:")
                print(json.dumps(latest_post, indent=2))
                
                return latest_post
            
            print("No posts found")
            return None

        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    last_post = fetch_last_linkedin_post()