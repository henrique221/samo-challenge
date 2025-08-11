# 🎬 Video Intelligence: One-Shot Multimodal Prompt Engineering

## 🧪 Prompt-Crafting Challenge Submission

**Developer:** Henrique Borges da Silva  
**Challenge:** Show Us Your Prompt-Crafting Superpower  
**Model Used:** Google Gemini 1.5 Flash (Multimodal)  

---

## 🎯 The One-Shot Prompt Solution

### The Problem
**Billions of hours of video content exist online, but the knowledge within is locked away.** To find a specific technique in a 30-minute tutorial or extract insights from a conference talk, you must watch the entire video. This is a massive inefficiency in our information age.

### The Solution  
**Seven carefully crafted one-shot prompts that transform any video into structured, searchable knowledge** - each analyzing an entire video in a single API call:

```python
# The Core Innovation: Each prompt processes ENTIRE videos in ONE shot

SENTIMENT_PROMPT = """Analyze the emotional tone and sentiment throughout the video.
Track:
- Overall sentiment (positive/negative/neutral)
- Emotional moments with timestamps
- Mood changes
- Energy level variations
Return as JSON with sentiment analysis."""

EDUCATIONAL_PROMPT = """Extract educational content and learning points from the video.
Identify:
- Main concepts explained
- Key takeaways
- Examples or demonstrations
- Action items or recommendations
Format as structured JSON for learning."""

OBJECTS_PROMPT = """Identify all objects, people, and scenes in the video.
For each scene change, list:
- Timestamp
- Objects visible
- People count and description
- Scene setting/location
Return as structured JSON."""
```

**The Magic:** These prompts transform hours of unstructured video into instant, actionable insights!

---

## ✨ Key Features

### 🎥 Video Input Options
- **File Upload**: Drag-and-drop support for local video files (MP4, AVI, MOV, MKV, WEBM)
- **Example Videos**: Pre-loaded sample videos from the /examples folder for quick testing
- **Smart Transcription**: Automatic video transcription using AI for content extraction

### 🧠 Seven Analysis Modes (One-Shot Each)
1. **📝 Summary** - Comprehensive overview with key topics and timestamps
2. **🔑 Key Moments** - Critical points with importance ratings
3. **💬 Transcript** - Complete audio/visual content extraction
4. **👁️ Objects** - Scene-by-scene object and people detection
5. **😊 Sentiment** - Emotional analysis with mood tracking
6. **🎓 Educational** - Learning objectives and concept extraction
7. **🔧 Custom** - User-defined prompts for specialized analysis

### 💬 Interactive Features
- **Real-time Chat**: Ask questions about the video content
- **Timestamp Navigation**: Click any timestamp to jump to that moment
- **Visual Timeline**: See key moments marked on the video progress bar
- **Streaming Responses**: Real-time AI responses using Server-Sent Events

### 🎨 UI Features
- **Professional Video Player**: Custom HTML5 controls with play/pause, seek, volume, speed control, picture-in-picture, and fullscreen
- **Drag & Drop Upload**: Intuitive file upload with visual feedback
- **Example Video Gallery**: Quick access to pre-loaded sample videos
- **Two-Step Loading**: Clean progress indicator showing Processing and Analysis stages
- **Responsive Design**: Works seamlessly on desktop and mobile devices

---

## 🚀 Quick Start (< 5 Minutes)

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/samo-challenge.git
cd samo-challenge

# 2. Set your Gemini API key (optional - works without for testing)
export GEMINI_API_KEY="your-api-key-here"

# 3. Start the application
docker-compose up -d --build

# 4. Open in browser
open http://localhost:5000
```

### Option 2: Local Python

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/samo-challenge.git
cd samo-challenge
pip install -r requirements.txt

# 2. Set API key (optional)
export GEMINI_API_KEY="your-api-key-here"

# 3. Run the app
python app.py

# 4. Open in browser
open http://localhost:5000
```

