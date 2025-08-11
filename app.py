from flask import Flask, render_template, request, jsonify, send_file, Response, session
import subprocess
import json
import os
import re
from pathlib import Path
import time
import mimetypes
import secrets
from datetime import datetime, timedelta
import threading
from video_analyzer import VideoAnalyzer, MockVideoAnalyzer
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Inicializar o analisador de vídeo
# Use MockVideoAnalyzer para testes ou VideoAnalyzer com API key real
use_mock = os.environ.get('USE_MOCK_ANALYZER', 'true').lower() == 'true'
api_key = os.environ.get('GEMINI_API_KEY', '')

if use_mock or not api_key:
    video_analyzer = MockVideoAnalyzer()
    print("Usando MockVideoAnalyzer (para usar Gemini real, defina GEMINI_API_KEY)")
else:
    video_analyzer = VideoAnalyzer()
    print("Usando VideoAnalyzer com Gemini API")

# Diretório para downloads
DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Dicionário para rastrear arquivos por sessão
session_files = {}

def extract_youtube_video_id(url):
    """Extrai o ID do vídeo do YouTube da URL"""
    try:
        parsed = urlparse(url)
        
        # youtube.com/watch?v=VIDEO_ID
        if 'youtube.com' in parsed.netloc or 'www.youtube.com' in parsed.netloc:
            if 'v' in parse_qs(parsed.query):
                video_id = parse_qs(parsed.query)['v'][0]
                print(f"Extracted video ID from watch URL: {video_id}")
                return video_id
            
            # youtube.com/embed/VIDEO_ID
            if '/embed/' in parsed.path:
                video_id = parsed.path.split('/embed/')[1].split('?')[0].split('/')[0]
                print(f"Extracted video ID from embed URL: {video_id}")
                return video_id
            
            # youtube.com/v/VIDEO_ID
            if '/v/' in parsed.path:
                video_id = parsed.path.split('/v/')[1].split('?')[0].split('/')[0]
                print(f"Extracted video ID from /v/ URL: {video_id}")
                return video_id
            
            # youtube.com/shorts/VIDEO_ID
            if '/shorts/' in parsed.path:
                video_id = parsed.path.split('/shorts/')[1].split('?')[0].split('/')[0]
                print(f"Extracted video ID from shorts URL: {video_id}")
                return video_id
        
        # youtu.be/VIDEO_ID
        if 'youtu.be' in parsed.netloc:
            video_id = parsed.path.lstrip('/').split('?')[0]
            print(f"Extracted video ID from youtu.be URL: {video_id}")
            return video_id
        
        print(f"Could not extract video ID from URL: {url}")
        return None
    except Exception as e:
        print(f"Error extracting YouTube video ID: {e}")
        return None

def get_youtube_transcript(video_id, languages=['pt', 'en', 'es']):
    """Busca a transcrição do YouTube em múltiplos idiomas"""
    try:
        print(f"Fetching YouTube transcript for video ID: {video_id}")
        
        # Create API instance
        api = YouTubeTranscriptApi()
        
        # Try to fetch transcript directly with language preference
        for language in languages:
            try:
                # This method automatically handles both manual and generated transcripts
                result = api.fetch(video_id, languages=[language])
                print(f"Found transcript in {language}")
                return format_transcript(result), language
            except Exception as e:
                error_msg = str(e)
                if "YouTube is blocking requests" in error_msg:
                    print(f"⚠️ YouTube is blocking transcript requests (IP ban)")
                    # Return a special marker to indicate IP blocking
                    return "IP_BLOCKED", "blocked"
                print(f"No transcript found for {language}: {e}")
                continue
        
        # If preferred languages fail, try to get any available transcript
        try:
            # Try English as fallback
            result = api.fetch(video_id, languages=['en'])
            print(f"Found fallback English transcript")
            return format_transcript(result), 'en'
        except:
            pass
        
        # Last resort: try to get transcript list and fetch the first available
        try:
            transcript_list = api.list(video_id)
            for transcript in transcript_list:
                try:
                    # Use the API fetch method with the transcript's language
                    result = api.fetch(video_id, languages=[transcript.language_code])
                    print(f"Using first available transcript: {transcript.language_code}")
                    return format_transcript(result), transcript.language_code
                except Exception as e:
                    print(f"Error fetching transcript for {transcript.language_code}: {e}")
                    continue
        except Exception as e:
            print(f"Error listing transcripts: {e}")
        
        print("No transcripts available at all")
        return None, None
        
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video {video_id}")
        return None, None
    except VideoUnavailable:
        print(f"Video {video_id} is unavailable")
        return None, None
    except Exception as e:
        print(f"Unexpected error fetching YouTube transcript: {e}")
        print(f"Error type: {type(e).__name__}")
        return None, None

