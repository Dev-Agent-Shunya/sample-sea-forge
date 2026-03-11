#!/usr/bin/env python3
"""
SeaForge Server
===============

FastAPI server for SeaForge real-time monitoring.
Provides REST API and WebSocket for live progress updates.
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn


# Get repo path
REPO_PATH = Path(__file__).parent.parent.resolve()
FEATURES_FILE = REPO_PATH / ".seaforge" / "features.json"

# Create FastAPI app
app = FastAPI(
    title="SeaForge Dashboard",
    description="Real-time monitoring for SeaForge development",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

def load_features() -> Dict[str, Any]:
    """Load features data."""
    if FEATURES_FILE.exists():
        with open(FEATURES_FILE) as f:
            return json.load(f)
    return {"features": [], "metadata": {}}

# Dashboard HTML
DASHBOARD_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SeaForge Dashboard 🌊</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .header {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            padding: 20px 40px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 28px;
            color: #00d4ff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header .status {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        .status.planning { background: #f39c12; color: #000; }
        .status.development { background: #00d4ff; color: #000; }
        .status.completed { background: #2ecc71; color: #000; }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 40px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .stat-card h3 {
            font-size: 14px;
            color: #8892b0;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-card .value {
            font-size: 36px;
            font-weight: 700;
            color: #fff;
        }
        .stat-card .value.success { color: #2ecc71; }
        .stat-card .value.warning { color: #f39c12; }
        .stat-card .value.info { color: #00d4ff; }

        .progress-section {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .progress-section h2 {
            font-size: 18px;
            margin-bottom: 20px;
            color: #fff;
        }
        .progress-bar {
            height: 30px;
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #0099cc);
            border-radius: 15px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 15px;
        }
        .progress-fill span {
            font-weight: 600;
            font-size: 14px;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }

        .feature-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s, border-color 0.2s;
        }
        .feature-card:hover {
            transform: translateY(-2px);
            border-color: rgba(0,212,255,0.3);
        }
        .feature-card h4 {
            font-size: 16px;
            color: #fff;
            margin-bottom: 8px;
        }
        .feature-card .id {
            font-size: 12px;
            color: #00d4ff;
            font-family: monospace;
            margin-bottom: 10px;
        }
        .feature-card .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin-top: 10px;
        }
        .status.completed { background: rgba(46,204,113,0.2); color: #2ecc71; }
        .status.in_progress { background: rgba(243,156,18,0.2); color: #f39c12; }
        .status.pending { background: rgba(136,146,176,0.2); color: #8892b0; }

        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(0,0,0,0.5);
            border-radius: 20px;
            font-size: 12px;
        }
        .connection-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #e74c3c;
        }
        .connection-dot.connected { background: #2ecc71; animation: pulse 2s infinite; }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .activity-log {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
            max-height: 300px;
            overflow-y: auto;
        }
        .activity-log h3 {
            font-size: 16px;
            margin-bottom: 15px;
            color: #fff;
        }
        .log-entry {
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 13px;
            color: #8892b0;
        }
        .log-entry:last-child { border-bottom: none; }
        .log-entry .time {
            color: #00d4ff;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="connection-status">
        <div class="connection-dot" id="connDot"></div>
        <span id="connText">Disconnected</span>
    </div>

    <div class="header">
        <h1>🌊 SeaForge Dashboard</h1>
        <div class="status" id="projectStatus">Not Started</div>
    </div>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Features</h3>
                <div class="value" id="totalFeatures">0</div>
            </div>
            <div class="stat-card">
                <h3>Completed</h3>
                <div class="value success" id="completedFeatures">0</div>
            </div>
            <div class="stat-card">
                <h3>In Progress</h3>
                <div class="value warning" id="inProgressFeatures">0</div>
            </div>
            <div class="stat-card">
                <h3>Progress</h3>
                <div class="value info" id="progressPercent">0%</div>
            </div>
        </div>

        <div class="progress-section">
            <h2>Overall Progress</h2>
            <div class="progress-bar">
                <div class="progress-fill" id="progressBar" style="width: 0%">
                    <span id="progressText">0%</span>
                </div>
            </div>
        </div>

        <h2 style="margin-bottom: 20px; font-size: 20px;">Features</h2>
        <div class="features-grid" id="featuresGrid">
            <!-- Features inserted here -->
        </div>

        <h2 style="margin: 30px 0 20px; font-size: 20px;">Activity Log</h2>
        <div class="activity-log" id="activityLog">
            <div class="log-entry"><span class="time" id="startTime"></span>Dashboard started...</div>
        </div>
    </div>

    <script>
        document.getElementById('startTime').textContent = new Date().toLocaleTimeString();

        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const connDot = document.getElementById('connDot');
        const connText = document.getElementById('connText');
        const activityLog = document.getElementById('activityLog');

        function addLog(message) {
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `<span class="time">${new Date().toLocaleTimeString()}</span>${message}`;
            activityLog.insertBefore(entry, activityLog.firstChild);
        }

        ws.onopen = () => {
            connDot.classList.add('connected');
            connText.textContent = 'Connected';
            addLog('Connected to SeaForge');
        };

        ws.onclose = () => {
            connDot.classList.remove('connected');
            connText.textContent = 'Disconnected';
            addLog('Disconnected from SeaForge');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        function updateDashboard(data) {
            // Update status
            const status = document.getElementById('projectStatus');
            status.textContent = data.metadata?.current_phase?.replace('_', ' ').toUpperCase() || 'NOT STARTED';
            status.className = 'status ' + (data.metadata?.current_phase || 'pending');

            // Update stats
            const features = data.features || [];
            const completed = features.filter(f => f.passes).length;
            const inProgress = features.filter(f => f.in_progress && !f.passes).length;
            const total = features.length;
            const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

            document.getElementById('totalFeatures').textContent = total;
            document.getElementById('completedFeatures').textContent = completed;
            document.getElementById('inProgressFeatures').textContent = inProgress;
            document.getElementById('progressPercent').textContent = percentage + '%';

            // Update progress bar
            document.getElementById('progressBar').style.width = percentage + '%';
            document.getElementById('progressText').textContent = percentage + '%';

            // Update features grid
            const grid = document.getElementById('featuresGrid');
            grid.innerHTML = features.map(f => `
                <div class="feature-card">
                    <div class="id">#${f.id.toString().padStart(3, '0')}</div>
                    <h4>${f.name}</h4>
                    <p style="font-size: 13px; color: #8892b0;">${f.category}</p>
                    <span class="status ${f.passes ? 'completed' : f.in_progress ? 'in_progress' : 'pending'}">
                        ${f.passes ? '✅ Completed' : f.in_progress ? '🔨 In Progress' : '⏳ Pending'}
                    </span>
                </div>
            `).join('') || '<div style="grid-column: 1/-1; text-align: center; color: #667; padding: 40px;">No features yet</div>';

            // Log updates
            if (data._new_update) {
                addLog(data._update_message || 'Dashboard updated');
            }
        }

        // Initial load via API
        fetch('/api/features')
            .then(r => r.json())
            .then(updateDashboard);

        // Poll for updates every 5 seconds
        setInterval(() => {
            fetch('/api/features')
                .then(r => r.json())
                .then(updateDashboard);
        }, 5000);
    </script>
</body>
</html>"""

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the dashboard HTML."""
    return HTMLResponse(content=DASHBOARD_HTML)

@app.get("/api/features")
async def get_features():
    """Get all features data."""
    return load_features()

@app.get("/api/stats")
async def get_stats():
    """Get progress statistics."""
    data = load_features()
    features = data.get("features", [])
    completed = sum(1 for f in features if f.get("passes"))
    total = len(features)
    percentage = (completed / total * 100) if total > 0 else 0

    return {
        "status": data.get("metadata", {}).get("current_phase", "unknown"),
        "completed": completed,
        "total": total,
        "percentage": round(percentage, 2),
        "in_progress": sum(1 for f in features if f.get("in_progress") and not f.get("passes"))
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await manager.connect(websocket)
    try:
        # Send initial data
        await websocket.send_json(load_features())

        while True:
            # Keep connection alive and broadcast updates
            await asyncio.sleep(2)
            await websocket.send_json(load_features())

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    print("🌊 Starting SeaForge Dashboard Server...")
    print("   URL: http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
