#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test different fonts in pandoc mode
测试pandoc模式下不同字体的效果
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

def test_different_fonts():
    """测试不同字体的效果"""
    
    print("="*80)
    print(" Pandoc 模式不同字体效果测试")
    print("="*80)
    
    # 测试内容
    markdown = """# 字体测试

这是测试内容，用于验证不同字体是否生效。

## 中文字体测试
- 微软雅黑: 微软雅黑字体测试
- 宋体: 宋体字体测试  
- 黑体: 黑体字体测试
- 楷体: 楷体字体测试
- 仿宋: 仿宋字体测试

## 英文字体测试
- Times New Roman: Times New Roman font test
- Arial: Arial font test
- Helvetica: Helvetica font test
- Georgia: Georgia font test
- Verdana: Verdana font test

## 代码测试
```python
def font_test():
    print("不同字体的代码显示效果")
    return True
```

## 数学公式
行内公式: $E = mc^2$

块公式:
$$\\int_0^1 x^2 dx = \\frac{1}{3}$$

## 表格测试
| 字体 | 效果 | 说明 |
|------|------|------|
| SimHei | 黑体 | 常用中文字体 |
| Arial | 英文字体 | 无衬线字体 |
| Times | 衬线字体 | 传统衬线字体 |

## 结束标记
FONT_TEST_END_MARKER
"""
    
    # 测试不同的字体
    font_tests = [
        {
            "name": "黑体测试",
            "font_name": "SimHei",
            "description": "Windows系统常见中文字体"
        },
        {
            "name": "宋体测试", 
            "font_name": "SimSun",
            "description": "Windows系统宋体"
        },
        {
            "name": "微软雅黑测试",
            "font_name": "Microsoft YaHei", 
            "description": "Windows系统微软雅黑"
        },
        {
            "name": "楷体测试",
            "font_name": "KaiTi",
            "description": "Windows系统楷体"
        },
        {
            "name": "Arial测试",
            "font_name": "Arial",
            "description": "英文字体，无衬线"
        },
        {
            "name": "Times New Roman测试",
            "font_name": "Times New Roman",
            "description": "英文字体，衬线"
        },
        {
            "name": "无字体测试（系统默认）",
            "font_name": None,
            "description": "使用系统默认字体"
        }
    ]
    
    # 固定字体大小，便于比较字体差异
    fixed_font_size = 16
    fixed_line_spacing = 1.4
    fixed_column_padding = 10
    
    for i, font_test in enumerate(font_tests):
        print(f"\n测试 {i+1}: {font_test['name']}")
        print("-" * 50)
        print(f"  字体名称: {font_test['font_name'] or '系统默认'}")
        print(f"  描述: {font_test['description']}")
        
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=markdown,
                width_pt=400.0,
                height_pt=600.0,
                font_name=font_test['font_name'],
                font_size=fixed_font_size,
                line_spacing=fixed_line_spacing,
                column_padding=fixed_column_padding
            )
            
            if success and pdf_bytes:
                # 检查生成的 LaTeX
                tex = PandocPDFGenerator.get_last_generated_tex()
                if tex:
                    import re
                    
                    # 检查字体设置
                    font_setting_found = False
                    if font_test['font_name']:
                        # 检查是否包含字体设置
                        if 'setCJKmainfont' in tex and font_test['font_name'] in tex:
                            print(f"  ✓ CJK字体设置正确: {font_test['font_name']}")
                            font_setting_found = True
                        elif 'fontspec' in tex and font_test['font_name'] in tex:
                            print(f"  ✓ 字体设置找到（fontspec）: {font_test['font_name']}")
                            font_setting_found = True
                        else:
                            print(f"  ⚠ 可能未正确设置字体: {font_test['font_name']}")
                    else:
                        print(f"  ✓ 使用系统默认字体")
                        font_setting_found = True
                    
                    # 检查字体大小设置
                    doc_match = re.search(r'\\documentclass\[([0-9.]+)pt\]', tex)
                    if doc_match:
                        actual_size = float(doc_match.group(1))
                        if actual_size == fixed_font_size:
                            print(f"  ✓ 字体大小设置正确: {actual_size}pt")
                        else:
                            print(f"  ✗ 字体大小错误: 期望{fixed_font_size}pt, 实际{actual_size}pt")
                    else:
                        print(f"  ✗ 无法找到字体大小设置")
                    
                    # 检查行距设置
                    expected_baselineskip = fixed_font_size * fixed_line_spacing
                    baseline_match = re.search(r'\\setlength\{\\baselineskip\}\{([0-9.]+)pt\}', tex)
                    if baseline_match:
                        actual_baseline = float(baseline_match.group(1))
                        if abs(actual_baseline - expected_baselineskip) < 0.1:
                            print(f"  ✓ 行距设置正确: {actual_baseline}pt")
                        else:
                            print(f"  ✗ 行距错误: 期望{expected_baselineskip}pt, 实际{actual_baseline}pt")
                    else:
                        print(f"  ✗ 无法找到行距设置")
                    
                    # 保存生成的 PDF
                    font_file_name = font_test['font_name'].replace(' ', '_') if font_test['font_name'] else 'system_default'
                    filename = f"test_different_fonts_{font_file_name}.pdf"
                    with open(filename, "wb") as f:
                        f.write(pdf_bytes)
                    print(f"  ✓ PDF 已保存: {filename}")
                    print(f"  📄 PDF 大小: {len(pdf_bytes)} bytes")
                    
                    # 检查是否生成了辅助文件（用于调试）
                    if tex and len(tex) > 0:
                        tex_filename = f"test_different_fonts_{font_file_name}.tex"
                        with open(tex_filename, "w", encoding="utf-8") as f:
                            f.write(tex)
                        print(f"  📝 LaTeX 已保存: {tex_filename}")
                    
                else:
                    print(f"  ✗ 无法获取生成的 LaTeX")
            else:
                error = PandocPDFGenerator.get_last_error()
                print(f"  ❌ PDF 生成失败: {error}")
                
                # 即使失败也保存LaTeX用于调试
                tex = PandocPDFGenerator.get_last_generated_tex()
                if tex:
                    font_file_name = font_test['font_name'].replace(' ', '_') if font_test['font_name'] else 'system_default'
                    tex_filename = f"test_failed_{font_file_name}.tex"
                    with open(tex_filename, "w", encoding="utf-8") as f:
                        f.write(tex)
                    print(f"  📝 失败LaTeX已保存: {tex_filename}")
                
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")
        
        print()
    
    print(f"{'='*80}")
    print("不同字体测试完成")
    print("\n建议:")
    print("1. 人工检查生成的PDF文件，观察字体是否不同")
    print("2. 特别注意中文字符的显示效果")
    print("3. 对比英文字符在不同字体下的差异")
    print("4. 检查字体回退机制（某些字体不可用时）")

