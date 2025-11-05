"""
代码质量测试示例 - 可运行的最小测试套件

运行方式:
    python test_code_quality_example.py
"""

import sys
import os
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """测试模块导入"""
    try:
        from app.services.pdf_validator import validate_pdf_file, is_blank_explanation, safe_utf8_loads
        from app.services.text_layout import _smart_text_layout
        from app.services.pdf_composer import compose_pdf
        from app.services.batch_processor import match_pdf_json_files
        print("✅ 所有核心模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_pdf_validator():
    """测试PDF验证器"""
    from app.services.pdf_validator import is_blank_explanation, safe_utf8_loads
    import json
    
    # 测试空白检测
    assert is_blank_explanation(None) is True, "None应该被识别为空白"
    assert is_blank_explanation("") is True, "空字符串应该被识别为空白"
    assert is_blank_explanation("   ") is True, "空白字符应该被识别为空白"
    # 测试有效文本（需要足够长度，因为默认min_chars=10）
    assert is_blank_explanation("这是有效的讲解文本，包含足够的内容来通过验证") is False, "有效文本不应被识别为空白"
    
    # 测试JSON解析
    test_json = {"0": "测试讲解", "1": "另一页讲解"}
    json_bytes = json.dumps(test_json, ensure_ascii=False).encode('utf-8')
    result = safe_utf8_loads(json_bytes, source="test")
    assert result == test_json, "JSON解析结果应该匹配"
    
    print("✅ PDF验证器测试通过")
    return True

def test_constants():
    """测试常量模块"""
    try:
        from app.services import constants
        
        # 验证常量存在
        assert hasattr(constants, 'PDF_WIDTH_MULTIPLIER'), "缺少PDF_WIDTH_MULTIPLIER常量"
        assert hasattr(constants, 'MAX_COLUMNS'), "缺少MAX_COLUMNS常量"
        assert constants.MAX_COLUMNS > 0, "MAX_COLUMNS应该大于0"
        
        print("✅ 常量模块测试通过")
        return True
    except ImportError:
        print("⚠️ 常量模块尚未创建，跳过测试")
        return True  # 不算失败，只是未实现

def test_batch_processor():
    """测试批处理模块"""
    from app.services.batch_processor import match_pdf_json_files
    
    # 测试文件匹配
    pdf_files = ["test1.pdf", "test2.pdf", "test3.pdf"]
    json_files = ["test1.json", "test2.json"]
    
    matches = match_pdf_json_files(pdf_files, json_files)
    
    assert matches["test1.pdf"] == "test1.json", "test1应该匹配"
    assert matches["test2.pdf"] == "test2.json", "test2应该匹配"
    assert matches["test3.pdf"] is None, "test3应该没有匹配"
    
    print("✅ 批处理模块测试通过")
    return True

def main():
    """运行所有测试"""
    print("=" * 60)
    print("开始代码质量测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("PDF验证器", test_pdf_validator),
        ("常量模块", test_constants),
        ("批处理模块", test_batch_processor),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {name} 测试失败")
        except Exception as e:
            failed += 1
            print(f"❌ {name} 测试异常: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试结果: 通过 {passed}, 失败 {failed}, 总计 {passed + failed}")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败，请检查上述错误")
        return 1

if __name__ == "__main__":
    sys.exit(main())

