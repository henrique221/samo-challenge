from django import forms
from .models import Download


class DownloadForm(forms.Form):
    url = forms.URLField(
        label='YouTube URL',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.youtube.com/watch?v=...',
            'required': True
        })
    )
    
    download_type = forms.ChoiceField(
        choices=Download.DOWNLOAD_TYPES,
        initial='video',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    quality = forms.ChoiceField(
        choices=[
            ('best', 'Best Quality'),
            ('1080p', '1080p'),
            ('720p', '720p'),
            ('480p', '480p'),
            ('360p', '360p'),
            ('worst', 'Lowest Quality'),
        ],
        initial='best',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )