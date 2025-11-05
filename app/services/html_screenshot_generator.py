#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Screenshot Generator
Generate single HTML file with PDF screenshots on left and markdown-rendered explanations on right
"""

import base64
import json
from typing import Dict, Optional, List
from .logger import get_logger

logger = get_logger()


class HTMLScreenshotGenerator:
    """Generate HTML screenshot view with scrollable PDF screenshots and column-layout explanations"""
    
    @staticmethod
    def _render_markdown_to_html(markdown_content: str) -> str:
        """
        Render markdown content to HTML
        
        Args:
            markdown_content: Markdown formatted text
            
        Returns:
            Rendered HTML string
        """
        if not markdown_content or not markdown_content.strip():
            return "<p>暂无讲解内容</p>"
        
        try:
            # Try using markdown library for rendering
            import markdown
            html_content = markdown.markdown(
                markdown_content,
                extensions=[
                    'fenced_code',  # Code block support
                    'tables',       # Table support
                    'nl2br',        # Auto line break
                    'sane_lists'    # Better list handling
                ]
            )
            return html_content
        except ImportError:
            # If markdown library not available, use simple text conversion
            html_content = markdown_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_content = html_content.replace('\n\n', '</p><p>').replace('\n', '<br>')
            return f"<p>{html_content}</p>"
        except Exception as e:
            # If rendering fails, return escaped original content
            logger.warning(f"Failed to render markdown: {e}")
            html_content = markdown_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_content = html_content.replace('\n\n', '</p><p>').replace('\n', '<br>')
            return f"<p>{html_content}</p>"
    
    @staticmethod
    def _generate_css_styles(
        font_name: str = "SimHei",
        font_size: int = 14,
        line_spacing: float = 1.2,
        column_count: int = 2,
        column_gap: int = 20,
        show_column_rule: bool = True
    ) -> str:
        """
        Generate CSS styles for HTML screenshot view
        
        Args:
            font_name: Font family name
            font_size: Font size in pt
            line_spacing: Line height multiplier
            column_count: Number of columns for explanation text
            column_gap: Gap between columns in px
            show_column_rule: Whether to show column separator line
            
        Returns:
            CSS string
        """
        column_rule = f"1px solid #ddd" if show_column_rule else "none"
        
        css = f"""
/* HTML Screenshot View Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: '{font_name}', 'Microsoft YaHei', 'SimHei', sans-serif;
    font-size: {font_size}pt;
    line-height: {line_spacing};
    color: #333;
    background-color: #f5f5f5;
    overflow: hidden;
}}

.main-container {{
    display: flex;
    height: 100vh;
    width: 100vw;
}}

/* Left panel: PDF screenshots */
.screenshots-panel {{
    flex: 1;
    max-width: 50%;
    background: #2c3e50;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 20px;
    position: relative;
}}

.screenshots-panel::-webkit-scrollbar {{
    width: 12px;
}}

.screenshots-panel::-webkit-scrollbar-track {{
    background: #34495e;
}}

.screenshots-panel::-webkit-scrollbar-thumb {{
    background: #7f8c8d;
    border-radius: 6px;
}}

.screenshots-panel::-webkit-scrollbar-thumb:hover {{
    background: #95a5a6;
}}

.page-screenshot {{
    margin-bottom: 30px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    transition: all 0.3s ease;
    position: relative;
}}

.page-screenshot.active {{
    box-shadow: 0 8px 32px rgba(52, 152, 219, 0.6);
    transform: scale(1.02);
}}

.page-screenshot img {{
    width: 100%;
    height: auto;
    display: block;
}}

.page-number-badge {{
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(52, 152, 219, 0.9);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 12pt;
    z-index: 10;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}}

/* Right panel: Explanations */
.explanations-panel {{
    flex: 1;
    max-width: 50%;
    background: white;
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
}}

.explanations-panel::-webkit-scrollbar {{
    width: 12px;
}}

.explanations-panel::-webkit-scrollbar-track {{
    background: #ecf0f1;
}}

.explanations-panel::-webkit-scrollbar-thumb {{
    background: #bdc3c7;
    border-radius: 6px;
}}

.explanations-panel::-webkit-scrollbar-thumb:hover {{
    background: #95a5a6;
}}

.explanation-header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px 30px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}}

.explanation-header h1 {{
    font-size: 24pt;
    font-weight: bold;
    margin: 0;
}}

