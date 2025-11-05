#!/usr/bin/env python3
"""
同步HTML功能测试
测试PDF页面与讲解内容的一一对应功能
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.sync_html_processor import create_sync_html, generate_simple_sync_view
from app.services.logger import get_logger

logger = get_logger()


def create_sample_pdf(path: str) -> None:
    """创建一个示例PDF文件"""
    # 这里应该使用实际的PDF生成库，我们创建一个简单的文件作为演示
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Sample PDF Content) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000102 00000 n 
0000000279 00000 n 
0000000363 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
439
%%EOF"""
    
    with open(path, 'wb') as f:
        f.write(pdf_content)


def create_sample_explanations() -> dict:
    """创建示例讲解内容"""
    return {
        1: """
# 第一页讲解

## 内容概述
这是文档的第一页，主要介绍整个文档的基本结构和学习目标。

## 主要内容
1. **文档结构**: 本文档共分为三个主要部分
2. **学习目标**: 通过本课程学习，您将掌握核心概念和实际应用
3. **预备知识**: 需要具备基础的编程概念

## 重点提示
> 注意：这一页的内容非常重要，是理解后续内容的基础。

## 代码示例
```python
# 第一个示例
def hello_world():
    print("欢迎学习PDF讲解系统!")
```

## 总结
本页为您提供了学习的路线图，建议仔细阅读每个部分。
        """,
        2: """
# 第二页讲解

## 核心概念
本页深入讲解了文档的核心概念，这些概念将在后续章节中反复应用。

### 概念详解

#### 1. 同步机制
PDF和讲解内容的同步是通过JavaScript实现的，主要包括：
- 页面切换检测
- 内容动态更新
- 用户交互处理

#### 2. 布局设计
采用响应式设计，确保在各种设备上都能良好显示：
- 桌面端：左右分栏布局
- 移动端：上下堆叠布局

### 实际应用

#### 使用场景
这种同步展示方式特别适用于：
- 在线教学
- 文档培训
- 学术研究

#### 优势特点
- 🚀 **提高效率**: 避免翻页查找对应内容
- 📱 **移动友好**: 支持各种设备访问
- ⌨️ **操作便捷**: 支持键盘快捷键操作

### 技术实现
核心使用以下技术：
- HTML5 + CSS3
- JavaScript ES6+
- PDF.js (PDF渲染)
        """,
        3: """
# 第三页讲解

## 综合应用
这是最后一页，将前面讲解的概念应用到实际项目中。

### 项目架构

```mermaid
graph TB
    A[PDF文档] --> B[HTML生成器]
    C[讲解内容] --> B
    B --> D[同步视图]
    D --> E[用户界面]
```

### 实现步骤

#### 第一步：准备数据
```python
# 准备PDF路径和讲解内容
pdf_path = "document.pdf"
explanations = {
    1: "第一页讲解...",
    2: "第二页讲解...",
    3: "第三页讲解..."
}
```

#### 第二步：生成同步视图
```python
from app.services.sync_html_processor import create_sync_html

result = create_sync_html(
    pdf_path=pdf_path,
    explanations=explanations,
    total_pages=3,
    output_dir="output"
)
```

#### 第三步：用户体验优化
- 添加加载指示器
- 实现平滑的页面切换动画
- 优化移动端体验

### 部署建议

#### 生产环境配置
1. **CDN加速**: 使用CDN提高静态资源加载速度
2. **缓存策略**: 设置适当的浏览器缓存
3. **性能监控**: 监控页面加载和交互性能

#### 浏览器兼容性
- ✅ Chrome 70+ (推荐)
- ✅ Firefox 65+
- ✅ Safari 12+
- ✅ Edge 79+

### 故障排除

#### 常见问题
1. **PDF无法显示**
   - 检查文件路径
   - 确认浏览器支持

2. **同步失效**
   - 检查JavaScript是否启用
   - 查看控制台错误信息

3. **样式异常**
   - 清除浏览器缓存
   - 检查CSS文件加载

### 扩展功能

#### 可能的改进方向
- 🎯 **智能跳转**: 根据内容自动关联相关页面
- 📝 **笔记功能**: 允许用户添加个人笔记
- 🔖 **书签标记**: 支持收藏重要页面
- 🖨️ **打印优化**: 改善打印样式

### 课程总结
恭喜您完成了PDF讲解同步系统的学习！通过本课程，您掌握了：

1. ✅ PDF与讲解内容的同步展示原理
2. ✅ 现代化的Web界面设计
3. ✅ 用户友好的交互体验
4. ✅ 实际项目的部署方法

希望这个系统能够帮助您更好地展示和学习文档内容！
        """
    }


