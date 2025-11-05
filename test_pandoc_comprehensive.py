#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最严格全面的 Pandoc PDF 生成器测试
测试所有场景、边界情况和错误处理
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path
import fitz

# 设置输出编码
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

sys.path.insert(0, str(Path(__file__).parent))

from app.services.pandoc_pdf_generator import PandocPDFGenerator
from app.services.pandoc_renderer import PandocRenderer
from app.services.logger import get_logger

logger = get_logger()


class ComprehensiveTestResult:
    """综合测试结果类"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.warnings = []
    
    def add_pass(self, test_name: str, details: str = ""):
        self.passed += 1
        msg = f"[PASS] {test_name}"
        if details:
            msg += f": {details}"
        print(msg)
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"[FAIL] {test_name}: {error}")
    
    def add_warning(self, test_name: str, warning: str):
        self.warnings.append((test_name, warning))
        print(f"[WARN] {test_name}: {warning}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*70}")
        print(f"综合测试总结: {self.passed}/{total} 通过, {self.failed}/{total} 失败")
        if self.warnings:
            print(f"\n警告 ({len(self.warnings)} 项):")
            for test_name, warning in self.warnings:
                print(f"  - {test_name}: {warning}")
        if self.errors:
            print(f"\n失败详情 ({len(self.errors)} 项):")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        print(f"{'='*70}")
        return self.failed == 0


def test_font_path_absolute():
    """测试1: 字体路径必须为绝对路径"""
    result = ComprehensiveTestResult()
    try:
        # 测试相对路径
        relative_path = "assets/fonts/SIMHEI.TTF"
        if os.path.exists(relative_path):
            # 检查模板中是否转换为绝对路径
            template = PandocPDFGenerator._create_latex_template(
                595.0, 842.0, relative_path, 12, 1.4, 10
            )
            
            # 提取路径
            import re
            path_match = re.search(r'Path=([^,}]+)', template)
            if path_match:
                latex_path = path_match.group(1).strip('{}')
                is_absolute = os.path.isabs(latex_path)
                
                if is_absolute:
                    result.add_pass("字体路径转换", "相对路径已转换为绝对路径")
                else:
                    result.add_fail("字体路径转换", f"路径仍为相对路径: {latex_path}")
            else:
                result.add_fail("字体路径转换", "未找到路径配置")
        else:
            result.add_warning("字体路径转换", "字体文件不存在，跳过测试")
            
    except Exception as e:
        result.add_fail("字体路径转换", f"异常: {str(e)}")
    return result


def test_chinese_content_verification():
    """测试2: 中文内容验证（生成后检查）"""
    result = ComprehensiveTestResult()
    try:
        latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
        if not latex_available:
            result.add_warning("中文内容验证", "LaTeX 不可用，跳过")
            return result
        
        test_cases = [
            ("简单中文", "这是测试文本。"),
            ("中文+英文", "这是测试文本。This is test text."),
            ("中文+数学", "公式：$E = mc^2$"),
            ("中文+代码", "代码：\n```python\nprint('hello')\n```"),
            ("长中文", "这是" * 100 + "一段很长的中文文本。" * 50),
        ]
        
        font_path = os.path.abspath("assets/fonts/SIMHEI.TTF") if os.path.exists("assets/fonts/SIMHEI.TTF") else None
        
        for case_name, content in test_cases:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=f"# {case_name}\n\n{content}",
                width_pt=595.0,
                height_pt=842.0,
                font_path=font_path,
                font_size=12,
                line_spacing=1.4,
                column_padding=10
            )
            
            if success and pdf_bytes:
                # 验证 PDF 内容
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                
                # 检查是否包含中文
                has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
                if has_chinese:
                    result.add_pass(f"中文内容验证: {case_name}", f"包含中文，提取文本长度: {len(text)}")
                else:
                    result.add_fail(f"中文内容验证: {case_name}", "PDF 不包含中文内容")
            else:
                result.add_fail(f"中文内容验证: {case_name}", f"生成失败: {success}")
                
    except Exception as e:
        result.add_fail("中文内容验证", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def test_template_robustness():
    """测试3: 模板健壮性（各种边界情况）"""
    result = ComprehensiveTestResult()
    try:
        test_cases = [
            ("最小尺寸", {"width_pt": 100.0, "height_pt": 100.0}),
            ("最大尺寸", {"width_pt": 5000.0, "height_pt": 5000.0}),
            ("极小字号", {"font_size": 6}),
            ("极大字号", {"font_size": 24}),
            ("极小行距", {"line_spacing": 0.5}),
            ("极大行距", {"line_spacing": 3.0}),
            ("零内边距", {"column_padding": 0}),
            ("大内边距", {"column_padding": 50}),
        ]
        
        base_params = {
            "width_pt": 595.0,
            "height_pt": 842.0,
            "font_path": None,
            "font_size": 12,
            "line_spacing": 1.4,
            "column_padding": 10
        }
        
        for case_name, overrides in test_cases:
            params = {**base_params, **overrides}
            try:
                template = PandocPDFGenerator._create_latex_template(**params)
                # 检查模板基本结构
                if "\\documentclass" in template and "$body$" in template:
                    result.add_pass(f"模板健壮性: {case_name}", f"参数: {overrides}")
                else:
                    result.add_fail(f"模板健壮性: {case_name}", "模板结构不完整")
            except Exception as e:
                result.add_fail(f"模板健壮性: {case_name}", f"异常: {str(e)}")
                
    except Exception as e:
        result.add_fail("模板健壮性", f"异常: {str(e)}")
    return result


def test_error_recovery():
    """测试4: 错误恢复机制"""
    result = ComprehensiveTestResult()
    try:
        # 测试无效参数
        invalid_cases = [
            ("负宽度", {"width_pt": -100, "height_pt": 842.0}),
            ("负高度", {"width_pt": 595.0, "height_pt": -100}),
            ("零宽度", {"width_pt": 0, "height_pt": 842.0}),
            ("零高度", {"width_pt": 595.0, "height_pt": 0}),
            ("负字号", {"font_size": -5}),
            ("零字号", {"font_size": 0}),
            ("负行距", {"line_spacing": -1.0}),
            ("零行距", {"line_spacing": 0}),
            ("负内边距", {"column_padding": -10}),
        ]
        
        base_params = {
            "markdown_content": "测试",
            "width_pt": 595.0,
            "height_pt": 842.0,
            "font_path": None,
            "font_size": 12,
            "line_spacing": 1.4,
            "column_padding": 10
        }
        
        for case_name, overrides in invalid_cases:
            params = {**base_params, **overrides}
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(**params)
            
            # 应该失败或返回 None
            if not success or pdf_bytes is None:
                result.add_pass(f"错误恢复: {case_name}", "正确处理了无效参数")
            else:
                result.add_fail(f"错误恢复: {case_name}", "应该失败但成功了")
                
    except Exception as e:
        result.add_fail("错误恢复", f"异常: {str(e)}")
    return result


def test_special_characters():
    """测试5: 特殊字符处理"""
    result = ComprehensiveTestResult()
    try:
        latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
        if not latex_available:
            result.add_warning("特殊字符处理", "LaTeX 不可用，跳过")
            return result
        
        special_cases = [
            ("数学公式", "$E = mc^2$ 和 $$\\int_0^1 x^2 dx$$"),
            ("代码块", "```python\nprint('hello')\n```"),
            ("表格", "| 列1 | 列2 |\n|-----|-----|\n| 数据 | 数据 |"),
            ("链接", "[链接](https://example.com)"),
            ("引用", "> 这是引用文本"),
            ("列表", "- 项目1\n- 项目2\n- 项目3"),
        ]
        
        font_path = os.path.abspath("assets/fonts/SIMHEI.TTF") if os.path.exists("assets/fonts/SIMHEI.TTF") else None
        
        for case_name, content in special_cases:
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=f"# {case_name}\n\n{content}",
                width_pt=595.0,
                height_pt=842.0,
                font_path=font_path,
                font_size=12,
                line_spacing=1.4,
                column_padding=10
            )
            
            if success and pdf_bytes:
                result.add_pass(f"特殊字符: {case_name}", f"PDF大小: {len(pdf_bytes)} bytes")
            else:
                result.add_fail(f"特殊字符: {case_name}", f"生成失败: {success}")
                
    except Exception as e:
        result.add_fail("特殊字符处理", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def test_multipage_handling():
    """测试6: 多页处理"""
    result = ComprehensiveTestResult()
    try:
        latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
        if not latex_available:
            result.add_warning("多页处理", "LaTeX 不可用，跳过")
            return result
        
        # 生成足够长的内容
        long_content = "# 长内容测试\n\n"
        for i in range(100):
            long_content += f"## 章节 {i+1}\n\n"
            long_content += f"这是第 {i+1} 个章节的内容。" * 5 + "\n\n"
        
        font_path = os.path.abspath("assets/fonts/SIMHEI.TTF") if os.path.exists("assets/fonts/SIMHEI.TTF") else None
        
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content=long_content,
            width_pt=595.0,
            height_pt=842.0,
            font_path=font_path,
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        
        if success and pdf_bytes:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = doc.page_count
            doc.close()
            
            if page_count > 1:
                result.add_pass("多页处理", f"成功生成 {page_count} 页")
            else:
                result.add_fail("多页处理", f"预期多页，实际 {page_count} 页")
        else:
            result.add_fail("多页处理", f"生成失败: {success}")
            
    except Exception as e:
        result.add_fail("多页处理", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def test_font_path_edge_cases():
    """测试7: 字体路径边界情况"""
    result = ComprehensiveTestResult()
    try:
        test_paths = [
            ("相对路径", "assets/fonts/SIMHEI.TTF"),
            ("绝对路径", os.path.abspath("assets/fonts/SIMHEI.TTF") if os.path.exists("assets/fonts/SIMHEI.TTF") else None),
            ("包含空格", "C:/Program Files/Fonts/arial.ttf"),
            ("不存在的路径", "nonexistent/font.ttf"),
            ("None", None),
            ("空字符串", ""),
        ]
        
        for case_name, font_path in test_paths:
            if font_path == "":
                font_path = None
            if font_path and not os.path.exists(font_path):
                result.add_warning(f"字体路径: {case_name}", "路径不存在，跳过")
                continue
                
            try:
                template = PandocPDFGenerator._create_latex_template(
                    595.0, 842.0, font_path, 12, 1.4, 10
                )
                
                if "\\setCJKmainfont" in template:
                    result.add_pass(f"字体路径: {case_name}", "模板生成成功")
                else:
                    result.add_fail(f"字体路径: {case_name}", "模板缺少字体设置")
            except Exception as e:
                result.add_fail(f"字体路径: {case_name}", f"异常: {str(e)}")
                
    except Exception as e:
        result.add_fail("字体路径边界情况", f"异常: {str(e)}")
    return result


def test_concurrent_generation():
    """测试8: 并发生成（连续多次调用）"""
    result = ComprehensiveTestResult()
    try:
        latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
        if not latex_available:
            result.add_warning("并发生成", "LaTeX 不可用，跳过")
            return result
        
        font_path = "assets/fonts/SIMHEI.TTF" if os.path.exists("assets/fonts/SIMHEI.TTF") else None
        
        success_count = 0
        for i in range(5):
            pdf_bytes, success = PandocPDFGenerator.generate_pdf(
                markdown_content=f"# 测试 {i+1}\n\n这是第 {i+1} 次测试。",
                width_pt=595.0,
                height_pt=842.0,
                font_path=font_path,
                font_size=12,
                line_spacing=1.4,
                column_padding=10
            )
            
            if success and pdf_bytes:
                success_count += 1
        
        if success_count == 5:
            result.add_pass("并发生成", f"5/5 次成功")
        else:
            result.add_fail("并发生成", f"只有 {success_count}/5 次成功")
            
    except Exception as e:
        result.add_fail("并发生成", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def run_comprehensive_tests():
    """运行所有综合测试"""
    print("="*70)
    print("开始运行最严格全面的 Pandoc PDF 生成器测试")
    print("="*70)
    print()
    
    all_results = ComprehensiveTestResult()
    
    tests = [
        ("字体路径绝对路径", test_font_path_absolute),
        ("中文内容验证", test_chinese_content_verification),
        ("模板健壮性", test_template_robustness),
        ("错误恢复机制", test_error_recovery),
        ("特殊字符处理", test_special_characters),
        ("多页处理", test_multipage_handling),
        ("字体路径边界情况", test_font_path_edge_cases),
        ("并发生成", test_concurrent_generation),
    ]
    
    for test_name, test_func in tests:
        print(f"\n【测试】{test_name}")
        print("-" * 70)
        try:
            result = test_func()
            all_results.passed += result.passed
            all_results.failed += result.failed
            all_results.warnings.extend(result.warnings)
            all_results.errors.extend(result.errors)
        except Exception as e:
            all_results.failed += 1
            all_results.errors.append((test_name, f"测试函数异常: {str(e)}"))
            print(f"[FAIL] {test_name}: 测试函数异常: {str(e)}")
            traceback.print_exc()
    
    print()
    return all_results.summary()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)

