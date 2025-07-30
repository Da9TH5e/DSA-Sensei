# youtube_videos/groq_transcript_analysis.py

from groq import Groq
import os

def analyze_with_groq(video_url: str, language: str, topic: str) -> bool:
    """Analyze video content using Groq API"""
    try:
        from youtube_videos.utils import extract_video_id
        from youtube_videos.youtube_api import get_youtube_transcript
        
        video_id = extract_video_id(video_url)
        transcript = get_youtube_transcript(video_id)
        
        if not transcript:
            print("[Groq Analysis] No transcript available.")
            return False
            
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Prepare the prompt
        prompt = f"""
        You are an expert video content classifier.

        Determine whether the following transcript from a programming video discusses *both* of the following:

        - Programming Language: {language}
        - Topic: {topic}

        Respond only with 'true' or 'false'. No explanations.

        Transcript (truncated if long):
        {transcript[:5000]}
        
        Return only 'true' or 'false'
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.1,
            max_tokens=10,
            stream=False
        )

        reply = response.choices[0].message.content.strip().lower()
        print(f"[Groq Analysis] {reply}")
        return reply == "true"
        
    except Exception as e:
        print(f"[Groq Analysis Error] {e}")
        return False