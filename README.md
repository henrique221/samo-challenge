# Video Intelligence - One-Shot Multimodal Prompt Solution

## 🧪 Challenge Submission: Prompt-Crafting Superpower

**Developer:** Henrique Borges da Silva

This project is my submission for the **"Show Us Your Prompt-Crafting Superpower"** challenge. It demonstrates how a single, well-crafted prompt can transform raw video content into structured, actionable insights.

## 🎯 The Problem & Solution

**Real-World Problem:** YouTube videos contain valuable information locked in unstructured audio-visual format, making it difficult to quickly extract insights, search content, or get specific information without watching the entire video.

**Creative Solution:** A one-shot multimodal prompt system that analyzes YouTube videos and provides 7 different types of structured analysis, plus interactive Q&A - all from a single video input.

## 🚀 Features

- **YouTube Video Download**: Downloads videos in optimized quality (720p) using yt-dlp
- **AI Video Analysis**: 7 different analysis modes powered by Google Gemini
  - 📝 Summary generation
  - 🔑 Key moments extraction  
  - 👀 Audio/Visual transcription
  - 🤓 Object detection
  - 😊 Sentiment analysis
  - 🎓 Educational points extraction
  - 🔧 Custom analysis with user prompts
- **Interactive Chat**: Ask questions about the video content with context-aware responses
- **Session Management**: Automatic cleanup of temporary files
- **Dockerized Deployment**: Easy setup and deployment with Docker
- **Modern UI**: Professional interface with real-time updates

## 🛠 Technology Stack

- **Backend**: Python Flask
- **AI Integration**: Google Gemini API (generative-ai)
- **Video Processing**: yt-dlp
- **Containerization**: Docker & Docker Compose
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 🎥 Demo Video

https://github.com/user-attachments/assets/video_demo/video.mp4

## 🚀 Quick Start (< 5 minutes)

### Prerequisites
- Docker and Docker Compose installed
- Google Gemini API key (optional - works with mock analyzer for testing)

### Setup & Run

1. Clone the repository:
```bash
git clone https://github.com/henriqueborges/samo-challenge.git
cd samo-challenge
```

2. Start the application (takes ~2-3 minutes first time):
```bash
docker-compose up -d --build
```

3. Open your browser:
```
http://localhost:5000
```

4. Try it out:
   - Paste any YouTube URL
   - Click "Analyze Video" 
   - Select an analysis mode (e.g., "Summary" or "Key Moments")
   - Watch the AI extract insights in seconds!

### Using with Gemini API

To use real AI analysis instead of the mock analyzer:

1. Set your Gemini API key as environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

2. Update docker-compose.yml to pass the environment variable:
```yaml
services:
  app:
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - USE_MOCK_ANALYZER=false
```

3. Restart the container:
```bash
docker-compose down
docker-compose up -d --build
```

## 🎮 Usage

### Web Interface

1. **Download Video**: 
   - Open http://localhost:5000 in your browser
   - Paste a YouTube URL in the input field
   - Click "Analyze Video" to download and prepare for analysis

2. **Analyze Content**:
   - Select an analysis mode from the dropdown menu
   - For custom analysis, select "Custom" and enter your specific prompt
   - Click "Run Analysis" to process the video

3. **Interactive Chat**:
   - After analysis, use the chat interface at the bottom
   - Ask any questions about the video content
   - The AI maintains context throughout the conversation

### Command Line (Original functionality)

The original command-line functionality is still available:

```bash
# Download video
docker-compose run --rm youtube-downloader "https://www.youtube.com/watch?v=VIDEO_ID"

# Download audio only
docker-compose run --rm youtube-downloader -a "https://www.youtube.com/watch?v=VIDEO_ID"

# View video info
docker-compose run --rm youtube-downloader -i "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 🏗 Architecture

### System Components

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│   Web Client    │────▶│   Flask Server   │────▶│  Video Analyzer │
│   (Browser)     │     │   (app.py)       │     │  (Gemini API)  │
│                 │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         │                       ▼                         │
         │              ┌──────────────────┐              │
         └─────────────▶│   yt-dlp Engine  │◀─────────────┘
                        │   (Downloads)    │
                        │                  │
                        └──────────────────┘
```

### Key Files

- `app.py` - Flask server with API endpoints
- `video_analyzer.py` - AI integration module with Gemini API
- `templates/index.html` - Web interface
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Service orchestration

## 📝 API Endpoints

- `GET /` - Main application interface
- `POST /download` - Download YouTube video
- `POST /analyze` - Analyze video with selected mode
- `POST /chat` - Interactive Q&A about video
- `GET /stream/<filename>` - Stream video for playback
- `POST /cleanup` - Clean session files
- `GET /analysis-modes` - Get available analysis modes

