#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extreme font size and font type differences test
极端字体大小和字体类型差异测试
"""

import os
import sys

# Set console encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pandoc_pdf_generator import PandocPDFGenerator

def test_extreme_differences():
    """测试极端差异以确保视觉效果明显"""
    
    print("="*80)
    print(" 极端字体差异测试")
    print("="*80)
    
    # 使用简单内容，便于观察差异
    simple_content = """# 字体测试

ABCDEFG abcdefg 1234567890

中文字体测试

**粗体测试**

代码: `print("hello")`

数学: $x^2 + y^2 = z^2$
"""
    
    # 测试极端字体大小差异
    extreme_sizes = [
        {"size": 8, "description": "超小字体 (8pt)"},
        {"size": 12, "description": "小字体 (12pt)"},  
        {"size": 18, "description": "中字体 (18pt)"},
        {"size": 28, "description": "大字体 (28pt)"},
        {"size": 36, "description": "超大字体 (36pt)"},
        {"size": 48, "description": "巨大字体 (48pt)"}
    ]
    
    print("\n1. 极端字体大小测试 (SimHei字体)")
    print("-" * 50)
    
    for size_test in extreme_sizes:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=f"# {size_test['description']}\n\n{simple_content}",
                width_pt=400.0,
                height_pt=300.0,
                font_name="SimHei",
                font_size=size_test['size'],
                line_spacing=1.2,
                column_padding=8
            )
            
            if success and pdf_bytes:
                filename = f"extreme_size_{size_test['size']}pt.pdf"
                with open(filename, "wb") as f:
                    f.write(pdf_bytes)
                print(f"  ✓ {size_test['description']}: {filename} ({len(pdf_bytes)} bytes)")
            else:
                print(f"  ❌ {size_test['description']}: 生成失败")
                
        except Exception as e:
            print(f"  ❌ {size_test['description']}: 异常 - {e}")
    
    # 测试极端字体类型差异
    print(f"\n\n2. 极端字体类型测试 (24pt)")
    print("-" * 50)
    
    font_tests = [
        {"font": "SimHei", "description": "中文黑体"},
        {"font": "Arial", "description": "英文无衬线"},
        {"font": "Times New Roman", "description": "英文衬线"},
        {"font": "Courier New", "description": "等宽字体"},
        {"font": "KaiTi", "description": "中文楷体"},
        {"font": "SimSun", "description": "中文宋体"}
    ]
    
    for font_test in font_tests:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=f"# {font_test['description']} (24pt)\n\n{simple_content}",
                width_pt=500.0,
                height_pt=400.0,
                font_name=font_test['font'],
                font_size=24,
                line_spacing=1.3,
                column_padding=10
            )
            
            if success and pdf_bytes:
                safe_font_name = font_test['font'].replace(' ', '_').replace('-', '_')
                filename = f"extreme_font_{safe_font_name}.pdf"
                with open(filename, "wb") as f:
                    f.write(pdf_bytes)
                print(f"  ✓ {font_test['description']}: {filename} ({len(pdf_bytes)} bytes)")
            else:
                print(f"  ❌ {font_test['description']}: 生成失败")
                
        except Exception as e:
            print(f"  ❌ {font_test['description']}: 异常 - {e}")
    
    # 组合测试：相同内容，不同设置
    print(f"\n\n3. 组合对比测试")
    print("-" * 50)
    
    combinations = [
        {"size": 10, "font": "SimHei", "name": "10pt_SimHei"},
        {"size": 32, "font": "SimHei", "name": "32pt_SimHei"},
        {"size": 32, "font": "Arial", "name": "32pt_Arial"},
        {"size": 32, "font": "Times New Roman", "name": "32pt_Times"},
    ]
    
    for combo in combinations:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=f"# {combo['name']} 对比测试\n\n对比内容\n\nABCDEFG abcdefg 123\n\n中文字体测试",
                width_pt=600.0,
                height_pt=400.0,
                font_name=combo['font'],
                font_size=combo['size'],
                line_spacing=1.2,
                column_padding=15
            )
            
            if success and pdf_bytes:
                filename = f"comparison_{combo['name']}.pdf"
                with open(filename, "wb") as f:
                    f.write(pdf_bytes)
                print(f"  ✓ {combo['name']}: {filename} ({len(pdf_bytes)} bytes)")
            else:
                print(f"  ❌ {combo['name']}: 生成失败")
                
        except Exception as e:
            print(f"  ❌ {combo['name']}: 异常 - {e}")

def analyze_why_sizes_look_same():
    """分析为什么字体大小看起来一样"""
    
    print(f"\n{'='*80}")
    print(" 字体大小相似性分析")
    print("="*80)
    
    print("""
可能的原因分析：

1. LaTeX 字体大小调整机制
   - LaTeX 会根据内容自动调整字体大小以适应版面
   - 特别是三栏布局时，字体可能被压缩
   
2. 字体本身的视觉特性
   - 不同字体在同一字号下的视觉大小确实可能相似
   - 例如：Arial 和 Times New Roman 在 16pt 时看起来差异不大
   
3. 观察条件
   - 需要更大的字体差异（如 12pt vs 28pt）才能看出明显区别
   - 建议使用极端值进行测试

4. 版面限制
   - 当内容较多时，LaTeX 可能会自动缩小字体以适应空间
   - 这也是为什么文件大小差异很大但视觉差异不明显的原因

建议：
- 使用极端字体大小差异（8pt vs 48pt）
- 比较相同字体的不同大小
- 单独测试纯文本内容，避免复杂元素干扰
    """)

if __name__ == "__main__":
    test_extreme_differences()
    analyze_why_sizes_look_same()
    
    print(f"\n{'='*80}")
    print("测试完成")
    print("\n文件清单:")
    print("极端大小测试: extreme_size_*.pdf")
    print("极端字体测试: extreme_font_*.pdf") 
    print("组合对比测试: comparison_*.pdf")
    print("\n检查建议:")
    print("1. 使用PDF阅读器逐个打开文件")
    print("2. 放大到相同比例进行对比")
    print("3. 特别关注文本行高和字符间距的差异")
    print("4. 比较相同大小不同字体的差异")
