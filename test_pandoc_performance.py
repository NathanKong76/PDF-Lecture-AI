#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandoc PDF 生成器性能测试
测试所有性能优化和潜在问题
"""

import os
import sys
import time
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


class PerformanceTestResult:
    """性能测试结果"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.times: List[float] = []
        self.success_count = 0
        self.fail_count = 0
        self.errors: List[str] = []
        self.avg_time: float = 0.0
        self.min_time: float = 0.0
        self.max_time: float = 0.0
    
    def add_result(self, elapsed: float, success: bool, error: str = ""):
        if success:
            self.times.append(elapsed)
            self.success_count += 1
        else:
            self.fail_count += 1
            if error:
                self.errors.append(error)
    
    def calculate_stats(self):
        if self.times:
            self.avg_time = sum(self.times) / len(self.times)
            self.min_time = min(self.times)
            self.max_time = max(self.times)
    
    def summary(self) -> str:
        self.calculate_stats()
        result = f"\n{'='*70}\n"
        result += f"测试: {self.test_name}\n"
        result += f"成功: {self.success_count}, 失败: {self.fail_count}\n"
        if self.times:
            result += f"平均时间: {self.avg_time:.2f}秒\n"
            result += f"最短时间: {self.min_time:.2f}秒\n"
            result += f"最长时间: {self.max_time:.2f}秒\n"
        if self.errors:
            result += f"错误: {len(self.errors)} 个\n"
            for i, error in enumerate(self.errors[:3], 1):  # 只显示前3个错误
                result += f"  错误 {i}: {error[:100]}\n"
        result += f"{'='*70}\n"
        return result


def test_tool_availability_check_performance():
    """测试1: 工具可用性检查性能（应该使用缓存）"""
    result = PerformanceTestResult("工具可用性检查性能")
    
    # 第一次检查（应该执行实际检查）
    start = time.time()
    pandoc_avail, _ = PandocRenderer.check_pandoc_available()
    elapsed1 = time.time() - start
    
    # 第二次检查（应该使用缓存）
    start = time.time()
    pandoc_avail2, _ = PandocRenderer.check_pandoc_available()
    elapsed2 = time.time() - start
    
    # 第三次检查（应该使用缓存）
    start = time.time()
    latex_avail, _ = PandocPDFGenerator.check_latex_engine_available()
    elapsed3 = time.time() - start
    
    # 第四次检查（应该使用缓存）
    start = time.time()
    latex_avail2, _ = PandocPDFGenerator.check_latex_engine_available()
    elapsed4 = time.time() - start
    
    print(f"第一次 Pandoc 检查: {elapsed1:.3f}秒")
    print(f"第二次 Pandoc 检查: {elapsed2:.3f}秒 (应使用缓存)")
    print(f"第一次 XeLaTeX 检查: {elapsed3:.3f}秒")
    print(f"第二次 XeLaTeX 检查: {elapsed4:.3f}秒 (应使用缓存)")
    
    # 验证缓存是否生效（第二次应该明显更快）
    if elapsed2 < elapsed1 * 0.5:  # 缓存应该至少快50%
        result.add_result(elapsed2, True)
        print("✓ Pandoc 缓存生效")
    else:
        result.add_result(elapsed2, False, "Pandoc 缓存未生效")
        print("✗ Pandoc 缓存可能未生效")
    
    if elapsed4 < elapsed3 * 0.5:
        result.add_result(elapsed4, True)
        print("✓ XeLaTeX 缓存生效")
    else:
        result.add_result(elapsed4, False, "XeLaTeX 缓存未生效")
        print("✗ XeLaTeX 缓存可能未生效")
    
    return result


def test_template_cache_performance():
    """测试2: 模板缓存性能"""
    result = PerformanceTestResult("模板缓存性能")
    
    params = {
        "width_pt": 595.0,
        "height_pt": 842.0,
        "font_path": None,
        "font_size": 12,
        "line_spacing": 1.4,
        "column_padding": 10
    }
    
    # 第一次生成模板（应该创建）
    start = time.time()
    template1 = PandocPDFGenerator._create_latex_template(**params)
    elapsed1 = time.time() - start
    
    # 第二次生成模板（应该使用缓存）
    start = time.time()
    template2 = PandocPDFGenerator._create_latex_template(**params)
    elapsed2 = time.time() - start
    
    print(f"第一次模板生成: {elapsed1:.3f}秒")
    print(f"第二次模板生成: {elapsed2:.3f}秒 (应使用缓存)")
    
    # 验证模板内容相同
    if template1 == template2:
        result.add_result(elapsed1, True)
        print("✓ 模板内容一致")
    else:
        result.add_result(elapsed1, False, "模板内容不一致")
        print("✗ 模板内容不一致")
    
    # 验证缓存是否生效（第二次应该明显更快）
    if elapsed2 < elapsed1 * 0.1:  # 缓存应该至少快90%
        result.add_result(elapsed2, True)
        print("✓ 模板缓存生效")
    else:
        result.add_result(elapsed2, False, "模板缓存未生效")
        print("✗ 模板缓存可能未生效")
    
    return result


