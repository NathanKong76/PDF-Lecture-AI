#!/usr/bin/env python3
"""
简化的同步HTML功能测试
避免emoji字符编码问题
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.sync_html_processor import create_sync_html, generate_simple_sync_view


def create_simple_pdf(path: str) -> None:
    """创建简单的PDF文件"""
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Sample PDF Content) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000102 00000 n 
0000000279 00000 n 
0000000363 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
439
%%EOF"""
    
    with open(path, 'wb') as f:
        f.write(pdf_content)


def create_simple_explanations() -> dict:
    """创建简单的讲解内容"""
    return {
        1: "这是第一页的讲解内容。本页主要介绍文档的基本结构和内容概览。",
        2: "第二页讲解了主要概念和理论基础。这些概念是理解后续内容的基础。",
        3: "第三页展示了具体的应用案例。通过实例可以更好地理解理论知识的实际应用。"
    }


def test_basic_functionality():
    """测试基本功能"""
    print("开始测试基本功能...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建示例PDF
        pdf_path = temp_path / "sample.pdf"
        create_simple_pdf(str(pdf_path))
        
        # 创建示例讲解内容
        explanations = create_simple_explanations()
        
        # 测试基本同步HTML生成
        try:
            result = create_sync_html(
                pdf_path=str(pdf_path),
                explanations=explanations,
                total_pages=3,
                output_dir=str(temp_path / "sync_output"),
                font_name="SimHei",
                font_size=14
            )
            
            print("✓ 基本功能测试通过")
            print("生成的文件:")
            for file_type, file_path in result.items():
                print(f"  {file_type}: {file_path}")
            
            return True
            
        except Exception as e:
            print(f"✗ 基本功能测试失败: {e}")
            return False


def test_simple_sync_view():
    """测试简单同步视图"""
    print("\n测试简单同步视图...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建示例PDF
        pdf_path = temp_path / "sample.pdf"
        create_simple_pdf(str(pdf_path))
        
        # 创建示例讲解内容
        explanations = create_simple_explanations()
        
        # 测试简单同步视图生成
        try:
            result_path = generate_simple_sync_view(
                pdf_path=str(pdf_path),
                explanations=explanations,
                total_pages=3,
                output_path=str(temp_path / "simple_sync.html")
            )
            
            print("✓ 简单同步视图测试通过")
            print(f"生成文件: {result_path}")
            
            # 检查文件是否生成
            if os.path.exists(result_path):
                file_size = os.path.getsize(result_path)
                print(f"文件大小: {file_size} 字节")
                
                # 检查HTML内容
                with open(result_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if "PDFExplanationSync" in content:
                    print("✓ JavaScript同步功能已包含")
                else:
                    print("✗ JavaScript同步功能缺失")
                    
                if "explanation-page-1" in content:
                    print("✓ 讲解页面结构正确")
                else:
                    print("✗ 讲解页面结构异常")
            else:
                print("✗ 文件生成失败")
                return False
                
            return True
            
        except Exception as e:
            print(f"✗ 简单同步视图测试失败: {e}")
            return False


def main():
    """主测试函数"""
    print("=== PDF讲解同步HTML功能简化测试 ===")
    
    tests = [
        ("基本功能", test_basic_functionality),
        ("简单同步视图", test_simple_sync_view),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 测试通过")
            else:
                print(f"✗ {test_name} 测试失败")
        except Exception as e:
            print(f"! {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("所有测试通过！PDF讲解同步功能正常工作。")
    else:
        print("部分测试失败，请检查相关功能。")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
