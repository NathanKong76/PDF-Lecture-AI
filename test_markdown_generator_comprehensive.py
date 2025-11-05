#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最严格全面的 Markdown 生成器测试
测试所有场景、边界情况和错误处理
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path
import base64

# 设置输出编码
if sys.platform == 'win32':
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

sys.path.insert(0, str(Path(__file__).parent))

from app.services.markdown_generator import (
    create_page_screenshot_markdown,
    generate_markdown_with_screenshots
)
from app.services.pdf_composer import _page_png_bytes
import fitz


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


def create_test_pdf() -> bytes:
    """创建测试 PDF"""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Test PDF Page 1", fontsize=12)
    page2 = doc.new_page()
    page2.insert_text((72, 72), "Test PDF Page 2", fontsize=12)
    
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_create_page_screenshot_markdown():
    """测试1: create_page_screenshot_markdown 函数"""
    result = ComprehensiveTestResult()
    try:
        # 创建测试截图
        test_pdf = create_test_pdf()
        doc = fitz.open(stream=test_pdf, filetype="pdf")
        screenshot_bytes = _page_png_bytes(doc, 0, 150)
        doc.close()
        
        # 测试1.1: 嵌入图片模式
        markdown1 = create_page_screenshot_markdown(
            page_num=1,
            screenshot_bytes=screenshot_bytes,
            explanation="这是测试讲解",
            embed_images=True
        )
        
        if "## 第 1 页" in markdown1 and "data:image/png;base64" in markdown1:
            result.add_pass("create_page_screenshot_markdown: 嵌入图片模式")
        else:
            result.add_fail("create_page_screenshot_markdown: 嵌入图片模式", "内容不正确")
        
        # 测试1.2: 外部图片模式
        markdown2 = create_page_screenshot_markdown(
            page_num=2,
            screenshot_bytes=screenshot_bytes,
            explanation="这是测试讲解2",
            embed_images=False,
            image_path="/path/to/page_2.png"
        )
        
        if "## 第 2 页" in markdown2 and "page_2.png" in markdown2 and "data:image/png;base64" not in markdown2:
            result.add_pass("create_page_screenshot_markdown: 外部图片模式")
        else:
            result.add_fail("create_page_screenshot_markdown: 外部图片模式", "内容不正确")
        
        # 测试1.3: 空讲解
        markdown3 = create_page_screenshot_markdown(
            page_num=3,
            screenshot_bytes=screenshot_bytes,
            explanation="",
            embed_images=True
        )
        
        if "（无讲解内容）" in markdown3:
            result.add_pass("create_page_screenshot_markdown: 空讲解处理")
        else:
            result.add_fail("create_page_screenshot_markdown: 空讲解处理", "未正确处理空讲解")
            
    except Exception as e:
        result.add_fail("create_page_screenshot_markdown", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def test_generate_markdown_with_screenshots_basic():
    """测试2: generate_markdown_with_screenshots 基本功能"""
    result = ComprehensiveTestResult()
    try:
        test_pdf = create_test_pdf()
        explanations = {0: "第一页讲解", 1: "第二页讲解"}
        
        # 测试2.1: 嵌入图片模式
        markdown_content, images_dir = generate_markdown_with_screenshots(
            src_bytes=test_pdf,
            explanations=explanations,
            screenshot_dpi=150,
            embed_images=True,
            title="测试文档"
        )
        
        if markdown_content and "测试文档" in markdown_content and images_dir is None:
            if "第 1 页" in markdown_content and "第 2 页" in markdown_content:
                result.add_pass("generate_markdown_with_screenshots: 嵌入图片模式", 
                             f"内容长度: {len(markdown_content)}")
            else:
                result.add_fail("generate_markdown_with_screenshots: 嵌入图片模式", "缺少页面内容")
        else:
            result.add_fail("generate_markdown_with_screenshots: 嵌入图片模式", 
                         f"markdown_content={bool(markdown_content)}, images_dir={images_dir}")
        
        # 测试2.2: 外部图片模式
        with tempfile.TemporaryDirectory() as temp_dir:
            images_dir_path = os.path.join(temp_dir, "test_images")
            markdown_content2, images_dir_return = generate_markdown_with_screenshots(
                src_bytes=test_pdf,
                explanations=explanations,
                screenshot_dpi=150,
                embed_images=False,
                title="测试文档2",
                images_dir=images_dir_path
            )
            
            if markdown_content2 and images_dir_return:
                # 检查图片文件是否存在
                if os.path.exists(images_dir_return):
                    image_files = [f for f in os.listdir(images_dir_return) if f.endswith('.png')]
                    if len(image_files) == 2:  # 应该有2个图片文件
                        result.add_pass("generate_markdown_with_screenshots: 外部图片模式", 
                                     f"生成 {len(image_files)} 个图片文件")
                    else:
                        result.add_fail("generate_markdown_with_screenshots: 外部图片模式", 
                                     f"图片文件数量不正确: {len(image_files)}")
                else:
                    result.add_fail("generate_markdown_with_screenshots: 外部图片模式", 
                                 "图片目录不存在")
            else:
                result.add_fail("generate_markdown_with_screenshots: 外部图片模式", 
                             f"markdown_content={bool(markdown_content2)}, images_dir={images_dir_return}")
                
    except Exception as e:
        result.add_fail("generate_markdown_with_screenshots: 基本功能", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def test_generate_markdown_edge_cases():
    """测试3: 边界情况"""
    result = ComprehensiveTestResult()
    try:
        test_pdf = create_test_pdf()
        
        # 测试3.1: 空讲解字典
        markdown1, _ = generate_markdown_with_screenshots(
            src_bytes=test_pdf,
            explanations={},
            embed_images=True
        )
        
        if markdown1 and "（无讲解内容）" in markdown1:
            result.add_pass("边界情况: 空讲解字典")
        else:
            result.add_fail("边界情况: 空讲解字典", "未正确处理")
        
        # 测试3.2: 部分页面有讲解
        explanations_partial = {0: "只有第一页有讲解"}
        markdown2, _ = generate_markdown_with_screenshots(
            src_bytes=test_pdf,
            explanations=explanations_partial,
            embed_images=True
        )
        
        if markdown2 and "只有第一页有讲解" in markdown2:
            # 检查第二页是否也有内容（即使没有讲解）
            if "第 2 页" in markdown2:
                result.add_pass("边界情况: 部分页面有讲解")
            else:
                result.add_fail("边界情况: 部分页面有讲解", "缺少第二页")
        else:
            result.add_fail("边界情况: 部分页面有讲解", "内容不正确")
        
        # 测试3.3: 超范围页码
        explanations_out_of_range = {0: "第一页", 10: "第11页（不存在）"}
        markdown3, _ = generate_markdown_with_screenshots(
            src_bytes=test_pdf,
            explanations=explanations_out_of_range,
            embed_images=True
        )
        
        if markdown3 and "第一页" in markdown3:
            result.add_pass("边界情况: 超范围页码")
        else:
            result.add_fail("边界情况: 超范围页码", "处理不正确")
            
    except Exception as e:
        result.add_fail("边界情况测试", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def test_generate_markdown_parameters():
    """测试4: 参数验证"""
    result = ComprehensiveTestResult()
    try:
        test_pdf = create_test_pdf()
        explanations = {0: "测试", 1: "测试"}
        
        # 测试4.1: 不同 DPI
        for dpi in [72, 150, 300]:
            try:
                markdown, _ = generate_markdown_with_screenshots(
                    src_bytes=test_pdf,
                    explanations=explanations,
                    screenshot_dpi=dpi,
                    embed_images=True
                )
                if markdown:
                    result.add_pass(f"参数测试: DPI={dpi}")
                else:
                    result.add_fail(f"参数测试: DPI={dpi}", "返回空内容")
            except Exception as e:
                result.add_fail(f"参数测试: DPI={dpi}", f"异常: {str(e)}")
        
        # 测试4.2: 自定义标题
        markdown, _ = generate_markdown_with_screenshots(
            src_bytes=test_pdf,
            explanations=explanations,
            title="自定义标题测试",
            embed_images=True
        )
        
        if markdown and "自定义标题测试" in markdown:
            result.add_pass("参数测试: 自定义标题")
        else:
            result.add_fail("参数测试: 自定义标题", "标题未正确应用")
            
    except Exception as e:
        result.add_fail("参数验证测试", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def test_generate_markdown_error_handling():
    """测试5: 错误处理"""
    result = ComprehensiveTestResult()
    try:
        # 测试5.1: 无效 PDF
        invalid_pdf = b"not a pdf"
        try:
            markdown, _ = generate_markdown_with_screenshots(
                src_bytes=invalid_pdf,
                explanations={0: "test"},
                embed_images=True
            )
            result.add_fail("错误处理: 无效PDF", "应该抛出异常但没有")
        except Exception:
            result.add_pass("错误处理: 无效PDF")
        
        # 测试5.2: 空 PDF bytes
        try:
            markdown, _ = generate_markdown_with_screenshots(
                src_bytes=b"",
                explanations={0: "test"},
                embed_images=True
            )
            result.add_fail("错误处理: 空PDF", "应该抛出异常但没有")
        except Exception:
            result.add_pass("错误处理: 空PDF")
            
    except Exception as e:
        result.add_fail("错误处理测试", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def test_generate_markdown_image_saving():
    """测试6: 图片保存功能"""
    result = ComprehensiveTestResult()
    try:
        test_pdf = create_test_pdf()
        explanations = {0: "测试", 1: "测试"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            images_dir_path = os.path.join(temp_dir, "images")
            
            markdown, images_dir_return = generate_markdown_with_screenshots(
                src_bytes=test_pdf,
                explanations=explanations,
                embed_images=False,
                images_dir=images_dir_path
            )
            
            # 检查图片目录
            if images_dir_return and os.path.exists(images_dir_return):
                image_files = sorted([f for f in os.listdir(images_dir_return) if f.endswith('.png')])
                
                if len(image_files) == 2:
                    # 检查文件是否可读
                    for img_file in image_files:
                        img_path = os.path.join(images_dir_return, img_file)
                        if os.path.getsize(img_path) > 0:
                            result.add_pass(f"图片保存: {img_file}", f"大小: {os.path.getsize(img_path)} bytes")
                        else:
                            result.add_fail(f"图片保存: {img_file}", "文件为空")
                    
                    # 检查 Markdown 中的图片引用
                    if "page_1.png" in markdown and "page_2.png" in markdown:
                        result.add_pass("图片保存: Markdown 引用")
                    else:
                        result.add_fail("图片保存: Markdown 引用", "引用不正确")
                else:
                    result.add_fail("图片保存", f"图片文件数量不正确: {len(image_files)}, 期望: 2")
            else:
                result.add_fail("图片保存", f"图片目录不存在: {images_dir_return}")
                
    except Exception as e:
        result.add_fail("图片保存测试", f"异常: {str(e)}")
        traceback.print_exc()
    return result


def run_comprehensive_tests():
    """运行所有综合测试"""
    print("="*70)
    print("开始运行最严格全面的 Markdown 生成器测试")
    print("="*70)
    print()
    
    all_results = ComprehensiveTestResult()
    
    tests = [
        ("create_page_screenshot_markdown", test_create_page_screenshot_markdown),
        ("generate_markdown_with_screenshots: 基本功能", test_generate_markdown_with_screenshots_basic),
        ("边界情况", test_generate_markdown_edge_cases),
        ("参数验证", test_generate_markdown_parameters),
        ("错误处理", test_generate_markdown_error_handling),
        ("图片保存功能", test_generate_markdown_image_saving),
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

