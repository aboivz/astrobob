# AstroBob Documentation

This directory contains the complete HTML documentation for AstroBob.

## Viewing Documentation Locally

The documentation uses JavaScript for search functionality, which requires an HTTP server (not file:// protocol).

### Option 1: Python HTTP Server (Recommended)

```bash
# From the docs directory
python serve.py

# Or specify a custom port
python serve.py 3000
```

Then open http://localhost:8000/index.html in your browser.

### Option 2: Python Built-in Server

```bash
# From the docs directory
python -m http.server 8000
```

Then open http://localhost:8000/index.html in your browser.

### Option 3: Node.js http-server

```bash
# Install globally
npm install -g http-server

# From the docs directory
http-server -p 8000
```

Then open http://localhost:8000/index.html in your browser.

### Option 4: VS Code Live Server Extension

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

## Documentation Structure

```
docs/
├── index.html              # Home page
├── quickstart.html         # Getting started guide
├── installation.html       # Installation instructions
├── configuration.html      # Configuration guide
├── cli-reference.html      # CLI command reference
├── mcp-tools.html          # MCP tools documentation
├── troubleshooting.html    # Troubleshooting guide
├── faq.html                # Frequently asked questions
├── styles.css              # Styling
├── search.js               # Search functionality
├── serve.py                # Local server script
└── README.md               # This file
```

## Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Search**: Client-side search across all pages
- **Syntax Highlighting**: Code examples with Prism.js
- **Navigation**: Sidebar navigation and breadcrumbs
- **Professional Styling**: Clean B2B design

## Publishing to GitHub Pages

To publish this documentation to GitHub Pages:

1. Push the `docs/` directory to your repository
2. Go to repository Settings → Pages
3. Set source to "Deploy from a branch"
4. Select branch: `main` and folder: `/docs`
5. Save and wait for deployment

Your documentation will be available at:
`https://yourusername.github.io/astrobob/`

## Building for Production

The documentation is static HTML and requires no build step. Simply:

1. Ensure all links are relative (already done)
2. Test locally with HTTP server
3. Deploy to any static hosting service

## Troubleshooting

### Search doesn't work

**Problem**: "Unsafe attempt to load URL" error in console

**Solution**: Use an HTTP server (see viewing options above). The file:// protocol has CORS restrictions that prevent JavaScript from working properly.

### Styles not loading

**Problem**: CSS not applied

**Solution**: 
- Ensure `styles.css` is in the same directory as HTML files
- Check browser console for 404 errors
- Verify file paths are relative (no leading `/`)

### Links broken

**Problem**: 404 errors when clicking links

**Solution**:
- All links should be relative (e.g., `quickstart.html` not `/quickstart.html`)
- Ensure all referenced HTML files exist
- Check for typos in filenames

## Contributing

To improve the documentation:

1. Edit HTML files directly
2. Test locally with HTTP server
3. Verify all links work
4. Check responsive design (resize browser)
5. Submit pull request

## License

MIT License - Same as AstroBob project