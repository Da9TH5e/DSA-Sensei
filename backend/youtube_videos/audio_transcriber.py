# youtube_videos/audio_transcriber.py

from groq import Groq
import os
import asyncio
import time

MAX_RETRIES = 3
RETRY_DELAY = 2

class GroqTranscriber:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.last_request_time = 0
        self.request_interval = 1.5

    def _extract_wait_time(self, error_msg: str) -> int:
        """Extract suggested wait time from rate limit error"""
        try:
            import re
            match = re.search(r'try again in (\d+)m(\d+)',error_msg)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                return (minutes * 60) + seconds
        except:
            pass

        return None
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """Handle transcription with proper response parsing"""
        if not audio_path or not os.path.exists(audio_path):
            print(f"Audio file not found")
            return None
        
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_interval:
            await asyncio.sleep(self.request_interval - elapsed)

        for attempt in range(MAX_RETRIES):
            try:
                with open(audio_path, 'rb') as audio_file:
                    response = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.client.audio.transcriptions.create(
                            file=audio_file,
                            model="whisper-large-v3",
                            response_format="text",
                        )
                    )

                    if isinstance(response, str):
                        return response
                    elif hasattr(response, 'text'):
                        return response.text
                    return str(response)
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Transcription error: {attempt + 1}, failed :{error_msg[:200]}")

                if "rate_limit" in error_msg.lower():
                    wait_time = self._extract_wait_time(error_msg) or (10 *(attempt + 1))
                    print(f"Rate limited. Wating {wait_time} seconds...")
                    time.sleep(wait_time)
                elif attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * (attempt + 1))
        return None

async def transcribe_audio_with_groq(audio_path: str) -> str:
    transcriber = GroqTranscriber()
    return await transcriber.transcribe_audio(audio_path)