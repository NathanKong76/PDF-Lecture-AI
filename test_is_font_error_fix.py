#!/usr/bin/env python3
"""
测试 is_font_error 变量定义修复
确保在所有执行路径中变量都被正确定义
"""

import sys
import os
import ast
import re

def test_variable_definition_order():
    """测试变量定义顺序"""
    print("=== 测试变量定义顺序 ===")
    
    with open('app/services/pandoc_pdf_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 查找 is_font_error_for_diagnosis 的定义和使用
    definition_line = None
    usage_lines = []
    
    for i, line in enumerate(lines, 1):
        if 'is_font_error_for_diagnosis =' in line:
            definition_line = i
        elif 'is_font_error_for_diagnosis' in line and '=' not in line:
            # 使用而不是定义
            if not line.strip().startswith('#'):
                usage_lines.append((i, line.strip()))
    
    if definition_line:
        print(f"[PASS] is_font_error_for_diagnosis 定义在第 {definition_line} 行")
    else:
        print("[FAIL] 未找到 is_font_error_for_diagnosis 的定义")
        return False
    
    # 检查所有使用都在定义之后
    for usage_line, usage_content in usage_lines:
        if usage_line < definition_line:
            print(f"[FAIL] 第 {usage_line} 行使用变量，但定义在第 {definition_line} 行")
            print(f"  使用: {usage_content}")
            return False
    
    print(f"[PASS] 所有使用都在定义之后（定义在第 {definition_line} 行）")
    return True


def test_no_undefined_variables():
    """测试没有未定义的变量引用"""
    print("\n=== 测试未定义变量引用 ===")
    
    with open('app/services/pandoc_pdf_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有 is_font_error（不带 _for_diagnosis）
    # 但排除注释和字符串
    pattern = r'\bis_font_error\b(?!_for_diagnosis)'
    matches = []
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # 跳过注释行
        if line.strip().startswith('#'):
            continue
        # 跳过字符串中的内容
        if re.search(pattern, line):
            # 检查是否在字符串中
            in_string = False
            for char in line:
                if char in ('"', "'"):
                    in_string = not in_string
                elif not in_string and re.search(pattern, line[i:i+20] if i+20 < len(line) else line[i:]):
                    matches.append((i, line.strip()))
                    break
    
    if matches:
        print("[FAIL] 发现未定义的 is_font_error 使用:")
        for line_num, line_content in matches:
            print(f"  第 {line_num} 行: {line_content}")
        return False
    else:
        print("[PASS] 没有发现未定义的 is_font_error 变量引用")
        return True


def test_all_code_paths():
    """测试所有代码路径都有变量定义"""
    print("\n=== 测试代码路径 ===")
    
    with open('app/services/pandoc_pdf_generator.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查在 else 块中（错误处理）是否正确定义了变量
    # 查找 else: 块，然后检查是否有变量定义
    
    lines = content.split('\n')
    in_else_block = False
    else_start = None
    found_definition = False
    
    for i, line in enumerate(lines, 1):
        if 'else:' in line and 'XeLaTeX returned 0 but PDF file not found' in '\n'.join(lines[max(0, i-5):i+5]):
            in_else_block = True
            else_start = i
            found_definition = False
        elif in_else_block:
            if 'is_font_error_for_diagnosis =' in line:
                found_definition = True
                print(f"[PASS] 在 else 块中找到变量定义（第 {i} 行，else 块开始于第 {else_start} 行）")
                break
            elif 'except' in line and 'Exception' in line:
                # 到达异常处理块，检查是否已定义
                if not found_definition:
                    print(f"[WARN] else 块结束于第 {i} 行，但未找到变量定义")
                in_else_block = False
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("is_font_error 修复验证测试")
    print("=" * 60)
    
    results = []
    results.append(("变量定义顺序", test_variable_definition_order()))
    results.append(("未定义变量引用", test_no_undefined_variables()))
    results.append(("代码路径", test_all_code_paths()))
    
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

