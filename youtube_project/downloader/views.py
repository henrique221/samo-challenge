from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from .models import Download
from .forms import DownloadForm
from .utils import YouTubeDownloader
import os
import json


def index(request):
    """Main page with download form and history"""
    if request.method == 'POST':
        form = DownloadForm(request.POST)
        if form.is_valid():
            # Create download record
            download = Download.objects.create(
                url=form.cleaned_data['url'],
                download_type=form.cleaned_data['download_type'],
                quality=form.cleaned_data['quality'],
                status='pending'
            )
            
            # Start download process (synchronous for now)
            downloader = YouTubeDownloader()
            success = downloader.download(download)
            
            if success:
                messages.success(request, f'Download completed: {download.title}')
            else:
                messages.error(request, f'Download failed: {download.error_message}')
            
            return redirect('downloader:index')
    else:
        form = DownloadForm()
    
    # Get recent downloads
    downloads = Download.objects.all()[:20]
    
    context = {
        'form': form,
        'downloads': downloads
    }
    return render(request, 'downloader/index.html', context)


def download_status(request, download_id):
    """Get download status via AJAX"""
    download = get_object_or_404(Download, id=download_id)
    return JsonResponse({
        'id': download.id,
        'status': download.status,
        'title': download.title,
        'progress': 0,  # TODO: Implement progress tracking
        'error_message': download.error_message,
        'file_size_mb': download.get_file_size_mb(),
        'duration': download.get_duration_formatted()
    })


def video_info(request):
    """Get video information without downloading"""
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'URL is required'}, status=400)
    
    downloader = YouTubeDownloader()
    info = downloader.get_info(url)
    
    if info:
        return JsonResponse(info)
    else:
        return JsonResponse({'error': 'Failed to get video information'}, status=400)


def download_file(request, download_id):
    """Serve downloaded file"""
    download = get_object_or_404(Download, id=download_id, status='completed')
    
    if not download.file_path or not os.path.exists(download.file_path):
        messages.error(request, 'File not found')
        return redirect('downloader:index')
    
    # Serve the file
    return FileResponse(
        open(download.file_path, 'rb'),
        as_attachment=True,
        filename=os.path.basename(download.file_path)
    )


def delete_download(request, download_id):
    """Delete a download record and its file"""
    if request.method == 'POST':
        download = get_object_or_404(Download, id=download_id)
        
        # Delete file if exists
        if download.file_path and os.path.exists(download.file_path):
            try:
                os.remove(download.file_path)
            except:
                pass
        
        # Delete record
        download.delete()
        messages.success(request, 'Download deleted successfully')
    
    return redirect('downloader:index')


def download_history(request):
    """Show all download history"""
    downloads = Download.objects.all()
    return render(request, 'downloader/history.html', {'downloads': downloads})