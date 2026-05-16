/**
 * Simple client-side search functionality for AstroBob documentation
 * 
 * This provides basic search across documentation pages without requiring
 * a backend search service.
 */

(function() {
    'use strict';
    
    // Search index - pages and their searchable content
    const searchIndex = [
        {
            title: 'Home',
            url: 'index.html',
            keywords: ['astrobob', 'memory', 'agent', 'bob', 'astradb', 'mcp', 'semantic', 'episodic', 'procedural', 'toolkit']
        },
        {
            title: 'Quick Start',
            url: 'quickstart.html',
            keywords: ['quickstart', 'tutorial', 'getting started', 'first steps', 'example', 'guide']
        },
        {
            title: 'Installation',
            url: 'installation.html',
            keywords: ['install', 'setup', 'uv', 'pip', 'pipx', 'python', 'requirements', 'dependencies']
        },
        {
            title: 'CLI Reference',
            url: 'cli-reference.html',
            keywords: ['cli', 'command', 'line', 'commands', 'astrobob', 'memory', 'recall', 'remember', 'init', 'doctor']
        },
        {
            title: 'MCP Tools',
            url: 'mcp-tools.html',
            keywords: ['mcp', 'tools', 'remember', 'recall', 'reflect', 'forget', 'audit', 'protocol']
        },
        {
            title: 'Troubleshooting',
            url: 'troubleshooting.html',
            keywords: ['troubleshooting', 'problems', 'issues', 'errors', 'debug', 'help', 'fix', 'cors']
        },
        {
            title: 'FAQ',
            url: 'faq.html',
            keywords: ['faq', 'questions', 'answers', 'help', 'common', 'frequently asked']
        }
    ];
    
    // Initialize search functionality
    function initSearch() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;
        
        // Create search results dropdown
        const resultsDiv = document.createElement('div');
        resultsDiv.className = 'search-results';
        resultsDiv.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 0.375rem;
            margin-top: 0.25rem;
            max-height: 400px;
            overflow-y: auto;
            display: none;
            z-index: 1000;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        `;
        
        const searchBox = searchInput.parentElement;
        searchBox.style.position = 'relative';
        searchBox.appendChild(resultsDiv);
        
        // Handle search input
        let searchTimeout;
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim().toLowerCase();
            
            if (query.length < 2) {
                resultsDiv.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query, resultsDiv);
            }, 300);
        });
        
        // Close results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchBox.contains(e.target)) {
                resultsDiv.style.display = 'none';
            }
        });
        
        // Handle keyboard navigation
        searchInput.addEventListener('keydown', function(e) {
            const items = resultsDiv.querySelectorAll('.search-result-item');
            const activeItem = resultsDiv.querySelector('.search-result-item.active');
            let currentIndex = Array.from(items).indexOf(activeItem);
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentIndex = Math.min(currentIndex + 1, items.length - 1);
                setActiveItem(items, currentIndex);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentIndex = Math.max(currentIndex - 1, 0);
                setActiveItem(items, currentIndex);
            } else if (e.key === 'Enter' && activeItem) {
                e.preventDefault();
                activeItem.click();
            } else if (e.key === 'Escape') {
                resultsDiv.style.display = 'none';
                searchInput.blur();
            }
        });
    }
    
    // Perform search and display results
    function performSearch(query, resultsDiv) {
        const results = searchIndex.filter(page => {
            const titleMatch = page.title.toLowerCase().includes(query);
            const keywordMatch = page.keywords.some(keyword => 
                keyword.toLowerCase().includes(query)
            );
            return titleMatch || keywordMatch;
        });
        
        if (results.length === 0) {
            resultsDiv.innerHTML = `
                <div style="padding: 1rem; text-align: center; color: #6b7280;">
                    No results found for "${query}"
                </div>
            `;
            resultsDiv.style.display = 'block';
            return;
        }
        
        resultsDiv.innerHTML = results.map((result, index) => `
            <a href="${result.url}" 
               class="search-result-item ${index === 0 ? 'active' : ''}"
               style="display: block; padding: 0.75rem 1rem; text-decoration: none; color: #111827; border-bottom: 1px solid #f3f4f6; transition: background-color 0.15s ease;">
                <div style="font-weight: 600; margin-bottom: 0.25rem;">${result.title}</div>
                <div style="font-size: 0.875rem; color: #6b7280;">${result.url}</div>
            </a>
        `).join('');
        
        resultsDiv.style.display = 'block';
        
        // Add hover effects
        const items = resultsDiv.querySelectorAll('.search-result-item');
        items.forEach(item => {
            item.addEventListener('mouseenter', function() {
                items.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                this.style.backgroundColor = '#f9fafb';
            });
            item.addEventListener('mouseleave', function() {
                this.style.backgroundColor = 'white';
            });
        });
    }
    
    // Set active item in search results
    function setActiveItem(items, index) {
        items.forEach((item, i) => {
            if (i === index) {
                item.classList.add('active');
                item.style.backgroundColor = '#f9fafb';
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('active');
                item.style.backgroundColor = 'white';
            }
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSearch);
    } else {
        initSearch();
    }
})();

// Made with Bob
