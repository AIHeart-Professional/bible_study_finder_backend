"""
Simple test version of the Bible Study Finder Backend API.
This version avoids complex dependencies and should work with Python 3.13.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os

class BibleStudyAPIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.send_json_response({
                "message": "Bible Study Finder API is running",
                "status": "healthy",
                "version": "1.0.0"
            })
        elif self.path == '/health':
            self.send_json_response({"status": "healthy"})
        elif self.path.startswith('/api/v1/resources'):
            self.send_json_response([])  # Empty resources for now
        elif self.path.startswith('/api/v1/categories'):
            self.send_json_response({
                "categories": [
                    "Bible Study",
                    "Devotional", 
                    "Commentary",
                    "Prayer",
                    "Theology",
                    "History",
                    "Youth",
                    "Small Group"
                ]
            })
        elif self.path.startswith('/api/v1/tags'):
            self.send_json_response({
                "tags": [
                    "beginner",
                    "intermediate",
                    "advanced",
                    "youth", 
                    "adult",
                    "family",
                    "small-group",
                    "individual"
                ]
            })
        else:
            self.send_json_response({"error": "Not Found"}, 404)
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path.startswith('/api/v1/resources'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                # Mock response - create resource
                response = {
                    "id": 1,
                    "title": data.get("title", ""),
                    "description": data.get("description", ""),
                    "category": data.get("category", ""),
                    "author": data.get("author", ""),
                    "url": data.get("url"),
                    "tags": data.get("tags", [])
                }
                self.send_json_response(response, 201)
            except json.JSONDecodeError:
                self.send_json_response({"error": "Invalid JSON"}, 400)
        else:
            self.send_json_response({"error": "Not Found"}, 404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response with CORS headers."""
        response_data = json.dumps(data, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        self.wfile.write(response_data.encode('utf-8'))
    
    def send_cors_headers(self):
        """Send CORS headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    
    def log_message(self, format, *args):
        """Custom log format."""
        print(f"{self.address_string()} - {format % args}")

def run_server(port=8000):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, BibleStudyAPIHandler)
    
    print(f"Bible Study Finder API running on http://localhost:{port}")
    print(f"API Documentation: This is a simple test server")
    print(f"Available endpoints:")
    print(f"  GET  / - Health check")
    print(f"  GET  /health - Health status") 
    print(f"  GET  /api/v1/resources - Get resources")
    print(f"  POST /api/v1/resources - Create resource")
    print(f"  GET  /api/v1/categories - Get categories")
    print(f"  GET  /api/v1/tags - Get tags")
    print()
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