### Try It Out!
1. **Upload a video file** or **select an example video** from the pre-loaded samples
2. Wait for automatic transcription to complete
3. Select **"Key Moments"** mode from the analysis options
4. Watch as the AI extracts all important points in seconds!

---

## 📊 Prompt & Model Details

### Model Configuration
- **Primary Model**: Google Gemini 1.5 Flash (multimodal capabilities)
- **Fallback**: Mock analyzer for testing without API key
- **Context Window**: Processes entire videos up to 1 hour in a single prompt

### System Prompts
Each analysis mode uses a specialized system instruction:
```python
SYSTEM_INSTRUCTION = """You are an expert video analyst. 
Always provide structured, detailed analysis in JSON format.
Include timestamps when relevant.
Be concise but comprehensive."""
```

### Tool Integration
- **Google Gemini API**: Multimodal AI for video analysis and transcription
- **FFmpeg**: Video processing and format handling
- **Server-Sent Events**: Streams chat responses in real-time

---

## 🎨 Why This is Creative & Useful

### Real-World Impact
- **Before**: Watch 60-minute lecture to find one concept → **60 minutes**
- **After**: Get summary + search specific topics → **30 seconds**

### Creative Elements
1. **Multimodal Understanding**: Analyzes both visual and audio content simultaneously
2. **Seven Perspectives**: One video generates seven different analytical viewpoints
3. **Interactive Knowledge Base**: Transforms static videos into queryable databases
4. **AI-Powered Transcription**: Direct video-to-text conversion using Gemini's multimodal capabilities

### Technical Innovation
- **One-Shot Processing**: Entire videos analyzed in single API calls
- **Structured Output**: JSON responses with consistent schema
- **Graceful Degradation**: Falls back to mock analysis when API unavailable
- **Session Management**: Automatic cleanup of temporary files

---

## 📁 Project Structure

```
samo-challenge/
├── app.py                    # Flask server with API endpoints
├── video_analyzer.py         # Core prompt engineering & Gemini integration
├── templates/
│   └── index.html           # Modern, responsive UI with video player
├── examples/                # Pre-loaded example videos
├── downloads/              # Temporary video storage
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Service orchestration
├── CLAUDE.md              # Development guide and notes
└── README.md              # This file
```

### Key Code Files

**`video_analyzer.py`** - The heart of the prompt engineering:
- Contains all seven analysis mode prompts
- Handles Gemini API integration
- Manages response parsing and structuring

**`app.py`** - Flask application:
- Video download/upload endpoints
- Analysis orchestration
- Chat interface with context management

**`templates/index.html`** - Interactive frontend:
- Drag-and-drop video upload
- Professional HTML5 video player with custom controls
- Example video gallery from /examples folder
- Real-time analysis display
- Clickable timestamps and chat interface

---

## 🔬 Technical Deep Dive

### The Prompt Engineering Approach

Each analysis mode uses a carefully crafted prompt that:
1. **Sets Clear Objectives**: Specifies exactly what to extract
2. **Defines Structure**: Requests JSON format with specific fields
3. **Provides Context**: Includes timestamps and importance ratings
4. **Ensures Completeness**: Analyzes entire video in one pass

Example - Sentiment Analysis Prompt:
```python
def analyze_sentiment(video):
    prompt = """Analyze the emotional tone and sentiment throughout the video.
    Track:
    - Overall sentiment (positive/negative/neutral)
    - Emotional moments with timestamps
    - Mood changes
    - Energy level variations
    Return as JSON with sentiment analysis."""
    
    # Single API call processes entire video
    response = gemini.generate_content([prompt, video])
    return parse_json_response(response)
```

### Handling Multimodal Input

The system processes both:
- **Visual frames**: Scene changes, objects, people
- **Audio track**: Speech, tone, music
- **Combined context**: Relates visual and audio for deeper understanding

---

## 📊 Meeting the Challenge Criteria

