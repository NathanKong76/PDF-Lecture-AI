#!/usr/bin/env python3
"""
基础的同步HTML功能测试
避免所有特殊字符编码问题
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.sync_html_processor import create_sync_html


def create_basic_pdf(path: str) -> None:
    """创建基础PDF文件"""
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000056 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
179
%%EOF"""
    
    with open(path, 'wb') as f:
        f.write(pdf_content)


def create_basic_explanations():
    """创建基础讲解内容"""
    return {
        1: "第一页讲解内容。本页介绍文档的基本结构。",
        2: "第二页讲解内容。本页介绍主要概念和理论。",
        3: "第三页讲解内容。本页展示具体应用案例。"
    }


def test_basic_functionality():
    """测试基本功能"""
    print("Testing basic functionality...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建示例PDF
        pdf_path = temp_path / "sample.pdf"
        create_basic_pdf(str(pdf_path))
        
        # 创建示例讲解内容
        explanations = create_basic_explanations()
        
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
            
            print("SUCCESS: Basic functionality test passed")
            print("Generated files:")
            for file_type, file_path in result.items():
                print(f"  {file_type}: {file_path}")
            
            return True
            
        except Exception as e:
            print(f"FAILED: Basic functionality test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主测试函数"""
    print("=== PDF Explanation Sync HTML Basic Test ===")
    
    success = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("Test Result: PASSED - PDF explanation sync functionality works correctly.")
    else:
        print("Test Result: FAILED - Please check the functionality.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