.current-page-indicator {{
    font-size: 14pt;
    margin-top: 8px;
    opacity: 0.9;
}}

.explanations-container {{
    flex: 1;
    position: relative;
}}

.explanation-item {{
    display: none;
    padding: 30px;
    animation: fadeIn 0.3s ease-in-out;
}}

.explanation-item.active {{
    display: block;
}}

.explanation-page-title {{
    font-size: 20pt;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 3px solid #3498db;
}}

/* Column layout for explanation content */
.explanation-content {{
    column-count: {column_count};
    column-gap: {column_gap}px;
    column-rule: {column_rule};
    text-align: justify;
    text-justify: inter-word;
}}

.explanation-content h1,
.explanation-content h2,
.explanation-content h3,
.explanation-content h4,
.explanation-content h5,
.explanation-content h6 {{
    color: #2c3e50;
    margin-top: 15px;
    margin-bottom: 12px;
    break-after: avoid;
    page-break-after: avoid;
}}

.explanation-content h1 {{
    font-size: 18pt;
    border-bottom: 2px solid #3498db;
    padding-bottom: 8px;
}}

.explanation-content h2 {{
    font-size: 16pt;
    color: #3498db;
}}

.explanation-content h3 {{
    font-size: 14pt;
}}

.explanation-content p {{
    margin-bottom: 12px;
    break-inside: avoid;
    page-break-inside: avoid;
}}

.explanation-content ul,
.explanation-content ol {{
    margin-left: 20px;
    margin-bottom: 12px;
    break-inside: avoid;
    page-break-inside: avoid;
}}

.explanation-content li {{
    margin-bottom: 6px;
}}

.explanation-content code {{
    background: #f8f9fa;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
    color: #e74c3c;
}}

.explanation-content pre {{
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 5px;
    padding: 15px;
    overflow-x: auto;
    margin: 15px 0;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 11pt;
    break-inside: avoid;
    page-break-inside: avoid;
}}

.explanation-content blockquote {{
    border-left: 4px solid #3498db;
    padding-left: 15px;
    margin: 15px 0;
    font-style: italic;
    color: #7f8c8d;
    background: #ecf0f1;
    padding: 15px;
    border-radius: 0 5px 5px 0;
    break-inside: avoid;
    page-break-inside: avoid;
}}

.explanation-content table {{
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    break-inside: avoid;
    page-break-inside: avoid;
}}

.explanation-content table th,
.explanation-content table td {{
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}}

.explanation-content table th {{
    background: #3498db;
    color: white;
    font-weight: bold;
}}

