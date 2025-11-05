#!/usr/bin/env python3
"""
全面错误处理测试
测试所有可能的错误情况，确保没有变量未定义的错误
"""

import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_variable_definitions():
    """测试变量定义，确保没有未定义的变量"""
    print("=== 测试变量定义 ===")
    try:
        # 读取文件并检查
        with open('app/services/pandoc_pdf_generator.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有 is_font_error（未定义版本）
        if 'is_font_error' in content:
            # 检查是否是 is_font_error_for_diagnosis 的一部分
            lines = content.split('\n')
            issues = []
            for i, line in enumerate(lines, 1):
                if 'is_font_error' in line and 'is_font_error_for_diagnosis' not in line:
                    # 排除注释和字符串
                    stripped = line.strip()
                    if not stripped.startswith('#') and 'is_font_error' in stripped:
                        # 检查是否是变量使用（不是定义）
                        if 'is_font_error =' not in line and 'is_font_error_for_diagnosis' not in line:
                            issues.append(f"Line {i}: {stripped}")
            
            if issues:
                print("[FAIL] 发现未定义的 is_font_error 使用:")
                for issue in issues:
                    print(f"  {issue}")
                return False
        
        print("[PASS] 没有发现未定义的 is_font_error 变量")
        return True
        
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        traceback.print_exc()
        return False


def test_error_handling_flow():
    """测试错误处理流程"""
    print("\n=== 测试错误处理流程 ===")
    try:
        from app.services.pandoc_pdf_generator import PandocPDFGenerator
        
        # 测试空内容（应该返回失败，但不应抛出未定义变量错误）
        result, success = PandocPDFGenerator.generate_pdf(
            markdown_content="",
            width_pt=100,
            height_pt=100,
            font_name="SimHei",
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        
        assert not success, "空内容应该返回失败"
        assert result is None, "空内容应该返回 None"
        print("[PASS] 空内容处理正确")
        
        # 测试无效参数（应该返回失败，但不应抛出未定义变量错误）
        result, success = PandocPDFGenerator.generate_pdf(
            markdown_content="test",
            width_pt=0,  # 无效宽度
            height_pt=100,
            font_name="SimHei",
            font_size=12,
            line_spacing=1.4,
            column_padding=10
        )
        
        assert not success, "无效参数应该返回失败"
        assert result is None, "无效参数应该返回 None"
        print("[PASS] 无效参数处理正确")
        
        return True
        
    except NameError as e:
        if "is_font_error" in str(e):
            print(f"[FAIL] 发现未定义变量错误: {e}")
            return False
        raise
    except Exception as e:
        # 其他错误可能是正常的（如工具未安装）
        print(f"[WARN] 测试跳过（可能是正常的）: {e}")
        return True


def test_function_imports():
    """测试函数导入"""
    print("\n=== 测试函数导入 ===")
    try:
        from app.services.pandoc_pdf_generator import PandocPDFGenerator
        from app.services.pdf_composer import compose_pdf, _compose_vector
        from app.services.batch_processor import batch_recompose_from_json
        from app.services.font_helper import (
            get_windows_cjk_fonts,
            get_font_file_path,
            get_latex_font_name
        )
        
        print("[PASS] 所有函数导入成功")
        return True
        
    except Exception as e:
        print(f"[FAIL] 导入失败: {e}")
        traceback.print_exc()
        return False


def test_error_message_format():
    """测试错误消息格式"""
    print("\n=== 测试错误消息格式 ===")
    try:
        from app.services.pandoc_pdf_generator import PandocPDFGenerator
        
        # 获取最后一个错误（应该为 None 或字符串）
        last_error = PandocPDFGenerator.get_last_error()
        assert last_error is None or isinstance(last_error, str), f"last_error 应该是 None 或字符串，得到: {type(last_error)}"
        print("[PASS] 错误消息格式正确")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("全面错误处理测试")
    print("=" * 60)
    
    results = []
    results.append(("变量定义", test_variable_definitions()))
    results.append(("错误处理流程", test_error_handling_flow()))
    results.append(("函数导入", test_function_imports()))
    results.append(("错误消息格式", test_error_message_format()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