### ✅ Creativity
- **Unique Solution**: Transforms videos into queryable knowledge bases
- **Multiple Perspectives**: Seven different analysis modes from one input
- **Real Value**: Solves actual time-wasting problem millions face daily

### ✅ Clarity
- **Well-Crafted Prompts**: Each mode has clear, purposeful instructions
- **Clean Output**: Structured JSON with consistent formatting
- **Easy to Understand**: Simple UI with obvious functionality

### ✅ Technical Polish
- **Quick Setup**: Under 5 minutes from clone to running
- **Professional UI**: Modern, responsive design with smooth interactions
- **Error Handling**: Graceful fallbacks and informative error messages
- **Production Ready**: Docker deployment, session management, cleanup

---

## 🎮 Advanced Usage

### Custom Prompts
Create your own analysis by selecting "Custom" mode:
```
"List all the programming languages mentioned in this video,
along with the timestamp when each is first discussed."
```

### Batch Processing (CLI)
```bash
# Analyze uploaded videos
curl -X POST http://localhost:5000/upload \
  -F "video=@path/to/video.mp4"

# Analyze example videos
curl -X POST http://localhost:5000/load-example/example.mp4
```

### API Integration
```python
import requests

# Upload and analyze video
with open('video.mp4', 'rb') as f:
    response = requests.post('http://localhost:5000/upload', 
        files={'video': f})

# Run sentiment analysis
analysis = requests.post('http://localhost:5000/analyze',
    json={'filename': response.json()['filename'], 'mode': 'sentiment'})

print(analysis.json()['result'])
```

---

## 📡 API Endpoints

### Core Endpoints
- `POST /upload` - Upload video file for analysis
- `POST /transcribe` - Generate transcript from uploaded video
- `POST /analyze` - Analyze video with selected mode
- `GET /chat/stream` - Server-sent events for streaming chat
- `POST /cleanup` - Remove session files

### Example Video Endpoints
- `GET /list-examples` - List available example videos
- `POST /load-example/<filename>` - Load and prepare example video

### Utility Endpoints
- `GET /analysis-modes` - Get available analysis modes
- `GET /files/<filename>` - Serve uploaded video files
- `GET /stream/<filename>` - Stream video content

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY` - Your Google Gemini API key (get one [here](https://makersuite.google.com/app/apikey))
- `USE_MOCK_ANALYZER` - Set to "false" for real analysis (default: mock mode for testing)
- `PORT` - Server port (default: 5000)

### Docker Compose Settings
```yaml
services:
  app:
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - USE_MOCK_ANALYZER=false
    ports:
      - "5000:5000"
```

---

## 📈 Performance & Limitations

### Performance
- **Processing Time**: 5-15 seconds per video (depending on length)
- **Video Length**: Tested up to 1 hour videos
- **Concurrent Users**: Handles multiple sessions with automatic cleanup

### Current Limitations
- **File Size**: 500MB max for uploads
- **Video Length**: Best results with videos under 1 hour
- **Language**: English-optimized (other languages work with varying accuracy)
- **API Requirements**: Requires Google Gemini API key for full functionality (mock mode available for testing)

---

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional analysis modes
- Multi-language support
- Performance optimizations
- UI enhancements

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Google Gemini Team** - For the powerful multimodal API
- **Flask Community** - For the robust web framework
- **Samo** - For the inspiring prompt-crafting challenge

---

## 🎬 Demo & Contact

- **Live Demo**: [Watch the demo video](https://drive.google.com/file/d/13ET1gWRlKaVdeK0s8i6JMuQPLNDE6nsi/view?usp=sharing)
- **GitHub**: [github.com/yourusername/samo-challenge](https://github.com/henrique221/samo-challenge)
- **Contact**: hborgesdasilva9294@gmail.com

---

**Built by Henrique Borges da Silva for the Samo Prompt-Crafting Challenge**

*Transforming the way we interact with video content through the power of prompt engineering.*