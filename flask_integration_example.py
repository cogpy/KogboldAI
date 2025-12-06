#!/usr/bin/env python3
"""
Flask Integration Example for KoboldAI Kernel

This example demonstrates how to integrate the KoboldAI kernel into a Flask
web application with SocketIO for real-time story generation.

Features:
- Kernel initialization on startup with graceful fallback
- Story state management per session
- Real-time token streaming via SocketIO
- World info integration
- Generation settings management
- Memory and author's note support

Usage:
    python3 flask_integration_example.py

Then navigate to http://localhost:5000 in your browser.
"""

from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import kobold_kernel_ffi as kernel
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kobold-kernel-demo-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
kernel_available = False
stories = {}  # Session ID -> Story state

def init_kernel():
    """Initialize the kernel on startup"""
    global kernel_available
    
    if kernel.is_available():
        logger.info("KoboldAI kernel library found")
        if kernel.init(memory_size_mb=256):
            kernel_available = True
            logger.info("✓ KoboldAI kernel initialized successfully")
            logger.info(f"  Version: {kernel.get_version()}")
            return True
        else:
            logger.error("✗ Failed to initialize kernel")
    else:
        logger.warning("✗ KoboldAI kernel not available - using Python fallback")
    
    return False

def get_or_create_story(session_id):
    """Get or create a story for the given session"""
    if session_id not in stories:
        if kernel_available:
            stories[session_id] = {
                'kernel_story': kernel.Story(),
                'chunks': [],
                'worldinfo': [],
                'settings': kernel.GenSettings(),
            }
        else:
            # Python fallback
            stories[session_id] = {
                'kernel_story': None,
                'chunks': [],
                'worldinfo': [],
                'settings': None,
            }
    
    return stories[session_id]

