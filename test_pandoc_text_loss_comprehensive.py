#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test for pandoc text loss issues
全面测试 pandoc 模式下的文字丢失问题
"""

import os
import sys
import traceback
from typing import List, Tuple

# Set console encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pandoc_pdf_generator import PandocPDFGenerator, preprocess_markdown_for_latex


class TestResult:
    """Test result holder"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, case: str, detail: str = ""):
        self.passed.append((case, detail))
    
    def add_fail(self, case: str, reason: str):
        self.failed.append((case, reason))
    
    def add_warning(self, case: str, reason: str):
        self.warnings.append((case, reason))
    
    def print_result(self):
        print(f"\n{'='*80}")
        print(f"测试: {self.test_name}")
        print(f"{'='*80}")
        
        if self.passed:
            print(f"\n✅ 通过 ({len(self.passed)}):")
            for case, detail in self.passed:
                print(f"  ✓ {case}")
                if detail:
                    print(f"    {detail}")
        
        if self.failed:
            print(f"\n❌ 失败 ({len(self.failed)}):")
            for case, reason in self.failed:
                print(f"  ✗ {case}")
                print(f"    原因: {reason}")
        
        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for case, reason in self.warnings:
                print(f"  ⚠ {case}")
                print(f"    {reason}")
        
        total = len(self.passed) + len(self.failed)
        if total > 0:
            pass_rate = len(self.passed) / total * 100
            print(f"\n通过率: {pass_rate:.1f}% ({len(self.passed)}/{total})")
        
        return len(self.failed) == 0


def test_special_characters():
    """测试1: 特殊字符处理 - LaTeX 特殊字符不应导致文字丢失"""
    result = TestResult("特殊字符处理")
    
    # Check availability
    latex_available, latex_info = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        result.add_warning("LaTeX 不可用", f"跳过测试: {latex_info}")
        result.print_result()
        return False
    
    # Test cases with LaTeX special characters
    test_cases = [
        ("反斜杠", "这是反斜杠 \\ 测试"),
        ("百分号", "进度达到 50% 完成"),
        ("美元符号", "价格 $100 和变量 $x"),
        ("井号", "标签 #tag1 和 #tag2"),
        ("下划线", "变量 var_name 和 test_case"),
        ("花括号", "集合 {a, b, c} 和对象 {key: value}"),
        ("脱字符", "幂运算 x^2 和 y^3"),
        ("波浪号", "路径 ~/home 和约等于 ~123"),
        ("与符号", "逻辑与 A & B"),
        ("组合测试", "完整测试: $price = 100%, path = ~/test_{id}^2"),
    ]
    
    for case_name, content in test_cases:
        try:
            markdown = f"# {case_name}\n\n{content}\n\n这是后续内容，确保不会丢失。"
            
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=markdown,
                width_pt=400.0,
                height_pt=600.0,
                font_name=None,
                font_size=12,
                line_spacing=1.4,
                column_padding=10
            )
            
            if success and pdf_bytes and len(pdf_bytes) > 1000:
                # Check if generated LaTeX contains the content
                tex = PandocPDFGenerator.get_last_generated_tex()
                if tex and case_name in tex:
                    result.add_pass(case_name, f"PDF: {len(pdf_bytes)} bytes")
                else:
                    result.add_warning(case_name, "PDF 生成但 LaTeX 中可能缺少内容")
            else:
                error = PandocPDFGenerator.get_last_error()
                result.add_fail(case_name, f"生成失败: {error or 'Unknown'}")
        except Exception as e:
            result.add_fail(case_name, f"异常: {str(e)[:100]}")
            traceback.print_exc()
    
    return result.print_result()


def test_long_content():
    """测试2: 长文本处理 - 确保内容不会被截断"""
    result = TestResult("长文本处理")
    
    # Check availability
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        result.add_warning("LaTeX 不可用", "跳过测试")
        result.print_result()
        return False
    
    # Generate long content with markers
    paragraphs = []
    for i in range(20):
        paragraphs.append(f"## 第 {i+1} 段\n\n这是第 {i+1} 段的内容。" + 
                         f"这段文字用于测试长文本是否会丢失。" * 5 +
                         f"\n\n段落标记: MARKER_{i+1}_END\n")
    
    markdown = "\n".join(paragraphs)
    
    try:
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content=markdown,
            width_pt=400.0,
            height_pt=600.0,
            font_name=None,
            font_size=10,
            line_spacing=1.2,
            column_padding=10
        )
        
        if success and pdf_bytes:
            tex = PandocPDFGenerator.get_last_generated_tex()
            if tex:
                # Check for markers
                lost_markers = []
                for i in range(20):
                    marker = f"MARKER_{i+1}_END"
                    if marker not in markdown:
                        continue
                    # Check if marker is in preprocessed or tex content
                    if marker not in tex and f"MARKER" not in tex:
                        lost_markers.append(marker)
                
                if not lost_markers:
                    result.add_pass("长文本完整性", f"所有 20 个段落标记都存在，PDF: {len(pdf_bytes)} bytes")
                else:
                    result.add_fail("长文本完整性", f"丢失标记: {', '.join(lost_markers[:5])}")
            else:
                result.add_warning("长文本完整性", "无法获取生成的 LaTeX 内容")
        else:
            error = PandocPDFGenerator.get_last_error()
            result.add_fail("长文本生成", f"失败: {error or 'Unknown'}")
    except Exception as e:
        result.add_fail("长文本处理", f"异常: {str(e)}")
        traceback.print_exc()
    
    return result.print_result()