def test_small_content_performance():
    """测试3: 小内容生成性能"""
    result = PerformanceTestResult("小内容生成性能")
    
    # 检查 LaTeX 是否可用
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        print("跳过: LaTeX 引擎不可用")
        return result
    
    markdown_content = "这是测试文本。\n\n包含**粗体**和*斜体*。"
    
    # 运行5次测试
    for i in range(5):
        start = time.time()
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content=markdown_content,
            width_pt=595.0,
            height_pt=842.0,
            font_path=None,
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        elapsed = time.time() - start
        
        if success and pdf_bytes:
            result.add_result(elapsed, True)
            print(f"  测试 {i+1}: {elapsed:.2f}秒, PDF大小: {len(pdf_bytes)}字节")
        else:
            result.add_result(elapsed, False, f"生成失败")
            print(f"  测试 {i+1}: {elapsed:.2f}秒, 失败")
    
    return result


def test_medium_content_performance():
    """测试4: 中等内容生成性能"""
    result = PerformanceTestResult("中等内容生成性能")
    
    # 检查 LaTeX 是否可用
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        print("跳过: LaTeX 引擎不可用")
        return result
    
    # 生成中等长度的内容（约5KB）
    markdown_content = "# 测试标题\n\n"
    for i in range(50):
        markdown_content += f"## 章节 {i+1}\n\n"
        markdown_content += f"这是第 {i+1} 个章节的内容。包含一些**粗体**和*斜体*文本。" * 5 + "\n\n"
    
    # 运行3次测试
    for i in range(3):
        start = time.time()
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content=markdown_content,
            width_pt=595.0,
            height_pt=842.0,
            font_path=None,
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        elapsed = time.time() - start
        
        if success and pdf_bytes:
            result.add_result(elapsed, True)
            print(f"  测试 {i+1}: {elapsed:.2f}秒, PDF大小: {len(pdf_bytes)}字节")
        else:
            result.add_result(elapsed, False, f"生成失败")
            print(f"  测试 {i+1}: {elapsed:.2f}秒, 失败")
    
    return result


def test_large_content_performance():
    """测试5: 大内容生成性能"""
    result = PerformanceTestResult("大内容生成性能")
    
    # 检查 LaTeX 是否可用
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        print("跳过: LaTeX 引擎不可用")
        return result
    
    # 生成大长度的内容（约50KB）
    markdown_content = "# 大内容测试\n\n"
    for i in range(500):
        markdown_content += f"## 章节 {i+1}\n\n"
        markdown_content += f"这是第 {i+1} 个章节的内容。" * 10 + "\n\n"
    
    # 运行2次测试
    for i in range(2):
        start = time.time()
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content=markdown_content,
            width_pt=595.0,
            height_pt=842.0,
            font_path=None,
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        elapsed = time.time() - start
        
        if success and pdf_bytes:
            result.add_result(elapsed, True)
            print(f"  测试 {i+1}: {elapsed:.2f}秒, PDF大小: {len(pdf_bytes)}字节")
        else:
            result.add_result(elapsed, False, f"生成失败")
            print(f"  测试 {i+1}: {elapsed:.2f}秒, 失败")
    
    return result


def test_concurrent_generation_performance():
    """测试6: 并发生成性能（模拟批量处理）"""
    result = PerformanceTestResult("并发生成性能")
    
    # 检查 LaTeX 是否可用
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        print("跳过: LaTeX 引擎不可用")
        return result
    
    # 准备10个不同的内容
    test_contents = []
    for i in range(10):
        content = f"# 文档 {i+1}\n\n这是第 {i+1} 个文档的内容。\n\n" * 10
        test_contents.append(content)
    
    # 顺序生成（模拟批量处理）
    start = time.time()
    success_count = 0
    for i, content in enumerate(test_contents):
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
            success_count += 1
            print(f"  文档 {i+1}: 成功, PDF大小: {len(pdf_bytes)}字节")
        else:
            print(f"  文档 {i+1}: 失败")
    
    elapsed = time.time() - start
    
    result.add_result(elapsed, success_count == len(test_contents))
    print(f"总时间: {elapsed:.2f}秒, 成功: {success_count}/{len(test_contents)}")
    print(f"平均每个文档: {elapsed/len(test_contents):.2f}秒")
    
    return result


