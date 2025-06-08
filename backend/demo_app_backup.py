#!/usr/bin/env python
"""Cloud Run optimized version of SEO Writing Tool."""

import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI(
    title="SEO Writing Tool",
    description="AI-Powered SEO Content Creation Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    """Main landing page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>✨ Scrib AI - Next-Gen SEO Writing Tool</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: #0a0a0a;
                color: #ffffff;
                line-height: 1.6;
                overflow-x: hidden;
            }
            
            /* Animated background */
            .bg-animation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                background: linear-gradient(45deg, #0a0a0a, #1a1a2e, #16213e, #0f3460);
                background-size: 400% 400%;
                animation: gradientBG 15s ease infinite;
            }
            
            @keyframes gradientBG {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            /* Floating particles */
            .particles {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                overflow: hidden;
            }
            
            .particle {
                position: absolute;
                width: 2px;
                height: 2px;
                background: #00d4ff;
                border-radius: 50%;
                animation: float 20s infinite linear;
                opacity: 0.6;
            }
            
            @keyframes float {
                0% { transform: translateY(100vh) translateX(0px); }
                100% { transform: translateY(-100px) translateX(100px); }
            }
            
            /* Header */
            .header {
                text-align: center;
                padding: 60px 20px;
                position: relative;
            }
            
            .logo {
                font-size: 3.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #00d4ff 0%, #5b73ff 50%, #ff6b9d 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 20px;
                text-shadow: 0 0 50px rgba(0, 212, 255, 0.3);
            }
            
            .tagline {
                font-size: 1.4rem;
                font-weight: 300;
                color: #a0a0a0;
                margin-bottom: 30px;
                letter-spacing: 0.5px;
            }
            
            .badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(0, 212, 255, 0.1);
                border: 1px solid rgba(0, 212, 255, 0.3);
                color: #00d4ff;
                padding: 12px 24px;
                border-radius: 50px;
                font-size: 0.9rem;
                font-weight: 500;
                backdrop-filter: blur(10px);
            }
            
            /* Container */
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 20px;
            }
            
            /* Status cards */
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 24px;
                margin: 60px 0;
            }
            
            .status-card {
                background: rgba(26, 26, 46, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 32px;
                text-align: center;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .status-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, #00d4ff, transparent);
            }
            
            .status-card:hover {
                transform: translateY(-8px);
                border-color: rgba(0, 212, 255, 0.4);
                box-shadow: 0 20px 40px rgba(0, 212, 255, 0.1);
            }
            
            .status-icon {
                font-size: 2.5rem;
                margin-bottom: 16px;
                filter: drop-shadow(0 0 10px currentColor);
            }
            
            .status-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 8px;
                color: #ffffff;
            }
            
            .status-desc {
                color: #a0a0a0;
                font-size: 0.9rem;
            }
            
            /* Demo section */
            .demo-section {
                background: rgba(26, 26, 46, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 40px;
                margin: 40px 0;
                backdrop-filter: blur(20px);
                position: relative;
            }
            
            .demo-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, #5b73ff, transparent);
            }
            
            .section-title {
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 16px;
                background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .section-desc {
                color: #a0a0a0;
                margin-bottom: 32px;
                font-size: 1.1rem;
            }
            
            /* Form elements */
            .input-group {
                margin-bottom: 24px;
            }
            
            textarea {
                width: 100%;
                min-height: 120px;
                padding: 20px;
                background: rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                color: #ffffff;
                font-size: 16px;
                font-family: inherit;
                resize: vertical;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }
            
            textarea:focus {
                outline: none;
                border-color: #00d4ff;
                box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
            }
            
            textarea::placeholder {
                color: #666;
            }
            
            /* Buttons */
            .btn {
                display: inline-flex;
                align-items: center;
                gap: 12px;
                padding: 16px 32px;
                background: linear-gradient(135deg, #00d4ff 0%, #5b73ff 100%);
                color: white;
                text-decoration: none;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                font-family: inherit;
            }
            
            .btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.5s ease;
            }
            
            .btn:hover::before {
                left: 100%;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
            }
            
            .btn-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                margin-top: 32px;
            }
            
            /* Loading and result states */
            .loading {
                display: none;
                text-align: center;
                padding: 40px;
                color: #00d4ff;
            }
            
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid rgba(0, 212, 255, 0.3);
                border-top: 3px solid #00d4ff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 16px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .result {
                display: none;
                background: rgba(0, 212, 255, 0.05);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 16px;
                padding: 24px;
                margin-top: 24px;
                backdrop-filter: blur(10px);
            }
            
            .result-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 16px;
                color: #00d4ff;
            }
            
            .content-output {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                line-height: 1.7;
                border-left: 4px solid #00d4ff;
            }
            
            .metrics {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 16px;
                margin-top: 16px;
            }
            
            .metric-item {
                text-align: center;
                padding: 12px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .metric-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #00d4ff;
            }
            
            .metric-label {
                font-size: 0.8rem;
                color: #a0a0a0;
                margin-top: 4px;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .logo { font-size: 2.5rem; }
                .tagline { font-size: 1.1rem; }
                .demo-section { padding: 24px; }
                .btn-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="bg-animation"></div>
        <div class="particles"></div>
        
        <div class="container">
            <div class="header">
                <div class="logo">✨ Scrib AI</div>
                <div class="tagline">Next-Generation SEO Writing Platform</div>
                <div class="badge">
                    🚀 Live • Cloud Deployed • AI-Powered
                </div>
            </div>
            
            <div class="status-grid">
                <div class="status-card">
                    <div class="status-icon">🧠</div>
                    <div class="status-title">Google Gemini AI</div>
                    <div class="status-desc">Real-time content generation with advanced AI models</div>
                </div>
                <div class="status-card">
                    <div class="status-icon">🔍</div>
                    <div class="status-title">Google Search API</div>
                    <div class="status-desc">Live competitor research and analysis</div>
                </div>
                <div class="status-card">
                    <div class="status-icon">📊</div>
                    <div class="status-title">SEO Analytics</div>
                    <div class="status-desc">Automated optimization and insights</div>
                </div>
                <div class="status-card">
                    <div class="status-icon">☁️</div>
                    <div class="status-title">Cloud Native</div>
                    <div class="status-desc">Globally accessible and scalable</div>
                </div>
            </div>
            
            <div class="demo-section">
                <div class="section-title">🎯 AI Content Generator</div>
                <div class="section-desc">Experience the power of AI-driven SEO content creation. Enter any topic and watch our advanced algorithms craft optimized content in seconds.</div>
                
                <div class="input-group">
                    <textarea id="topicInput" placeholder="例: 誕生花について、読者の心を掴む記事を書いてください..."></textarea>
                </div>
                
                <button class="btn" onclick="generateContent()">
                    <span>🤖</span>
                    <span>Generate AI Content</span>
                </button>
                
                <div id="loading" class="loading">
                    <div class="loading-spinner"></div>
                    <div>AI is crafting your content...</div>
                </div>
                
                <div id="result" class="result">
                    <div class="result-title">✨ Generated Content</div>
                    <div id="contentOutput" class="content-output"></div>
                    <div id="metrics" class="metrics"></div>
                </div>
            </div>
            
            <div class="demo-section">
                <div class="section-title">🛠️ Developer APIs</div>
                <div class="section-desc">Explore our powerful APIs for seamless integration into your workflow.</div>
                
                <div class="btn-grid">
                    <a href="/api/generate" class="btn">
                        <span>🤖</span>
                        <span>Content API</span>
                    </a>
                    <a href="/api/search" class="btn">
                        <span>🔍</span>
                        <span>Search API</span>
                    </a>
                    <a href="/health" class="btn">
                        <span>💊</span>
                        <span>Health Check</span>
                    </a>
                    <a href="/docs" class="btn">
                        <span>📖</span>
                        <span>Documentation</span>
                    </a>
                </div>
            </div>
        </div>
        
        <script>
            // Create floating particles
            function createParticles() {
                const particlesContainer = document.querySelector('.particles');
                const particleCount = 50;
                
                for (let i = 0; i < particleCount; i++) {
                    const particle = document.createElement('div');
                    particle.className = 'particle';
                    particle.style.left = Math.random() * 100 + '%';
                    particle.style.animationDelay = Math.random() * 20 + 's';
                    particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
                    particlesContainer.appendChild(particle);
                }
            }
            
            // Initialize particles on load
            document.addEventListener('DOMContentLoaded', createParticles);
            
            async function generateContent() {
                const topic = document.getElementById('topicInput').value;
                if (!topic) {
                    // Create custom notification instead of alert
                    showNotification('Please enter a topic to generate content', 'warning');
                    return;
                }
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ topic: topic })
                    });
                    
                    const result = await response.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    
                    if (result.success) {
                        document.getElementById('contentOutput').innerHTML = result.content;
                        
                        // Enhanced metrics display
                        document.getElementById('metrics').innerHTML = `
                            <div class="metric-item">
                                <div class="metric-value">${result.metrics.length}</div>
                                <div class="metric-label">Characters</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value">${result.metrics.keywords}</div>
                                <div class="metric-label">Keywords</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value">${result.metrics.seo_score}</div>
                                <div class="metric-label">SEO Score</div>
                            </div>
                            <div class="metric-item">
                                <div class="metric-value">${Math.ceil(result.metrics.length / 400)}</div>
                                <div class="metric-label">Read Time (min)</div>
                            </div>
                        `;
                        
                        document.getElementById('result').style.display = 'block';
                        showNotification('Content generated successfully!', 'success');
                    } else {
                        showNotification('Generation failed: ' + result.error, 'error');
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    showNotification('Error: ' + error.message, 'error');
                }
            }
            
            // Custom notification system
            function showNotification(message, type = 'info') {
                // Remove existing notifications
                const existing = document.querySelector('.notification');
                if (existing) existing.remove();
                
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                notification.innerHTML = `
                    <div class="notification-content">
                        <span class="notification-icon">
                            ${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}
                        </span>
                        <span>${message}</span>
                    </div>
                `;
                
                // Add notification styles
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(26, 26, 46, 0.95);
                    border: 1px solid ${type === 'success' ? '#00d4ff' : type === 'error' ? '#ff6b9d' : type === 'warning' ? '#ffb366' : '#00d4ff'};
                    color: white;
                    padding: 16px 24px;
                    border-radius: 12px;
                    backdrop-filter: blur(10px);
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                `;
                
                // Add slide-in animation
                const style = document.createElement('style');
                style.textContent = `
                    @keyframes slideIn {
                        from { transform: translateX(100%); opacity: 0; }
                        to { transform: translateX(0); opacity: 1; }
                    }
                    .notification-content {
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        font-weight: 500;
                    }
                `;
                document.head.appendChild(style);
                
                document.body.appendChild(notification);
                
                // Auto remove after 4 seconds
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.style.animation = 'slideIn 0.3s ease reverse';
                        setTimeout(() => notification.remove(), 300);
                    }
                }, 4000);
            }
            
            // Add some interactive effects
            document.addEventListener('mousemove', (e) => {
                const cursor = document.querySelector('.cursor-effect');
                if (!cursor) {
                    const effect = document.createElement('div');
                    effect.className = 'cursor-effect';
                    effect.style.cssText = `
                        position: fixed;
                        width: 20px;
                        height: 20px;
                        background: radial-gradient(circle, rgba(0, 212, 255, 0.3) 0%, transparent 70%);
                        border-radius: 50%;
                        pointer-events: none;
                        z-index: 9999;
                        transition: transform 0.1s ease;
                    `;
                    document.body.appendChild(effect);
                }
                
                const effect = document.querySelector('.cursor-effect');
                effect.style.left = (e.clientX - 10) + 'px';
                effect.style.top = (e.clientY - 10) + 'px';
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/generate")
async def generate_content(request: Request):
    """Generate content using Gemini AI."""
    try:
        data = await request.json()
        topic = data.get('topic', '')
        
        if not topic:
            return JSONResponse({
                "success": False,
                "error": "Topic is required"
            })
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return JSONResponse({
                "success": False,
                "error": "API key not configured"
            })
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
        あなたは日本のSEOライティング専門家です。
        「{topic}」について、SEO最適化された200-300文字の記事導入部を作成してください。
        
        要件:
        - 読者の興味を引く書き出し
        - キーワードを自然に含める
        - 専門性を感じさせる内容
        - 読みやすい文章構造
        """
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            content = response.text
            
            # Calculate metrics
            char_count = len(content)
            keyword_count = content.count(topic)
            seo_score = min(90, 60 + (keyword_count * 10) + (char_count // 10))
            
            return JSONResponse({
                "success": True,
                "content": content,
                "metrics": {
                    "length": char_count,
                    "keywords": keyword_count,
                    "seo_score": seo_score
                }
            })
        else:
            return JSONResponse({
                "success": False,
                "error": "No content generated"
            })
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@app.get("/api/search")
async def search_demo():
    """Search API demo."""
    try:
        import requests
        
        api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            return JSONResponse({
                "success": False,
                "error": "Search API not configured"
            })
        
        query = "誕生花 花言葉"
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'num': 3
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            for item in data.get('items', [])[:3]:
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            
            return JSONResponse({
                "success": True,
                "query": query,
                "results": results
            })
        else:
            return JSONResponse({
                "success": False,
                "error": f"Search failed: {response.status_code}"
            })
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@app.get("/health")
async def health_check():
    """Health check for Cloud Run."""
    return {
        "status": "healthy",
        "service": "SEO Writing Tool",
        "version": "1.0.0",
        "apis": {
            "gemini": bool(os.getenv('GEMINI_API_KEY')),
            "search": bool(os.getenv('GOOGLE_SEARCH_API_KEY'))
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)