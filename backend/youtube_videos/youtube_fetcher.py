# youtube_fetcher.py

import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from filter_videos.filter_pipeline import VideoFilter
from youtube_videos.youtube_api import search_youtube_videos
from youtube_videos.gemini_pipeline import summarize_video_with_gemini

def extract_video_id(youtube_url):
    match = re.search(r"v=([a-zA-Z0-9_-]{11})", youtube_url)
    return match.group(1) if match else None

def process_video(video_url):
    print(f"🎬 Processing: {video_url}")
    
    summary = summarize_video_with_gemini(video_url)
    if not summary:
        print("❌ Failed to generate summary.")
        return
    
    print(f"\n📝 Summary:\n{summary}\n")

def fetch_videos(query, max_results=5):
    return search_youtube_videos(query, max_results=max_results)

if __name__ == "__main__":
    # CLI mode
    if len(sys.argv) == 2:
        video_url = sys.argv[1]
        process_video(video_url)
        sys.exit(0)

    # Interactive mode
    selected_language = input("Enter language (e.g., C++): ").strip()
    selected_topic = input("Enter topic (e.g., recursion): ").strip().lower()

    vf = VideoFilter()

    print("\n🔍 Fetching videos...")
    videos = fetch_videos(f"{selected_language} {selected_topic}")

    print("\n🔍 Filtering videos...")
    passed_videos = [v for v in videos if vf.filter_video(v, selected_language, selected_topic)]

    print(f"\n🎯 {len(passed_videos)} videos passed filtering.")

    if passed_videos:
        print("\n▶️ Processing filtered videos...\n")
        for video in passed_videos:
            print(f"\n▶️ {video['title']}")
            process_video(video['url'])