.explanation-content table tr:nth-child(even) {{
    background: #f8f9fa;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* Navigation controls */
.nav-controls {{
    position: fixed;
    bottom: 30px;
    right: 30px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 15px 20px;
    border-radius: 25px;
    display: flex;
    align-items: center;
    gap: 15px;
    z-index: 1000;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}}

.nav-btn {{
    background: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-size: 12pt;
    font-weight: bold;
    transition: all 0.3s ease;
}}

.nav-btn:hover:not(:disabled) {{
    background: #2980b9;
    transform: translateY(-2px);
}}

.nav-btn:disabled {{
    background: #7f8c8d;
    cursor: not-allowed;
    opacity: 0.5;
}}

.page-info {{
    font-weight: bold;
    font-size: 14pt;
    min-width: 80px;
    text-align: center;
}}

/* Loading indicator */
.loading {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(255, 255, 255, 0.95);
    padding: 30px 50px;
    border-radius: 15px;
    text-align: center;
    z-index: 10000;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}}

.loading::after {{
    content: '';
    display: block;
    width: 40px;
    height: 40px;
    margin: 15px auto 0;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}}

@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

/* Responsive design */
@media (max-width: 1024px) {{
    .main-container {{
        flex-direction: column;
    }}
    
    .screenshots-panel,
    .explanations-panel {{
        max-width: 100%;
        height: 50vh;
    }}
    
    .explanation-content {{
        column-count: 1;
    }}
}}

@media (max-width: 768px) {{
    body {{
        font-size: 12pt;
    }}
    
    .explanation-header h1 {{
        font-size: 18pt;
    }}
    
    .explanation-content {{
        column-count: 1;
        padding: 20px;
    }}
    
    .nav-controls {{
        bottom: 15px;
        right: 15px;
        padding: 10px 15px;
    }}
}}

/* Print styles */
@media print {{
    .nav-controls,
    .loading {{
        display: none;
    }}
    
    .main-container {{
        flex-direction: column;
    }}
    
    .screenshots-panel,
    .explanations-panel {{
        max-width: 100%;
        overflow: visible;
    }}
}}
"""
        return css
    
    @staticmethod
    def _generate_javascript(total_pages: int) -> str:
        """
        Generate JavaScript for scroll synchronization
        
        Args:
            total_pages: Total number of pages
            
        Returns:
            JavaScript string
        """
        js = f"""
// HTML Screenshot View Synchronization
class ScreenshotExplanationSync {{
    constructor() {{
        this.currentPage = 1;
        this.totalPages = {total_pages};
        this.observer = null;
        this.init();
    }}
    
    init() {{
        // Remove loading indicator
        const loading = document.querySelector('.loading');
        if (loading) {{
            setTimeout(() => loading.remove(), 500);
        }}
        
        // Setup intersection observer
        this.setupObserver();
        
        // Setup navigation controls
        this.setupControls();
        
        // Show first page
        this.showExplanation(1);
    }}
    
    setupObserver() {{
        const options = {{
            root: document.querySelector('.screenshots-panel'),
            rootMargin: '-20% 0px -20% 0px',
            threshold: 0.5
        }};
        
        this.observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    const pageNum = parseInt(entry.target.dataset.page);
                    this.showExplanation(pageNum);
                    
                    // Add active class to current screenshot
                    document.querySelectorAll('.page-screenshot').forEach(el => {{
                        el.classList.remove('active');
                    }});
                    entry.target.classList.add('active');
                }}
            }});
        }}, options);
        
        // Observe all page screenshots
        document.querySelectorAll('.page-screenshot').forEach(el => {{
            this.observer.observe(el);
        }});
    }}
    
    setupControls() {{
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        
        if (prevBtn) {{
            prevBtn.addEventListener('click', () => this.goToPrevPage());
        }}
        
        if (nextBtn) {{
            nextBtn.addEventListener('click', () => this.goToNextPage());
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            switch(e.key) {{
                case 'ArrowUp':
                case 'ArrowLeft':
                    e.preventDefault();
                    this.goToPrevPage();
                    break;
                case 'ArrowDown':
                case 'ArrowRight':
                case ' ':
                    e.preventDefault();
                    this.goToNextPage();
                    break;
                case 'Home':
                    e.preventDefault();
                    this.goToPage(1);
                    break;
                case 'End':
                    e.preventDefault();
                    this.goToPage(this.totalPages);
                    break;
            }}
        }});
    }}
    
    showExplanation(pageNum) {{
        if (pageNum < 1 || pageNum > this.totalPages) {{
            return;
        }}
        
        this.currentPage = pageNum;
        
        // Hide all explanations
        document.querySelectorAll('.explanation-item').forEach(el => {{
            el.classList.remove('active');
        }});
        
        // Show current explanation
        const targetExplanation = document.getElementById(`explanation-${{pageNum}}`);
        if (targetExplanation) {{
            targetExplanation.classList.add('active');
        }}
        
        // Update page indicator
        const indicator = document.querySelector('.current-page-indicator');
        if (indicator) {{
            indicator.textContent = `第 ${{pageNum}} 页 / 共 ${{this.totalPages}} 页`;
        }}
        
        // Update page info in controls
        const pageInfo = document.querySelector('.page-info');
        if (pageInfo) {{
            pageInfo.textContent = `${{pageNum}} / ${{this.totalPages}}`;
        }}
        
        // Update button states
        this.updateButtons();
        
        // Update document title
        document.title = `第${{pageNum}}页 - HTML截图版`;
    }}
    
    goToPage(pageNum) {{
        if (pageNum < 1 || pageNum > this.totalPages) {{
            return;
        }}
        
        // Scroll to the page screenshot
        const screenshot = document.getElementById(`page-${{pageNum}}`);
        if (screenshot) {{
            screenshot.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
    }}
    
    goToPrevPage() {{
        if (this.currentPage > 1) {{
            this.goToPage(this.currentPage - 1);
        }}
    }}
    
    goToNextPage() {{
        if (this.currentPage < this.totalPages) {{
            this.goToPage(this.currentPage + 1);
        }}
    }}
    
    updateButtons() {{
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        
        if (prevBtn) {{
            prevBtn.disabled = this.currentPage <= 1;
        }}
        
        if (nextBtn) {{
            nextBtn.disabled = this.currentPage >= this.totalPages;
        }}
    }}
}}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {{
    window.sync = new ScreenshotExplanationSync();
    console.log('HTML Screenshot View initialized with {{}} pages', {total_pages});
}});

