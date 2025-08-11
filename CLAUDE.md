# Video Intelligence System - Claude Development Guide

## Quick Start

### Build and Run
```bash
# Build and start the application
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

Access the application at http://localhost:5000

## Architecture Overview

This is a Flask-based video analysis system with:
- **Backend**: Python Flask with session management
- **Video Download**: yt-dlp for YouTube video downloading
- **AI Analysis**: Google Gemini API for video analysis (with mock fallback)
- **Transcription**: YouTube transcript API integration
- **Frontend**: HTML5 with custom video player controls
- **Deployment**: Docker containerized application

## Key Features

1. **YouTube Video Download**: Downloads videos in 720p quality
2. **YouTube Transcript Extraction**: Fetches existing YouTube transcripts when available
3. **AI Video Analysis**: 7 different analysis modes using Gemini
4. **Interactive Chat**: Context-aware Q&A about video content
5. **Professional Video Player**: Custom HTML5 controls with all standard features

## Important Implementation Details

### YouTube Transcript Integration
The system checks for YouTube transcripts before processing:
- Extracts video ID from various YouTube URL formats
- Attempts to fetch transcripts in order: pt, en, es, then any available
- Caches transcripts in Flask session to avoid redundant API calls
- Skips `/transcribe` endpoint when YouTube transcript is cached
- Falls back to video analysis when transcripts unavailable

### Session Management
- Each user session tracks downloaded files
- Video transcriptions and analysis results are cached in session
- Automatic cleanup of files older than 30 minutes

### API Endpoints
- `POST /download` - Downloads video and checks for YouTube transcript
- `POST /transcribe` - Generates transcript (skipped if YouTube transcript exists)
- `POST /analyze` - Analyzes video with selected mode
- `GET /chat/stream` - Server-sent events for streaming chat responses
- `POST /cleanup` - Removes session files

## Known Limitations

### YouTube API Blocking in Docker/WSL
YouTube may block transcript API requests from Docker/WSL environments due to IP restrictions. The system detects this and provides appropriate user feedback.

### Performance Considerations
- Video downloads limited to 720p for optimal processing
- Analysis results cached to reduce API calls
- Transcripts cached in session for reuse

## Development Commands

### Testing with Mock Analyzer
```bash
export USE_MOCK_ANALYZER=true
docker-compose up -d --build
```

### Using Real Gemini API
```bash
export GEMINI_API_KEY="your-api-key"
export USE_MOCK_ANALYZER=false
docker-compose up -d --build
```

### Debugging
```bash
# View container logs
docker-compose logs -f app

# Enter container shell
docker-compose exec app bash

# Check Python dependencies
docker-compose exec app pip list
```

## File Structure
```
samo-challenge/
├── app.py                  # Main Flask application
├── video_analyzer.py       # AI integration module
├── templates/
│   └── index.html         # Web interface with video player
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Service orchestration
└── downloads/           # Temporary video storage
```

## Common Tasks

### Adding New Analysis Modes
1. Update `video_analyzer.py` to add new analysis method
2. Add mode to `/analysis-modes` endpoint in `app.py`
3. Update UI dropdown in `index.html`

### Modifying Video Player
Video player controls are in `index.html`:
- `initializeVideoControls()` function handles all player interactions
- CSS variables in `:root` control theming
- Player supports: play/pause, progress, volume, speed, PiP, fullscreen

### Handling New Video Sources
1. Update URL extraction in `extract_youtube_video_id()` 
2. Modify download command construction in `/download` endpoint
3. Test with various URL formats

## Security Notes
- Session keys are randomly generated
- No permanent storage of videos (30-minute cleanup)
- API keys should be set via environment variables
- Input validation on all endpoints

## Troubleshooting

### Container Won't Start
```bash
# Check for port conflicts
sudo lsof -i :5000

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### YouTube Transcript Not Found
- Check if video has captions enabled
- Verify URL format is supported
- Check for IP blocking (common in Docker)

### Video Analysis Fails
- Ensure video file exists in downloads/
- Check Gemini API key is valid
- Verify file size is within limits

## Recent Updates
- Professional video player with custom controls
- YouTube transcript fetching before download
- Automatic skip of transcribe endpoint when YouTube transcript exists
- IP blocking detection and user notification
- Comprehensive .gitignore file

## Next Steps
Potential improvements:
- Add subtitle display in video player
- Implement video chapter detection
- Add batch video processing
- Enhance chat context with timestamps
- Add export functionality for analysis results