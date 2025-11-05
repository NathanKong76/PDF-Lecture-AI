#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze PDF visual differences
分析PDF文件的视觉差异
"""

import os
import sys
import re
import fitz  # PyMuPDF

# Set console encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def extract_pdf_text_info(pdf_path):
    """提取PDF文件的文本信息用于分析"""
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]  # 第一页
        
        # 获取文本块
        text_dict = page.get_text("dict")
        
        font_info = []
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        font_info.append({
                            "text": span.get("text", ""),
                            "size": span.get("size", 0),
                            "font": span.get("font", ""),
                            "flags": span.get("flags", 0),
                            "color": span.get("color", 0)
                        })
        
        doc.close()
        return font_info
    except Exception as e:
        print(f"  ⚠ 无法分析PDF {pdf_path}: {e}")
        return []

def analyze_font_differences():
    """分析不同字体的PDF差异"""
    
    print("="*80)
    print(" PDF 字体差异分析")
    print("="*80)
    
    # 分析相同大小不同字体的PDF
    test_files = [
        ("SimHei", "test_different_fonts_SimHei.pdf"),
        ("Arial", "test_different_fonts_Arial.pdf"),
        ("Times New Roman", "test_different_fonts_Times_New_Roman.pdf"),
        ("System Default", "test_different_fonts_system_default.pdf")
    ]
    
    print("\n分析相同字体大小(16pt)不同字体的PDF:")
    print("-" * 60)
    
    for font_name, pdf_file in test_files:
        if os.path.exists(pdf_file):
            print(f"\n字体: {font_name}")
            print(f"文件: {pdf_file}")
            print(f"文件大小: {os.path.getsize(pdf_file)} bytes")
            
            # 提取文本信息
            font_info = extract_pdf_text_info(pdf_file)
            
            if font_info:
                # 分析字体信息
                sizes = set()
                fonts = set()
                for info in font_info:
                    if info["text"].strip():  # 只分析有内容的文本
                        sizes.add(round(info["size"], 1))
                        fonts.add(info["font"])
                
                print(f"  字体名称: {', '.join(sorted(fonts))}")
                print(f"  字体大小: {sorted(sizes)}")
                print(f"  文本块数量: {len([info for info in font_info if info['text'].strip()])}")
            else:
                print("  ⚠ 无法提取文本信息")
        else:
            print(f"\n字体: {font_name}")
            print(f"  ❌ 文件不存在: {pdf_file}")
    
    # 分析相同字体不同大小的PDF
    print(f"\n\n分析相同字体(SimHei)不同大小的PDF:")
    print("-" * 60)
    
    size_files = [
        ("12pt", "test_size_vs_font_12pt_黑体.pdf"),
        ("16pt", "test_size_vs_font_16pt_黑体.pdf"),
        ("20pt", "test_size_vs_font_20pt_黑体.pdf")
    ]
    
    for size_name, pdf_file in size_files:
        if os.path.exists(pdf_file):
            print(f"\n大小: {size_name}")
            print(f"文件: {pdf_file}")
            print(f"文件大小: {os.path.getsize(pdf_file)} bytes")
            
            font_info = extract_pdf_text_info(pdf_file)
            
            if font_info:
                sizes = set()
                fonts = set()
                for info in font_info:
                    if info["text"].strip():
                        sizes.add(round(info["size"], 1))
                        fonts.add(info["font"])
                
                print(f"  字体名称: {', '.join(sorted(fonts))}")
                print(f"  实际字体大小: {sorted(sizes)}")
            else:
                print("  ⚠ 无法提取文本信息")
        else:
            print(f"\n大小: {size_name}")
            print(f"  ❌ 文件不存在: {pdf_file}")

def create_visual_comparison_test():
    """创建视觉对比测试"""
    
    print(f"\n{'='*80}")
    print(" 创建视觉对比测试文档")
    print("="*80)
    
    from app.services.pandoc_pdf_generator import PandocPDFGenerator
    
    # 创建对比测试内容 - 使用相同文本但明显不同的字体大小
    markdown_template = """# 字体大小视觉对比测试

## 测试文本 (应该显示为不同大小)

这是标准大小的文本，用于对比。

**粗体文本测试** - 用于验证字体粗细效果

### 代码块测试
```python
def test_function():
    # 这是一条注释
    return "Hello, World!"
```

### 列表测试
- 项目1
- 项目2
- 项目3

### 表格测试
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A1  | B1  | C1  |
| A2  | B2  | C2  |

### 数学公式测试
行内公式: $E = mc^2$

块公式:
$$\\int_0^1 x^2 dx = \\frac{1}{3}$$

### 特殊字符测试
- 百分号: 50%
- 下划线: test_variable
- 美元符号: $100
- 花括号: {key: value}

结束标记: VISUAL_TEST_END
"""
    
    # 明显不同的字体大小
    test_sizes = [10, 14, 18, 24]
    
    print("生成视觉对比PDF (相同内容，不同大小):")
    
    for size in test_sizes:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=f"# {size}pt 字体大小测试\n\n{markdown_template}",
                width_pt=420.0,
                height_pt=640.0,
                font_name="SimHei",
                font_size=size,
                line_spacing=1.4,
                column_padding=10
            )
            
            if success and pdf_bytes:
                filename = f"visual_test_{size}pt.pdf"
                with open(filename, "wb") as f:
                    f.write(pdf_bytes)
                print(f"  ✓ 生成: {filename} ({len(pdf_bytes)} bytes)")
            else:
                print(f"  ❌ 失败: {size}pt")
                
        except Exception as e:
            print(f"  ❌ 异常: {size}pt - {e}")

def debug_latex_differences():
    """调试LaTeX差异"""
    
    print(f"\n{'='*80}")
    print(" LaTeX 差异调试")
    print("="*80)
    
    # 比较不同字体的LaTeX文件
    tex_files = [
        ("SimHei", "test_different_fonts_SimHei.tex"),
        ("Arial", "test_different_fonts_Arial.tex"),
        ("Microsoft YaHei", "test_different_fonts_Microsoft_YaHei.tex")
    ]
    
    for font_name, tex_file in tex_files:
        if os.path.exists(tex_file):
            print(f"\n字体: {font_name}")
            print(f"LaTeX文件: {tex_file}")
            
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取关键设置
            doc_match = re.search(r'\\documentclass\[([0-9.]+)pt\]', content)
            baseline_match = re.search(r'\\setlength\{\\baselineskip\}\{([0-9.]+)pt\}', content)
            cjk_match = re.search(r'\\setCJKmainfont\{([^}]+)\}', content)
            
            print(f"  文档类: {doc_match.group(0) if doc_match else '未找到'}")
            print(f"  行距: {baseline_match.group(0) if baseline_match else '未找到'}")
            print(f"  CJK字体: {cjk_match.group(0) if cjk_match else '未找到'}")
            
            # 检查文件大小
            print(f"  文件大小: {len(content)} 字符")

if __name__ == "__main__":
    analyze_font_differences()
    create_visual_comparison_test()
    debug_latex_differences()
    
    print(f"\n{'='*80}")
    print("分析完成")
    print("\n建议:")
    print("1. 使用PDF阅读器打开生成的PDF文件")
    print("2. 仔细观察字体大小的实际视觉效果")
    print("3. 特别关注文本的高度和间距差异")
    print("4. 对比不同字体文件的中文字符显示效果")