def test_different_parameters_performance():
    """测试7: 不同参数组合性能"""
    result = PerformanceTestResult("不同参数组合性能")
    
    # 检查 LaTeX 是否可用
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        print("跳过: LaTeX 引擎不可用")
        return result
    
    markdown_content = "测试不同参数组合。" * 20
    
    test_cases = [
        {"font_size": 10, "line_spacing": 1.2},
        {"font_size": 12, "line_spacing": 1.4},
        {"font_size": 14, "line_spacing": 1.6},
        {"font_size": 16, "line_spacing": 2.0},
    ]
    
    for i, params in enumerate(test_cases):
        start = time.time()
        pdf_bytes, success = PandocPDFGenerator.generate_pdf(
            markdown_content=markdown_content,
            width_pt=595.0,
            height_pt=842.0,
            font_path=None,
            **params,
            column_padding=10
        )
        elapsed = time.time() - start
        
        if success and pdf_bytes:
            result.add_result(elapsed, True)
            print(f"  参数组合 {i+1}: {elapsed:.2f}秒, PDF大小: {len(pdf_bytes)}字节")
        else:
            result.add_result(elapsed, False, f"生成失败")
            print(f"  参数组合 {i+1}: {elapsed:.2f}秒, 失败")
    
    return result


def test_timeout_behavior():
    """测试8: 超时行为（验证动态超时设置）"""
    result = PerformanceTestResult("超时行为")
    
    # 检查 LaTeX 是否可用
    latex_available, _ = PandocPDFGenerator.check_latex_engine_available()
    if not latex_available:
        print("跳过: LaTeX 引擎不可用")
        return result
    
    # 测试小内容（应该快速完成）
    small_content = "小内容测试"
    start = time.time()
    pdf_bytes, success = PandocPDFGenerator.generate_pdf(
        markdown_content=small_content,
        width_pt=595.0,
        height_pt=842.0,
        font_path=None,
        font_size=12,
        line_spacing=1.4,
        column_padding=10
    )
    elapsed_small = time.time() - start
    
    # 测试大内容（应该使用更长的超时）
    large_content = "# 大内容\n\n" + "这是大内容测试。\n\n" * 1000
    start = time.time()
    pdf_bytes2, success2 = PandocPDFGenerator.generate_pdf(
        markdown_content=large_content,
        width_pt=595.0,
        height_pt=842.0,
        font_path=None,
        font_size=12,
        line_spacing=1.4,
        column_padding=10
    )
    elapsed_large = time.time() - start
    
    print(f"小内容生成时间: {elapsed_small:.2f}秒")
    print(f"大内容生成时间: {elapsed_large:.2f}秒")
    
    if success and success2:
        result.add_result(elapsed_small, True)
        result.add_result(elapsed_large, True)
        print("✓ 超时设置正常")
    else:
        result.add_result(elapsed_small, False, "小内容生成失败")
        result.add_result(elapsed_large, False, "大内容生成失败")
        print("✗ 生成失败")
    
    return result


def run_all_performance_tests():
    """运行所有性能测试"""
    print("="*70)
    print("开始运行 Pandoc PDF 生成器性能测试")
    print("="*70)
    print()
    
    all_results: List[PerformanceTestResult] = []
    
    tests = [
        ("工具可用性检查性能", test_tool_availability_check_performance),
        ("模板缓存性能", test_template_cache_performance),
        ("小内容生成性能", test_small_content_performance),
        ("中等内容生成性能", test_medium_content_performance),
        ("大内容生成性能", test_large_content_performance),
        ("并发生成性能", test_concurrent_generation_performance),
        ("不同参数组合性能", test_different_parameters_performance),
        ("超时行为", test_timeout_behavior),
    ]
    
    for test_name, test_func in tests:
        print(f"\n【性能测试】{test_name}")
        print("-" * 70)
        try:
            result = test_func()
            all_results.append(result)
            print(result.summary())
        except Exception as e:
            print(f"[ERROR] {test_name}: {str(e)}")
            traceback.print_exc()
    
    # 总结
    print("\n" + "="*70)
    print("性能测试总结")
    print("="*70)
    
    total_tests = 0
    total_success = 0
    total_fail = 0
    
    for result in all_results:
        result.calculate_stats()
        total_tests += result.success_count + result.fail_count
        total_success += result.success_count
        total_fail += result.fail_count
        
        print(f"\n{result.test_name}:")
        print(f"  成功: {result.success_count}, 失败: {result.fail_count}")
        if result.times:
            print(f"  平均时间: {result.avg_time:.2f}秒")
            print(f"  时间范围: {result.min_time:.2f}秒 - {result.max_time:.2f}秒")
    
    print(f"\n总计: {total_success}/{total_tests} 成功, {total_fail}/{total_tests} 失败")
    print("="*70)
    
    return total_fail == 0


if __name__ == "__main__":
    success = run_all_performance_tests()
    sys.exit(0 if success else 1)

