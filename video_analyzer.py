"""
Video Analysis Module using Google Gemini API
Based on video-analyzer project architecture
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from flask import jsonify

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class VideoAnalyzer:
    """Video analysis using Google Gemini multimodal capabilities"""
    
    def __init__(self):
        self.model = None
        self.stream_model = None
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            # Configure for streaming
            self.stream_model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
        
        # Analysis modes similar to video-analyzer project
        self.modes = {
            'summary': {
                'emoji': '📝',
                'prompt': """Analyze this video and provide:
                1. A comprehensive summary of the main content
                2. Key topics discussed or shown
                3. Important moments with timestamps
                Format the response as structured JSON with sections for summary, key_topics, and moments.""",
                'description': 'Comprehensive video summary'
            },
            'key_moments': {
                'emoji': '🔑',
                'prompt': """Identify the most important moments in this video.
                For each key moment, provide:
                - Timestamp (approximate time in the video)
                - Description of what happens
                - Why it's important
                Return as JSON with an array of moments.""",
                'description': 'Extract key moments'
            },
            'transcript': {
                'emoji': '💬',
                'prompt': """Extract all spoken dialogue and important text from the video.
                Include:
                - Speaker identification (if possible)
                - Timestamps for major sections
                - Any on-screen text that appears
                Format as JSON with transcript sections.""",
                'description': 'Extract dialogue and text'
            },
            'objects': {
                'emoji': '👁️',
                'prompt': """Identify all objects, people, and scenes in the video.
                For each scene change, list:
                - Timestamp
                - Objects visible
                - People count and description
                - Scene setting/location
                Return as structured JSON.""",
                'description': 'Detect objects and scenes'
            },
            'sentiment': {
                'emoji': '😊',
                'prompt': """Analyze the emotional tone and sentiment throughout the video.
                Track:
                - Overall sentiment (positive/negative/neutral)
                - Emotional moments with timestamps
                - Mood changes
                - Energy level variations
                Return as JSON with sentiment analysis.""",
                'description': 'Analyze emotional content'
            },
            'educational': {
                'emoji': '🎓',
                'prompt': """Extract educational content and learning points from the video.
                Identify:
                - Main concepts explained
                - Key takeaways
                - Examples or demonstrations
                - Action items or recommendations
                Format as structured JSON for learning.""",
                'description': 'Extract educational content'
            },
            'custom': {
                'emoji': '🔧',
                'prompt_template': """Analyze this video according to the following instructions:
                {user_prompt}
                
                Return the analysis in structured JSON format.""",
                'description': 'Custom analysis'
            }
        }
        
        # System instruction for consistent responses
        self.system_instruction = """You are an expert video analyst. 
        Always provide structured, detailed analysis in JSON format.
        Include timestamps when relevant.
        Be concise but comprehensive."""
    
    def upload_video_file(self, file_path: str) -> Optional[Any]:
        """Upload video file to Gemini for processing"""
        if not self.model:
            return None
            
        try:
            print(f"Uploading video: {file_path}")
            video_file = genai.upload_file(path=file_path)
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                print("Processing video...")
                time.sleep(5)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise ValueError("Video processing failed")
            
            print("Video uploaded successfully")
            return video_file
            
        except Exception as e:
            print(f"Error uploading video: {e}")
            return None
    
    def analyze_video(self, video_path: str, mode: str = 'summary', 
                     custom_prompt: str = None) -> Dict:
        """
        Analyze video using specified mode
        
        Args:
            video_path: Path to video file
            mode: Analysis mode from self.modes
            custom_prompt: Custom prompt for 'custom' mode
            
        Returns:
            Dict with analysis results
        """
        if not self.model:
            return {
                'error': 'Gemini API key not configured',
                'status': 'failed'
            }
        
        try:
            # Upload video
            video_file = self.upload_video_file(video_path)
            if not video_file:
                return {
                    'error': 'Failed to upload video',
                    'status': 'failed'
                }
            
            # Get prompt for mode
            mode_config = self.modes.get(mode, self.modes['summary'])
            
            if mode == 'custom' and custom_prompt:
                prompt = mode_config['prompt_template'].format(user_prompt=custom_prompt)
            else:
                prompt = mode_config.get('prompt', self.modes['summary']['prompt'])
            
            # Generate analysis
            print(f"Analyzing video with mode: {mode}")
            response = self.model.generate_content([
                prompt,
                video_file
            ])
            
            # Parse response
            try:
                response_text = response.text
                
                # Try to extract JSON from markdown code block first
                import re
                json_in_markdown = re.search(r'```json\n([\s\S]*?)\n```', response_text)
                if json_in_markdown:
                    # Parse JSON from markdown block
                    analysis_data = json.loads(json_in_markdown.group(1))
                else:
                    # Try to find raw JSON
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        analysis_data = json.loads(json_match.group())
                    else:
                        # Fallback to plain text
                        analysis_data = {'summary': response_text}
            except Exception as e:
                print(f"Error parsing response: {e}")
                analysis_data = {'summary': response.text}
            
            # Make sure we return a flat structure
            # Remove any nested 'analysis' keys
            while isinstance(analysis_data, dict) and 'analysis' in analysis_data and len(analysis_data) == 1:
                analysis_data = analysis_data['analysis']
            
            analysis_content = analysis_data
            
            return {
                'status': 'success',
                'mode': mode,
                'mode_emoji': mode_config['emoji'],
                'mode_description': mode_config['description'],
                'analysis': analysis_content,
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"Error analyzing video: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def analyze_with_timecodes(self, video_path: str) -> Dict:
        """
        Special analysis to extract timecoded moments (similar to video-analyzer)
        
        Returns:
            Dict with timecoded analysis
        """
        if not self.model:
            return {
                'error': 'Gemini API key not configured',
                'status': 'failed'
            }
        
        try:
            video_file = self.upload_video_file(video_path)
            if not video_file:
                return {
                    'error': 'Failed to upload video',
                    'status': 'failed'
                }
            
            # Prompt specifically for timecoded analysis
            prompt = """Analyze this video and provide a detailed timeline with timecodes.
            For each significant moment or scene change, provide:
            {
                "timecodes": [
                    {
                        "time": "00:00",
                        "text": "Description of what happens",
                        "objects": ["list", "of", "visible", "objects"],
                        "importance": 1-10 scale,
                        "category": "intro/content/conclusion/transition"
                    }
                ]
            }
            
            Be thorough and include all significant moments.
            Format times as MM:SS or HH:MM:SS.
            """
            
            response = self.model.generate_content([prompt, video_file])
            
            # Parse timecoded response
            try:
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    timecode_data = json.loads(json_match.group())
                else:
                    timecode_data = {'timecodes': []}
            except:
                timecode_data = {'timecodes': []}
            
            return {
                'status': 'success',
                'timecodes': timecode_data.get('timecodes', []),
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"Error in timecode analysis: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def chat_about_video(self, video_path: str, question: str, 
                        context: List[Dict] = None) -> str:
        """
        Answer questions about the video using chat interface
        
        Args:
            video_path: Path to video file
            question: User's question about the video
            context: Previous conversation context
            
        Returns:
            AI response about the video
        """
        if not self.model:
            return "Gemini API key not configured. Cannot analyze video."
        
        try:
            video_file = self.upload_video_file(video_path)
            if not video_file:
                return "Failed to process video for analysis."
            
            # Build conversation with context
            messages = []
            
            # Add system context
            messages.append(f"""You are analyzing a video and answering questions about it.
            Be helpful, accurate, and reference specific moments when relevant.
            User question: {question}""")
            
            # Add video
            messages.append(video_file)
            
            # Generate response
            response = self.model.generate_content(messages)
            
            return response.text
            
        except Exception as e:
            return f"Error analyzing video: {str(e)}"
    
    def analyze_with_transcript(self, transcript: str, mode: str = 'summary', 
                               custom_prompt: str = None) -> Dict:
        """
        Analyze using existing transcript (e.g., from YouTube)
        
        Args:
            transcript: Pre-existing transcript text
            mode: Analysis mode
            custom_prompt: Custom prompt for 'custom' mode
            
        Returns:
            Dict with analysis results
        """
        if not self.model:
            return {
                'error': 'Gemini API key not configured',
                'status': 'failed'
            }
        
        try:
            # Get prompt for mode
            mode_config = self.modes.get(mode, self.modes['summary'])
            
            if mode == 'custom' and custom_prompt:
                prompt = custom_prompt
            else:
                prompt = mode_config['prompt']
            
            # Build the full prompt with transcript
            full_prompt = f"""Analyze this video transcript and {prompt}
            
            Transcript:
            {transcript}
            
            Provide a structured analysis in JSON format."""
            
            # Generate analysis
            response = self.model.generate_content(full_prompt)
            
            # Try to parse JSON response
            try:
                import json
                analysis_data = json.loads(response.text)
            except:
                # If not JSON, return as text
                analysis_data = {'analysis': response.text}
            
            return {
                'status': 'success',
                'mode': mode,
                'mode_emoji': mode_config['emoji'],
                'mode_description': mode_config['description'],
                'analysis': analysis_data,
                'source': 'transcript',
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"Error analyzing with transcript: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def chat_with_transcription(self, transcription: str, question: str,
                                context: List[Dict] = None) -> str:
        """
        Answer questions using transcription text only (no video file)
        
        Args:
            transcription: Video transcription text
            question: User's question
            context: Previous conversation context
            
        Returns:
            AI response based on transcription
        """
        if not self.model:
            return "Gemini API key not configured."
        
        try:
            # Build context from previous messages
            context_str = ""
            if context:
                for msg in context[-5:]:  # Last 5 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    context_str += f"{role}: {content}\n"
            
            # Create prompt with transcription
            prompt = f"""Based on this video transcription, answer the user's question.
            
            Video Transcription:
            {transcription[:4000]}  # Limit to avoid token issues
            
            Previous Conversation:
            {context_str if context_str else "No previous context"}
            
            User Question: {question}
            
            Please provide a helpful, specific answer based on the video content.
            Reference specific parts of the video when relevant."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_quick_transcription(self, video_path: str) -> Dict:
        """
        Get a quick transcription with timestamps for chat context
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dict with transcription and timestamps
        """
        if not self.model:
            return {'error': 'API not configured', 'transcription': ''}
        
        try:
            video_file = self.upload_video_file(video_path)
            if not video_file:
                return {'error': 'Failed to upload', 'transcription': ''}
            
            # Quick transcription prompt
            prompt = """Extract a quick transcription of this video with timestamps.
            Format: [MM:SS] Text content
            Focus on main dialogue and important moments.
            Keep it concise but informative."""
            
            response = self.model.generate_content([prompt, video_file])
            
            return {
                'transcription': response.text,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {'error': str(e), 'transcription': ''}
    
    def chat_stream(self, transcription: str, question: str, 
                   context: List[Dict] = None, video_path: str = None):
        """
        Stream chat responses for real-time interaction
        
        Args:
            transcription: Video transcription text
            question: User's question
            context: Previous conversation
            video_path: Optional path to video file (for fallback)
            
        Yields:
            Streamed response chunks
        """
        if not self.stream_model:
            yield "API not configured"
            return
        
        try:
            # Build enhanced prompt with transcription
            prompt = f"""Based on this video transcription, answer the question:
            
            Transcription:
            {transcription[:3000] if transcription else 'Not available'}
            
            Question: {question}
            
            Previous context: {str(context[-3:]) if context else 'None'}
            
            Provide a helpful, specific answer. Reference timestamps when relevant."""
            
            # Use transcription-based response for speed
            response = self.stream_model.generate_content(
                prompt,
                stream=True
            )
            
            # Stream the response
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"Error: {str(e)}"


# Fallback analyzer for when Gemini is not available
class MockVideoAnalyzer:
    """Mock analyzer for testing without API key"""
    
    def analyze_video(self, video_path: str, mode: str = 'summary', 
                     custom_prompt: str = None) -> Dict:
        """Return mock analysis for testing"""
        
        mock_analyses = {
            'summary': {
                'summary': 'This is a mock video analysis. The actual analysis will extract key information from your video.',
                'key_topics': ['Topic 1', 'Topic 2', 'Topic 3'],
                'moments': [
                    {'time': '00:15', 'description': 'Introduction'},
                    {'time': '01:30', 'description': 'Main content'},
                    {'time': '03:45', 'description': 'Conclusion'}
                ]
            },
            'key_moments': {
                'moments': [
                    {
                        'time': '00:30',
                        'description': 'Important point discussed',
                        'importance': 'High'
                    },
                    {
                        'time': '02:15',
                        'description': 'Key demonstration',
                        'importance': 'Critical'
                    }
                ]
            },
            'transcript': {
                'transcript': [
                    {'time': '00:00', 'text': 'Video begins...'},
                    {'time': '00:30', 'text': 'Main content starts...'}
                ]
            }
        }
        
        return {
            'status': 'success',
            'mode': mode,
            'analysis': mock_analyses.get(mode, mock_analyses['summary']),
            'note': 'This is mock data. Configure GEMINI_API_KEY for real analysis.',
            'timestamp': time.time()
        }
    
    def analyze_with_timecodes(self, video_path: str) -> Dict:
        """Return mock timecoded analysis"""
        return {
            'status': 'success',
            'timecodes': [
                {
                    'time': '00:00',
                    'text': 'Video introduction',
                    'objects': ['person', 'background'],
                    'importance': 8,
                    'category': 'intro'
                },
                {
                    'time': '00:30',
                    'text': 'Main content begins',
                    'objects': ['presenter', 'screen'],
                    'importance': 10,
                    'category': 'content'
                }
            ],
            'note': 'This is mock data. Configure GEMINI_API_KEY for real analysis.',
            'timestamp': time.time()
        }
    
    def chat_about_video(self, video_path: str, question: str, 
                        context: List[Dict] = None) -> str:
        """Return mock chat response"""
        responses = {
            'summary': 'This video appears to contain important information that would be analyzed with the Gemini API.',
            'what': 'The video content would be analyzed to answer your specific question.',
            'default': f'To answer "{question}", I would need to analyze the video with the Gemini API. Please configure your API key.'
        }
        
        # Simple keyword matching for mock responses
        question_lower = question.lower()
        if 'summary' in question_lower or 'summarize' in question_lower:
            return responses['summary']
        elif 'what' in question_lower:
            return responses['what']
        else:
            return responses['default']
    
    def analyze_with_transcript(self, transcript: str, mode: str = 'summary', 
                               custom_prompt: str = None) -> Dict:
        """Mock analysis using transcript"""
        mock_analyses = {
            'summary': {
                'summary': 'Mock analysis of the YouTube transcript.',
                'key_topics': ['Extracted from transcript'],
                'source': 'youtube_transcript'
            },
            'key_moments': {
                'moments': [
                    {'time': '00:30', 'description': 'Key moment from transcript'},
                    {'time': '01:00', 'description': 'Another important point'}
                ]
            }
        }
        
        return {
            'status': 'success',
            'mode': mode,
            'analysis': mock_analyses.get(mode, mock_analyses['summary']),
            'source': 'transcript',
            'note': 'Mock analysis using YouTube transcript',
            'timestamp': time.time()
        }
    
    def chat_with_transcription(self, transcription: str, question: str,
                                context: List[Dict] = None) -> str:
        """Mock transcription-based chat for testing"""
        return f"""Based on the video transcription, here's my response to "{question}":
        
        This is a mock response using the transcription for testing purposes.
        The actual implementation would analyze the transcription and provide relevant answers.
        
        To get real AI-powered responses, please configure your GEMINI_API_KEY."""
    
    def get_quick_transcription(self, video_path: str) -> Dict:
        """Return mock transcription for testing"""
        return {
            'transcription': """[00:00] Mock video transcription begins
[00:15] Important point discussed in the video
[00:30] Another key moment with relevant content
[01:00] Main topic elaboration
[01:30] Examples and demonstrations
[02:00] Conclusion and summary points
This is mock transcription data. Configure GEMINI_API_KEY for real transcription.""",
            'timestamp': time.time()
        }
    
    def chat_stream(self, transcription: str, question: str, 
                   context: List[Dict] = None, video_path: str = None):
        """Mock streaming response for testing"""
        mock_response = f"""Based on the video content, here's my analysis of your question: "{question}"
        
        The video contains important information that would be fully analyzed with the Gemini API.
        This is a mock streaming response for testing purposes.
        
        To get real-time AI analysis, please configure your GEMINI_API_KEY environment variable."""
        
        # Simulate streaming by yielding words
        words = mock_response.split()
        for i in range(0, len(words), 2):
            chunk = ' '.join(words[i:i+2])
            yield chunk + ' '
            time.sleep(0.05)  # Simulate streaming delay


def get_analyzer() -> VideoAnalyzer:
    """Get appropriate analyzer based on API key availability"""
    if GEMINI_API_KEY:
        return VideoAnalyzer()
    else:
        print("Warning: GEMINI_API_KEY not configured. Using mock analyzer.")
        return MockVideoAnalyzer()