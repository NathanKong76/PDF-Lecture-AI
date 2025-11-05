#!/usr/bin/env python3
"""
测试续页内容重复问题的修复效果
"""

import sys
import os
import io

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import fitz
from app.services.pdf_processor import compose_pdf


def create_test_pdf(width: int = 400, height: int = 600) -> bytes:
    """创建测试PDF"""
    doc = fitz.open()
    page = doc.new_page(width=width, height=height)
    page.insert_text((50, 100), "原PDF内容", fontsize=12)
    bio = io.BytesIO()
    doc.save(bio)
    doc.close()
    return bio.getvalue()


def test_continuation_page_duplication():
    """测试续页内容重复问题"""
    print("🔍 测试续页内容重复问题修复效果\n")

    src_bytes = create_test_pdf(400, 600)

    # 创建一个非常长的文本，确保会产生多个续页
    long_explanation = """
# 非常长的技术讲解内容

这是一个非常详细的技术讲解内容，来自LLM的生成结果。
通常这种讲解会包含大量的专业术语和技术细节，需要占用较大的页面空间。

## 技术要点

1. 算法复杂度分析：时间复杂度O(n log n)，空间复杂度O(n)
2. 数据结构选择：使用平衡二叉树确保查找效率
3. 并发处理机制：采用多线程架构提高系统吞吐量
4. 错误处理策略：实现优雅降级和故障恢复机制

## 代码示例

```python
def process_data(data):
    try:
        # 数据预处理
        cleaned = preprocess(data)
        # 特征提取
        features = extract_features(cleaned)
        # 模型推理
        result = model.predict(features)
        return result
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return fallback_result()
```

## 性能优化建议

- 使用缓存机制减少重复计算
- 实现异步处理提高响应速度
- 采用分布式架构扩展系统容量
- 监控关键指标确保服务稳定性

## 深入分析

在实际应用中，我们需要考虑更多的细节和边界情况。例如：

1. 当数据量特别大的时候，我们需要考虑分批处理的策略
2. 当系统负载过高的时候，需要有合理的限流和降级机制
3. 在分布式环境中，需要考虑数据一致性和事务处理
4. 对于实时性要求高的场景，需要优化算法和数据结构

## 实际案例研究

让我们通过一个实际的案例来说明这些概念的应用：

在某电商平台的推荐系统中，我们需要处理海量的用户行为数据，
包括浏览、点击、购买等行为。为了提供个性化的推荐，我们采用
了深度学习模型来分析用户兴趣。

### 数据处理流程

1. 数据收集：从各个业务系统收集用户行为日志
2. 数据清洗：去除无效和异常数据
3. 特征工程：提取用户和商品的特征向量
4. 模型训练：使用深度学习模型进行训练
5. 在线推理：为用户实时生成推荐结果

### 技术挑战

在实现过程中，我们遇到了很多技术挑战：

1. 数据量大：每天产生数十亿条用户行为数据
2. 实时性要求高：需要在几百毫秒内返回推荐结果
3. 准确性要求高：推荐结果的点击率需要持续提升
4. 系统稳定性：需要保证7x24小时稳定运行

## 解决方案

为了应对这些挑战，我们采用了以下解决方案：

### 分布式架构

使用微服务架构将系统拆分为多个独立的服务，包括：

1. 数据收集服务：负责收集和预处理用户行为数据
2. 特征计算服务：实时计算用户和商品的特征向量
3. 模型训练服务：定期训练和更新推荐模型
4. 在线推荐服务：为用户提供实时推荐

### 缓存优化

使用多级缓存来提升系统性能：

1. 本地缓存：缓存热点数据和计算结果
2. 分布式缓存：使用Redis集群缓存用户画像
3. 数据库缓存：优化数据库查询性能

### 算法优化

不断优化推荐算法以提升推荐效果：

1. 深度学习模型：使用DNN、Wide&Deep等模型
2. 在线学习：实时更新模型参数
3. 多目标优化：同时优化点击率、转化率等多个指标

## 总结

通过以上技术方案和优化措施，我们成功构建了一个高性能、高可用的推荐系统，
能够为用户提供精准的个性化推荐，有效提升了用户体验和业务指标。
""" * 2  # 减少重复次数以避免过于极端的情况

    print(f"📝 测试超长文本内容")
    print(f"文本长度：{len(long_explanation)} 字符")

    try:
        explanations = {0: long_explanation}
        result_bytes = compose_pdf(
            src_bytes=src_bytes,
            explanations=explanations,
            right_ratio=0.5,
            font_size=10,  # 适中字体
            render_mode="text",  # 使用文本模式避免HTML渲染问题
            line_spacing=1.2
        )

        result_doc = fitz.open(stream=result_bytes)
        print(f"✅ 生成PDF成功：{result_doc.page_count} 页")

        # 检查每一页的内容，确保没有重复
        page_contents = []
        duplicate_found = False
        
        for i in range(result_doc.page_count):
            page = result_doc.load_page(i)
            text = page.get_text()
            clean_text = text.replace("···PDF··", "").replace("···········", "").strip()
            
            # 检查是否有重复内容（使用更宽松的比较方式）
            is_duplicate = False
            for existing_content in page_contents:
                # 如果新内容包含在已有内容中，或者是已有内容的子集，则认为是重复
                if clean_text in existing_content or existing_content in clean_text:
                    # 但要排除非常短的文本（可能是页码等重复元素）
                    if len(clean_text) > 50:
                        is_duplicate = True
                        break
            
            if is_duplicate:
                print(f"❌ 发现重复内容在第{i+1}页")
                duplicate_found = True
            else:
                page_contents.append(clean_text)
                print(f"  第{i+1}页：{len(clean_text)} 字符内容")
                
        result_doc.close()

        if not duplicate_found:
            print("✅ 未发现续页内容重复问题")
            return True
        else:
            print("❌ 发现续页内容重复问题")
            return False

    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_continuation_pages():
    """测试多个续页场景"""
    print("\n" + "="*60)
    print("🔍 测试多个续页场景")
    print("="*60)

    src_bytes = create_test_pdf(400, 600)
    
    # 创建极端长文本以确保生成多个续页
    extreme_long_text = "这是非常长的文本内容。" * 100
    
    print(f"📝 测试极端长文本")
    print(f"文本长度：{len(extreme_long_text)} 字符")

    try:
        explanations = {0: extreme_long_text}
        result_bytes = compose_pdf(
            src_bytes=src_bytes,
            explanations=explanations,
            right_ratio=0.5,
            font_size=9,  # 更小的字体
            render_mode="text",
            line_spacing=1.1
        )

        result_doc = fitz.open(stream=result_bytes)
        print(f"✅ 生成PDF成功：{result_doc.page_count} 页")

        # 检查内容分布
        total_chars = 0
        page_contents = []
        duplicate_found = False
        
        for i in range(result_doc.page_count):
            page = result_doc.load_page(i)
            text = page.get_text()
            clean_text = text.replace("···PDF··", "").replace("···········", "").strip()
            total_chars += len(clean_text)
            
            # 检查是否有重复内容（使用更宽松的比较方式）
            is_duplicate = False
            for existing_content in page_contents:
                # 如果新内容包含在已有内容中，或者是已有内容的子集，则认为是重复
                if clean_text in existing_content or existing_content in clean_text:
                    # 但要排除非常短的文本（可能是页码等重复元素）
                    if len(clean_text) > 50:
                        is_duplicate = True
                        break
            
            if is_duplicate:
                print(f"❌ 发现重复内容在第{i+1}页")
                duplicate_found = True
            else:
                page_contents.append(clean_text)
                print(f"  第{i+1}页：{len(clean_text)} 字符内容")
            
        result_doc.close()
        
        print(f"总计字符数：{total_chars}")
        print(f"原始文本长度：{len(extreme_long_text)}")
        
        # 检查是否有合理的字符数分布（不应该远远超过原始文本）
        if total_chars < len(extreme_long_text) * 2 and not duplicate_found:  # 允许一些格式字符的增加
            print("✅ 内容分布合理，无明显重复")
            return True
        else:
            print("❌ 内容可能存在重复")
            return False

    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "="*60)
    print("🔍 测试边界情况")
    print("="*60)

    src_bytes = create_test_pdf(400, 600)
    
    # 测试空文本
    try:
        explanations = {0: ""}
        result_bytes = compose_pdf(
            src_bytes=src_bytes,
            explanations=explanations,
            right_ratio=0.5,
            font_size=12,
            render_mode="text",
            line_spacing=1.4
        )
        result_doc = fitz.open(stream=result_bytes)
        print(f"✅ 空文本测试通过：{result_doc.page_count} 页")
        result_doc.close()
    except Exception as e:
        print(f"❌ 空文本测试失败：{e}")
        return False

    # 测试短文本
    try:
        explanations = {0: "短文本测试"}
        result_bytes = compose_pdf(
            src_bytes=src_bytes,
            explanations=explanations,
            right_ratio=0.5,
            font_size=12,
            render_mode="text",
            line_spacing=1.4
        )
        result_doc = fitz.open(stream=result_bytes)
        print(f"✅ 短文本测试通过：{result_doc.page_count} 页")
        result_doc.close()
    except Exception as e:
        print(f"❌ 短文本测试失败：{e}")
        return False

    return True


def main():
    """主测试函数"""
    print("🚀 开始测试续页内容重复问题修复效果\n")
    
    test1_result = test_continuation_page_duplication()
    test2_result = test_multiple_continuation_pages()
    test3_result = test_edge_cases()
    
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    if test1_result and test2_result and test3_result:
        print("🎉 所有测试通过！续页内容重复问题已修复。")
        return True
    else:
        print("⚠️  部分测试失败，请检查上述问题。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)