# HTML Template (embedded for simplicity)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>KoboldAI Kernel Demo</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
        }
        .header {
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }
        .status.active { background: #0f4;  color: #000; }
        .status.inactive { background: #f44; color: #fff; }
        .container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .panel {
            background: #16213e;
            padding: 20px;
            border-radius: 10px;
        }
        .story-text {
            background: #0f3460;
            padding: 15px;
            border-radius: 5px;
            min-height: 300px;
            max-height: 500px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: 'Georgia', serif;
            line-height: 1.6;
        }
        textarea {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: none;
            background: #0f3460;
            color: #eee;
            font-family: inherit;
            resize: vertical;
        }
        button {
            background: #0f4;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 10px;
        }
        button:hover { background: #0d3; }
        button:disabled { background: #666; cursor: not-allowed; }
        .setting {
            margin: 10px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="range"] {
            width: 100%;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #0f3460;
        }
        .worldinfo-entry {
            background: #0f3460;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 KoboldAI Kernel Demo</h1>
        <span class="status {{ 'active' if kernel_active else 'inactive' }}">
            {{ 'Kernel Active' if kernel_active else 'Python Fallback' }}
        </span>
        {% if kernel_active %}
        <span style="margin-left: 10px; color: #888;">Version: {{ version }}</span>
        {% endif %}
    </div>
    
    <div class="container">
        <div class="panel">
            <h2>Story</h2>
            <div class="story-text" id="story"></div>
            <textarea id="input" placeholder="Enter your story text..." rows="3"></textarea>
            <button onclick="addChunk()">Add to Story</button>
            <button onclick="generate()" disabled>Generate (Not Implemented)</button>
        </div>
        
        <div class="panel">
            <h2>Settings</h2>
            
            <div class="setting">
                <label for="memory">Memory:</label>
                <textarea id="memory" rows="2" placeholder="Story memory..."></textarea>
                <button onclick="setMemory()">Set Memory</button>
            </div>
            
            <div class="setting">
                <label for="authors-note">Author's Note:</label>
                <textarea id="authors-note" rows="2" placeholder="[Author's note...]"></textarea>
                <button onclick="setAuthorsNote()">Set Author's Note</button>
            </div>
            
            <h3>World Info</h3>
            <div id="worldinfo-list"></div>
            <div class="setting">
                <label>Keywords:</label>
                <input type="text" id="wi-keywords" placeholder="dragon, magic">
                <label>Content:</label>
                <textarea id="wi-content" rows="2" placeholder="World info content..."></textarea>
                <label>
                    <input type="checkbox" id="wi-selective" checked> Selective (keyword-triggered)
                </label>
                <button onclick="addWorldInfo()">Add World Info</button>
            </div>
            
            {% if kernel_active %}
            <h3>Memory Stats</h3>
            <div id="memory-stats"></div>
            <button onclick="updateStats()">Refresh Stats</button>
            {% endif %}
        </div>
    </div>
    
    <script>
        const socket = io();
        let chunkCount = 0;
        
        // Update story display
        function updateStory(text) {
            const storyDiv = document.getElementById('story');
            storyDiv.textContent = text;
            storyDiv.scrollTop = storyDiv.scrollHeight;
        }
        
        // Add chunk to story
        function addChunk() {
            const input = document.getElementById('input');
            const text = input.value.trim();
            
            if (!text) return;
            
            socket.emit('add_chunk', {
                text: text,
                chunk_num: chunkCount++
            });
            
            input.value = '';
        }
        
        // Set memory
        function setMemory() {
            const memory = document.getElementById('memory').value;
            socket.emit('set_memory', { text: memory });
        }
        
        // Set author's note
        function setAuthorsNote() {
            const note = document.getElementById('authors-note').value;
            socket.emit('set_authors_note', { text: note });
        }
        
        // Add world info
        function addWorldInfo() {
            const keywords = document.getElementById('wi-keywords').value;
            const content = document.getElementById('wi-content').value;
            const selective = document.getElementById('wi-selective').checked;
            
            if (!content.trim()) return;
            
            socket.emit('add_worldinfo', {
                keywords: keywords || null,
                content: content,
                selective: selective
            });
            
            document.getElementById('wi-keywords').value = '';
            document.getElementById('wi-content').value = '';
        }
        
        // Update memory stats
        function updateStats() {
            socket.emit('get_memory_stats');
        }
        
        // Socket event handlers
        socket.on('story_updated', function(data) {
            updateStory(data.text);
        });
        
        socket.on('worldinfo_added', function(data) {
            const list = document.getElementById('worldinfo-list');
            const entry = document.createElement('div');
            entry.className = 'worldinfo-entry';
            entry.innerHTML = `
                <strong>${data.keywords || '[Always Active]'}</strong><br>
                ${data.content.substring(0, 100)}${data.content.length > 100 ? '...' : ''}
            `;
            list.appendChild(entry);
        });
        
        socket.on('memory_stats', function(stats) {
            const statsDiv = document.getElementById('memory-stats');
            statsDiv.innerHTML = `
                <div class="metric"><span>Total:</span><span>${(stats.total_bytes / 1024 / 1024).toFixed(2)} MB</span></div>
                <div class="metric"><span>Used:</span><span>${(stats.used_bytes / 1024).toFixed(2)} KB</span></div>
                <div class="metric"><span>Peak:</span><span>${(stats.peak_bytes / 1024).toFixed(2)} KB</span></div>
                <div class="metric"><span>Allocations:</span><span>${stats.num_allocations}</span></div>
            `;
        });
        
        socket.on('error', function(data) {
            alert('Error: ' + data.message);
        });
        
        // Initialize stats on load
        {% if kernel_active %}
        updateStats();
        {% endif %}
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the main page"""
    return render_template_string(
        HTML_TEMPLATE,
        kernel_active=kernel_available,
        version=kernel.get_version() if kernel_available else 'N/A'
    )

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    session_id = request.sid
    logger.info(f"Client connected: {session_id}")
    emit('connected', {'kernel_active': kernel_available})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    session_id = request.sid
    logger.info(f"Client disconnected: {session_id}")
    
    # Clean up story state
    if session_id in stories:
        del stories[session_id]

@socketio.on('add_chunk')
def handle_add_chunk(data):
    """Add a chunk to the story"""
    session_id = request.sid
    story_state = get_or_create_story(session_id)
    
    text = data.get('text', '')
    chunk_num = data.get('chunk_num', 0)
    
    try:
        if kernel_available:
            # Use kernel
            chunk = kernel.StoryChunk(text, chunk_num=chunk_num, token_count=len(text.split()))
            story_state['kernel_story'].append_chunk(chunk)
        
        # Update local state
        story_state['chunks'].append(text)
        
        # Send updated story
        full_text = '\n'.join(story_state['chunks'])
        emit('story_updated', {'text': full_text})
        
        logger.info(f"Added chunk {chunk_num} for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error adding chunk: {e}")
        emit('error', {'message': str(e)})

@socketio.on('set_memory')
def handle_set_memory(data):
    """Set story memory"""
    session_id = request.sid
    story_state = get_or_create_story(session_id)
    
    text = data.get('text', '')
    
    try:
        if kernel_available and story_state['kernel_story']:
            story_state['kernel_story'].set_memory(text)
        
        logger.info(f"Set memory for session {session_id}")
        emit('memory_set', {'success': True})
        
    except Exception as e:
        logger.error(f"Error setting memory: {e}")
        emit('error', {'message': str(e)})

@socketio.on('set_authors_note')
def handle_set_authors_note(data):
    """Set author's note"""
    session_id = request.sid
    story_state = get_or_create_story(session_id)
    
    text = data.get('text', '')
    
    try:
        if kernel_available and story_state['kernel_story']:
            story_state['kernel_story'].set_authors_note(text)
        
        logger.info(f"Set author's note for session {session_id}")
        emit('authors_note_set', {'success': True})
        
    except Exception as e:
        logger.error(f"Error setting author's note: {e}")
        emit('error', {'message': str(e)})

@socketio.on('add_worldinfo')
def handle_add_worldinfo(data):
    """Add a world info entry"""
    session_id = request.sid
    story_state = get_or_create_story(session_id)
    
    keywords = data.get('keywords')
    content = data.get('content', '')
    selective = data.get('selective', True)
    
    try:
        if kernel_available and story_state['kernel_story']:
            entry = kernel.WorldInfoEntry(
                keywords=keywords,
                content=content,
                selective=selective,
                constant=not selective
            )
            story_state['kernel_story'].add_worldinfo(entry)
        
        # Update local state
        story_state['worldinfo'].append({
            'keywords': keywords,
            'content': content,
            'selective': selective
        })
        
        emit('worldinfo_added', {
            'keywords': keywords,
            'content': content,
            'selective': selective
        })
        
        logger.info(f"Added world info entry for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error adding world info: {e}")
        emit('error', {'message': str(e)})

@socketio.on('get_memory_stats')
def handle_get_memory_stats():
    """Get memory statistics"""
    try:
        if kernel_available:
            stats = kernel.get_memory_stats()
            emit('memory_stats', stats)
        else:
            emit('error', {'message': 'Kernel not available'})
            
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        emit('error', {'message': str(e)})

def main():
    """Main entry point"""
    # Initialize kernel
    init_kernel()
    
    # Start Flask app
    logger.info("Starting Flask server on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    try:
        main()
    finally:
        # Cleanup on exit
        if kernel_available:
            kernel.shutdown()
            logger.info("Kernel shutdown complete")
