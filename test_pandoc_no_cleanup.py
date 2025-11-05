#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test pandoc with no temp cleanup for debugging"""

import os
import sys
import subprocess
import tempfile

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
    print(" Test with No Cleanup")
    print("="*80)
    
    # Create temp directory manually
    temp_dir = tempfile.mkdtemp(prefix='pandoc_test_debug_')
    print(f"\nTemp directory: {temp_dir}")
    print("(Directory will NOT be cleaned up)")
    
    # Generate template and markdown
    from app.services.pandoc_renderer import PandocRenderer
    
    # Write markdown
    md_file = os.path.join(temp_dir, 'input.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"✓ Markdown written to: {md_file}")
    
    # Generate template
    template = PandocPDFGenerator._create_latex_template(
        width_pt=400.0,
        height_pt=600.0,
        font_name=None,
        font_size=12,
        line_spacing=1.4,
        column_padding=10
    )
    
    template_file = os.path.join(temp_dir, 'template.tex')
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"✓ Template written to: {template_file}")
    
    # Run pandoc
    pandoc_cmd = PandocRenderer._pandoc_exe
    if pandoc_cmd == 'pandoc':
        PandocRenderer.check_pandoc_available()
        pandoc_cmd = PandocRenderer._pandoc_exe
    
    tex_file = os.path.join(temp_dir, 'output.tex')
    pandoc_args = [
        pandoc_cmd,
        md_file,
        '--from=markdown+tex_math_single_backslash',
        '--to=latex',
        '--template', template_file,
        '--standalone',
    ]
    
    print(f"\nRunning pandoc...")
    process = subprocess.run(
        pandoc_args,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=10,
        shell=False,
        cwd=temp_dir
    )
    
    if process.returncode != 0:
        print(f"✗ Pandoc failed: {process.stderr[:500]}")
        return
    
    # Save processed LaTeX
    tex_content = process.stdout
    processed_tex_file = os.path.join(temp_dir, 'processed.tex')
    with open(processed_tex_file, 'w', encoding='utf-8') as f:
        f.write(tex_content)
    print(f"✓ Processed LaTeX written to: {processed_tex_file}")
    
    # Run xelatex
    xelatex_path = PandocPDFGenerator._xelatex_path or 'xelatex'
    xelatex_args = [
        xelatex_path,
        '-interaction=nonstopmode',
        '-halt-on-error',
        '-synctex=0',
        '-output-directory', temp_dir,
        processed_tex_file
    ]
    
    print(f"\nRunning xelatex...")
    xelatex_process = subprocess.run(
        xelatex_args,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=30,
        shell=False,
        cwd=temp_dir
    )
    
    print(f"XeLaTeX return code: {xelatex_process.returncode}")
    
    # List all files in temp directory
    print(f"\nFiles in temp directory:")
    try:
        files = os.listdir(temp_dir)
        for f in sorted(files):
            full_path = os.path.join(temp_dir, f)
            size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
            print(f"  - {f} ({size} bytes)")
    except Exception as e:
        print(f"✗ Failed to list directory: {e}")
    
    # Check for PDF
    pdf_file = os.path.join(temp_dir, 'processed.pdf')
    if os.path.exists(pdf_file):
        size = os.path.getsize(pdf_file)
        print(f"\n✓ PDF found: {pdf_file} ({size} bytes)")
    else:
        print(f"\n✗ PDF not found at: {pdf_file}")
    
    print(f"\n{'='*80}")
    print(f"Temp directory preserved at: {temp_dir}")
    print(f"You can manually inspect the files there.")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

