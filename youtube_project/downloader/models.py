from django.db import models
from django.utils import timezone


class Download(models.Model):
    DOWNLOAD_TYPES = [
        ('video', 'Video'),
        ('audio', 'Audio Only'),
        ('playlist', 'Playlist'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('downloading', 'Downloading'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=500, blank=True)
    download_type = models.CharField(max_length=10, choices=DOWNLOAD_TYPES, default='video')
    quality = models.CharField(max_length=10, default='best')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(default=0)
    duration = models.IntegerField(default=0, help_text="Duration in seconds")
    thumbnail = models.URLField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title or self.url} - {self.get_status_display()}"
    
    def get_file_size_mb(self):
        """Return file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    def get_duration_formatted(self):
        """Return duration in HH:MM:SS format"""
        if self.duration:
            hours = self.duration // 3600
            minutes = (self.duration % 3600) // 60
            seconds = self.duration % 60
            if hours:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            return f"{minutes:02d}:{seconds:02d}"
        return "00:00"