def format_transcript(transcript_data):
    """Formata a transcrição com timestamps"""
    formatted = []
    for entry in transcript_data:
        # Handle both dict and FetchedTranscriptSnippet object formats
        if hasattr(entry, 'start'):
            # It's a FetchedTranscriptSnippet object
            start_time = entry.start
            text = entry.text.replace('\n', ' ')
        else:
            # It's a dictionary
            start_time = entry['start']
            text = entry['text'].replace('\n', ' ')
        
        # Converter segundos para formato MM:SS
        minutes = int(start_time // 60)
        seconds = int(start_time % 60)
        timestamp = f"[{minutes:02d}:{seconds:02d}]"
        
        formatted.append(f"{timestamp} {text}")
    
    return '\n'.join(formatted)

def cleanup_old_files():
    """Remove arquivos mais antigos que 30 minutos"""
    while True:
        try:
            current_time = time.time()
            for file_path in DOWNLOADS_DIR.glob('*'):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > 1800:  # 30 minutos
                        try:
                            file_path.unlink()
                            print(f"Arquivo antigo removido: {file_path.name}")
                        except:
                            pass
        except Exception as e:
            print(f"Erro na limpeza: {e}")
        time.sleep(300)  # Verificar a cada 5 minutos

# Iniciar thread de limpeza
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    """Página principal com formulário"""
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    """Extract quick transcription with timestamps for chat context"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename é obrigatório'}), 400
        
        # Check if we have cached transcription
        if 'video_transcriptions' not in session:
            session['video_transcriptions'] = {}
        
        if filename in session['video_transcriptions']:
            return jsonify({
                'success': True,
                'transcription': session['video_transcriptions'][filename],
                'cached': True
            })
        
        file_path = DOWNLOADS_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Get quick transcription
        transcription = video_analyzer.get_quick_transcription(str(file_path))
        
        # Cache it
        session['video_transcriptions'][filename] = transcription
        session.modified = True
        
        return jsonify({
            'success': True,
            'transcription': transcription,
            'cached': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    """Processa o download do vídeo e retorna informações completas"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL é obrigatória'}), 400
        
        # Verificar se é um vídeo do YouTube e tentar obter transcrição
        youtube_transcript = None
        transcript_language = None
        video_id = extract_youtube_video_id(url)
        
        if video_id:
            print(f"YouTube video detected, ID: {video_id}")
            youtube_transcript, transcript_language = get_youtube_transcript(video_id)
            
            # Check for IP blocking
            if youtube_transcript == "IP_BLOCKED":
                print("⚠️ YouTube is blocking transcript API due to IP restrictions")
                print("This commonly happens in Docker/WSL/Cloud environments")
                youtube_transcript = None
                transcript_language = None
                # You could add a flag to inform the user about this
                ip_blocked = True
            elif youtube_transcript:
                print(f"YouTube transcript found in language: {transcript_language}")
                ip_blocked = False
            else:
                print("No YouTube transcript available")
                ip_blocked = False
        
        # Primeiro, obter informações completas do vídeo
        info_cmd = ['yt-dlp', '--dump-json', '--skip-download', url]
        info_result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
        
        video_info = {}
        if info_result.returncode == 0:
            try:
                full_info = json.loads(info_result.stdout)
                video_info = {
                    'title': full_info.get('title', 'video'),
                    'thumbnail': full_info.get('thumbnail', ''),
                    'duration': full_info.get('duration', 0),
                    'uploader': full_info.get('uploader', 'Unknown'),
                    'view_count': full_info.get('view_count', 0),
                    'description': full_info.get('description', '')[:500],
                    'upload_date': full_info.get('upload_date', '')
                }
                title = video_info['title']
            except:
                title = 'video'
        else:
            title = 'video'
        
        # Limpar título para nome de arquivo
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:100]
        
        # Construir comando yt-dlp para download
        timestamp = str(int(time.time()))
        filename = f"{safe_title}_{timestamp}.mp4"
        output_path = str(DOWNLOADS_DIR / filename)
        
        cmd = ['yt-dlp']
        cmd.extend(['-o', output_path])
        
        # Baixar em qualidade média (720p ou menor disponível)
        cmd.extend(['-f', 'best[height<=720]/best'])
        
        # Garantir que seja MP4
        cmd.extend(['--merge-output-format', 'mp4'])
        
        cmd.append(url)
        
        # Executar download
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Verificar se o arquivo existe
            file_path = Path(output_path)
            if file_path.exists():
                file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                
                # Rastrear arquivo na sessão
                if 'session_id' not in session:
                    session['session_id'] = secrets.token_hex(16)
                
                session_id = session['session_id']
                if session_id not in session_files:
                    session_files[session_id] = []
                session_files[session_id].append(filename)
                
                # Armazenar transcrição do YouTube se disponível
                if youtube_transcript:
                    if 'video_transcriptions' not in session:
                        session['video_transcriptions'] = {}
                    session['video_transcriptions'][filename] = youtube_transcript
                    session.modified = True
                    print(f"YouTube transcript cached for {filename}")
                
                response_data = {
                    'success': True,
                    'filename': filename,
                    'size': f'{file_size:.2f} MB',
                    'video_info': video_info,
                    'has_youtube_transcript': youtube_transcript is not None,
                    'transcript_language': transcript_language
                }
                
                # Add IP blocking warning if detected
                if 'ip_blocked' in locals() and ip_blocked:
                    response_data['transcript_blocked'] = True
                    response_data['blocked_reason'] = 'YouTube API blocked due to IP restrictions (common in Docker/WSL)'
                
                return jsonify(response_data)
            else:
                # Tentar encontrar o arquivo com padrão similar
                pattern = f"{safe_title}_{timestamp}*"
                files = list(DOWNLOADS_DIR.glob(pattern))
                if files:
                    filename = files[0].name
                    file_size = files[0].stat().st_size / (1024 * 1024)
                    
                    # Armazenar transcrição do YouTube se disponível
                    if youtube_transcript:
                        if 'video_transcriptions' not in session:
                            session['video_transcriptions'] = {}
                        session['video_transcriptions'][filename] = youtube_transcript
                        session.modified = True
                        print(f"YouTube transcript cached for {filename}")
                    
                    response_data = {
                        'success': True,
                        'filename': filename,
                        'size': f'{file_size:.2f} MB',
                        'video_info': video_info,
                        'has_youtube_transcript': youtube_transcript is not None,
                        'transcript_language': transcript_language
                    }
                    
                    # Add IP blocking warning if detected
                    if 'ip_blocked' in locals() and ip_blocked:
                        response_data['transcript_blocked'] = True
                        response_data['blocked_reason'] = 'YouTube API blocked due to IP restrictions (common in Docker/WSL)'
                    
                    return jsonify(response_data)
                else:
                    return jsonify({'error': 'Arquivo não encontrado após download'}), 500
        else:
            error_msg = result.stderr[:500] if result.stderr else 'Erro no download'
            return jsonify({'error': error_msg}), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Download demorou muito tempo'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/info', methods=['POST'])
