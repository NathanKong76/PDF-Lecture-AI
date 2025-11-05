from __future__ import annotations

# Import all functions from the modularized components
from .pdf_validator import (
    safe_utf8_loads,
    is_blank_explanation,
    validate_pdf_file,
    pages_with_blank_explanations
)

from .text_layout import (
    _smart_text_layout
)

from .pdf_composer import (
    _page_png_bytes,
    _compose_vector,
    compose_pdf
)

from .batch_processor import (
    match_pdf_json_files,
    batch_recompose_from_json,
    batch_recompose_from_json_async
)

from .markdown_generator import (
    create_page_screenshot_markdown,
    generate_markdown_with_screenshots
)

# For backward compatibility, import everything into this namespace
__all__ = [
    "safe_utf8_loads",
    "is_blank_explanation",
    "validate_pdf_file",
    "pages_with_blank_explanations",
    "_smart_text_layout",
    "_page_png_bytes",
    "_compose_vector",
    "compose_pdf",
    "match_pdf_json_files",
    "batch_recompose_from_json",
    "batch_recompose_from_json_async",
    "create_page_screenshot_markdown",
    "generate_markdown_with_screenshots"
]