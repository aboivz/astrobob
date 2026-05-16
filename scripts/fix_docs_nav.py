#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix documentation navigation to only link to existing pages.
"""

from pathlib import Path
import re
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Existing pages
EXISTING_PAGES = [
    'index.html',
    'quickstart.html',
    'installation.html',
    'cli-reference.html',
    'mcp-tools.html',
    'troubleshooting.html',
    'faq.html'
]

# Correct sidebar navigation HTML
CORRECT_SIDEBAR_NAV = '''                <nav class="sidebar-nav">
                    <div class="nav-section">
                        <div class="nav-section-title">Getting Started</div>
                        <a href="quickstart.html">Quick Start</a>
                        <a href="installation.html">Installation</a>
                    </div>
                    <div class="nav-section">
                        <div class="nav-section-title">Usage</div>
                        <a href="cli-reference.html">CLI Reference</a>
                        <a href="mcp-tools.html">MCP Tools</a>
                    </div>
                    <div class="nav-section">
                        <div class="nav-section-title">Reference</div>
                        <a href="troubleshooting.html">Troubleshooting</a>
                        <a href="faq.html">FAQ</a>
                    </div>
                </nav>'''

# Correct header navigation
CORRECT_HEADER_NAV = '''                <nav class="main-nav">
                    <a href="index.html">Home</a>
                    <a href="quickstart.html">Quick Start</a>
                    <a href="installation.html">Installation</a>
                    <a href="https://github.com/aboivz/astrobob" target="_blank">GitHub</a>
                </nav>'''

docs_dir = Path(__file__).parent.parent / 'docs'

for html_file in docs_dir.glob('*.html'):
    print(f"Processing {html_file.name}...")
    
    content = html_file.read_text(encoding='utf-8')
    
    # Fix sidebar navigation
    # Find the sidebar-nav section and replace it
    sidebar_pattern = r'<nav class="sidebar-nav">.*?</nav>'
    content = re.sub(sidebar_pattern, CORRECT_SIDEBAR_NAV.strip(), content, flags=re.DOTALL)
    
    # Fix header navigation (keep active class logic)
    # We'll do this more carefully to preserve active class
    header_pattern = r'<nav class="main-nav">.*?</nav>'
    
    # Determine which page should be active
    active_page = html_file.name
    header_nav = CORRECT_HEADER_NAV
    
    # Add active class to current page
    if active_page == 'index.html':
        header_nav = header_nav.replace('<a href="index.html">', '<a href="index.html" class="active">')
    elif active_page == 'quickstart.html':
        header_nav = header_nav.replace('<a href="quickstart.html">', '<a href="quickstart.html" class="active">')
    elif active_page == 'installation.html':
        header_nav = header_nav.replace('<a href="installation.html">', '<a href="installation.html" class="active">')
    
    content = re.sub(header_pattern, header_nav.strip(), content, flags=re.DOTALL)
    
    # Add active class to sidebar based on current page
    if active_page == 'quickstart.html':
        content = content.replace('<a href="quickstart.html">', '<a href="quickstart.html" class="active">')
    elif active_page == 'installation.html':
        content = content.replace('<a href="installation.html">', '<a href="installation.html" class="active">')
    elif active_page == 'cli-reference.html':
        content = content.replace('<a href="cli-reference.html">', '<a href="cli-reference.html" class="active">')
    elif active_page == 'mcp-tools.html':
        content = content.replace('<a href="mcp-tools.html">', '<a href="mcp-tools.html" class="active">')
    elif active_page == 'troubleshooting.html':
        content = content.replace('<a href="troubleshooting.html">', '<a href="troubleshooting.html" class="active">')
    elif active_page == 'faq.html':
        content = content.replace('<a href="faq.html">', '<a href="faq.html" class="active">')
    
    # Write back
    html_file.write_text(content, encoding='utf-8')
    print(f"  [OK] Fixed {html_file.name}")

print("\n[OK] All navigation links fixed!")
print(f"[OK] Updated {len(list(docs_dir.glob('*.html')))} HTML files")

# Made with Bob
