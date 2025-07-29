# test_youtube_fetcher.py

import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from filter_videos.filter_pipeline import VideoFilter
from youtube_videos.youtube_fetcher import fetch_videos, process_video

def prompt_user_input():
    lang = input("Enter programming language (e.g., C++, Java): ").strip()
    topic = input("Enter topic (e.g., recursion): ").strip()
    return lang, topic

async def main():
    language, topic = prompt_user_input()

    print(f"\nFetching YouTube videos for: {language} {topic}")
    videos = fetch_videos(f"{language} {topic}", max_results=10)

    if not videos:
        print("No videos fetched.")
        return

    print(f"Total videos fetched: {len(videos)}")

    vf = VideoFilter()
    filtered_videos = [video for video in videos if vf.filter_video(video, language, topic)]

    print(f"\n{len(filtered_videos)} Videos Passed Filtering:")
    for video in filtered_videos:
        print(f"• {video['title']} ({video['url']})")

    print("\n Processing filtered videos...\n")
    for video in filtered_videos:
        print(f"{video['title']}")
        await process_video(video['url'])

if __name__ == "__main__":
    asyncio.run(main())
