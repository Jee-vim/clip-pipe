#!/usr/bin/env python3
"""
Simple HTTP server for managing _jobs.json file.
This server allows the web interface to read and write the _jobs.json file.
"""

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import pathlib

# Get the project root directory
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
JOBS_FILE = DATA_DIR / "_jobs.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

class JobsRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT / "web-manager"), **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/jobs':
            self.serve_jobs_file()
        elif parsed_path.path == '/api/accounts':
            self.serve_accounts()
        else:
            super().do_GET()
    
    def do_PUT(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/jobs':
            self.save_jobs_file()
        else:
            self.send_error(404, "File not found")
    
    def serve_jobs_file(self):
        try:
            if JOBS_FILE.exists():
                with open(JOBS_FILE, 'r', encoding='utf-8') as f:
                    jobs_data = json.load(f)
            else:
                jobs_data = []
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(jobs_data).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error reading jobs file: {str(e)}".encode('utf-8'))
    
    def serve_accounts(self):
        try:
            accounts_dir = PROJECT_ROOT / "accounts"
            accounts = []
            
            if accounts_dir.exists():
                for item in accounts_dir.iterdir():
                    if item.is_dir():
                        accounts.append(item.name)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(accounts).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error reading accounts: {str(e)}".encode('utf-8'))
    
    def save_jobs_file(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Validate JSON before saving
            jobs_data = json.loads(post_data.decode('utf-8'))
            
            # Create backup
            if JOBS_FILE.exists():
                backup_file = JOBS_FILE.with_suffix('.json.bak')
                with open(JOBS_FILE, 'r', encoding='utf-8') as original:
                    with open(backup_file, 'w', encoding='utf-8') as backup:
                        backup.write(original.read())
            
            # Save new data
            with open(JOBS_FILE, 'w', encoding='utf-8') as f:
                json.dump(jobs_data, f, indent=2, ensure_ascii=False)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b"Jobs saved successfully")
            
        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Invalid JSON: {str(e)}".encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error saving jobs file: {str(e)}".encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    port = 8080
    
    print(f"🚀 Starting Jobs Manager Web Server")
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"📄 Jobs File: {JOBS_FILE}")
    print(f"🌐 Server: http://localhost:{port}")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        server = HTTPServer(('localhost', port), JobsRequestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()