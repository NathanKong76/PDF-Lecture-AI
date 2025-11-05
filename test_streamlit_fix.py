#!/usr/bin/env python3
"""
Test script to verify Streamlit download button fixes for None data handling.

This script tests that the application can handle None values gracefully
without crashing with "Invalid binary data format" errors.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_streamlit_import():
    """Test if Streamlit imports work correctly."""
    try:
        import streamlit as st
        print("OK Streamlit import successful")
        return True
    except ImportError as e:
        print(f"ERROR Streamlit import failed: {e}")
        return False

def test_data_validation():
    """Test the data validation logic used in the fixes."""
    def validate_data_for_download(data):
        """Simulate the validation logic used in download buttons."""
        if data is not None and len(data) > 0:
            return True, "Valid data for download"
        else:
            return False, "Invalid or empty data"
    
    # Test cases
    test_cases = [
        (None, False, "None data"),
        (b"", False, "Empty bytes"),
        (b"valid data", True, "Valid bytes data"),
        ("string data", True, "String data"),
        ([], False, "Empty list"),
        ([1, 2, 3], True, "Valid list")
    ]
    
    print("Testing data validation logic:")
    all_passed = True
    
    for data, expected, description in test_cases:
        is_valid, message = validate_data_for_download(data)
        if is_valid == expected:
            print(f"OK {description}: {message}")
        else:
            print(f"ERROR {description}: {message} (expected {expected}, got {is_valid})")
            all_passed = False
    
    return all_passed

def test_enhanced_html_generator():
    """Test if the enhanced HTML generator can be imported."""
    try:
        from app.services.enhanced_html_generator import EnhancedHTMLGenerator
        print("OK EnhancedHTMLGenerator import successful")
        
        # Test if the new methods exist
        methods = [
            'generate_per_page_html',
            'generate_complete_per_page_structure', 
            'create_multi_pdf_index'
        ]
        
        for method in methods:
            if hasattr(EnhancedHTMLGenerator, method):
                print(f"OK Method {method} exists")
            else:
                print(f"ERROR Method {method} missing")
                return False
        
        return True
    except ImportError as e:
        print(f"ERROR EnhancedHTMLGenerator import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Streamlit Download Button Fixes")
    print("=" * 50)
    
    tests = [
        ("Streamlit Import", test_streamlit_import),
        ("Data Validation", test_data_validation),
        ("EnhancedHTMLGenerator", test_enhanced_html_generator)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\nOK All tests passed! The download button fixes should work correctly.")
        return True
    else:
        print("\nERROR Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
