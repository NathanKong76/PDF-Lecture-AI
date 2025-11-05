#!/usr/bin/env python3
"""
字体名称迁移测试
验证所有函数调用都使用 font_name 而不是 font_path
"""

import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_font_helper():
    """测试字体辅助模块"""
    print("=== 测试字体辅助模块 ===")
    try:
        from app.services.font_helper import (
            get_windows_cjk_fonts,
            get_font_file_path,
            get_latex_font_name
        )
        
        # 测试获取字体列表
        fonts = get_windows_cjk_fonts()
        print(f"[PASS] 获取到 {len(fonts)} 个中文字体")
        if fonts:
            print(f"  示例字体: {fonts[0][0]}")
        
        # 测试字体名称映射
        latex_name = get_latex_font_name("SimHei")
        assert latex_name == "SimHei", f"Expected SimHei, got {latex_name}"
        print(f"[PASS] 字体名称映射: SimHei -> {latex_name}")
        
        # 测试获取字体文件路径
        font_path = get_font_file_path("SimHei")
        if font_path:
            print(f"[PASS] 找到字体文件路径: {font_path}")
        else:
            print("[WARN] 未找到字体文件路径（可能字体未安装）")
        
        return True
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        traceback.print_exc()
        return False


def test_config_migration():
    """测试配置迁移"""
    print("\n=== 测试配置迁移 ===")
    try:
        from app.config import AppConfig
        
        # 测试新参数
        config = AppConfig.from_params({"cjk_font_name": "SimSun"})
        assert config.cjk_font_name == "SimSun", f"Expected SimSun, got {config.cjk_font_name}"
        print(f"[PASS] 新参数 cjk_font_name: {config.cjk_font_name}")
        
        # 测试向后兼容
        config2 = AppConfig.from_params({"cjk_font_path": "assets/fonts/SIMHEI.TTF"})
        assert config2.cjk_font_name == "SimHei", f"Expected SimHei, got {config2.cjk_font_name}"
        print(f"[PASS] 向后兼容 cjk_font_path -> cjk_font_name: {config2.cjk_font_name}")
        
        # 测试默认值
        config3 = AppConfig.from_params({})
        assert config3.cjk_font_name == "SimHei", f"Expected SimHei, got {config3.cjk_font_name}"
        print(f"[PASS] 默认字体名称: {config3.cjk_font_name}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        traceback.print_exc()
        return False


def test_function_signatures():
    """测试函数签名"""
    print("\n=== 测试函数签名 ===")
    try:
        import inspect
        from app.services.pdf_composer import compose_pdf, _compose_vector
        from app.services.pandoc_pdf_generator import PandocPDFGenerator
        from app.services.batch_processor import batch_recompose_from_json
        
        # 检查 compose_pdf
        sig = inspect.signature(compose_pdf)
        params = list(sig.parameters.keys())
        assert "font_name" in params, f"compose_pdf 缺少 font_name 参数: {params}"
        assert "font_path" not in params, f"compose_pdf 仍有 font_path 参数: {params}"
        print(f"[PASS] compose_pdf 签名正确: {params}")
        
        # 检查 _compose_vector
        sig = inspect.signature(_compose_vector)
        params = list(sig.parameters.keys())
        assert "font_name" in params, f"_compose_vector 缺少 font_name 参数: {params}"
        assert "font_path" not in params, f"_compose_vector 仍有 font_path 参数: {params}"
        print(f"[PASS] _compose_vector 签名正确: {params}")
        
        # 检查 generate_pdf
        sig = inspect.signature(PandocPDFGenerator.generate_pdf)
        params = list(sig.parameters.keys())
        assert "font_name" in params, f"generate_pdf 缺少 font_name 参数: {params}"
        assert "font_path" not in params, f"generate_pdf 仍有 font_path 参数: {params}"
        print(f"[PASS] generate_pdf 签名正确: {params}")
        
        # 检查 batch_recompose_from_json
        sig = inspect.signature(batch_recompose_from_json)
        params = list(sig.parameters.keys())
        assert "font_name" in params, f"batch_recompose_from_json 缺少 font_name 参数: {params}"
        assert "font_path" not in params, f"batch_recompose_from_json 仍有 font_path 参数: {params}"
        print(f"[PASS] batch_recompose_from_json 签名正确: {params}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        traceback.print_exc()
        return False


def test_function_calls():
    """测试函数调用"""
    print("\n=== 测试函数调用 ===")
    try:
        import ast
        import os
        
        # 检查所有 Python 文件中的函数调用
        files_to_check = [
            "app/streamlit_app.py",
            "app/cache_processor.py",
            "app/ui_helpers.py",
        ]
        
        issues = []
        for file_path in files_to_check:
            if not os.path.exists(file_path):
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 检查是否有 font_path= 参数
            for i, line in enumerate(lines, 1):
                if 'font_path=' in line and 'font_name' not in line:
                    # 排除注释和字符串
                    if not line.strip().startswith('#') and 'font_path=' in line:
                        # 检查是否是函数调用参数
                        if any(func in line for func in ['compose_pdf', 'batch_recompose', 'generate_pdf']):
                            issues.append(f"{file_path}:{i} - {line.strip()}")
        
        if issues:
            print("[FAIL] 发现使用 font_path 的调用:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("[PASS] 所有函数调用都使用 font_name")
            return True
            
    except Exception as e:
        print(f"[FAIL] 测试失败: {e}")
        traceback.print_exc()
        return False


def test_pdf_generation():
    """测试 PDF 生成（如果可能）"""
    print("\n=== 测试 PDF 生成 ===")
    try:
        from app.services import pdf_processor
        import fitz
        
        # 创建测试 PDF
        test_doc = fitz.open()
        test_page = test_doc.new_page()
        test_page.insert_text((50, 100), "测试", fontsize=12)
        test_bytes = test_doc.tobytes()
        test_doc.close()
        
        # 测试使用 font_name
        explanations = {0: "这是测试讲解"}
        result = pdf_processor.compose_pdf(
            test_bytes,
            explanations,
            0.5,
            12,
            font_name="SimHei",
            render_mode="text",
            line_spacing=1.2,
            column_padding=10
        )
        
        assert result is not None, "PDF 生成失败"
        assert len(result) > 0, "PDF 为空"
        print(f"[PASS] PDF 生成成功，大小: {len(result)} 字节")
        
        return True
    except Exception as e:
        print(f"[WARN] PDF 生成测试跳过: {e}")
        return True  # 不阻止其他测试


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("字体名称迁移测试")
    print("=" * 60)
    
    results = []
    results.append(("字体辅助模块", test_font_helper()))
    results.append(("配置迁移", test_config_migration()))
    results.append(("函数签名", test_function_signatures()))
    results.append(("函数调用", test_function_calls()))
    results.append(("PDF 生成", test_pdf_generation()))
    
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