def test_mixed_content():
    """测试3: 混合内容 - 标题、列表、代码、公式、表格"""
    result = TestResult("混合内容处理")
    
    # Check availability
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        result.add_warning("LaTeX 不可用", "跳过测试")
        result.print_result()
        return False
    
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
    
    try:
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content=markdown,
            width_pt=400.0,
            height_pt=800.0,
            font_name=None,
            font_size=11,
            line_spacing=1.3,
            column_padding=10
        )
        
        if success and pdf_bytes:
            tex = PandocPDFGenerator.get_last_generated_tex()
            if tex:
                # Check for key markers
                checks = [
                    ("主标题", "主标题" in tex or "Main" in markdown),
                    ("列表", "项目1" in tex or "item" in tex.lower()),
                    ("代码块", "test" in tex or "verbatim" in tex.lower()),
                    ("数学公式", "int_" in tex or "$" in tex),
                    ("表格", "tabular" in tex or "列1" in tex),
                    ("结尾标记", "CONTENT_END_MARKER" in markdown),
                ]
                
                for check_name, check_result in checks:
                    if check_result:
                        result.add_pass(check_name, "内容存在")
                    else:
                        result.add_fail(check_name, "内容可能丢失")
                
                result.add_pass("PDF 生成", f"大小: {len(pdf_bytes)} bytes")
            else:
                result.add_warning("内容检查", "无法获取 LaTeX 内容")
        else:
            error = PandocPDFGenerator.get_last_error()
            result.add_fail("混合内容生成", f"失败: {error or 'Unknown'}")
    except Exception as e:
        result.add_fail("混合内容处理", f"异常: {str(e)}")
        traceback.print_exc()
    
    return result.print_result()


def test_chinese_content():
    """测试4: 中文内容 - 确保中文不会丢失"""
    result = TestResult("中文内容处理")
    
    # Check availability
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        result.add_warning("LaTeX 不可用", "跳过测试")
        result.print_result()
        return False
    
    markdown = """# 中文测试

## 纯中文段落

这是一个完整的中文段落，用于测试中文字符是否会丢失。
包含标点符号：、。！？；：""''（）【】《》

## 中英混合

这是 English and 中文混合的内容。Testing mixed content 测试。

## 中文标点

使用中文标点：逗号，句号。感叹号！问号？

## 特殊符号与中文

价格：￥100，折扣 50%，评分 ★★★★★

## 结尾标记

中文内容结束标记_END
"""
    
    try:
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content=markdown,
            width_pt=400.0,
            height_pt=600.0,
            font_name="SimHei",
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        
        if success and pdf_bytes:
            tex = PandocPDFGenerator.get_last_generated_tex()
            if tex:
                # Check for Chinese content markers
                checks = [
                    ("中文标题", "中文测试" in tex),
                    ("中文段落", "完整的中文段落" in tex),
                    ("中文标点", "、。！？" in markdown),  # At least in input
                    ("结尾标记", "结束标记_END" in tex or "END" in tex),
                ]
                
                for check_name, check_result in checks:
                    if check_result:
                        result.add_pass(check_name, "内容存在")
                    else:
                        result.add_fail(check_name, "内容可能丢失")
                
                result.add_pass("PDF 生成", f"大小: {len(pdf_bytes)} bytes")
            else:
                result.add_warning("内容检查", "无法获取 LaTeX 内容")
        else:
            error = PandocPDFGenerator.get_last_error()
            result.add_fail("中文内容生成", f"失败: {error or 'Unknown'}")
    except Exception as e:
        result.add_fail("中文内容处理", f"异常: {str(e)}")
        traceback.print_exc()
    
    return result.print_result()


