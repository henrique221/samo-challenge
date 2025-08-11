// Loading overlay functions
function showLoading(status, message) {
    const overlay = document.getElementById('loadingOverlay');
    const statusEl = document.getElementById('loadingStatus');
    const messageEl = document.getElementById('loadingMessage');
    
    overlay.classList.add('active');
    statusEl.textContent = status;
    messageEl.textContent = message;
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('active');
    clearInterval(messageInterval);
}

function updateLoadingStep(stepName, state) {
    const step = document.getElementById(`step-${stepName}`);
    if (step) {
        step.classList.remove('active', 'completed');
        if (state) {
            step.classList.add(state);
        }
    }
}

const loadingMessages = {
    download: [
        "Connecting to video source...",
        "Downloading video content...",
        "Processing video data...",
        "Almost there..."
    ],
    process: [
        "Extracting video frames...",
        "Preparing for analysis...",
        "Optimizing video quality..."
    ],
    analyze: [
        "AI is analyzing your video...",
        "Extracting key moments...",
        "Generating insights...",
        "Finalizing analysis..."
    ]
};

let messageIndex = 0;
let messageInterval;

function startMessageRotation(stage) {
    messageIndex = 0;
    clearInterval(messageInterval);
    
    messageInterval = setInterval(() => {
        const messages = loadingMessages[stage] || [];
        if (messages.length > 0) {
            document.getElementById('loadingMessage').textContent = 
                messages[messageIndex % messages.length];
            messageIndex++;
        }
    }, 2000);
}

// Complete flow with loading
async function processVideoComplete() {
    const url = document.getElementById('videoUrl').value.trim();
    if (!url) {
        showAlert('<i class="bi bi-exclamation-triangle"></i> Please enter a video URL', 'error');
        return;
    }
    
    // Show loading overlay
    showLoading('Downloading video...', 'Please wait while we fetch your video');
    updateLoadingStep('download', 'active');
    startMessageRotation('download');
    
    try {
        // Step 1: Download video
        const downloadResponse = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        
        const downloadData = await downloadResponse.json();
        
        if (!downloadData.success) {
            throw new Error(downloadData.error || 'Download failed');
        }
        
        // Store video data
        currentVideo = downloadData;
        
        // Update loading state
        updateLoadingStep('download', 'completed');
        updateLoadingStep('process', 'active');
        showLoading('Processing video...', 'Preparing your video for analysis');
        startMessageRotation('process');
        
        // Fetch transcription in background
        fetchTranscription(downloadData.filename);
        
        // Wait a bit for visual effect
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Step 2: Analyze video
        updateLoadingStep('process', 'completed');
        updateLoadingStep('analyze', 'active');
        showLoading('Analyzing video...', 'AI is processing your video');
        startMessageRotation('analyze');
        
        const analyzeResponse = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: downloadData.filename,
                mode: 'summary',
                custom_prompt: null
            })
        });
        
        const analyzeData = await analyzeResponse.json();
        
        if (!analyzeData.success) {
            throw new Error(analyzeData.error || 'Analysis failed');
        }
        
        // Step 3: Everything successful - show UI
        updateLoadingStep('analyze', 'completed');
        
        // Wait a moment to show completion
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Hide loading
        hideLoading();
        
        // Now show everything at once
        showCompleteUI(downloadData, analyzeData);
        
    } catch (error) {
        hideLoading();
        showAlert(`<i class="bi bi-x-circle"></i> Error: ${error.message}`, 'error');
    }
}

function showCompleteUI(videoData, analysisData) {
    // Remove centered class from input
    document.getElementById('inputSection').classList.remove('centered');
    
    // Show main content grid
    const mainContent = document.getElementById('mainContent');
    mainContent.style.display = 'grid';
    mainContent.classList.add('fade-in');
    
    // Setup video player
    const videoPlayer = document.getElementById('videoPlayer');
    videoPlayer.src = `/stream/${videoData.filename}`;
    videoPlayer.style.display = 'block';
    document.getElementById('videoPlaceholder').style.display = 'none';
    
    // Show video info
    if (videoData.video_info) {
        const info = videoData.video_info;
        document.getElementById('videoTitle').textContent = info.title || 'Untitled Video';
        document.getElementById('videoMeta').innerHTML = `
            <span><i class="bi bi-person"></i> ${info.uploader || 'Unknown'}</span>
            <span><i class="bi bi-eye"></i> ${(info.view_count || 0).toLocaleString()} views</span>
            <span><i class="bi bi-clock"></i> ${formatDuration(info.duration || 0)}</span>
        `;
        document.getElementById('videoInfo').style.display = 'block';
    }
    
    // Show analysis section with slight delay
    setTimeout(() => {
        const analysisSection = document.getElementById('analysisSection');
        if (analysisSection) {
            analysisSection.style.display = 'block';
            analysisSection.classList.add('fade-in');
        }
        
        // Show mode selector
        document.getElementById('modeSelector').style.display = 'block';
        document.getElementById('analysisLoading').style.display = 'none';
        
        // Display analysis results
        displayAnalysisResults(analysisData.result);
        
        // Update status
        const status = document.getElementById('analysisStatus');
        status.style.display = 'block';
        status.innerHTML = `
            <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.85em;">
                <i class="bi bi-check-circle"></i> Analysis Complete
            </span>
        `;
        
        // Show chat section
        const chatSection = document.getElementById('chatSection');
        if (chatSection) {
            chatSection.style.display = 'block';
            chatSection.classList.add('fade-in');
            enableChat();
        }
    }, 300);
    
    // Clear URL input
    document.getElementById('videoUrl').value = '';
    
    // Show success message
    showAlert('<i class="bi bi-check-circle"></i> Video analysis complete!', 'success');
}