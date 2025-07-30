# youtube_videos/transcript_utils.py

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pydub import AudioSegment
import os
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_videos.audio_transcriber import transcribe_audio_with_whisper
from youtube_videos.utils import extract_video_id

# Create a dedicated directory for audio files
AUDIO_CACHE_DIR = os.path.join(os.path.dirname(__file__), "audio_cache")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
MAX_RETRIES = 3
RETRY_DELAY = 2

async def download_audio(video_url: str) -> list:
    """Download and split audio into two parts asynchronously"""
    loop = asyncio.get_event_loop()
    video_id = extract_video_id(video_url)
    output_path = os.path.join(AUDIO_CACHE_DIR, f"{video_id}.mp3")

    for attempt in range(MAX_RETRIES):
        try:
            if os.path.exists(output_path):
                os.remove(output_path)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                downloaded_path = ydl.prepare_filename(info)

                if os.path.exists(output_path):
                    with ThreadPoolExecutor() as executor:
                        return await loop.run_in_executor(executor, split_audio_file, output_path)

            return []
        except Exception as e:
            print(f"Audio download failed: {attempt + 1} - {str(e)}")
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
    return []


async def get_or_generate_transcript(video_url: str) -> str:
    """Async pipeline: transcript from YouTube or audio split and processed."""
    video_id = extract_video_id(video_url)
    if not video_id:
        print("Invalid video URL")
        return None

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        if transcript:
            return '\n'.join([t['text'] for t in transcript])
    except Exception as e:
        print(f"YouTube transcript unavailable: {str(e)[:200]}")

    print("Falling back to audio transcription...")
    audio_paths = await download_audio(video_url)
    if not audio_paths:
        print("Audio could not be downloaded or split.")
        return None

    transcript = ""
    for path in audio_paths:
        loop = asyncio.get_event_loop()
        part = await loop.run_in_executor(None, transcribe_audio_with_whisper, path)
        
        try:
            if part:
                transcript += part.strip() + "\n"
        except Exception as e:
            print(f"Error transcribing {path}: {str(e)[:200]}")
        finally:
            cleanup_audio(path)

    return transcript.strip() if transcript.strip() else None

def split_audio_file(file_path: str) -> list[str]:
    """Split audio into 2 parts and return the new file paths"""
    try:
        audio = AudioSegment.from_file(file_path)
        half_point = len(audio) // 2

        chunk1 = audio[:half_point]
        chunk2 = audio[half_point:]

        chunk1_path = file_path.replace(".mp3", "_part1.mp3")
        chunk2_path = file_path.replace(".mp3", "_part2.mp3")

        chunk1.export(chunk1_path, format="mp3")
        chunk2.export(chunk2_path, format="mp3")

        print(f"Original duration: {len(audio)} ms")
        print(f"Part 1: {len(chunk1)} ms, Part 2: {len(chunk2)} ms")

        return [chunk1_path, chunk2_path]
    except Exception as e:
        print(f"Error splitting audio: {str(e)}")
        return []

def cleanup_audio(file_path: str):
    """Safe audio file cleanup with verification"""
    if not file_path:
        return
        
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up: {file_path}")
    except Exception as e:
        print(f"Could not clean up {file_path}: {str(e)[:200]}")