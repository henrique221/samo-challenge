#!/usr/bin/env python3
"""
YouTube Video Downloader using yt-dlp command line tool

DISCLAIMER: This script is for educational purposes only. 
Please respect copyright laws and YouTube's Terms of Service.
Only download videos you have permission to download.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path


def check_ytdlp():
    """Check if yt-dlp is installed."""
    try:
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: yt-dlp is not installed.")
        print("Please install it using one of these methods:")
        print("  - pipx install yt-dlp")
        print("  - pip install yt-dlp")
        print("  - Or download from: https://github.com/yt-dlp/yt-dlp")
        return False


def download_video(url, output_dir="downloads", quality="best", audio_only=False):
    """
    Download a YouTube video or audio.
    
    Args:
        url: YouTube video URL
        output_dir: Directory to save the downloaded file
        quality: Video quality (best, worst, or specific format)
        audio_only: Download only audio if True
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Build command
    cmd = ['yt-dlp']
    cmd.extend(['-o', os.path.join(output_dir, '%(title)s.%(ext)s')])
    
    if audio_only:
        cmd.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '192K'])
        print(f"Downloading audio from: {url}")
    else:
        if quality == "best":
            cmd.extend(['-f', 'best'])
        elif quality == "worst":
            cmd.extend(['-f', 'worst'])
        else:
            cmd.extend(['-f', quality])
        print(f"Downloading video ({quality} quality) from: {url}")
    
    cmd.append(url)
    
    try:
        # Run yt-dlp command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        print(f"\n✓ Successfully downloaded")
        print(f"✓ Saved to: {output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error downloading video: {e.stderr}")
        return False


def download_playlist(url, output_dir="downloads", quality="best"):
    """
    Download all videos from a YouTube playlist.
    
    Args:
        url: YouTube playlist URL
        output_dir: Directory to save the downloaded files
        quality: Video quality
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Build command
    cmd = ['yt-dlp']
    cmd.extend(['-o', os.path.join(output_dir, '%(playlist_index)s - %(title)s.%(ext)s')])
    
    if quality == "best":
        cmd.extend(['-f', 'best'])
    elif quality == "worst":
        cmd.extend(['-f', 'worst'])
    else:
        cmd.extend(['-f', quality])
    
    cmd.append(url)
    
    print(f"Downloading playlist from: {url}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        print(f"\n✓ Successfully downloaded playlist")
        print(f"✓ Saved to: {output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error downloading playlist: {e.stderr}")
        return False


def get_video_info(url):
    """
    Get information about a YouTube video without downloading.
    
    Args:
        url: YouTube video URL
    """
    cmd = ['yt-dlp', '--dump-json', '--no-download', url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        print("\n📹 Video Information:")
        print(f"Title: {info.get('title', 'N/A')}")
        print(f"Duration: {info.get('duration', 0)} seconds")
        print(f"Uploader: {info.get('uploader', 'N/A')}")
        
        view_count = info.get('view_count')
        if view_count:
            print(f"Views: {view_count:,}")
        else:
            print(f"Views: N/A")
            
        print(f"Upload Date: {info.get('upload_date', 'N/A')}")
        
        # Show available formats
        formats = info.get('formats', [])
        if formats:
            print("\n📊 Available Formats:")
            seen_resolutions = set()
            for f in formats:
                height = f.get('height')
                if height and height not in seen_resolutions:
                    seen_resolutions.add(height)
                    print(f"  - {height}p ({f.get('ext', 'N/A')})")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error getting video info: {e.stderr}")
        return False
    except json.JSONDecodeError:
        print(f"\n✗ Error parsing video information")
        return False


def main():
    # Check if yt-dlp is installed
    if not check_ytdlp():
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Download YouTube videos and playlists",
        epilog="DISCLAIMER: Respect copyright laws and YouTube's Terms of Service."
    )
    
    parser.add_argument("url", help="YouTube video or playlist URL")
    parser.add_argument("-o", "--output", default="downloads", 
                        help="Output directory (default: downloads)")
    parser.add_argument("-q", "--quality", default="best",
                        help="Video quality: best, worst, or specific format (default: best)")
    parser.add_argument("-a", "--audio-only", action="store_true",
                        help="Download audio only (MP3)")
    parser.add_argument("-p", "--playlist", action="store_true",
                        help="Download entire playlist")
    parser.add_argument("-i", "--info", action="store_true",
                        help="Show video information without downloading")
    
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("YouTube Video Downloader")
    print("="*50)
    
    if args.info:
        success = get_video_info(args.url)
    elif args.playlist:
        success = download_playlist(args.url, args.output, args.quality)
    else:
        success = download_video(args.url, args.output, args.quality, args.audio_only)
    
    if success:
        print("\n✅ Operation completed successfully!")
    else:
        print("\n❌ Operation failed. Please check the URL and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()