#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量重新生成功能使用示例
展示如何使用批量重新生成服务
"""

import os
import sys
import json

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.batch_regeneration_service import BatchRegenerationService


def example_batch_regeneration():
    """演示批量重新生成功能"""
    
    print("=" * 60)
    print("批量重新生成功能使用示例")
    print("=" * 60)
    
    # 示例1: 准备测试数据
    print("\n📝 示例数据准备...")
    
    # 假设我们有两个PDF文件和对应的JSON
    test_cases = [
        {
            "pdf_name": "sample1.pdf",
            "json_data": {
                "1": "# 第一页标题\n\n这是**第一页**的讲解内容。\n\n- 要点1\n- 要点2",
                "2": "# 第二页标题\n\n这是第二页的内容，包含代码：\n\n```python\ndef hello():\n    print('Hello')\n```",
                "3": "# 第三页\n\n这是第三页的讲解。"
            }
        },
        {
            "pdf_name": "sample2.pdf",
            "json_data": {
                "1": "## 示例文档\n\n这是另一个PDF的讲解内容。",
                "2": "继续第二页的讲解..."
            }
        }
    ]
    
    # 注意：实际使用时需要提供真实的PDF字节数据
    # 这里只是展示API的使用方式
    
    print("\n📋 数据结构说明：")
    print("- pdf_json_pairs: [(pdf_bytes, json_bytes, pdf_name), ...]")
    print("- output_mode: 'PDF讲解版' | 'Markdown截图讲解' | '分页HTML版'")
    print("- params: 生成参数字典")
    
    # 示例2: 配置参数
    print("\n⚙️ 配置参数示例：")
    
    params_per_page_html = {
        "html_font_name": "SimHei",
        "html_font_size": 14,
        "html_line_spacing": 1.2
    }
    print(f"分页HTML版参数: {params_per_page_html}")
    
    params_pdf = {
        "right_ratio": 0.48,
        "font_size": 20,
        "cjk_font_name": "SimHei",
        "render_mode": "markdown",
        "line_spacing": 1.2,
        "column_padding": 10
    }
    print(f"PDF讲解版参数: {params_pdf}")
    
    params_markdown = {
        "screenshot_dpi": 150,
        "embed_images": True,
        "markdown_title": "PDF文档讲解"
    }
    print(f"Markdown截图讲解参数: {params_markdown}")
    
    # 示例3: 使用说明
    print("\n📖 使用说明：")
    print("""
1. 准备数据：
   - 读取PDF文件为字节数据
   - 准备对应的JSON讲解数据
   
2. 调用批量生成：
   results = BatchRegenerationService.regenerate_pdf_batch(
       pdf_json_pairs=pdf_json_pairs,
       output_mode="分页HTML版",
       params=params
   )
   
3. 处理结果：
   for pdf_name, result in results.items():
       if result["status"] == "completed":
           # 成功 - 获取生成的内容
           if "zip_bytes" in result:
               # 保存ZIP文件
               with open(f"{pdf_name}_output.zip", 'wb') as f:
                   f.write(result["zip_bytes"])
       else:
           # 失败 - 查看错误信息
           print(f"错误: {result['error']}")
    """)
    
    # 示例4: 创建扁平化ZIP
    print("\n📦 创建扁平化ZIP（分页HTML版）：")
    print("""
# 对于分页HTML版，使用专门的方法创建ZIP
zip_bytes = BatchRegenerationService.create_flattened_zip_for_per_page_html(
    batch_results=results,
    output_filename="batch_per_page_html.zip"
)

# ZIP文件结构：
PDF文件名1/
├── page_1.html
├── page_2.html
├── ...
└── PDF文件名1.pdf

PDF文件名2/
├── page_1.html
├── page_2.html
├── ...
└── PDF文件名2.pdf

json/
├── PDF文件名1.json
└── PDF文件名2.json
    """)
    
    # 示例5: 其他输出模式
    print("\n📝 其他输出模式：")
    print("""
# PDF讲解版
zip_bytes = BatchRegenerationService.create_zip_for_other_modes(
    batch_results=results,
    output_mode="PDF讲解版",
    output_filename="batch_pdf_docs.zip"
)

# Markdown截图讲解
zip_bytes = BatchRegenerationService.create_zip_for_other_modes(
    batch_results=results,
    output_mode="Markdown截图讲解",
    output_filename="batch_markdown_docs.zip"
)
    """)
    
    # 示例6: 完整工作流程
    print("\n🔄 完整工作流程示例：")
    print("""
def batch_regenerate_workflow(pdf_files, json_files):
    '''批量重新生成的完整工作流程'''
    
    # 1. 匹配PDF和JSON文件
    matches = BatchRegenerationService.match_pdf_json_files(
        pdf_names=[f.name for f in pdf_files],
        json_names=[f.name for f in json_files]
    )
    
    # 2. 准备数据对
    pdf_json_pairs = []
    for pdf_file, json_file in matches.items():
        if json_file:
            pdf_bytes = read_file(pdf_file)
            json_bytes = read_file(json_file)
            pdf_json_pairs.append((pdf_bytes, json_bytes, pdf_file))
    
    # 3. 批量生成
    results = BatchRegenerationService.regenerate_pdf_batch(
        pdf_json_pairs=pdf_json_pairs,
        output_mode="分页HTML版",
        params={
            "html_font_name": "SimHei",
            "html_font_size": 14,
            "html_line_spacing": 1.2
        }
    )
    
    # 4. 创建ZIP包
    zip_bytes = BatchRegenerationService.create_flattened_zip_for_per_page_html(
        batch_results=results
    )
    
    # 5. 保存结果
    with open("batch_output.zip", 'wb') as f:
        f.write(zip_bytes)
    
    return results
    """)
    
    # 示例7: 结果统计
    print("\n📊 结果统计示例：")
    print("""
def print_statistics(results):
    '''打印批量生成的统计信息'''
    total = len(results)
    completed = sum(1 for r in results.values() if r["status"] == "completed")
    failed = total - completed
    
    print(f"总计: {total} 个PDF")
    print(f"成功: {completed} 个")
    print(f"失败: {failed} 个")
    
    # 详细信息
    for pdf_name, result in results.items():
        if result["status"] == "completed":
            pages = result.get("total_pages", 0)
            print(f"✓ {pdf_name}: {pages} 页")
        else:
            error = result.get("error", "未知错误")
            print(f"✗ {pdf_name}: {error}")
    """)
    
    print("\n" + "=" * 60)
    print("✨ 使用示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    example_batch_regeneration()

