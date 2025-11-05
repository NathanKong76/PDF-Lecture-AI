#!/usr/bin/env python3
"""
同步HTML功能演示
生成一个实际的示例，展示PDF页面与讲解内容的一一对应功能
"""

import os
import tempfile
from pathlib import Path
from app.services.sync_html_processor import create_sync_html


def create_demo_pdf(path: str) -> None:
    """创建演示用的PDF文件"""
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 100 >>
stream
BT
/F1 16 Tf
50 700 Td
(PDF Explanation Sync Demo) Tj
0 -30 Td
(This is a sample PDF) Tj
0 -30 Td
(for demonstrating the sync feature) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000056 00000 n 
0000000115 00000 n 
0000000250 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
350
%%EOF"""
    
    with open(path, 'wb') as f:
        f.write(pdf_content)


def create_demo_explanations():
    """创建演示用的讲解内容"""
    return {
        1: """
# 第一页讲解

## 欢迎使用PDF讲解同步系统

这是一个演示页面，展示了PDF页面与讲解内容的一一对应功能。

### 主要特点

1. **实时同步**: 当您切换PDF页面时，右侧的讲解内容会自动更新
2. **用户友好**: 支持鼠标点击和键盘快捷键操作
3. **响应式设计**: 在各种设备上都能良好显示

### 操作说明

- **鼠标操作**: 点击PDF下方的"上一页"/"下一页"按钮
- **键盘操作**: 
  - 左右方向键切换页面
  - 空格键下一页
  - Home键跳转到首页

### 技术实现

本系统使用现代Web技术实现：
- HTML5 + CSS3布局
- JavaScript处理同步逻辑
- PDF.js渲染PDF内容
        """,
        2: """
# 第二页讲解

## 核心功能介绍

这一页深入介绍了系统的核心功能和工作原理。

### 同步机制

PDF与讲解内容的同步是通过以下方式实现的：

1. **页面检测**: 监听PDF查看器的页面变化
2. **内容映射**: 根据页码查找对应的讲解内容
3. **界面更新**: 动态更新右侧的讲解显示区域

### 布局设计

系统采用分栏布局设计：

```
┌─────────────────┬─────────────────┐
│   PDF查看器      │   讲解内容区     │
│                │                │
│  [上一页][1/3]   │   (滚动查看)     │
│   [下一页]      │                │
└─────────────────┴─────────────────┘
```

### 用户体验优化

- 流畅的页面切换动画
- 直观的页面指示器
- 清晰的字体和配色方案
        """,
        3: """
# 第三页讲解

## 应用场景与扩展

这是最后一页，介绍了系统的应用场景和未来扩展方向。

### 适用场景

1. **在线教育**: 课程讲义和教学材料展示
2. **企业培训**: 产品文档和操作手册
3. **学术研究**: 论文阅读和研究资料
4. **技术文档**: API文档和使用指南

### 技术优势

- **跨平台兼容**: 支持各种操作系统和浏览器
- **部署简单**: 只需生成HTML文件，无需服务器
- **性能优秀**: 纯前端实现，加载速度快
- **易于定制**: 可根据需求修改样式和功能

### 未来扩展方向

- 书签和笔记功能
- 全文搜索支持
- 深色模式主题
- 语音朗读功能
- 协作编辑功能

### 总结

PDF讲解同步功能为数字化学习和文档展示提供了强有力的工具，大大提升了用户的阅读体验和学习效率。
        """
    }


def main():
    """主函数"""
    print("=== PDF讲解同步功能演示 ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        demo_output_dir = temp_path / "demo_sync_output"
        
        # 创建演示PDF
        pdf_path = temp_path / "demo_document.pdf"
        create_demo_pdf(str(pdf_path))
        
        # 创建演示讲解内容
        explanations = create_demo_explanations()
        
        print("正在生成同步HTML文件...")
        
        # 生成同步HTML
        try:
            result = create_sync_html(
                pdf_path=str(pdf_path),
                explanations=explanations,
                total_pages=3,
                output_dir=str(demo_output_dir),
                font_name="SimHei",
                font_size=14,
                line_spacing=1.2
            )
            
            print("SUCCESS: 演示文件生成成功！")
            print("\n生成的文件:")
            for file_type, file_path in result.items():
                print(f"  {file_type}: {file_path}")
            
            print(f"\n演示文件保存在: {demo_output_dir}")
            print("\n使用方法:")
            print("1. 打开 index.html 查看导航页面")
            print("2. 打开 sync_view.html 进入同步阅读模式")
            print("3. 使用鼠标点击或键盘快捷键操作")
            
            return True
            
        except Exception as e:
            print(f"FAILED: 生成演示文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n" + "="*50)
        print("演示完成！PDF讲解同步功能已成功实现。")
        print("请打开生成的HTML文件体验功能。")
    else:
        print("\n演示失败，请检查错误信息。")
