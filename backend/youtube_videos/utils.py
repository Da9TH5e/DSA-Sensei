# youtube_videos/utils.py

from urllib.parse import urlparse, parse_qs

def extract_video_id(youtube_url):
    """Extracts YouTube video ID from various URL formats."""
    if not youtube_url:
        return None
        
    parsed = urlparse(youtube_url)
    
    # Handle standard URLs (www.youtube.com/watch?v=ID)
    if parsed.query:
        video_id = parse_qs(parsed.query).get('v')
        if video_id and video_id[0]:
            return video_id[0]
    
    # Handle shortened URLs (youtu.be/ID) and embed URLs
    if parsed.path:
        return parsed.path.split('/')[-1] or None
    
    return None