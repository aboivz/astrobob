#!/usr/bin/env python3
"""
Simple HTTP server for viewing AstroBob documentation locally.

Usage:
    python serve.py [port]

Default port: 8000
"""

import http.server
import socketserver
import sys
from pathlib import Path

# Get port from command line or use default
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

# Change to docs directory
docs_dir = Path(__file__).parent
print(f"Serving documentation from: {docs_dir}")

# Create server
Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.html': 'text/html',
})

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"\n✓ Documentation server running at http://localhost:{PORT}")
    print(f"✓ Open http://localhost:{PORT}/index.html in your browser")
    print(f"\nPress Ctrl+C to stop the server\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)

# Made with Bob