## 🧠 AI Analysis Modes

### 1. Summary
Generates a comprehensive paragraph summarizing the video content with timecodes.

### 2. Key Moments
Extracts important moments and highlights with precise timestamps.

### 3. Transcript (A/V Captions)
Creates detailed captions describing both visual scenes and spoken text.

### 4. Objects Detected
Identifies and lists objects visible in key frames throughout the video.

### 5. Sentiment Analysis
Analyzes the emotional tone and sentiment changes throughout the video.

### 6. Educational Points
Extracts educational content and learning points from the video.

### 7. Custom Analysis
Allows users to provide their own prompts for specialized analysis.

## 💡 The One-Shot Prompt Approach

### Prompt Solution
This system uses **one-shot multimodal prompts** that analyze entire YouTube videos in a single API call. Each analysis mode is a carefully crafted prompt that transforms unstructured video content into structured, actionable data.

### Model & Integration
- **Model**: Google Gemini 1.5 Pro (multimodal)
- **System Prompt**: Structured output using function calling for consistent JSON responses
- **Tool Integration**: YouTube transcript API for enhanced context when available

### Example One-Shot Prompts

Each analysis mode uses a **single prompt** that processes the **entire video** in one API call:

```python
# 1. Summary Mode - Complete video understanding in one shot
prompt = """Analyze this video and provide:
1. A comprehensive summary of the main content
2. Key topics discussed or shown
3. Important moments with timestamps
Format the response as structured JSON with sections for summary, key_topics, and moments."""

# 2. Key Moments Extraction - Identifies all highlights in one pass
prompt = """Identify the most important moments in this video.
For each key moment, provide:
- Timestamp (approximate time in the video)
- Description of what happens
- Why it's important
Return as JSON with an array of moments."""

# 3. Educational Content Extraction - Full learning analysis
prompt = """Extract educational content and learning points from the video.
Identify:
- Main concepts explained
- Key takeaways
- Examples or demonstrations
- Action items or recommendations
Format as structured JSON."""
```

**The Magic**: Each prompt above analyzes hours of video in a single API call, transforming unstructured content into structured, actionable data!

## ✨ Why This Solution is Creative & Useful

### Real-World Problem Solved
- **Before**: Watch a 30-minute tutorial to find one specific technique
- **After**: Get instant summaries, search specific moments, or ask questions

### Creative Elements
1. **7-in-1 Analysis**: One video input generates 7 different analysis types
2. **Multimodal Magic**: Combines visual + audio understanding in single prompts
3. **Interactive Knowledge**: Transforms static videos into queryable knowledge bases
4. **YouTube Integration**: Intelligently uses existing transcripts when available

### Technical Innovation
- **Function Calling**: Ensures structured, consistent outputs from creative prompts
- **Context Caching**: Maintains video understanding across multiple queries
- **Streaming Responses**: Real-time chat responses using Server-Sent Events
- **Fallback Intelligence**: Gracefully handles API limits with mock analyzer

## 📊 Meeting the Evaluation Criteria

### 🎨 Creativity
- **Unique Approach**: Uses multimodal prompts to "watch" videos like a human would
- **Practical Value**: Solves the real problem of information locked in video format
- **Delightful UX**: Professional video player with instant AI insights

### 📝 Clarity
- **Well-Crafted Prompts**: Each analysis mode uses clear, purposeful prompting
- **Structured Output**: Function calling ensures consistent, parseable results
- **Easy to Understand**: Simple UI with clear analysis modes

### 💻 Technical Polish
- **Clean Architecture**: Dockerized, modular, well-documented code
- **Quick Setup**: < 5 minutes from clone to running
- **Production Ready**: Error handling, caching, session management
- **Fallback Support**: Works without API key using mock analyzer

## 📁 File Structure

```
samo-challenge/
├── app.py                 # Flask application
├── video_analyzer.py      # AI analysis module
├── templates/
│   └── index.html        # Web interface
├── downloads/            # Temporary video storage
├── Dockerfile           # Container definition
├── docker-compose.yml   # Service configuration
└── README.md           # This file
```

## 🔧 Environment Variables

- `GEMINI_API_KEY` - Your Google Gemini API key
- `USE_MOCK_ANALYZER` - Set to "false" to use real API (default: "true")

## ⚠️ Legal Notice

This tool is for educational purposes only. Respect copyright laws and YouTube's Terms of Service. Only download videos you have permission to download.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google Gemini team for the powerful multimodal AI API
- yt-dlp community for the robust video downloading tool
- Samo for the inspiring prompt-crafting challenge
- Original video-analyzer project for architecture inspiration

---

**Built with ❤️ for Samo's AI Challenge by Henrique Borges da Silva**

*This project demonstrates how AI can transform video content into structured, searchable, and interactive knowledge.*