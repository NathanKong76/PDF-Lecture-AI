#!/usr/bin/env python3
"""
Test script for the new per-page HTML functionality.

This script tests the enhanced HTML generation features including:
1. Per-page HTML generation with navigation
2. Folder structure management
3. Multi-PDF index page generation
"""

import os
import tempfile
import shutil
from pathlib import Path
import fitz

# Add the project root to Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.enhanced_html_generator import EnhancedHTMLGenerator

def test_per_page_html_generation():
    """Test per-page HTML generation functionality."""
    print("Testing Per-Page HTML Generation...")
    
    # Create mock explanations data
    explanations = {
        1: "<h2>第一章 概述</h2><p>这是第一章的讲解内容。</p><p>包含详细的技术说明和代码示例。</p>",
        2: "<h2>第二章 安装</h2><p>本章介绍如何安装软件包。</p><ul><li>步骤1</li><li>步骤2</li></ul>",
        3: "<h2>第三章 配置</h2><p>配置选项说明。</p><pre><code>config.json</code></pre>",
        4: "<h2>第四章 使用</h2><p>使用方法详解。</p>",
        5: "<h2>第五章 最佳实践</h2><p>推荐的使用方式和注意事项。</p>"
    }
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory(prefix="test_per_page_html_") as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Create a test PDF file
        test_pdf_path = os.path.join(temp_dir, "test_document.pdf")
        create_test_pdf(test_pdf_path)
        
        # Generate per-page HTML structure
        print("Generating per-page HTML structure...")
        generated_files = EnhancedHTMLGenerator.generate_complete_per_page_structure(
            explanations=explanations,
            pdf_filename="test_document.pdf",
            total_pages=5,
            output_dir=temp_dir,
            font_name="SimHei",
            font_size=14,
            line_spacing=1.2
        )
        
        # Check generated files
        print("Generated files:")
        for filename, filepath in generated_files.items():
            print(f"  OK {filename} -> {filepath}")
        
        # Verify all expected files exist
        expected_files = ["page_1.html", "page_2.html", "page_3.html", "page_4.html", "page_5.html", "index.html"]
        for expected_file in expected_files:
            if expected_file in generated_files:
                print(f"  OK {expected_file} generated successfully")
            else:
                print(f"  ERROR {expected_file} missing!")
                return False
        
        # Test single page HTML generation
        print("\nTesting individual page generation...")
        for page_num in range(1, 6):
            page_html = EnhancedHTMLGenerator.generate_per_page_html(
                page_number=page_num,
                total_pages=5,
                explanation_content=explanations[page_num],
                pdf_filename="test_document.pdf",
                font_name="SimHei",
                font_size=14,
                line_spacing=1.2,
                output_folder=temp_dir
            )
            
            if f"第 {page_num} 页" in page_html:
                print(f"  OK Page {page_num} HTML generated correctly")
            else:
                print(f"  ERROR Page {page_num} HTML generation failed")
                return False
        
        print("\nPer-page HTML generation test completed successfully!")
        return True

def create_test_pdf(pdf_path):
    """Create a simple test PDF file."""
    try:
        # Create a simple PDF with multiple pages
        doc = fitz.open()
        
        for page_num in range(1, 6):
            page = doc.new_page()
            
            # Add some text content
            text = f"这是第 {page_num} 页的内容\n\n"
            text += f"Page {page_num} Content\n\n"
            text += "This is a test PDF for per-page HTML generation."
            
            point = fitz.Point(72, 72)  # Top left margin
            page.insert_text(point, text, fontsize=12)
        
        doc.save(pdf_path)
        doc.close()
        print(f"Test PDF created: {pdf_path}")
        return True
        
    except Exception as e:
        print(f"Failed to create test PDF: {e}")
        return False

def test_multi_pdf_index():
    """Test multi-PDF index page generation."""
    print("\nTesting Multi-PDF Index Page Generation...")
    
    # Create mock PDF information
    pdf_info_list = [
        {
            "name": "document1",
            "title": "用户手册 - Document 1",
            "pages": 10,
            "folder": "user_manual"
        },
        {
            "name": "document2", 
            "title": "技术文档 - Document 2",
            "pages": 15,
            "folder": "tech_docs"
        },
        {
            "name": "document3",
            "title": "API参考 - Document 3",
            "pages": 25,
            "folder": "api_reference"
        }
    ]
    
    # Generate main index page
    index_file = "test_main_index.html"
    try:
        result_file = EnhancedHTMLGenerator.create_multi_pdf_index(
            pdf_info_list=pdf_info_list,
            output_file=index_file
        )
        
        # Check if file was created
        if os.path.exists(result_file):
            print(f"Main index page created: {result_file}")
            
            # Check file content
            with open(result_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "PDF讲解文档库" in content:
                print("Index page contains expected title")
            else:
                print("Index page missing expected title")
                return False
                
            # Check if all PDFs are included
            for pdf_info in pdf_info_list:
                if pdf_info["title"] in content:
                    print(f"PDF '{pdf_info['title']}' included in index")
                else:
                    print(f"PDF '{pdf_info['title']}' missing from index")
                    return False
                    
            print("Multi-PDF index test completed successfully!")
            return True
            
        else:
            print(f"Index page not created: {result_file}")
            return False
            
    except Exception as e:
        print(f"Multi-PDF index generation failed: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(index_file):
            os.remove(index_file)

def main():
    """Main test function."""
    print("Starting Per-Page HTML Feature Tests")
    print("=" * 50)
    
    # Test per-page HTML generation
    success1 = test_per_page_html_generation()
    
    # Test multi-PDF index generation
    success2 = test_multi_pdf_index()
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"  Per-Page HTML Generation: {'PASSED' if success1 else 'FAILED'}")
    print(f"  Multi-PDF Index Generation: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 and success2:
        print("\nAll tests passed! The per-page HTML feature is working correctly.")
        return True
    else:
        print("\nSome tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    main()
