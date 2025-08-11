import os
import json
import subprocess
from pathlib import Path
from django.conf import settings
from django.utils import timezone


class YouTubeDownloader:
    def __init__(self):
        self.downloads_dir = settings.DOWNLOADS_DIR
        Path(self.downloads_dir).mkdir(parents=True, exist_ok=True)
    
    def download(self, download_obj):
        """
        Download a video/audio using yt-dlp
        Updates the download_obj with results
        """
        try:
            # Update status to downloading
            download_obj.status = 'downloading'
            download_obj.save()
            
            # Get video info first
            info = self.get_info(download_obj.url)
            if info:
                download_obj.title = info.get('title', 'Unknown')
                download_obj.duration = info.get('duration', 0)
                download_obj.thumbnail = info.get('thumbnail', '')
                download_obj.save()
            
            # Build command
            output_template = os.path.join(self.downloads_dir, '%(title)s.%(ext)s')
            cmd = ['yt-dlp']
            cmd.extend(['-o', output_template])
            
            # Add format options
            if download_obj.download_type == 'audio':
                cmd.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '192K'])
            else:
                if download_obj.quality == 'best':
                    cmd.extend(['-f', 'best'])
                elif download_obj.quality == 'worst':
                    cmd.extend(['-f', 'worst'])
                else:
                    # Try specific quality, fallback to best if not available
                    cmd.extend(['-f', f'best[height<={download_obj.quality[:-1]}]'])
            
            # Add URL
            cmd.append(download_obj.url)
            
            # Execute download
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                # Success - find the downloaded file
                files = list(Path(self.downloads_dir).glob('*'))
                # Sort by modification time to get the most recent file
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                if files:
                    downloaded_file = files[0]
                    download_obj.file_path = str(downloaded_file)
                    download_obj.file_size = downloaded_file.stat().st_size
                    download_obj.status = 'completed'
                    download_obj.completed_at = timezone.now()
                else:
                    download_obj.status = 'failed'
                    download_obj.error_message = 'Downloaded file not found'
            else:
                # Failed
                download_obj.status = 'failed'
                download_obj.error_message = result.stderr[:500] if result.stderr else 'Unknown error'
            
            download_obj.save()
            return download_obj.status == 'completed'
            
        except subprocess.TimeoutExpired:
            download_obj.status = 'failed'
            download_obj.error_message = 'Download timeout'
            download_obj.save()
            return False
        except Exception as e:
            download_obj.status = 'failed'
            download_obj.error_message = str(e)[:500]
            download_obj.save()
            return False
    
    def get_info(self, url):
        """Get video information without downloading"""
        try:
            cmd = ['yt-dlp', '--dump-json', '--no-download', url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': [
                        {
                            'format_id': f.get('format_id'),
                            'ext': f.get('ext'),
                            'height': f.get('height'),
                            'filesize': f.get('filesize', 0)
                        }
                        for f in info.get('formats', [])
                        if f.get('height')
                    ]
                }
        except:
            pass
        return None