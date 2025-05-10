# --- filter_videos/filter_pipeline.py ---

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Dict
from youtube_videos.youtube_api import get_video_details
from youtube_videos.gemini_pipeline import analyze_with_gemini  # <-- NEW
from concurrent.futures import ThreadPoolExecutor
import subprocess


class VideoFilter:
    def filter_videos_batch(self, videos, language, topic):
        from threading import Lock
        lock = Lock()
        passed = []

        def filter_and_collect(video):
            if self.filter_video(video, language, topic):
                with lock:
                    passed.append(video)

        with ThreadPoolExecutor() as executor:
            executor.map(filter_and_collect, videos)

        return passed

    def filter_video(self, video: Dict, language: str, topic: str) -> bool:
        print(f"\n🔍 Filtering: {video.get('title')}")

        title = video.get('title', '')
        description = video.get('description', '')
        url = video.get('url', '')

        # Step 1: Check title
        if language.lower() in title.lower() or topic.lower() in title.lower():
            print(f"✅ Match found in title: '{title}'")
            return True

        # Step 2: Check description
        if language.lower() in description.lower() or topic.lower() in description.lower():
            print("✅ Match found in description")
            return True

        # Step 3: Optional - Check tags (not implemented unless tags available)
        # If tags are included, check here.

        # Step 4: Use Gemini to deeply analyze
        print("⚠️ No match found in title/description — using Gemini fallback...")
        gemini_passed = analyze_with_gemini(url, language, topic)

        if gemini_passed:
            print("✅ Gemini detected relevant content")
            return True

        print("❌ Gemini did not detect relevant content")
        return False


def filter_videos_for_user():
    selected_language = input("Enter programming language (e.g. C++): ").strip()
    selected_topic = input("Enter topic (e.g. recursion): ").strip()

    print("\n🎥 Fetching videos...")
    videos = get_video_details(f"{selected_language} {selected_topic}")
    vf = VideoFilter()

    passed = vf.filter_videos_batch(videos, selected_language, selected_topic)

    print(f"\n🎯 {len(passed)} videos passed filtering.")

    if passed:
        print("\n▶️ Sending videos to youtube_fetcher.py for Gemini summary + questions...\n")
        for vid in passed:
            subprocess.run(["python", "youtube_videos/youtube_fetcher.py", vid["url"]], check=True)

    return passed

if __name__ == "__main__":
    filter_videos_for_user()
