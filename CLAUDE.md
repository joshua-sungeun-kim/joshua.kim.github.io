# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal portfolio website hosted on GitHub Pages (joshua.kim.github.io). It's a single-page application built with vanilla HTML, CSS, and minimal JavaScript, showcasing professional experience in full-stack development.

## Repository Structure

```
joshua.kim.github.io/
├── index.html                    # Main portfolio page (single HTML file with embedded CSS)
├── KakaoTalk_Photo_2025-07-23-15-39-48.png  # Profile image asset
└── CLAUDE.md                      # This file
```

## Common Development Tasks

### Deployment
The site automatically deploys to GitHub Pages when changes are pushed to the main branch:
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

### Local Development
Since this is a static HTML site, you can open it directly in a browser:
```bash
open index.html  # macOS
```

Or use a simple HTTP server for local development:
```bash
python3 -m http.server 8000
# Then visit http://localhost:8000
```

## Architecture & Design Patterns

### CSS Architecture
- **CSS Variables**: Custom properties defined in `:root` for consistent theming (colors, spacing)
- **Mobile-First Responsive Design**: Media queries at 768px breakpoint
- **BEM-like Naming**: Component-based class naming (e.g., `.hero-title`, `.project-card`)
- **Dark Theme**: Primary dark color scheme with gold and teal accents

### Key Components
1. **Navigation**: Fixed header with smooth scroll links
2. **Hero Section**: Landing area with stats and animations
3. **Project Cards**: Grid layout showcasing portfolio items
4. **Skills Grid**: Categorized technical expertise
5. **Contact Section**: Links to external profiles

### Animation System
- CSS keyframe animations (`fadeInUp`)
- Hover effects with transitions
- Backdrop filters for glassmorphism effects

## Important Notes

- **GitHub Pages**: The repository name must match `[username].github.io` format for user site hosting
- **Assets**: Images should be optimized for web performance
- **Single File**: All styles are embedded in index.html for simplicity and faster loading
- **No Build Process**: Pure HTML/CSS, no bundlers or preprocessors needed