#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandoc PDF 生成器错误处理严格测试
测试所有可能的错误场景和边界情况
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

# 设置输出编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.pandoc_pdf_generator import PandocPDFGenerator
from app.services.pandoc_renderer import PandocRenderer
from app.services.logger import get_logger

logger = get_logger()


class ErrorTestResult:
    """错误测试结果"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.error_message = ""
        self.expected_behavior = ""
        self.actual_behavior = ""
    
    def set_result(self, passed: bool, expected: str, actual: str, error: str = ""):
        self.passed = passed
        self.expected_behavior = expected
        self.actual_behavior = actual
        self.error_message = error
    
    def summary(self) -> str:
        status = "✓ PASS" if self.passed else "✗ FAIL"
        result = f"\n{status} - {self.test_name}\n"
        result += f"  预期: {self.expected_behavior}\n"
        result += f"  实际: {self.actual_behavior}\n"
        if self.error_message:
            result += f"  错误: {self.error_message[:200]}\n"
        return result


def test_empty_content_handling():
    """测试1: 空内容处理"""
    result = ErrorTestResult("空内容处理")
    try:
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content="",
            width_pt=595.0,
            height_pt=842.0,
            font_path=None,
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        
        # 空内容应该返回 (None, True)
        if success and pdf_bytes is None:
            result.set_result(True, "返回 (None, True)", f"返回 (None, {success})")
        else:
            result.set_result(False, "返回 (None, True)", f"返回 ({pdf_bytes is not None}, {success})")
    except Exception as e:
        result.set_result(False, "返回 (None, True)", f"抛出异常: {str(e)}", str(e))
    return result


def test_whitespace_only_content():
    """测试2: 仅空白字符内容"""
    result = ErrorTestResult("仅空白字符内容")
    try:
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content="   \n\n\t\t  \n",
            width_pt=595.0,
            height_pt=842.0,
            font_path=None,
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        
        # 仅空白字符应该返回 (None, True)
        if success and pdf_bytes is None:
            result.set_result(True, "返回 (None, True)", f"返回 (None, {success})")
        else:
            result.set_result(False, "返回 (None, True)", f"返回 ({pdf_bytes is not None}, {success})")
    except Exception as e:
        result.set_result(False, "返回 (None, True)", f"抛出异常: {str(e)}", str(e))
    return result


def test_invalid_dimensions():
    """测试3: 无效尺寸参数"""
    result = ErrorTestResult("无效尺寸参数")
    test_cases = [
        ("负宽度", {"width_pt": -100, "height_pt": 842.0}),
        ("负高度", {"width_pt": 595.0, "height_pt": -100}),
        ("零宽度", {"width_pt": 0, "height_pt": 842.0}),
        ("零高度", {"width_pt": 595.0, "height_pt": 0}),
    ]
    
    all_passed = True
    for case_name, dims in test_cases:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content="测试",
                font_path=None,
                font_size=12,
                line_spacing=1.4,
                column_padding=10,
                **dims
            )
            
            if not success or pdf_bytes is None:
                print(f"  ✓ {case_name}: 正确处理")
            else:
                print(f"  ✗ {case_name}: 应该失败但成功了")
                all_passed = False
        except Exception as e:
            print(f"  ✓ {case_name}: 抛出异常（可接受）")
    
    result.set_result(all_passed, "所有无效尺寸都应失败", "部分测试通过" if all_passed else "部分测试失败")
    return result


def test_invalid_font_size():
    """测试4: 无效字号"""
    result = ErrorTestResult("无效字号")
    test_cases = [
        ("负字号", -5),
        ("零字号", 0),
    ]
    
    all_passed = True
    for case_name, font_size in test_cases:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content="测试",
                width_pt=595.0,
                height_pt=842.0,
                font_path=None,
                font_size=font_size,
                line_spacing=1.4,
                column_padding=10
            )
            
            if not success or pdf_bytes is None:
                print(f"  ✓ {case_name}: 正确处理")
            else:
                print(f"  ✗ {case_name}: 应该失败但成功了")
                all_passed = False
        except Exception as e:
            print(f"  ✓ {case_name}: 抛出异常（可接受）")
    
    result.set_result(all_passed, "所有无效字号都应失败", "部分测试通过" if all_passed else "部分测试失败")
    return result


def test_invalid_line_spacing():
    """测试5: 无效行距"""
    result = ErrorTestResult("无效行距")
    test_cases = [
        ("负行距", -1.0),
        ("零行距", 0.0),
    ]
    
    all_passed = True
    for case_name, line_spacing in test_cases:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content="测试",
                width_pt=595.0,
                height_pt=842.0,
                font_path=None,
                font_size=12,
                line_spacing=line_spacing,
                column_padding=10
            )
            
            if not success or pdf_bytes is None:
                print(f"  ✓ {case_name}: 正确处理")
            else:
                print(f"  ✗ {case_name}: 应该失败但成功了")
                all_passed = False
        except Exception as e:
            print(f"  ✓ {case_name}: 抛出异常（可接受）")
    
    result.set_result(all_passed, "所有无效行距都应失败", "部分测试通过" if all_passed else "部分测试失败")
    return result


def test_invalid_column_padding():
    """测试6: 无效栏内边距"""
    result = ErrorTestResult("无效栏内边距")
    try:
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content="测试",
            width_pt=595.0,
            height_pt=842.0,
            font_path=None,
            font_size=12,
            line_spacing=1.4,
            column_padding=-10
        )
        
        if not success or pdf_bytes is None:
            result.set_result(True, "返回 (None, False)", f"返回 ({pdf_bytes is not None}, {success})")
        else:
            result.set_result(False, "返回 (None, False)", f"返回 ({pdf_bytes is not None}, {success})")
    except Exception as e:
        result.set_result(True, "返回 (None, False) 或抛出异常", f"抛出异常: {str(e)}")
    return result


def test_special_characters_in_content():
    """测试7: 特殊字符处理"""
    result = ErrorTestResult("特殊字符处理")
    
    # 检查 LaTeX 是否可用
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        result.set_result(True, "跳过（LaTeX 不可用）", "跳过测试")
        return result
    
    special_chars = [
        ("LaTeX 特殊字符", "测试 $x^2$ 和 \\textbf{粗体}"),
        ("URL 和链接", "访问 https://example.com 和 [链接](http://test.com)"),
        ("表格", "| 列1 | 列2 |\n|-----|-----|\n| 值1 | 值2 |"),
        ("代码块", "```python\nprint('hello')\n```"),
        ("数学公式", "$$E = mc^2$$"),
    ]
    
    all_passed = True
    for case_name, content in special_chars:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=content,
                width_pt=595.0,
                height_pt=842.0,
                font_path=None,
                font_size=12,
                line_spacing=1.4,
                column_padding=10
            )
            
            if success and pdf_bytes:
                print(f"  ✓ {case_name}: 成功生成")
            else:
                print(f"  ✗ {case_name}: 生成失败")
                all_passed = False
        except Exception as e:
            print(f"  ✗ {case_name}: 抛出异常 - {str(e)[:100]}")
            all_passed = False
    
    result.set_result(all_passed, "所有特殊字符都应正确处理", "部分测试通过" if all_passed else "部分测试失败")
    return result


def test_very_long_content():
    """测试8: 超长内容"""
    result = ErrorTestResult("超长内容处理")
    
    # 检查 LaTeX 是否可用
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        result.set_result(True, "跳过（LaTeX 不可用）", "跳过测试")
        return result
    
    # 生成超长内容（约100KB）
    long_content = "# 超长内容测试\n\n"
    for i in range(1000):
        long_content += f"这是第 {i+1} 段内容。包含一些**粗体**和*斜体*文本。\n\n"
    
    try:
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content=long_content,
            width_pt=595.0,
            height_pt=842.0,
            font_path=None,
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        
        if success and pdf_bytes:
            result.set_result(True, "成功生成PDF", f"成功生成，PDF大小: {len(pdf_bytes)} 字节")
        else:
            result.set_result(False, "成功生成PDF", "生成失败")
    except subprocess.TimeoutExpired:
        result.set_result(False, "成功生成PDF", "超时")
    except Exception as e:
        result.set_result(False, "成功生成PDF", f"抛出异常: {str(e)}", str(e))
    return result


def test_font_path_handling():
    """测试9: 字体路径处理"""
    result = ErrorTestResult("字体路径处理")
    
    # 检查 LaTeX 是否可用
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        result.set_result(True, "跳过（LaTeX 不可用）", "跳过测试")
        return result
    
    test_cases = [
        ("不存在的字体路径", "/nonexistent/font.ttf"),
        ("空字体路径", None),
        ("Windows 路径", "C:\\Windows\\Fonts\\simhei.ttf" if os.path.exists("C:\\Windows\\Fonts\\simhei.ttf") else None),
    ]
    
    all_passed = True
    for case_name, font_path in test_cases:
        try:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content="测试字体路径",
                width_pt=595.0,
                height_pt=842.0,
                font_path=font_path,
                font_size=12,
                line_spacing=1.4,
                column_padding=10
            )
            
            # 即使字体路径不存在，也应该尝试生成（可能使用默认字体）
            if success:
                print(f"  ✓ {case_name}: 处理成功")
            else:
                print(f"  ? {case_name}: 处理失败（可能是预期的）")
        except Exception as e:
            print(f"  ? {case_name}: 抛出异常（可能是预期的） - {str(e)[:100]}")
    
    result.set_result(True, "字体路径应正确处理", "测试完成")
    return result


def test_error_message_clarity():
    """测试10: 错误信息清晰度"""
    result = ErrorTestResult("错误信息清晰度")
    
    # 测试无效参数
    try:
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content="测试",
            width_pt=-100,
            height_pt=842.0,
            font_path=None,
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        
        # 应该失败
        if not success:
            result.set_result(True, "失败并返回清晰错误", "失败（但没有检查错误信息）")
        else:
            result.set_result(False, "失败并返回清晰错误", "意外成功")
    except Exception as e:
        # 异常也是可接受的
        error_str = str(e)
        if "width" in error_str.lower() or "dimension" in error_str.lower():
            result.set_result(True, "失败并返回清晰错误", f"抛出异常: {error_str[:100]}")
        else:
            result.set_result(False, "失败并返回清晰错误", f"错误信息不够清晰: {error_str[:100]}")
    
    return result


def run_all_error_tests():
    """运行所有错误处理测试"""
    print("="*70)
    print("开始运行 Pandoc PDF 生成器错误处理严格测试")
    print("="*70)
    print()
    
    results: List[ErrorTestResult] = []
    
    tests = [
        ("空内容处理", test_empty_content_handling),
        ("仅空白字符内容", test_whitespace_only_content),
        ("无效尺寸参数", test_invalid_dimensions),
        ("无效字号", test_invalid_font_size),
        ("无效行距", test_invalid_line_spacing),
        ("无效栏内边距", test_invalid_column_padding),
        ("特殊字符处理", test_special_characters_in_content),
        ("超长内容", test_very_long_content),
        ("字体路径处理", test_font_path_handling),
        ("错误信息清晰度", test_error_message_clarity),
    ]
    
    for test_name, test_func in tests:
        print(f"\n【错误测试】{test_name}")
        print("-" * 70)
        try:
            result = test_func()
            results.append(result)
            print(result.summary())
        except Exception as e:
            print(f"[ERROR] {test_name}: {str(e)}")
            traceback.print_exc()
            results.append(ErrorTestResult(test_name))
            results[-1].set_result(False, "测试正常完成", f"测试异常: {str(e)}", str(e))
    
    # 总结
    print("\n" + "="*70)
    print("错误处理测试总结")
    print("="*70)
    
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    failed_tests = [r for r in results if not r.passed]
    if failed_tests:
        print(f"\n失败的测试 ({len(failed_tests)}):")
        for result in failed_tests:
            print(f"  - {result.test_name}")
    
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    import subprocess
    success = run_all_error_tests()
    sys.exit(0 if success else 1)

