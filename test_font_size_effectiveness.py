#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test font size effectiveness in pandoc mode
测试 pandoc 模式下字体大小设置是否生效
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

def test_font_size_effectiveness():
    """测试不同字体大小是否生成不同的 LaTeX"""
    
    print("="*80)
    print(" Pandoc 模式字体大小效果测试")
    print("="*80)
    
    # 测试内容
    markdown = """# 字体大小测试

这是测试内容，用于验证字体大小设置是否生效。

## 正常文字
这是普通的段落文字，用于观察字体大小变化。

### 代码示例
```python
def test():
    return "Hello World"
```

### 数学公式
行内公式: $E = mc^2$

块公式:
$$\\int_0^1 x^2 dx = \\frac{1}{3}$$

### 表格
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A1  | B1  | C1  |
| A2  | B2  | C2  |

## 结束标记
TEST_END_MARKER
"""
    
    # 测试不同的字体大小
    font_sizes = [8, 12, 16, 20]
    
    for font_size in font_sizes:
        print(f"\n测试字体大小: {font_size}pt")
        print("-" * 40)
        
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=markdown,
                width_pt=400.0,
                height_pt=600.0,
                font_name=None,  # 使用系统默认字体
                font_size=font_size,
                line_spacing=1.4,
                column_padding=10
            )
            
            if success and pdf_bytes:
                # 检查生成的 LaTeX
                tex = PandocPDFGenerator.get_last_generated_tex()
                if tex:
                    # 检查 LaTeX 中的字体大小设置
                    import re
                    doc_match = re.search(r'\\documentclass\[([0-9.]+)pt\]', tex)
                    if doc_match:
                        actual_size = float(doc_match.group(1))
                        if actual_size == font_size:
                            print(f"  ✓ LaTeX 文档类设置正确: fontsize={actual_size}pt")
                        else:
                            print(f"  ✗ LaTeX 文档类设置不正确: 期望{font_size}pt, 实际{actual_size}pt")
                    else:
                        print(f"  ✗ 无法找到 LaTeX 文档类设置")
                    
                    # 检查行距设置
                    expected_baselineskip = font_size * 1.4
                    baseline_match = re.search(r'\\setlength\{\\baselineskip\}\{([0-9.]+)pt\}', tex)
                    if baseline_match:
                        actual_baseline = float(baseline_match.group(1))
                        if abs(actual_baseline - expected_baselineskip) < 0.1:  # 允许小数精度差异
                            print(f"  ✓ 行距设置正确: baselineskip={actual_baseline}pt")
                        else:
                            print(f"  ✗ 行距设置不正确: 期望{expected_baselineskip}pt, 实际{actual_baseline}pt")
                    else:
                        print(f"  ✗ 无法找到行距设置")
                    
                    # 保存生成的 PDF 用于人工验证
                    filename = f"test_font_size_{font_size}pt.pdf"
                    with open(filename, "wb") as f:
                        f.write(pdf_bytes)
                    print(f"  ✓ PDF 已保存: {filename}")
                    print(f"  📄 PDF 大小: {len(pdf_bytes)} bytes")
                else:
                    print(f"  ✗ 无法获取生成的 LaTeX")
            else:
                error = PandocPDFGenerator.get_last_error()
                print(f"  ❌ PDF 生成失败: {error}")
                
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
    
    print(f"\n{'='*80}")
    print("测试完成")
    print("\n建议:")
    print("1. 人工检查生成的 PDF 文件，观察字体大小是否变化")
    print("2. 使用 PDF 阅读器放大查看，确认字体确实不同")
    print("3. 比较不同字体大小文件的视觉效果")

if __name__ == "__main__":
    test_font_size_effectiveness()