def test_font_size_vs_font_type():
    """对比测试：字体大小 vs 字体类型"""
    
    print(f"\n{'='*80}")
    print("字体大小 vs 字体类型对比测试")
    print("="*80)
    
    # 相同内容，不同字体大小和字体类型
    markdown = "ABCDEFG abcdefg 123456 中文字体测试 Font Test"
    
    # 测试组合
    test_combinations = [
        {"size": 12, "font": "SimHei", "name": "12pt_黑体"},
        {"size": 16, "font": "SimHei", "name": "16pt_黑体"},  
        {"size": 20, "font": "SimHei", "name": "20pt_黑体"},
        {"size": 16, "font": "Arial", "name": "16pt_Arial"},
        {"size": 16, "font": "Times New Roman", "name": "16pt_Times"},
        {"size": 16, "font": None, "name": "16pt_系统默认"},
    ]
    
    for combo in test_combinations:
        print(f"\n测试: {combo['name']}")
        
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=f"# {combo['name']}\n\n{markdown}",
                width_pt=400.0,
                height_pt=300.0,
                font_name=combo['font'],
                font_size=combo['size'],
                line_spacing=1.2,
                column_padding=8
            )
            
            if success and pdf_bytes:
                filename = f"test_size_vs_font_{combo['name']}.pdf"
                with open(filename, "wb") as f:
                    f.write(pdf_bytes)
                print(f"  ✓ 已保存: {filename} ({len(pdf_bytes)} bytes)")
            else:
                print(f"  ❌ 失败: {combo['name']}")
                
        except Exception as e:
            print(f"  ❌ 异常: {combo['name']} - {str(e)}")

if __name__ == "__main__":
    test_different_fonts()
    test_font_size_vs_font_type()
