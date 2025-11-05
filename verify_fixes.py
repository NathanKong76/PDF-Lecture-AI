#!/usr/bin/env python3
"""
验证修复后的HTML功能
检查所有用户报告的问题是否已修复
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def verify_all_pages_generated():
    """验证是否为所有页面生成HTML文件"""
    print("Testing: Generate HTML files for all pages...")
    
    try:
        from app.services.html_pdf_generator import HtmlPDFGenerator
        
        # 模拟有5页的PDF，但只有2页有讲解内容
        explanations = {
            1: "First page explanation",
            3: "Third page explanation"
        }
        
        html_files = HtmlPDFGenerator.generate_explanation_html(
            explanations=explanations,
            total_pages=5,  # 总共5页
            font_name="SimHei",
            font_size=14,
            line_spacing=1.2,
            column_padding=10,
            max_chars_per_column=2000
        )
        
        # 应该生成5个HTML文件（每页一个）
        assert len(html_files) == 5, f"Expected 5 HTML files, got {len(html_files)}"
        
        # 检查文件名
        expected_files = ["page_1.html", "page_2.html", "page_3.html", "page_4.html", "page_5.html"]
        actual_files = [filename for filename, _ in html_files]
        
        for expected in expected_files:
            assert expected in actual_files, f"Missing file: {expected}"
        
        print("[PASS] All pages generated HTML files")
        return True
        
    except Exception as e:
        print(f"[FAIL] Page count verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_markdown_rendering():
    """验证Markdown内容被正确转换为HTML"""
    print("\nTesting: Markdown content converted to HTML...")
    
    try:
        from app.services.html_pdf_generator import HtmlPDFGenerator
        
        # 包含Markdown格式的讲解内容
        markdown_content = """
# Title 1
This is **bold text** and *italic text*.

## Title 2
- List item 1
- List item 2

[Link text](http://example.com)
        """.strip()
        
        # 使用generate_explanation_html来测试完整的转换流程
        explanations = {1: markdown_content}
        html_files = HtmlPDFGenerator.generate_explanation_html(
            explanations=explanations,
            total_pages=1,
            font_name="SimHei",
            font_size=14,
            line_spacing=1.2,
            column_padding=10,
            max_chars_per_column=2000
        )
        
        # 获取生成的HTML内容
        html_content = html_files[0][1] if html_files else ""
        
        # 检查HTML中是否包含转换后的内容
        assert "<h1>Title 1</h1>" in html_content, "Title 1 not converted correctly"
        assert "<strong>bold text</strong>" in html_content, "Bold text not converted correctly"
        assert "<em>italic text</em>" in html_content, "Italic text not converted correctly"
        assert "<h2>Title 2</h2>" in html_content, "Title 2 not converted correctly"
        assert "<li>List item 1</li>" in html_content, "List not converted correctly"
        
        print("[PASS] Markdown content correctly converted to HTML")
        return True
        
    except Exception as e:
        print(f"[FAIL] Markdown rendering verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_zip_includes_pdf():
    """验证ZIP文件包含PDF文件"""
    print("\nTesting: ZIP file contains PDF...")
    
    try:
        from app.ui_helpers import build_zip_cache_html
        
        # 模拟包含PDF字节的HTML结果
        mock_results = {
            "test.pdf": {
                "status": "completed",
                "html_content": "<html><body>Test HTML</body></html>",
                "explanations": {1: "Explanation 1"},
                "pdf_bytes": b"Fake PDF content for testing",
                "html_files": [("page_1.html", "<html><body>Page 1</body></html>")],
                "index_html": "<html><body>Index</body></html>"
            }
        }
        
        # 构建ZIP
        zip_bytes = build_zip_cache_html(mock_results)
        
        assert zip_bytes is not None, "ZIP building failed"
        
        # 验证ZIP内容
        import zipfile
        import io
        
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
            file_list = zip_file.namelist()
            
            # 检查是否包含PDF文件
            pdf_files = [f for f in file_list if f.endswith('.pdf')]
            assert len(pdf_files) > 0, f"No PDF files in ZIP, contained files: {file_list}"
            
            # 检查是否包含HTML文件
            html_files = [f for f in file_list if f.endswith('.html')]
            assert len(html_files) > 0, f"No HTML files in ZIP, contained files: {file_list}"
            
            # 检查是否包含JSON文件
            json_files = [f for f in file_list if f.endswith('.json')]
            assert len(json_files) > 0, f"No JSON files in ZIP, contained files: {file_list}"
        
        print("[PASS] ZIP file correctly contains PDF, HTML and JSON files")
        return True
        
    except Exception as e:
        print(f"[FAIL] ZIP PDF inclusion verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主验证函数"""
    print("HTML Function Fix Verification")
    print("=" * 50)
    
    tests = [
        verify_all_pages_generated,
        verify_markdown_rendering,
        verify_zip_includes_pdf,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All issues have been fixed!")
        print("\nFix Summary:")
        print("1. Now generates HTML files for all pages of the PDF (including pages without explanations)")
        print("2. Downloaded ZIP packages now include the original PDF file")
        print("3. Markdown content is now correctly converted to HTML format for rendering")
        return True
    else:
        print(f"Warning: {total - passed} verification failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
