# youtube_videos/audio_transcriber.py

import os
import whisper

MAX_RETRIES = 3
RETRY_DELAY = 2

class WhisperTranscriber:
    model = whisper.load_model("base")
    """Handles audio transcription using Groq API with rate limiting and error handling"""
    
    def transcribe_audio(self, audio_path: str) -> str:
        """Handle transcription with proper response parsing"""
        if not audio_path or not os.path.exists(audio_path):
            print(f"Audio file not found")
            return None
        
        try:
            result = self.model.transcribe(audio_path)
            return result["text"]
        except Exception as e:
            print(f"Local transcription error: {str(e)[:200]}")
            return None
        
def transcribe_audio_with_whisper(audio_path: str) -> str:
    transcriber = WhisperTranscriber()
    return transcriber.transcribe_audio(audio_path)