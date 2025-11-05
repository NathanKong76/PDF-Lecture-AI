#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug mixed content test"""

import os
import sys

# Set console encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pandoc_pdf_generator import PandocPDFGenerator

markdown = """# 主标题

这是介绍段落。

## 列表测试

### 无序列表
- 项目1
- 项目2
- 项目3

### 有序列表
1. 第一项
2. 第二项
3. 第三项

## 代码测试

行内代码: `print("hello")`

代码块:
```python
def test():
    return "测试代码块内容不丢失"
```

## 数学公式测试

行内公式: $E = mc^2$

块公式:
$$\\int_0^1 x^2 dx = \\frac{1}{3}$$

## 表格测试

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| A1  | B1  | C1  |
| A2  | B2  | C2  |

## 引用测试

> 这是引用内容
> 多行引用测试

## 强调测试

**粗体文本** 和 *斜体文本* 和 ***粗斜体***

## 链接测试

[链接文本](https://example.com)

## 结尾标记

CONTENT_END_MARKER
"""

def main():
    print("="*80)
    print(" Mixed Content Debug Test")
    print("="*80)
    
    pdf_bytes, success = PandocPDFGenerator.generate_pdf(
        markdown_content=markdown,
        width_pt=400.0,
        height_pt=800.0,
        font_name=None,
        font_size=11,
        line_spacing=1.3,
        column_padding=10
    )
    
    print(f"\nResult: success={success}, pdf_size={len(pdf_bytes) if pdf_bytes else 0} bytes")
    
    if success and pdf_bytes:
        with open("debug_mixed_content.pdf", "wb") as f:
            f.write(pdf_bytes)
        print(f"✓ PDF saved to: debug_mixed_content.pdf")
        
        # Check LaTeX content
        tex = PandocPDFGenerator.get_last_generated_tex()
        if tex:
            with open("debug_mixed_content.tex", "w", encoding="utf-8") as f:
                f.write(tex)
            print(f"✓ LaTeX saved to: debug_mixed_content.tex")
            
            # Check for key content
            checks = [
                ("主标题", "主标题" in tex),
                ("列表", "项目1" in tex or "item" in tex.lower()),
                ("代码块", "test" in tex or "verbatim" in tex.lower()),
                ("数学公式", "int_" in tex or "frac" in tex),
                ("表格", "tabular" in tex or "列1" in tex),
                ("结尾标记", "CONTENT_END_MARKER" in tex or "END" in tex),
            ]
            
            print("\nContent checks:")
            for name, result in checks:
                status = "✓" if result else "✗"
                print(f"  {status} {name}")
    else:
        error = PandocPDFGenerator.get_last_error()
        print(f"\n❌ Error: {error}")
        
        # Still check LaTeX even on failure
        tex = PandocPDFGenerator.get_last_generated_tex()
        if tex:
            with open("debug_mixed_content_failed.tex", "w", encoding="utf-8") as f:
                f.write(tex)
            print(f"✓ Failed LaTeX saved to: debug_mixed_content_failed.tex")
            print(f"  LaTeX length: {len(tex)} bytes")
        else:
            print("⚠️  No generated LaTeX available")

if __name__ == "__main__":
    main()