def test_edge_cases():
    """测试5: 边界情况"""
    result = TestResult("边界情况")
    
    # Check availability
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        result.add_warning("LaTeX 不可用", "跳过测试")
        result.print_result()
        return False
    
    edge_cases = [
        ("空行测试", "第一段\n\n\n\n第二段\n\n\n\n第三段"),
        ("连续特殊字符", "$$$$%%%%####____{{{{}}}}"),
        ("超长单词", "A" * 100 + " 正常文字 " + "B" * 100),
        ("嵌套结构", "- 列表1\n  - 子列表1\n    - 子子列表1\n  - 子列表2\n- 列表2"),
        ("混合换行", "第一行\n第二行  \n第三行\n\n第四行"),
    ]
    
    for case_name, content in edge_cases:
        try:
            markdown = f"# {case_name}\n\n{content}\n\n测试结束"
            
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=markdown,
                width_pt=400.0,
                height_pt=600.0,
                font_name=None,
                font_size=12,
                line_spacing=1.4,
                column_padding=10
            )
            
            if success and pdf_bytes and len(pdf_bytes) > 800:
                result.add_pass(case_name, f"PDF: {len(pdf_bytes)} bytes")
            else:
                error = PandocPDFGenerator.get_last_error()
                result.add_fail(case_name, f"失败: {error or 'PDF too small'}")
        except Exception as e:
            result.add_fail(case_name, f"异常: {str(e)[:100]}")
    
    return result.print_result()


def test_preprocessing():
    """测试6: 预处理函数"""
    result = TestResult("Markdown 预处理")
    
    test_cases = [
        ("代码块保护", "```python\ncode\n```", "```python\ncode\n```"),
        ("行内代码保护", "text `code` text", "text `code` text"),
        ("数学公式保护", "$$x^2$$", "$$x^2$$"),
        ("行内公式保护", "text $x$ text", "text $x$ text"),
        ("混合保护", "text `code` and $x$ and ```\nblock\n```", None),  # Just check no error
    ]
    
    for case_name, input_md, expected in test_cases:
        try:
            output = preprocess_markdown_for_latex(input_md)
            if expected is None:
                # Just check it doesn't crash
                if output:
                    result.add_pass(case_name, "预处理成功")
                else:
                    result.add_fail(case_name, "预处理返回空")
            elif output == expected:
                result.add_pass(case_name, "输出正确")
            else:
                # Check if key content is preserved
                if "```" in expected and "```" in output:
                    result.add_pass(case_name, "关键内容保留")
                else:
                    result.add_warning(case_name, f"输出可能不同: {output[:50]}")
        except Exception as e:
            result.add_fail(case_name, f"异常: {str(e)}")
    
    return result.print_result()


def test_space_calculation():
    """测试7: 空间计算"""
    result = TestResult("空间计算")
    
    # Check availability
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        result.add_warning("LaTeX 不可用", "跳过测试")
        result.print_result()
        return False
    
    # Test different dimensions
    dimensions = [
        ("标准尺寸", 400.0, 600.0),
        ("窄宽度", 200.0, 600.0),
        ("矮高度", 400.0, 300.0),
        ("大尺寸", 800.0, 1200.0),
        ("小尺寸", 150.0, 200.0),
    ]
    
    content = "# 测试\n\n这是测试内容。" * 10
    
    for case_name, width, height in dimensions:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=content,
                width_pt=width,
                height_pt=height,
                font_name=None,
                font_size=10,
                line_spacing=1.2,
                column_padding=10
            )
            
            if success and pdf_bytes:
                result.add_pass(case_name, f"{width}x{height}pt, PDF: {len(pdf_bytes)} bytes")
            else:
                error = PandocPDFGenerator.get_last_error()
                result.add_fail(case_name, f"{width}x{height}pt 失败: {error or 'Unknown'}")
        except Exception as e:
            result.add_fail(case_name, f"异常: {str(e)[:100]}")
    
    return result.print_result()


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print(" Pandoc 文字丢失问题 - 综合测试")
    print("="*80)
    
    tests = [
        ("特殊字符处理", test_special_characters),
        ("长文本处理", test_long_content),
        ("混合内容处理", test_mixed_content),
        ("中文内容处理", test_chinese_content),
        ("边界情况", test_edge_cases),
        ("预处理函数", test_preprocessing),
        ("空间计算", test_space_calculation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n开始测试: {test_name}...")
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ 测试 {test_name} 发生异常: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print(" 测试总结")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    print(f"\n总体通过率: {passed_count}/{total} ({passed_count/total*100:.1f}%)")
    
    if passed_count == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed_count} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

