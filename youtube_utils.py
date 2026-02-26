import os
import tempfile
from pathlib import Path
from typing import Optional
from pytubefix import YouTube
from pytubefix.cli import on_progress

def download_youtube_audio(url: str, output_dir: Optional[str] = None) -> Optional[str]:
    """
    Download audio from YouTube video using pytubefix
    
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
        
        # Create YouTube object with progress callback
        yt = YouTube(url, on_progress_callback=on_progress)
        
        # Get audio stream (highest quality audio-only)
        audio_stream = yt.streams.get_audio_only()
        
        if not audio_stream:
            # Fallback: get lowest quality video (which has audio)
            audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not audio_stream:
            raise Exception("No audio stream available for this video")
        
        # Download the audio
        print(f"Downloading: {yt.title}")
        output_file = audio_stream.download(
            output_path=output_dir,
            filename_prefix="youtube_audio_"
        )
        
        # Convert to mp3 if it's not already
        if not output_file.endswith('.mp3'):
            # pytubefix downloads as mp4/webm, we'll rename for consistency
            mp3_file = output_file.rsplit('.', 1)[0] + '.mp3'
            os.rename(output_file, mp3_file)
            output_file = mp3_file
        
        print(f"Successfully downloaded: {output_file}")
        return output_file
        
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
        yt = YouTube(url)
        
        return {
            'title': yt.title,
            'duration': yt.length,
            'author': yt.author,
            'views': yt.views,
            'publish_date': str(yt.publish_date) if yt.publish_date else 'Unknown',
            'description': yt.description[:500] if yt.description else '',
            'thumbnail': yt.thumbnail_url,
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
        'm.youtube.com/watch?v=',
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

def get_available_streams(url: str) -> list:
    """
    Get list of available audio streams for a video
    
    Args:
        url: YouTube video URL
        
    Returns:
        List of available audio streams
    """
    try:
        yt = YouTube(url)
        audio_streams = yt.streams.filter(only_audio=True).all()
        
        streams_info = []
        for stream in audio_streams:
            streams_info.append({
                'itag': stream.itag,
                'mime_type': stream.mime_type,
                'abr': stream.abr,
                'filesize': stream.filesize,
            })
        
        return streams_info
    
    except Exception as e:
        print(f"Error getting streams: {str(e)}")
        return []
