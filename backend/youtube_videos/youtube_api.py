#youtube_api.py

import requests
from youtube_videos.config import YOUTUBE_API_KEY

def search_youtube_videos(query, max_results=5):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = []

        for item in data.get("items", []):
            video_id = item["id"].get("videoId")
            if not video_id:
                print(f" Skipping video due to missing videoId in response: {item}")
                continue

            title = item["snippet"]["title"]

            video_data = {
                "title": title,
                "id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
            results.append(video_data)

        return results
    else:
        print(f" Error fetching YouTube videos: {response.text}")
        return {"error": response.text}

def get_video_details(query, max_results=5):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = []

        for item in data.get("items", []):
            video_id = item["id"].get("videoId")
            if not video_id:
                print(f" Skipping video due to missing videoId in response: {item}")
                continue 

            snippet = item["snippet"]
            title = snippet.get("title", "")
            description = snippet.get("description", "")

            video_data = {
                "id": video_id,
                "title": title,
                "description": description,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
            results.append(video_data)

        return results
    else:
        print(f" Error fetching YouTube videos: {response.text}")
        return []

    
def get_youtube_transcript(video_id):
    url = f"https://www.youtube.com/api/timedtext?lang=en&v={video_id}"
    response = requests.get(url)

    if response.status_code != 200 or "<transcript>" not in response.text:
        return None

    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(response.text)
        transcript = ' '.join([node.text for node in root.findall('text') if node.text])
        return transcript
    except Exception as e:
        print(f"[Transcript Parsing Error] {e}")
        return None
