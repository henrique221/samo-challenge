from django.contrib import admin
from .models import Download


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ['title', 'download_type', 'quality', 'status', 'created_at', 'file_size']
    list_filter = ['status', 'download_type', 'created_at']
    search_fields = ['title', 'url']
    readonly_fields = ['created_at', 'completed_at']
    
    def file_size(self, obj):
        return f"{obj.get_file_size_mb()} MB" if obj.file_size else "-"
    file_size.short_description = "Size"