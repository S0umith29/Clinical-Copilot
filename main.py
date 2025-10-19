"""Main FastAPI application for Clinical Question Copilot."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
from datetime import datetime

from copilot_engine import ClinicalQuestionCopilot
from config import settings
 

# Initialize FastAPI app
app = FastAPI(
    title="Clinical Question Copilot",
    description="AI assistant for ICU and hospital clinical questions, grounded in MIMIC-IV demo data",
    version="1.0.0"
)

# Initialize the copilot engine
copilot = ClinicalQuestionCopilot()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")

# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    user_id: Optional[str] = None

class QuestionResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    guardrail_triggered: bool
    guardrail_reason: Optional[str] = None
    suggestions: Optional[List[str]] = None
    context_used: bool = False
    timestamp: str
    

class StatsResponse(BaseModel):
    knowledge_base: Dict[str, Any]
    total_interactions: int
    clinical_questions: int
    guardrail_triggers: int

# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Process a clinical question."""
    try:
        response = copilot.process_question(request.question, request.user_id)
        
        return QuestionResponse(
            answer=response["answer"],
            sources=response["sources"],
            confidence=response["confidence"],
            guardrail_triggered=response["guardrail_triggered"],
            guardrail_reason=response.get("guardrail_reason"),
            suggestions=response.get("suggestions"),
            context_used=response.get("context_used", False),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/api/suggestions", response_model=List[str])
async def get_suggestions():
    """Get suggested clinical questions."""
    return copilot.suggest_questions()

 

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics."""
    stats = copilot.get_system_stats()
    return StatsResponse(**stats)

@app.get("/api/history")
async def get_history(user_id: Optional[str] = None):
    """Get conversation history."""
    return copilot.get_conversation_history(user_id)

@app.delete("/api/history")
async def clear_history():
    """Clear conversation history."""
    copilot.clear_history()
    return {"message": "History cleared"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Create templates directory and HTML template
os.makedirs("templates", exist_ok=True)

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clinical Question Copilot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .main-content {
            display: flex;
            min-height: 600px;
        }
        
        .sidebar {
            width: 300px;
            background: #f8f9fa;
            padding: 30px;
            border-right: 1px solid #e9ecef;
        }
        
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .chat-messages {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
            max-height: 500px;
        }
        
        .message {
            margin-bottom: 20px;
            padding: 15px 20px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .bot-message {
            background: #f1f3f4;
            color: #333;
            margin-right: auto;
        }
        
        .guardrail-message {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        
        .sources {
            margin-top: 15px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 10px;
            font-size: 0.9rem;
        }
        
        .source-item {
            margin-bottom: 10px;
            padding: 10px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
        }
        
        .input-area {
            padding: 20px 30px;
            border-top: 1px solid #e9ecef;
            background: white;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
        }
        
        .question-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .question-input:focus {
            border-color: #007bff;
        }
        
        .ask-button {
            padding: 15px 30px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .ask-button:hover {
            background: #0056b3;
        }
        
        .ask-button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        
        .suggestions {
            margin-bottom: 30px;
        }
        
        .suggestions h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        
        .suggestion-item {
            padding: 10px 15px;
            margin-bottom: 8px;
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9rem;
        }
        
        .suggestion-item:hover {
            background: #007bff;
            color: white;
            transform: translateX(5px);
        }
        
        .stats {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .stats h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }
        
        .loading.show {
            display: block;
        }
        
        .confidence-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            margin-left: 10px;
        }
        
        .confidence-high {
            background: #d4edda;
            color: #155724;
        }
        
        .confidence-medium {
            background: #fff3cd;
            color: #856404;
        }
        
        .confidence-low {
            background: #f8d7da;
            color: #721c24;
        }
        
        @media (max-width: 768px) {
            .main-content {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                border-right: none;
                border-bottom: 1px solid #e9ecef;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Clinical Question Copilot</h1>
            <p>AI assistant for ICU and hospital clinical questions, grounded in MIMIC-IV demo data</p>
        </div>
        
        <div class="main-content">
            <div class="sidebar">
                <div class="suggestions">
                    <h3>Suggested Questions</h3>
                    <div id="suggestions-list">
                        <!-- Suggestions will be loaded here -->
                    </div>
                </div>
                
                <div class="stats">
                    <h3>System Stats</h3>
                    <div id="stats-content">
                        <!-- Stats will be loaded here -->
                    </div>
                </div>

 
            </div>
            
            <div class="chat-area">
                <div class="chat-messages" id="chat-messages">
                    <div class="message bot-message">
                        <strong>Clinical Question Copilot</strong><br>
                        Welcome! I can help with clinical questions related to ICU and hospital medicine. 
                        Ask me about protocols, treatments, or patient management based on MIMIC-IV demo data.
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    <p>Processing your clinical question...</p>
                </div>
                
                <div class="input-area">
                    <div class="input-group">
                        <input 
                            type="text" 
                            class="question-input" 
                            id="question-input" 
                            placeholder="Ask a clinical question (e.g., 'What are the ventilator settings for ARDS?')"
                            onkeypress="handleKeyPress(event)"
                        >
                        <button class="ask-button" id="ask-button" onclick="askQuestion()">
                            Ask
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let conversationHistory = [];
        
        // Load suggestions and stats on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadSuggestions();
            loadStats();
        });
        
        async function loadSuggestions() {
            try {
                const response = await fetch('/api/suggestions');
                const suggestions = await response.json();
                
                const suggestionsList = document.getElementById('suggestions-list');
                suggestionsList.innerHTML = '';
                
                suggestions.slice(0, 5).forEach(suggestion => {
                    const item = document.createElement('div');
                    item.className = 'suggestion-item';
                    item.textContent = suggestion;
                    item.onclick = () => {
                        document.getElementById('question-input').value = suggestion;
                        askQuestion();
                    };
                    suggestionsList.appendChild(item);
                });
            } catch (error) {
                console.error('Error loading suggestions:', error);
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                const statsContent = document.getElementById('stats-content');
                statsContent.innerHTML = `
                    <div class="stat-item">
                        <span>Total Interactions:</span>
                        <span>${stats.total_interactions}</span>
                    </div>
                    <div class="stat-item">
                        <span>Clinical Questions:</span>
                        <span>${stats.clinical_questions}</span>
                    </div>
                    <div class="stat-item">
                        <span>Knowledge Base:</span>
                        <span>${stats.knowledge_base.total_documents} docs</span>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                askQuestion();
            }
        }
        
        async function askQuestion() {
            const input = document.getElementById('question-input');
            const question = input.value.trim();
            
            if (!question) return;
            
            // Add user message to chat
            addMessage(question, 'user');
            input.value = '';
            
            // Show loading
            document.getElementById('loading').classList.add('show');
            document.getElementById('ask-button').disabled = true;
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        question: question,
                        user_id: 'web_user'
                    })
                });
                
                const result = await response.json();
                
                // Add bot response to chat
                addBotMessage(result);
                
                // Update stats
                loadStats();
                
            } catch (error) {
                addMessage('Sorry, there was an error processing your question. Please try again.', 'bot');
                console.error('Error:', error);
            } finally {
                document.getElementById('loading').classList.remove('show');
                document.getElementById('ask-button').disabled = false;
            }
        }
        
        function addMessage(text, type) {
            const messagesContainer = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.textContent = text;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function addBotMessage(result) {
            const messagesContainer = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            
            let className = 'bot-message';
            if (result.guardrail_triggered) {
                className += ' guardrail-message';
            }
            
            messageDiv.className = `message ${className}`;
            
            let confidenceClass = 'confidence-low';
            if (result.confidence > 0.7) confidenceClass = 'confidence-high';
            else if (result.confidence > 0.4) confidenceClass = 'confidence-medium';
            
            let html = `
                <strong>Clinical Question Copilot</strong>
                <span class="confidence-badge ${confidenceClass}">
                    Confidence: ${(result.confidence * 100).toFixed(0)}%
                </span><br>
                ${result.answer}
            `;
            
            if (result.sources && result.sources.length > 0) {
                const main = result.sources[0];
                html += '<div class="sources">';
                html += '<strong>Main Source:</strong>';
                html += `
                    <div class="source-item">
                        <strong>${main.type === 'protocol' ? 'Protocol' : 'Clinical Case'}:</strong>
                        ${main.type === 'protocol' ? (main.title || 'Unknown') : `${main.patient_id} - ${main.diagnosis}`}
                        ${main.source_name ? `<br><small>Source: ${main.source_name}</small>` : ''}
                        <br><small>Rank: ${main.rank || 1} • Similarity: ${(main.similarity * 100).toFixed(0)}%</small>
                        <br><small>${main.content_preview || ''}</small>
                    </div>
                `;
                if (result.sources.length > 1) {
                    html += '<br><strong>Additional Sources:</strong>';
                    result.sources.slice(1).forEach(source => {
                        html += `
                            <div class="source-item">
                                <strong>${source.type === 'protocol' ? 'Protocol' : 'Clinical Case'}:</strong>
                                ${source.type === 'protocol' ? (source.title || 'Unknown') : `${source.patient_id} - ${source.diagnosis}`}
                                ${source.source_name ? `<br><small>Source: ${source.source_name}</small>` : ''}
                                <br><small>Rank: ${source.rank || ''} • Similarity: ${(source.similarity * 100).toFixed(0)}%</small>
                            </div>
                        `;
                    });
                }
                html += '</div>';
            }
            
            if (result.suggestions && result.suggestions.length > 0) {
                html += '<div class="sources"><strong>Try asking:</strong><br>';
                result.suggestions.forEach(suggestion => {
                    html += `<div class="suggestion-item" onclick="document.getElementById('question-input').value='${suggestion}'; askQuestion();">${suggestion}</div>`;
                });
                html += '</div>';
            }
            
            messageDiv.innerHTML = html;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        
    </script>
</body>
</html>
"""

# Write the HTML template
with open("templates/index.html", "w") as f:
    f.write(html_template)

if __name__ == "__main__":
    print("Starting Clinical Question Copilot...")
    print("Loading MIMIC-IV demo knowledge base...")
    print("Initializing clinical guardrails...")
    print("Starting web server...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
