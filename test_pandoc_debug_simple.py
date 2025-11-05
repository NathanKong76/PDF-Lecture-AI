#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug simple pandoc generation"""

import os
import sys

# Set console encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pandoc_pdf_generator import PandocPDFGenerator

def main():
    print("="*80)
    print(" Simple Pandoc Debug Test")
    print("="*80)
    
    # Check availability
    latex_available, latex_info = PandocPDFGenerator.check_latex_engine_available()
    print(f"\nLaTeX available: {latex_available}")
    print(f"LaTeX info: {latex_info}")
    
    if not latex_available:
        print("\n❌ LaTeX not available, cannot test")
        return
    
    # Simple test
    print("\n" + "="*80)
    print(" Test 1: Minimal content without font")
    print("="*80)
    
    markdown = "# Test\n\nHello World"
    print(f"\nInput markdown:\n{markdown}\n")
    
    pdf_bytes, success = PandocPDFGenerator.generate_pdf(
        markdown_content=markdown,
        width_pt=400.0,
        height_pt=600.0,
        font_name=None,  # No custom font
        font_size=12,
        line_spacing=1.4,
        column_padding=10
    )
    
    print(f"\nResult: success={success}, pdf_size={len(pdf_bytes) if pdf_bytes else 0} bytes")
    
    if not success:
        error = PandocPDFGenerator.get_last_error()
        print(f"\n❌ Error: {error}")
        
        # Get generated LaTeX
        tex = PandocPDFGenerator.get_last_generated_tex()
        if tex:
            print(f"\n{'='*80}")
            print(" Generated LaTeX (first 2000 chars):")
            print("="*80)
            print(tex[:2000])
            print("\n[... truncated ...]" if len(tex) > 2000 else "")
            
            # Save to file for inspection
            with open("debug_latex.tex", "w", encoding="utf-8") as f:
                f.write(tex)
            print(f"\n✓ Full LaTeX saved to: debug_latex.tex")
        else:
            print("\n⚠️  No generated LaTeX available")
    else:
        print(f"\n✅ PDF generated successfully")
        with open("debug_output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print(f"✓ PDF saved to: debug_output.pdf")

if __name__ == "__main__":
    main()

