# --- gemini_pipeline.py ---

from youtube_videos.gemini_config import genai

model = genai.GenerativeModel("gemini-2.0-flash")

def summarize_video_with_gemini(video_url):
    prompt = f"Summarize the key concepts of this video: {video_url}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini] Error generating summary: {e}")
        return None

def analyze_with_gemini(video_url: str, language: str, topic: str) -> bool:
    summary = summarize_video_with_gemini(video_url)
    if not summary:
        return False

    combined_text = summary.lower()
    return language.lower() in combined_text or topic.lower() in combined_text
