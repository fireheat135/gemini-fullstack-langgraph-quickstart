#!/usr/bin/env python
"""Simple web demo for SEO Writing Tool."""

import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Add src to path for imports
sys.path.append('src')

app = FastAPI(title="SEO Writing Tool Demo", version="1.0.0")

# Enable CORS for all origins (demo only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with demo interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SEO Writing Tool - Demo</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
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
                background: linear-gradient(45deg, #2196F3, #21CBF3);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .header h1 {
                margin: 0 0 10px 0;
                font-size: 2.5em;
                font-weight: 700;
            }
            .header p {
                margin: 0;
                font-size: 1.2em;
                opacity: 0.9;
            }
            .badge {
                display: inline-block;
                background: rgba(255,255,255,0.2);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                margin-top: 10px;
            }
            .content {
                padding: 40px;
            }
            .status {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .status-card {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 30px;
                border-left: 5px solid #28a745;
            }
            .status-card h3 {
                margin: 0 0 15px 0;
                color: #333;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .status-card ul {
                margin: 0;
                padding-left: 20px;
            }
            .status-card li {
                margin-bottom: 8px;
                color: #666;
            }
            .workflow {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
            }
            .workflow h3 {
                margin: 0 0 20px 0;
                color: #856404;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .steps {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
            .step {
                background: white;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                border: 2px solid #ffeaa7;
                transition: transform 0.2s;
            }
            .step:hover {
                transform: translateY(-5px);
            }
            .step-number {
                background: #f39c12;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 10px;
                font-weight: bold;
            }
            .demo-buttons {
                display: flex;
                gap: 20px;
                justify-content: center;
                margin: 40px 0;
            }
            .btn {
                padding: 15px 30px;
                border: none;
                border-radius: 10px;
                font-size: 1.1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                text-decoration: none;
                display: inline-block;
            }
            .btn-primary {
                background: linear-gradient(45deg, #2196F3, #21CBF3);
                color: white;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(33, 150, 243, 0.3);
            }
            .btn-secondary {
                background: #6c757d;
                color: white;
            }
            .btn-secondary:hover {
                background: #5a6268;
                transform: translateY(-2px);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            .feature {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 15px;
                padding: 30px;
                text-align: center;
            }
            .feature h4 {
                margin: 0 0 15px 0;
                color: #333;
            }
            .feature p {
                color: #666;
                line-height: 1.6;
                margin: 0;
            }
            .icon {
                font-size: 1.5em;
                margin-right: 10px;
            }
            .footer {
                background: #343a40;
                color: white;
                padding: 30px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 SEO Writing Tool</h1>
                <p>AI-Powered Content Creation Platform</p>
                <div class="badge">Phase 2 Demo - 75% Complete</div>
            </div>
            
            <div class="content">
                <div class="status">
                    <div class="status-card">
                        <h3>✅ 実装済み機能</h3>
                        <ul>
                            <li>7ステップSEOワークフロー</li>
                            <li>高度統計分析エンジン</li>
                            <li>マルチAI統合</li>
                            <li>コンテンツ生成システム</li>
                            <li>記事タギング・メタデータ</li>
                            <li>パフォーマンス予測</li>
                        </ul>
                    </div>
                    
                    <div class="status-card" style="border-left-color: #ffc107;">
                        <h3>🚧 進行中</h3>
                        <ul>
                            <li>REST API エンドポイント</li>
                            <li>フロントエンド統合</li>
                            <li>リアルタイム進捗</li>
                            <li>キーワードリサーチAPI</li>
                        </ul>
                    </div>
                </div>
                
                <div class="workflow">
                    <h3>🔄 7ステップワークフロー</h3>
                    <div class="steps">
                        <div class="step">
                            <div class="step-number">1</div>
                            <strong>リサーチ</strong>
                            <p>キーワード分析・競合調査</p>
                        </div>
                        <div class="step">
                            <div class="step-number">2</div>
                            <strong>企画</strong>
                            <p>4パターン記事企画案</p>
                        </div>
                        <div class="step">
                            <div class="step-number">3</div>
                            <strong>執筆</strong>
                            <p>AI記事執筆・SEO最適化</p>
                        </div>
                        <div class="step">
                            <div class="step-number">4</div>
                            <strong>修正</strong>
                            <p>品質チェック・改善提案</p>
                        </div>
                        <div class="step">
                            <div class="step-number">5</div>
                            <strong>出稿</strong>
                            <p>スケジュール・CMS連携</p>
                        </div>
                        <div class="step">
                            <div class="step-number">6</div>
                            <strong>分析</strong>
                            <p>パフォーマンス測定</p>
                        </div>
                        <div class="step">
                            <div class="step-number">7</div>
                            <strong>改善</strong>
                            <p>継続的最適化</p>
                        </div>
                    </div>
                </div>
                
                <div class="demo-buttons">
                    <a href="/demo" class="btn btn-primary">📊 コマンドライン デモ実行</a>
                    <a href="/docs" class="btn btn-secondary">📖 API ドキュメント</a>
                    <a href="/status" class="btn btn-secondary">📋 実装状況</a>
                </div>
                
                <div class="features">
                    <div class="feature">
                        <h4>🧬 因果推論分析</h4>
                        <p>DID、CausalImpact、合成コントロール法による科学的効果測定</p>
                    </div>
                    <div class="feature">
                        <h4>🤖 マルチAI対応</h4>
                        <p>Gemini、OpenAI、Anthropic Claude の自動フォールバック</p>
                    </div>
                    <div class="feature">
                        <h4>📈 予測モデリング</h4>
                        <p>記事公開前のパフォーマンス予測と最適化提案</p>
                    </div>
                    <div class="feature">
                        <h4>🏗️ モジュラー設計</h4>
                        <p>拡張可能なアーキテクチャとプラグインシステム</p>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>SEO Writing Tool - Phase 2 Implementation Complete (75%)</p>
                <p>Ready for API Integration & Production Deployment</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/demo")
async def run_demo():
    """Run command line demo."""
    try:
        # Import and run the demo
        from demo_app import main as run_demo_main
        
        # Capture demo output
        import io
        import contextlib
        
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            success = run_demo_main()
        
        demo_output = output.getvalue()
        
        html_response = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>Demo Results</title>
            <style>
                body {{ font-family: monospace; padding: 20px; background: #1e1e1e; color: #fff; }}
                .output {{ background: #2d2d2d; padding: 20px; border-radius: 10px; white-space: pre-wrap; }}
                .back {{ margin: 20px 0; }}
                .back a {{ color: #4fc3f7; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="back"><a href="/">← Back to Home</a></div>
            <h1>Demo Execution Results</h1>
            <div class="output">{demo_output}</div>
            <div class="back"><a href="/">← Back to Home</a></div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_response)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Demo Error</h1><p>{str(e)}</p><a href='/'>Back</a>")

@app.get("/status")
async def status():
    """Show current status."""
    status_html = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>Implementation Status</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .status-item { margin: 15px 0; }
            .completed { color: #28a745; }
            .pending { color: #ffc107; }
            .back { margin: 20px 0; }
            .back a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="back"><a href="/">← Back to Home</a></div>
            <h1>📊 Implementation Status Report</h1>
            
            <h2>✅ Completed Components (Phase 2 - 75%)</h2>
            <div class="completed">
                <div class="status-item">✅ SEO Workflow Graph (1,043 lines)</div>
                <div class="status-item">✅ Advanced Statistical Analyzer (1,512 lines)</div>
                <div class="status-item">✅ Article Analytics Models (847 lines)</div>
                <div class="status-item">✅ Multi-AI Service Manager</div>
                <div class="status-item">✅ Content Generation Engine</div>
                <div class="status-item">✅ Frontend Components (React + TypeScript)</div>
                <div class="status-item">✅ Database Schema & Models</div>
            </div>
            
            <h2>🚧 In Progress (API Integration)</h2>
            <div class="pending">
                <div class="status-item">⚠️ REST API Endpoints</div>
                <div class="status-item">⚠️ Frontend-Backend Integration</div>
                <div class="status-item">⚠️ Real-time Workflow Progress</div>
                <div class="status-item">⚠️ Authentication System</div>
            </div>
            
            <h2>📈 Technical Achievements</h2>
            <ul>
                <li>🧬 <strong>Causal Inference Engine</strong>: DID, CausalImpact, Synthetic Control, RDD</li>
                <li>📊 <strong>Statistical Analysis</strong>: Multiple regression, clustering, time series</li>
                <li>🤖 <strong>Multi-AI Integration</strong>: Gemini, OpenAI, Anthropic with fallback</li>
                <li>🔄 <strong>7-Step Workflow</strong>: Complete automation from research to improvement</li>
                <li>🏗️ <strong>Modular Architecture</strong>: 60+ Python modules, 20+ React components</li>
            </ul>
            
            <h2>🎯 Next Priority Tasks</h2>
            <ol>
                <li>Create /api/seo-workflow/* endpoints</li>
                <li>Create /api/analytics/* endpoints</li>
                <li>Connect frontend to backend APIs</li>
                <li>Implement real-time progress tracking</li>
                <li>Deploy for production testing</li>
            </ol>
            
            <div class="back"><a href="/">← Back to Home</a></div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=status_html)

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting SEO Writing Tool Web Demo...")
    print("📍 Access: http://localhost:8080")
    print("📊 Demo: http://localhost:8080/demo")
    print("📋 Status: http://localhost:8080/status")
    print("📖 API Docs: http://localhost:8080/docs")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )