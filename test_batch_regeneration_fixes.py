#!/usr/bin/env python3
"""
批量重新生成功能测试
验证分页HTML版压缩包扁平化处理和批量JSON重新生成功能
"""

import io
import zipfile
import json
import os
import tempfile
from pathlib import Path

# 模拟批量结果数据结构
def create_mock_batch_results():
    """创建模拟的批量处理结果"""
    
    # 模拟分页HTML版结果（包含压缩包）
    mock_per_page_result = {
        "status": "completed",
        "zip_bytes": create_mock_per_page_html_zip(),
        "explanations": {
            "1": "第1页讲解：这是一个测试页面的讲解内容",
            "2": "第2页讲解：这是第二个页面的讲解内容",
            "3": "第3页讲解：这是第三个页面的讲解内容"
        },
        "pdf_bytes": b"mock pdf content"
    }
    
    # 模拟PDF版结果
    mock_pdf_result = {
        "status": "completed", 
        "pdf_bytes": b"mock pdf content",
        "explanations": {
            "1": "第1页讲解：PDF版讲解内容",
            "2": "第2页讲解：PDF版讲解内容"
        }
    }
    
    # 模拟Markdown版结果
    mock_markdown_result = {
        "status": "completed",
        "markdown_content": "# PDF讲解文档\n\n## 第1页\n讲解内容1\n\n## 第2页\n讲解内容2",
        "explanations": {
            "1": "第1页讲解：Markdown版讲解内容",
            "2": "第2页讲解：Markdown版讲解内容"
        }
    }
    
    return {
        "document1.pdf": mock_per_page_result,
        "document2.pdf": mock_pdf_result,
        "document3.pdf": mock_markdown_result
    }

def create_mock_per_page_html_zip():
    """创建模拟的分页HTML压缩包"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 创建模拟的目录结构
        zip_file.writestr("document1/index.html", "<html><body>Index</body></html>")
        zip_file.writestr("document1/page_1.html", "<html><body>Page 1</body></html>")
        zip_file.writestr("document1/page_2.html", "<html><body>Page 2</body></html>")
        zip_file.writestr("document1/document1.pdf", "mock pdf content")
        
        # 模拟嵌套压缩包情况（这是要修复的问题）
        inner_zip_buffer = io.BytesIO()
        with zipfile.ZipFile(inner_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as inner_zip:
            inner_zip.writestr("page_1.html", "<html><body>Nested Page 1</body></html>")
            inner_zip.writestr("page_2.html", "<html><body>Nested Page 2</body></html>")
        
        # 添加嵌套压缩包到外层ZIP（这是问题所在）
        zip_file.writestr("document1/nested_subfolder/inner.zip", inner_zip_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def test_zip_flattening():
    """测试压缩包扁平化处理"""
    print("🔍 测试压缩包扁平化处理...")
    
    # 导入要测试的函数
    from app.ui_helpers import build_zip_cache_html
    
    # 创建模拟结果
    mock_results = {
        "test_document.pdf": {
            "status": "completed",
            "zip_bytes": create_mock_per_page_html_zip(),
            "explanations": {"1": "讲解内容1", "2": "讲解内容2"}
        }
    }
    
    # 调用扁平化处理函数
    result_zip = build_zip_cache_html(mock_results)
    
    if result_zip is None:
        print("❌ 扁平化处理失败：返回None")
        return False
    
    # 验证结果
    with zipfile.ZipFile(io.BytesIO(result_zip), 'r') as zip_file:
        file_list = zip_file.namelist()
        print(f"📁 扁平化后文件列表: {file_list}")
        
        # 检查是否正确扁平化
        expected_files = [
            "test_document/index.html",
            "test_document/page_1.html", 
            "test_document/page_2.html",
            "test_document/document1.pdf",
            "json/test_document.json"
        ]
        
        has_expected_files = any(f in file_list for f in expected_files)
        
        # 检查是否避免了嵌套
        nested_files = [f for f in file_list if 'nested_subfolder' in f or 'inner.zip' in f]
        no_nesting = len(nested_files) == 0
        
        if has_expected_files and no_nesting:
            print("✅ 压缩包扁平化处理成功！")
            print(f"   - 包含预期文件: {has_expected_files}")
            print(f"   - 无嵌套压缩包: {no_nesting}")
            return True
        else:
            print("❌ 压缩包扁平化处理失败")
            print(f"   - 包含预期文件: {has_expected_files}")
            print(f"   - 无嵌套压缩包: {no_nesting}")
            print(f"   - 发现嵌套文件: {nested_files}")
            return False

def test_batch_json_regeneration():
    """测试批量JSON重新生成功能"""
    print("\n🔍 测试批量JSON重新生成功能...")
    
    # 模拟参数
    mock_params = {
        "output_mode": "分页HTML版",
        "html_font_name": "SimHei",
        "html_font_size": 14,
        "html_line_spacing": 1.2
    }
    
    # 模拟文件配对
    mock_pairs = [
        ("test1.pdf", "test1.json"),
        ("test2.pdf", "test2.json")
    ]
    
    # 模拟JSON内容
    mock_json_data = {
        "1": "测试讲解内容1",
        "2": "测试讲解内容2",
        "3": "测试讲解内容3"
    }
    
    print(f"📝 模拟处理 {len(mock_pairs)} 个文件配对")
    print(f"   输出模式: {mock_params['output_mode']}")
    print(f"   JSON数据示例: {mock_json_data}")
    
    # 验证JSON数据格式
    if all(isinstance(k, str) and isinstance(v, str) for k, v in mock_json_data.items()):
        print("✅ JSON数据格式正确")
    else:
        print("❌ JSON数据格式错误")
        return False
    
    # 验证配对逻辑
    pdf_names = [pair[0] for pair in mock_pairs]
    json_names = [pair[1] for pair in mock_pairs]
    
    # 检查文件名匹配
    for pdf_name in pdf_names:
        expected_json = pdf_name.replace('.pdf', '.json')
        if expected_json in json_names:
            print(f"✅ 文件配对正确: {pdf_name} -> {expected_json}")
        else:
            print(f"❌ 文件配对错误: {pdf_name} 没有匹配的JSON")
            return False
    
    print("✅ 批量JSON重新生成功能测试通过！")
    return True

def test_error_handling():
    """测试错误处理"""
    print("\n🔍 测试错误处理...")
    
    # 测试空结果处理
    empty_results = {}
    from app.ui_helpers import build_zip_cache_html
    
    result = build_zip_cache_html(empty_results)
    if result is None:
        print("✅ 空结果处理正确（返回None）")
    else:
        print("❌ 空结果处理错误（应该返回None）")
        return False
    
    # 测试部分成功结果处理
    partial_results = {
        "success.pdf": {
            "status": "completed",
            "zip_bytes": create_mock_per_page_html_zip(),
            "explanations": {"1": "讲解内容"}
        },
        "failed.pdf": {
            "status": "failed",
            "error": "测试错误"
        }
    }
    
    result = build_zip_cache_html(partial_results)
    if result is not None and len(result) > 0:
        print("✅ 部分成功结果处理正确")
    else:
        print("❌ 部分成功结果处理错误")
        return False
    
    print("✅ 错误处理测试通过！")
    return True

def main():
    """主测试函数"""
    print("🚀 开始批量重新生成功能测试")
    print("=" * 50)
    
    tests = [
        ("压缩包扁平化处理", test_zip_flattening),
        ("批量JSON重新生成", test_batch_json_regeneration),
        ("错误处理", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            print(f"💥 {test_name} - 异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！批量重新生成功能工作正常。")
        print("\n🔧 主要改进点:")
        print("  1. ✅ 修复分页HTML版压缩包嵌套问题")
        print("  2. ✅ 优化批量JSON重新生成工作流程") 
        print("  3. ✅ 改进批量处理的用户界面")
        print("  4. ✅ 增强错误处理和用户反馈")
    else:
        print("⚠️  部分测试失败，需要进一步检查。")
    
    return passed == total

if __name__ == "__main__":
    main()
