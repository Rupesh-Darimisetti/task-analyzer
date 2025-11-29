#!/usr/bin/env python3
"""
Simple HTTP server for serving the Task Analyzer frontend
Runs on port 8001
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8001
FRONTEND_DIR = Path(__file__).parent / "frontend"

class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    os.chdir(FRONTEND_DIR)
    handler = FrontendHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"✅ Frontend server running on http://127.0.0.1:{PORT}/")
        print(f"📁 Serving files from: {FRONTEND_DIR}")
        print(f"🔗 Backend API: http://127.0.0.1:8000/api/tasks")
        print(f"\n📋 Task Analyzer is ready!")
        print(f"   - Frontend: http://127.0.0.1:{PORT}/")
        print(f"   - Backend: http://127.0.0.1:8000/")
        print(f"\n💡 Tip: Open http://127.0.0.1:{PORT}/ in your browser")
        print(f"\nPress Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Server stopped")
