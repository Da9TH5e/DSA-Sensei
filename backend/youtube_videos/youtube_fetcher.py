import asyncio
import sys
import os
import tempfile


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from question_generator.generator import generate_questions
from youtube_videos.transcript_utils import download_audio, get_or_generate_transcript
from filter_videos.filter_pipeline import VideoFilter
from youtube_videos.youtube_api import search_youtube_videos, get_youtube_transcript
from youtube_videos.utils import extract_video_id

TEMP_AUDIO_DIR = os.path.join(tempfile.gettempdir(), "youtube_audio_temp")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

async def process_video(video_url):
    print(f" Processing: {video_url}")
    
    video_id = extract_video_id(video_url)
    transcript = get_youtube_transcript(video_id)

    if not transcript:
        print(" No transcript available via YouTube API. Trying audio transcription...")
        
        audio_path = await download_audio(video_url)
        
        if not audio_path:
            audio_path = download_with_yt_dlp(video_url)
        
        if audio_path:
            transcript = await get_or_generate_transcript(video_url)

    
    try:
        print(" Generating coding questions...")
        questions = generate_questions(transcript)
        print("\n Questions Generated:\n")
        print(questions)
    except Exception as e:
        print(f" Error during question generation: {e}")

def fetch_videos(query, max_results=5):
    return search_youtube_videos(query, max_results=max_results)

def download_with_yt_dlp(video_url):
    try:
        import yt_dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(TEMP_AUDIO_DIR, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"yt-dlp fallback failed: {e}")
        return None

async def main():
    if len(sys.argv) == 2:
        video_url = sys.argv[1]
        await process_video(video_url)
        return

    selected_language = input("Enter language (e.g., C++): ").strip()
    selected_topic = input("Enter topic (e.g., recursion): ").strip().lower()

    vf = VideoFilter()
    print("\n Fetching videos...")
    videos = vf.filter_video(f"{selected_language} {selected_topic}")

    print("\n Filtering videos...")
    passed_videos = [v for v in videos if vf.filter_video(v, selected_language, selected_topic)]

    print(f"\n {len(passed_videos)} videos passed filtering.")

    if passed_videos:
        print("\n Processing filtered videos...\n")
        for video in passed_videos:
            print(f"\n▶ {video['title']}")
            await process_video(video['url'])

if __name__ == "__main__":
    asyncio.run(main())
