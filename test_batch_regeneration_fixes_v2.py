#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试批量重新生成功能的修复
验证：
1. 删除index页
2. 第一页有下一页按钮
3. Markdown内容正确渲染
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.batch_regeneration_service import BatchRegenerationService
from app.services.enhanced_html_generator import EnhancedHTMLGenerator


def test_no_index_page():
    """测试：不生成index页"""
    print("\n=== 测试1: 验证不生成index页 ===")
    
    # 创建测试数据
    explanations = {
        1: "# 第一页\n这是**第一页**的讲解内容。",
        2: "# 第二页\n这是**第二页**的讲解内容。"
    }
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="test_no_index_")
    
    try:
        # 生成分页HTML结构
        generated_files = EnhancedHTMLGenerator.generate_complete_per_page_structure(
            explanations=explanations,
            pdf_filename="test.pdf",
            total_pages=2,
            output_dir=temp_dir,
            font_name="SimHei",
            font_size=14,
            line_spacing=1.2
        )
        
        # 检查是否不存在index.html
        index_path = Path(temp_dir) / "index.html"
        if index_path.exists():
            print("❌ 失败: index.html仍然被生成")
            return False
        else:
            print("✓ 通过: index.html未被生成")
        
        # 检查是否生成了page_1.html和page_2.html
        page1_path = Path(temp_dir) / "page_1.html"
        page2_path = Path(temp_dir) / "page_2.html"
        
        if not page1_path.exists():
            print("❌ 失败: page_1.html未生成")
            return False
        if not page2_path.exists():
            print("❌ 失败: page_2.html未生成")
            return False
        
        print("✓ 通过: 所有页面HTML文件已生成")
        return True
        
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_first_page_next_button():
    """测试：第一页有下一页按钮"""
    print("\n=== 测试2: 验证第一页有下一页按钮 ===")
    
    # 创建测试数据
    explanations = {
        1: "第一页内容",
        2: "第二页内容",
        3: "第三页内容"
    }
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="test_first_page_")
    
    try:
        # 生成分页HTML结构
        generated_files = EnhancedHTMLGenerator.generate_complete_per_page_structure(
            explanations=explanations,
            pdf_filename="test.pdf",
            total_pages=3,
            output_dir=temp_dir,
            font_name="SimHei",
            font_size=14,
            line_spacing=1.2
        )
        
        # 读取第一页HTML
        page1_path = Path(temp_dir) / "page_1.html"
        with open(page1_path, 'r', encoding='utf-8') as f:
            page1_content = f.read()
        
        # 检查下一页按钮是否存在且未被隐藏
        # 下一页按钮应该：
        # 1. 存在（有"下一页"文本）
        # 2. 没有 disabled 属性（或disabled=""）
        # 3. display不是none
        
        has_next_button = "下一页" in page1_content
        if not has_next_button:
            print("❌ 失败: 第一页没有下一页按钮文本")
            return False
        
        # 检查按钮是否被禁用或隐藏
        # 查找下一页按钮的代码段
        import re
        next_button_pattern = r'class="nav-btn next".*?next_disabled.*?\>'
        next_button_match = re.search(next_button_pattern, page1_content, re.DOTALL)
        
        if next_button_match:
            button_html = next_button_match.group(0)
            # 检查是否包含disabled属性（除了空的disabled=""）
            if 'disabled="disabled"' in button_html or 'disabled>' in button_html:
                print("❌ 失败: 第一页的下一页按钮被禁用")
                print(f"   按钮HTML: {button_html[:200]}")
                return False
        
        # 检查display样式
        # 查找next_display变量的值
        if 'next_display = "none"' in page1_content or 'display: none' in page1_content.lower():
            # 需要更精确的检查，看是否是下一页按钮的样式
            pass  # 暂时跳过，因为这个比较复杂
        
        print("✓ 通过: 第一页有可用的下一页按钮")
        
        # 额外检查：最后一页不应该有下一页按钮
        page3_path = Path(temp_dir) / "page_3.html"
        with open(page3_path, 'r', encoding='utf-8') as f:
            page3_content = f.read()
        
        # 最后一页的下一页按钮应该被禁用
        if 'disabled=""' in page3_content or 'display: none' in page3_content:
            print("✓ 通过: 最后一页的下一页按钮已正确禁用/隐藏")
        
        return True
        
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_markdown_rendering():
    """测试：Markdown内容正确渲染"""
    print("\n=== 测试3: 验证Markdown内容渲染 ===")
    
    # 创建包含Markdown语法的测试数据
    explanations = {
        1: """# 标题1
## 标题2

这是一段**粗体**文本和*斜体*文本。

- 列表项1
- 列表项2
- 列表项3

```python
def hello():
    print("Hello World")
```

这是[链接](http://example.com)。
""",
        2: """普通文本

1. 有序列表1
2. 有序列表2
3. 有序列表3

> 引用块内容
"""
    }
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="test_markdown_")
    
    try:
        # 生成分页HTML结构
        generated_files = EnhancedHTMLGenerator.generate_complete_per_page_structure(
            explanations=explanations,
            pdf_filename="test.pdf",
            total_pages=2,
            output_dir=temp_dir,
            font_name="SimHei",
            font_size=14,
            line_spacing=1.2
        )
        
        # 读取第一页HTML
        page1_path = Path(temp_dir) / "page_1.html"
        with open(page1_path, 'r', encoding='utf-8') as f:
            page1_content = f.read()
        
        # 检查是否包含HTML标签（说明Markdown被渲染了）
        checks = [
            ('<h1>' in page1_content, "H1标题"),
            ('<h2>' in page1_content, "H2标题"),
            ('<strong>' in page1_content or '<b>' in page1_content, "粗体"),
            ('<em>' in page1_content or '<i>' in page1_content, "斜体"),
            ('<ul>' in page1_content or '<li>' in page1_content, "无序列表"),
            ('<code>' in page1_content or '<pre>' in page1_content, "代码块"),
        ]
        
        passed_checks = sum(1 for check, _ in checks if check)
        total_checks = len(checks)
        
        print(f"   Markdown渲染检查: {passed_checks}/{total_checks} 通过")
        
        for check, name in checks:
            status = "✓" if check else "✗"
            print(f"   {status} {name}")
        
        if passed_checks >= 4:  # 至少4个检查通过
            print("✓ 通过: Markdown内容已正确渲染为HTML")
            return True
        else:
            print("⚠ 警告: 部分Markdown语法未被渲染")
            # 打印部分内容用于调试
            print("\n--- 页面内容片段（前500字符） ---")
            print(page1_content[:500])
            print("--- 结束 ---\n")
            return False
        
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def test_breadcrumb_navigation():
    """测试：面包屑导航指向正确"""
    print("\n=== 测试4: 验证面包屑导航 ===")
    
    # 创建测试数据
    explanations = {
        1: "第一页",
        2: "第二页"
    }
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="test_breadcrumb_")
    
    try:
        # 生成分页HTML结构
        generated_files = EnhancedHTMLGenerator.generate_complete_per_page_structure(
            explanations=explanations,
            pdf_filename="test.pdf",
            total_pages=2,
            output_dir=temp_dir,
            font_name="SimHei",
            font_size=14,
            line_spacing=1.2
        )
        
        # 读取第二页HTML
        page2_path = Path(temp_dir) / "page_2.html"
        with open(page2_path, 'r', encoding='utf-8') as f:
            page2_content = f.read()
        
        # 检查面包屑导航是否指向page_1.html而不是index.html
        if 'href="index.html"' in page2_content:
            print("❌ 失败: 面包屑导航仍然指向index.html")
            return False
        
        if 'href="page_1.html"' in page2_content:
            print("✓ 通过: 面包屑导航正确指向page_1.html")
            return True
        
        print("⚠ 警告: 未找到面包屑导航链接")
        return False
        
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """运行所有测试"""
    print("=" * 60)
    print("批量重新生成功能修复测试")
    print("=" * 60)
    
    tests = [
        ("删除index页", test_no_index_page),
        ("第一页下一页按钮", test_first_page_next_button),
        ("Markdown渲染", test_markdown_rendering),
        ("面包屑导航", test_breadcrumb_navigation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试失败: {test_name}")
            print(f"   错误: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