// Expose global functions
window.goToPage = function(pageNum) {{
    if (window.sync) {{
        window.sync.goToPage(pageNum);
    }}
}};
"""
        return js
    
    @staticmethod
    def generate_html_screenshot_view(
        screenshot_data: List[Dict[str, any]],
        explanations: Dict[int, str],
        total_pages: int,
        title: str = "PDF文档讲解",
        font_name: str = "SimHei",
        font_size: int = 14,
        line_spacing: float = 1.2,
        column_count: int = 2,
        column_gap: int = 20,
        show_column_rule: bool = True
    ) -> str:
        """
        Generate complete HTML screenshot view
        
        Args:
            screenshot_data: List of dicts with 'page_num' and 'image_bytes' keys
            explanations: Dict mapping page numbers (1-indexed) to explanation text
            total_pages: Total number of pages
            title: Document title
            font_name: Font family name
            font_size: Font size in pt
            line_spacing: Line height multiplier
            column_count: Number of columns for explanation text
            column_gap: Gap between columns in px
            show_column_rule: Whether to show column separator line
            
        Returns:
            Complete HTML document string
        """
        logger.info(f"Generating HTML screenshot view for {total_pages} pages with {column_count} columns")
        
        # Generate CSS and JavaScript
        css_styles = HTMLScreenshotGenerator._generate_css_styles(
            font_name, font_size, line_spacing, column_count, column_gap, show_column_rule
        )
        javascript_code = HTMLScreenshotGenerator._generate_javascript(total_pages)
        
        # Generate screenshot HTML
        screenshots_html = ""
        for data in screenshot_data:
            page_num = data['page_num']
            image_bytes = data['image_bytes']
            
            # Convert image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            screenshots_html += f"""
            <div class="page-screenshot" id="page-{page_num}" data-page="{page_num}">
                <div class="page-number-badge">第 {page_num} 页</div>
                <img src="data:image/png;base64,{base64_image}" alt="第{page_num}页截图" />
            </div>
            """
        
        # Generate explanations HTML
        explanations_html = ""
        for page_num in range(1, total_pages + 1):
            explanation_text = explanations.get(page_num, "")
            
            # Render markdown to HTML
            if explanation_text.strip():
                explanation_html = HTMLScreenshotGenerator._render_markdown_to_html(explanation_text)
            else:
                explanation_html = "<p>暂无讲解内容</p>"
            
            explanations_html += f"""
            <div class="explanation-item" id="explanation-{page_num}" data-page="{page_num}">
                <div class="explanation-page-title">📖 第 {page_num} 页讲解</div>
                <div class="explanation-content">
                    {explanation_html}
                </div>
            </div>
            """
        
        # Generate complete HTML document
        html_document = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - HTML截图版</title>
    <style>{css_styles}</style>
</head>
<body>
    <!-- Loading indicator -->
    <div class="loading">
        <div style="font-size: 16pt; font-weight: bold; color: #2c3e50;">正在加载...</div>
    </div>
    
    <div class="main-container">
        <!-- Left panel: PDF screenshots -->
        <div class="screenshots-panel">
            {screenshots_html}
        </div>
        
        <!-- Right panel: Explanations -->
        <div class="explanations-panel">
            <div class="explanation-header">
                <h1>📚 {title}</h1>
                <div class="current-page-indicator">第 1 页 / 共 {total_pages} 页</div>
            </div>
            <div class="explanations-container">
                {explanations_html}
            </div>
        </div>
    </div>
    
    <!-- Navigation controls -->
    <div class="nav-controls">
        <button class="nav-btn" id="prev-btn" title="上一页 (↑)">‹ 上一页</button>
        <span class="page-info">1 / {total_pages}</span>
        <button class="nav-btn" id="next-btn" title="下一页 (↓)">下一页 ›</button>
    </div>
    
    <script>{javascript_code}</script>
</body>
</html>
"""
        
        logger.info(f"HTML screenshot view generated successfully, size: {len(html_document)} bytes")
        return html_document