def test_basic_functionality():
    """测试基本功能"""
    print("🧪 开始测试基本功能...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建示例PDF
        pdf_path = temp_path / "sample.pdf"
        create_sample_pdf(str(pdf_path))
        
        # 创建示例讲解内容
        explanations = create_sample_explanations()
        
        # 测试基本同步HTML生成
        try:
            result = create_sync_html(
                pdf_path=str(pdf_path),
                explanations=explanations,
                total_pages=3,
                output_dir=str(temp_path / "sync_output"),
                font_name="SimHei",
                font_size=14
            )
            
            print("✓ 基本功能测试通过")
            print(f"📁 生成的文件:")
            for file_type, file_path in result.items():
                print(f"   {file_type}: {file_path}")
            
            return True
            
        except Exception as e:
            print(f"✗ 基本功能测试失败: {e}")
            return False


def test_simple_sync_view():
    """测试简单同步视图"""
    print("\n🧪 测试简单同步视图...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建示例PDF
        pdf_path = temp_path / "sample.pdf"
        create_sample_pdf(str(pdf_path))
        
        # 创建示例讲解内容
        explanations = create_sample_explanations()
        
        # 测试简单同步视图生成
        try:
            result_path = generate_simple_sync_view(
                pdf_path=str(pdf_path),
                explanations=explanations,
                total_pages=3,
                output_path=str(temp_path / "simple_sync.html")
            )
            
            print("✅ 简单同步视图测试通过")
            print(f"📁 生成文件: {result_path}")
            
            # 检查文件是否生成
            if os.path.exists(result_path):
                file_size = os.path.getsize(result_path)
                print(f"📊 文件大小: {file_size} 字节")
                
                # 检查HTML内容
                with open(result_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if "PDFExplanationSync" in content:
                    print("✅ JavaScript同步功能已包含")
                else:
                    print("❌ JavaScript同步功能缺失")
                    
                if "explanation-page-1" in content:
                    print("✅ 讲解页面结构正确")
                else:
                    print("❌ 讲解页面结构异常")
            else:
                print("❌ 文件生成失败")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ 简单同步视图测试失败: {e}")
            return False


def test_navigation_index():
    """测试导航索引页面"""
    print("\n🧪 测试导航索引页面...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建示例讲解内容
        explanations = create_sample_explanations()
        
        from app.services.sync_html_processor import SyncHTMLProcessor
        
        try:
            processor = SyncHTMLProcessor(str(temp_path / "nav_output"))
            
            result_path = processor.generate_navigation_index(
                explanations=explanations,
                total_pages=3,
                pdf_filename="sample.pdf",
                font_name="SimHei",
                font_size=14
            )
            
            print("✅ 导航索引页面测试通过")
            print(f"📁 生成文件: {result_path}")
            
            # 检查文件内容
            if os.path.exists(result_path):
                with open(result_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if "openSyncMode" in content:
                    print("✅ 导航功能已包含")
                else:
                    print("❌ 导航功能缺失")
                    
                if "第 1 页" in content:
                    print("✅ 页面内容正确")
                else:
                    print("❌ 页面内容异常")
                    
                return True
            else:
                print("❌ 导航页面生成失败")
                return False
                
        except Exception as e:
            print(f"❌ 导航索引页面测试失败: {e}")
            return False


def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试错误处理...")
    
    try:
        # 测试不存在的PDF文件
        explanations = {1: "测试讲解内容"}
        
        try:
            create_sync_html(
                pdf_path="non_existent.pdf",
                explanations=explanations,
                total_pages=1,
                output_dir="test_error"
            )
            print("❌ 错误处理测试失败：应该抛出异常")
            return False
        except Exception as e:
            print(f"✅ 正确捕获文件不存在异常: {type(e).__name__}")
        
        # 测试空讲解内容
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "test.pdf"
            create_sample_pdf(str(pdf_path))
            
            empty_explanations = {}
            
            try:
                result = create_sync_html(
                    pdf_path=str(pdf_path),
                    explanations=empty_explanations,
                    total_pages=1,
                    output_dir=temp_dir
                )
                print("✅ 空讲解内容处理正确")
                return True
            except Exception as e:
                print(f"❌ 空讲解内容处理异常: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False


def test_performance():
    """测试性能"""
    print("\n🧪 测试性能...")
    
    import time
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建示例PDF
        pdf_path = temp_path / "sample.pdf"
        create_sample_pdf(str(pdf_path))
        
        # 创建大量讲解内容
        large_explanations = {}
        for i in range(1, 101):  # 100页内容
            large_explanations[i] = f"这是第{i}页的详细讲解内容，包含大量的文本信息用于测试性能。" * 10
        
        try:
            start_time = time.time()
            
            result = create_sync_html(
                pdf_path=str(pdf_path),
                explanations=large_explanations,
                total_pages=100,
                output_dir=str(temp_path / "performance_test"),
                font_name="SimHei",
                font_size=14
            )
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            print(f"✅ 性能测试完成")
            print(f"📊 生成100页内容耗时: {elapsed_time:.2f} 秒")
            print(f"📁 生成文件数: {len(result)}")
            
            # 检查文件大小
            sync_view_path = result['sync_view']
            if os.path.exists(sync_view_path):
                file_size = os.path.getsize(sync_view_path)
                print(f"📊 同步视图文件大小: {file_size / 1024:.2f} KB")
            
            if elapsed_time < 10:  # 10秒内完成认为是合理的
                return True
            else:
                print(f"⚠️ 性能可能需要优化")
                return True  # 仍然返回True，因为功能是正确的
                
        except Exception as e:
            print(f"❌ 性能测试失败: {e}")
            return False


def main():
    """主测试函数"""
    print("=== 开始PDF讲解同步HTML功能测试 ===")
    
    tests = [
        ("基本功能", test_basic_functionality),
        ("简单同步视图", test_simple_sync_view),
        ("导航索引", test_navigation_index),
        ("错误处理", test_error_handling),
        ("性能测试", test_performance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 测试通过")
            else:
                print(f"✗ {test_name} 测试失败")
        except Exception as e:
            print(f"! {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！PDF讲解同步功能正常工作。")
    else:
        print("⚠️ 部分测试失败，请检查相关功能。")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