def get_video_info():
    """Obtém informações do vídeo sem baixar"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL é obrigatória'}), 400
        
        cmd = ['yt-dlp', '--dump-json', '--no-download', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            
            # Formatar duração
            duration = info.get('duration', 0)
            duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
            
            return jsonify({
                'success': True,
                'title': info.get('title', 'Unknown'),
                'uploader': info.get('uploader', 'Unknown'),
                'duration': duration_str,
                'views': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', ''),
                'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
            })
        else:
            return jsonify({'error': 'Não foi possível obter informações do vídeo'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files/<filename>')
def download_file(filename):
    """Serve o arquivo para download"""
    file_path = DOWNLOADS_DIR / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return "Arquivo não encontrado", 404

@app.route('/stream/<filename>')
def stream_video(filename):
    """Stream de vídeo para o player HTML5 com suporte a range requests"""
    file_path = DOWNLOADS_DIR / filename
    if not file_path.exists():
        return "Arquivo não encontrado", 404
    
    # Get file size
    file_size = file_path.stat().st_size
    
    # Parse range header
    range_header = request.headers.get('range', None)
    byte_start = 0
    byte_end = file_size - 1
    
    if range_header:
        match = re.search(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            byte_start = int(match.group(1))
            if match.group(2):
                byte_end = int(match.group(2))
    
    # Calculate content length
    content_length = byte_end - byte_start + 1
    
    # Read the requested chunk
    def generate():
        with open(file_path, 'rb') as f:
            f.seek(byte_start)
            remaining = content_length
            
            while remaining > 0:
                chunk_size = min(8192, remaining)
                data = f.read(chunk_size)
                if not data:
                    break
                remaining -= len(data)
                yield data
    
    # Prepare response headers
    mimetype = mimetypes.guess_type(file_path)[0] or 'video/mp4'
    
    response = Response(
        generate(),
        status=206,  # Partial Content
        mimetype=mimetype,
        headers={
            'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(content_length),
            'Content-Type': mimetype,
        }
    )
    
    return response

@app.route('/cleanup', methods=['POST'])
def cleanup_session_files():
    """Remove arquivos da sessão atual"""
    try:
        if 'session_id' in session:
            session_id = session['session_id']
            if session_id in session_files:
                for filename in session_files[session_id]:
                    file_path = DOWNLOADS_DIR / filename
                    if file_path.exists():
                        try:
                            file_path.unlink()
                            print(f"Arquivo removido: {filename}")
                        except Exception as e:
                            print(f"Erro ao remover {filename}: {e}")
                session_files.pop(session_id, None)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/list-downloads')
def list_downloads():
    """Lista arquivos baixados da sessão atual"""
    files = []
    if 'session_id' in session:
        session_id = session['session_id']
        if session_id in session_files:
            for filename in session_files[session_id]:
                file_path = DOWNLOADS_DIR / filename
                if file_path.exists():
                    files.append({
                        'name': filename,
                        'size': f'{file_path.stat().st_size / (1024 * 1024):.2f} MB',
                        'modified': time.strftime('%d/%m/%Y %H:%M', time.localtime(file_path.stat().st_mtime))
                    })
    files.sort(key=lambda x: x['name'], reverse=True)
    return jsonify(files)

@app.route('/analyze', methods=['POST'])
def analyze_video():
    """Analisa o vídeo usando IA"""
    try:
        data = request.json
        filename = data.get('filename')
        mode = data.get('mode', 'summary')
        custom_prompt = data.get('custom_prompt')
        
        if not filename:
            return jsonify({'error': 'Filename é obrigatório'}), 400
        
        file_path = DOWNLOADS_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Check if we have cached analysis for this video
        if 'video_analysis' not in session:
            session['video_analysis'] = {}
        
        cache_key = f"{filename}_{mode}"
        
        # Use cached result if available
        if cache_key in session['video_analysis']:
            print(f"Using cached analysis for {cache_key}")
            return jsonify({
                'success': True,
                'result': session['video_analysis'][cache_key],
                'cached': True
            })
        
        # Check if we have YouTube transcript available
        if 'video_transcriptions' in session and filename in session['video_transcriptions']:
            youtube_transcript = session['video_transcriptions'][filename]
            print(f"Using YouTube transcript for {mode} analysis")
            
            # For transcript mode, just return the transcript
            if mode == 'transcript':
                result = {
                    'transcript': youtube_transcript,
                    'source': 'youtube',
                    'status': 'success'
                }
            else:
                # For other modes, analyze using the transcript
                result = video_analyzer.analyze_with_transcript(
                    transcript=youtube_transcript,
                    mode=mode,
                    custom_prompt=custom_prompt
                )
                result['youtube_source'] = True
            
            # Cache the result
            session['video_analysis'][cache_key] = result
            session.modified = True
            
            return jsonify({
                'success': True,
                'result': result,
                'cached': False,
                'source': 'youtube_transcript'
            })
        
        # Realizar análise normal (sem transcrição do YouTube)
        print(f"No YouTube transcript available, using video analysis for {mode}")
        result = video_analyzer.analyze_video(
            str(file_path),
            mode=mode,
            custom_prompt=custom_prompt
        )
        
        # Cache the result
        session['video_analysis'][cache_key] = result
        session.modified = True
        
        # Store transcript if it's a transcript analysis
        if mode == 'transcript' and result:
            session['video_transcript'] = result
            session.modified = True
        
        return jsonify({
            'success': True,
            'result': result,
            'cached': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat_about_video():
    """Chat sobre o vídeo usando IA com contexto em cache"""
    try:
        data = request.json
        transcription = data.get('transcription', '')
        question = data.get('question')
        context = data.get('context', [])
        
        if not question:
            return jsonify({'error': 'Question é obrigatório'}), 400
        
        if not transcription:
            return jsonify({'error': 'Transcription não disponível'}), 400
        
        # Use transcription-based chat for faster responses
        response = video_analyzer.chat_with_transcription(
            transcription=transcription,
            question=question,
            context=context
        )
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/stream', methods=['GET'])
def chat_stream():
    """Stream chat responses for faster interaction using SSE"""
    try:
        # Get parameters from query string for SSE
        transcription = request.args.get('transcription', '')
        question = request.args.get('question')
        context_str = request.args.get('context', '[]')
        
        try:
            context = json.loads(context_str)
        except:
            context = []
        
        if not question:
            def error_stream():
                yield f"data: {json.dumps({'type': 'error', 'content': 'Question é obrigatório'})}\n\n"
            return Response(error_stream(), mimetype='text/event-stream')
        
        # Check if we should use cached YouTube transcript
        if transcription == 'YOUTUBE_CACHED':
            # Get the filename from session or context
            if 'video_transcriptions' in session:
                # Find the most recent transcript (assuming it's the current video)
                transcripts = session.get('video_transcriptions', {})
                if transcripts:
                    # Get the last added transcript
                    transcription = list(transcripts.values())[-1]
                    print("Using cached YouTube transcript for chat")
        
        if not transcription or transcription == 'YOUTUBE_CACHED':
            def error_stream():
                yield f"data: {json.dumps({'type': 'error', 'content': 'Transcription não disponível'})}\n\n"
            return Response(error_stream(), mimetype='text/event-stream')
        
        def generate():
            try:
                # Send initial acknowledgment
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
                
                # Use streaming from video analyzer with transcription
                stream_generator = video_analyzer.chat_stream(
                    transcription=transcription,
                    question=question,
                    context=context,
                    video_path=None  # No file path needed
                )
                
                # Stream the response chunks
                for chunk in stream_generator:
                    if chunk:
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        return Response(error_stream(), mimetype='text/event-stream')

@app.route('/analysis-modes')
def get_analysis_modes():
    """Retorna os modos de análise disponíveis"""
    modes = [
        {'id': 'summary', 'name': 'Resumo', 'emoji': '📝'},
        {'id': 'key_moments', 'name': 'Momentos-chave', 'emoji': '🔑'},
        {'id': 'transcript', 'name': 'Transcrição A/V', 'emoji': '👀'},
        {'id': 'objects', 'name': 'Objetos detectados', 'emoji': '🤓'},
        {'id': 'sentiment', 'name': 'Análise de sentimento', 'emoji': '😊'},
        {'id': 'educational', 'name': 'Pontos educacionais', 'emoji': '🎓'},
        {'id': 'custom', 'name': 'Personalizado', 'emoji': '🔧'}
    ]
    return jsonify(modes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)