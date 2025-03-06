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
params = {
    'q': 'memberAndApplication',
    'count': 50,
    'startTime': start_time
}

def fetch_last_linkedin_post():
    try:
        #API call
        response = requests.get(BASE_URL, headers=headers, params=params) 
        print(f"API Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            posts = []
            
            #query the json to find the data I need
            for element in data.get('elements', []):
                if (element.get('resourceName') == 'ugcPosts' and 
                    element.get('method') == 'CREATE'):
                    
                    activity = element.get('activity', {})
                    content = (activity.get('specificContent', {})
                             .get('com.linkedin.ugc.ShareContent', {}))
                    
                    post_urn = element.get('resourceId', '')a
                    timestamp = element.get('capturedAt', 0)
                    
                    post_date = datetime.fromtimestamp(timestamp/1000)
                    print(f"Found post from: {post_date}")
                    
                    posts.append({
                        'content': content.get('shareCommentary', {}).get('text', ''),
                        'url': f"https://www.linkedin.com/feed/update/{post_urn}",
                        'published_at': datetime.fromtimestamp(timestamp/1000).isoformat(),
                        'timestamp': timestamp
                    })
            
            if posts:
                # Sort by timestamp descending, grab the most recent
                posts.sort(key=lambda x: x['timestamp'], reverse=True)
                latest_post = posts[0]
                
                # Remove 'timestamp' from final output
                del latest_post['timestamp']
                
                # -----------------------------------------------------------------
                # 1. PARSE THE DATE FROM 'published_at'
                # -----------------------------------------------------------------
                published_at_str = latest_post["published_at"]
                post_datetime = datetime.fromisoformat(published_at_str)  
                # format to YYYY-MM-DD
                post_date_str = post_datetime.strftime("%Y-%m-%d")
                
                # -----------------------------------------------------------------
                # 2. FIND ALL MATCHING IMAGES IN /images FOLDER
                # -----------------------------------------------------------------
                images_dir = "images"  # Adjust if needed
                image_list = []
                
                if os.path.isdir(images_dir):
                    for filename in os.listdir(images_dir):
                        # Check if filename starts with 'YYYY-MM-DD' AND ends with '.jpeg'
                        if (filename.startswith(post_date_str) and 
                            filename.lower().endswith(".jpeg")):
                            image_list.append(filename)
                
                # Sort filenames for consistency, e.g. ["2025-02-13_1.jpeg", "2025-02-13_2.jpeg"]
                image_list.sort()


                # -----------------------------------------------------------------
                # 3. PREPEND THE GITHUB BASE URL TO THE IMAGE NAMES + ADD ALT ATTRIBUTE
                # -----------------------------------------------------------------
                base_url = "https://raw.githubusercontent.com/GiacomoIono/linkedin-posts/refs/heads/main/images/"
                full_url_list = []
                for fn in image_list:
                    full_image_url = base_url + fn
                    # Each item in the final list is now an object with 'url' and 'alt'
                    full_url_list.append({
                        "url": full_image_url,
                        "alt": ""  # alt text left empty
                    })
                
                # -----------------------------------------------------------------
                # 4. ADD THE ARRAY OF FILENAMES INTO THE JSON
                # -----------------------------------------------------------------
                latest_post["images"] = full_url_list
                
                # -----------------------------------------------------------------
                # 5. SAVE TO JSON FILE
                # -----------------------------------------------------------------
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
