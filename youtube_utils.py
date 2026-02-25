import os
import tempfile
from pathlib import Path
from typing import Optional
import yt_dlp

def download_youtube_audio(url: str, output_dir: Optional[str] = None) -> Optional[str]:
    """
    Download audio from YouTube video
    
    Args:
        url: YouTube video URL
        output_dir: Directory to save audio (uses temp dir if None)
        
    Returns:
        Path to downloaded audio file or None if failed
    """
    try:
        # Use temp directory if not specified
        if output_dir is None:
            output_dir = tempfile.gettempdir()
        
        # Generate unique filename
        output_template = os.path.join(output_dir, 'youtube_audio_%(id)s.%(ext)s')
        
        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'restrictfilenames': True,
            'noplaylist': True,
            'prefer_ffmpeg': True,
        }
        
        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info
            info = ydl.extract_info(url, download=True)
            
            if info is None:
                raise Exception("Failed to extract video information")
            
            # Get video ID
            video_id = info.get('id', 'unknown')
            
            # Construct expected filename
            audio_file = os.path.join(output_dir, f'youtube_audio_{video_id}.mp3')
            
            # Check if file exists
            if os.path.exists(audio_file):
                return audio_file
            else:
                # Try alternate naming patterns
                for pattern in [f'youtube_audio_{video_id}.*', f'*{video_id}*.mp3']:
                    matches = list(Path(output_dir).glob(pattern))
                    if matches:
                        return str(matches[0])
                
                raise Exception(f"Downloaded audio file not found: {audio_file}")
    
    except Exception as e:
        print(f"Error downloading YouTube audio: {str(e)}")
        raise Exception(f"Failed to download audio from YouTube: {str(e)}")

def get_video_info(url: str) -> dict:
    """
    Get information about a YouTube video without downloading
    
    Args:
        url: YouTube video URL
        
    Returns:
        Dictionary with video information
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', 'Unknown'),
                'description': info.get('description', '')[:500],  # First 500 chars
            }
    
    except Exception as e:
        print(f"Error getting video info: {str(e)}")
        return {}

def validate_youtube_url(url: str) -> bool:
    """
    Validate if URL is a valid YouTube URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_patterns = [
        'youtube.com/watch?v=',
        'youtu.be/',
        'youtube.com/embed/',
        'youtube.com/v/',
    ]
    
    return any(pattern in url.lower() for pattern in valid_patterns)

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "1:23:45")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"
