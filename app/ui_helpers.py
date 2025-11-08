"""
UI helper functions for Streamlit app.

This module contains helper functions to reduce code duplication
and improve maintainability of the main Streamlit app.
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
import streamlit as st

from app.services import pdf_processor
from app.services import constants


class StateManager:
    """Manages Streamlit session state with type safety."""
    
    @staticmethod
    def initialize():
        """Initialize all required session state variables."""
        defaults = {
            "batch_results": {},
            "batch_processing": False,
            "batch_zip_bytes": None,
            "batch_json_results": {},
            "batch_json_processing": False,
            "batch_json_zip_bytes": None,
            "detailed_progress_tracker": None,
        }
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def get_batch_results() -> Dict[str, Dict[str, Any]]:
        """Get batch results from session state."""
        return st.session_state.get("batch_results", {})
    
    @staticmethod
    def set_batch_results(value: Dict[str, Dict[str, Any]]):
        """Set batch results in session state."""
        st.session_state["batch_results"] = value
    
    @staticmethod
    def is_processing() -> bool:
        """Check if batch processing is in progress."""
        return st.session_state.get("batch_processing", False)
    
    @staticmethod
    def set_processing(value: bool):
        """Set batch processing status."""
        st.session_state["batch_processing"] = value
    
    @staticmethod
    def get_progress_tracker():
        """Get detailed progress tracker from session state."""
        return st.session_state.get("detailed_progress_tracker")
    
    @staticmethod
    def set_progress_tracker(tracker):
        """Set detailed progress tracker in session state."""
        st.session_state["detailed_progress_tracker"] = tracker


def display_batch_status():
    """Display current batch processing status."""
    batch_results = StateManager.get_batch_results()
    if not batch_results:
        return
    
    total_files = len(batch_results)
    completed_files = sum(1 for r in batch_results.values() if r.get("status") == "completed")
    failed_files = sum(1 for r in batch_results.values() if r.get("status") == "failed")
    processing_files = sum(1 for r in batch_results.values() if r.get("status") == "processing")
    
    if processing_files > 0:
        st.info(f"🔄 正在处理中... 已完成: {completed_files}/{total_files} 个文件")
    elif completed_files > 0:
        st.success(f"✅ 处理完成！成功: {completed_files} 个文件，失败: {failed_files} 个文件")
    elif failed_files > 0:
        st.error(f"❌ 处理失败！失败: {failed_files} 个文件")


def validate_file_upload(uploaded_files: List, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate file upload and parameters.
    
    Args:
        uploaded_files: List of uploaded files
        params: Processing parameters
        
    Returns:
        (is_valid, error_message)
    """
    if not uploaded_files:
        return False, "请先上传 PDF 文件"
    
    if len(uploaded_files) > constants.MAX_FILES_PER_BATCH:
        return False, f"最多只能上传{constants.MAX_FILES_PER_BATCH}个文件"
    
    if not params.get("api_key"):
        provider = (params.get("llm_provider") or "gemini").lower()
        if provider == "openai":
            return False, "请在侧边栏填写 OpenAI API Key"
        return False, "请在侧边栏填写 GEMINI_API_KEY"
    
    return True, None


def process_single_file_pdf(
    uploaded_file: Optional[Any],
    filename: str,
    src_bytes: bytes,
    params: Dict[str, Any],
    cached_result: Optional[Dict[str, Any]],
    file_hash: str,
    on_progress: Optional[Callable[[int, int], None]] = None,
    on_page_status: Optional[Callable[[int, str, Optional[str]], None]] = None,
) -> Dict[str, Any]:
    """
    Process a single PDF file in PDF mode.
    
    Args:
        uploaded_file: Uploaded file object (optional, not used if src_bytes provided)
        filename: File name
        src_bytes: PDF file bytes
        params: Processing parameters
        cached_result: Cached result if available
        file_hash: File hash for cache
        on_progress: Progress callback (done, total)
        on_page_status: Page status callback (page_index, status, error)
        
    Returns:
        Processing result dictionary
    """
    from app.cache_processor import get_file_hash, save_result_to_file, load_result_from_file
    
    column_padding_value = params.get("column_padding", 10)
    
    # Try to use cached result
    if cached_result and cached_result.get("status") == "completed":
        st.info(f"📋 {filename} 使用缓存结果")
        try:
            result_bytes = pdf_processor.compose_pdf(
                src_bytes,
                cached_result["explanations"],
                params["right_ratio"],
                params["font_size"],
                font_name=(params.get("cjk_font_name") or "SimHei"),
                render_mode=params.get("render_mode", "markdown"),
                line_spacing=params["line_spacing"],
                column_padding=column_padding_value
            )
            return {
                "status": "completed",
                "pdf_bytes": result_bytes,
                "explanations": cached_result["explanations"],
                "failed_pages": cached_result["failed_pages"],
                "json_bytes": None
            }
        except Exception as e:
            st.warning(f"缓存重新合成失败，尝试重新处理: {str(e)}")
            # Fall through to reprocessing
    
    # Process from scratch with progress callbacks
    try:
        explanations, preview_images, failed_pages = pdf_processor.generate_explanations(
            src_bytes=src_bytes,
            api_key=params["api_key"],
            model_name=params["model_name"],
            user_prompt=params["user_prompt"],
            temperature=params["temperature"],
            max_tokens=params["max_tokens"],
            dpi=params["dpi"],
            concurrency=params["concurrency"],
            rpm_limit=params["rpm_limit"],
            tpm_budget=params["tpm_budget"],
            rpd_limit=params["rpd_limit"],
            on_progress=on_progress,
            use_context=params.get("use_context", False),
            context_prompt=params.get("context_prompt", None),
            llm_provider=params.get("llm_provider", "gemini"),
            api_base=params.get("api_base"),
            on_page_status=on_page_status,
        )
        
        result_bytes = pdf_processor.compose_pdf(
            src_bytes,
            explanations,
            params["right_ratio"],
            params["font_size"],
            font_name=(params.get("cjk_font_name") or "SimHei"),
            render_mode=params.get("render_mode", "markdown"),
            line_spacing=params["line_spacing"],
            column_padding=column_padding_value
        )
        
        result = {
            "status": "completed",
            "pdf_bytes": result_bytes,
            "explanations": explanations,
            "failed_pages": failed_pages
        }
        
        # Save to cache file
        save_result_to_file(file_hash, result)
        
        return result
        
    except Exception as e:
        return {
            "status": "failed",
            "pdf_bytes": None,
            "explanations": {},
            "failed_pages": [],
            "error": str(e)
        }


def process_single_file_markdown(
    uploaded_file: Optional[Any],
    filename: str,
    src_bytes: bytes,
    params: Dict[str, Any],
    cached_result: Optional[Dict[str, Any]],
    file_hash: str,
    on_progress: Optional[Callable[[int, int], None]] = None,
    on_page_status: Optional[Callable[[int, str, Optional[str]], None]] = None,
) -> Dict[str, Any]:
    """
    Process a single file in Markdown mode.
    
    Args:
        uploaded_file: Uploaded file object (optional, not used if src_bytes provided)
        filename: File name
        src_bytes: PDF file bytes
        params: Processing parameters
        cached_result: Cached result if available
        file_hash: File hash for cache
        on_progress: Progress callback
        on_page_status: Page status callback
        
    Returns:
        Processing result dictionary
    """
    from app.cache_processor import save_result_to_file
    
    # Try to use cached result
    if cached_result and cached_result.get("status") == "completed":
        st.info(f"📋 {filename} 使用缓存结果")
        try:
            markdown_content, explanations, failed_pages, _ = pdf_processor.process_markdown_mode(
                src_bytes=src_bytes,
                api_key=params["api_key"],
                model_name=params["model_name"],
                user_prompt=params["user_prompt"],
                temperature=params["temperature"],
                max_tokens=params["max_tokens"],
                dpi=params["dpi"],
                screenshot_dpi=params["screenshot_dpi"],
                concurrency=params["concurrency"],
                rpm_limit=params["rpm_limit"],
                tpm_budget=params["tpm_budget"],
                rpd_limit=params["rpd_limit"],
                embed_images=params["embed_images"],
                title=params["markdown_title"],
                use_context=params.get("use_context", False),
                context_prompt=params.get("context_prompt", None),
                llm_provider=params.get("llm_provider", "gemini"),
                api_base=params.get("api_base"),
            )
            return {
                "status": "completed",
                "markdown_content": markdown_content,
                "explanations": explanations,
                "failed_pages": failed_pages
            }
        except Exception as e:
            st.warning(f"缓存重新生成失败，尝试重新处理: {str(e)}")
            # Fall through to reprocessing
    
    # Process from scratch
    with st.spinner(f"处理 {filename} 中..."):
        # Generate explanations with progress callbacks
        explanations, preview_images, failed_pages = pdf_processor.generate_explanations(
            src_bytes=src_bytes,
            api_key=params["api_key"],
            model_name=params["model_name"],
            user_prompt=params["user_prompt"],
            temperature=params["temperature"],
            max_tokens=params["max_tokens"],
            dpi=params["dpi"],
            concurrency=params["concurrency"],
            rpm_limit=params["rpm_limit"],
            tpm_budget=params["tpm_budget"],
            rpd_limit=params["rpd_limit"],
            on_progress=on_progress,
            use_context=params.get("use_context", False),
            context_prompt=params.get("context_prompt", None),
            llm_provider=params.get("llm_provider", "gemini"),
            api_base=params.get("api_base"),
            on_page_status=on_page_status,
        )
        
        # Generate markdown
        markdown_content, _images_dir = pdf_processor.generate_markdown_with_screenshots(
            src_bytes=src_bytes,
            explanations=explanations,
            screenshot_dpi=params["screenshot_dpi"],
            embed_images=params["embed_images"],
            title=params["markdown_title"],
        )
        
        result = {
            "status": "completed",
            "markdown_content": markdown_content,
            "explanations": explanations,
            "failed_pages": failed_pages
        }
        
        # Save to cache
        save_result_to_file(file_hash, result)
        
        return result


def process_single_file_html_screenshot(
    uploaded_file: Optional[Any],
    filename: str,
    src_bytes: bytes,
    params: Dict[str, Any],
    cached_result: Optional[Dict[str, Any]],
    file_hash: str,
    on_progress: Optional[Callable[[int, int], None]] = None,
    on_page_status: Optional[Callable[[int, str, Optional[str]], None]] = None,
) -> Dict[str, Any]:
    """
    Process a single file in HTML screenshot mode.
    
    Args:
        uploaded_file: Uploaded file object (optional, not used if src_bytes provided)
        filename: File name
        src_bytes: PDF file bytes
        params: Processing parameters
        cached_result: Cached result if available
        file_hash: File hash for cache
        on_progress: Progress callback
        on_page_status: Page status callback
        
    Returns:
        Processing result dictionary
    """
    from app.cache_processor import save_result_to_file
    
    # Try to use cached result
    if cached_result and cached_result.get("status") == "completed":
        st.info(f"📋 {filename} 使用缓存结果")
        try:
            # Generate HTML from cached explanations
            base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
            # Use user-configured title if provided, otherwise use filename
            title = params.get("markdown_title", "").strip() or base_name
            html_content = pdf_processor.generate_html_screenshot_document(
                src_bytes=src_bytes,
                explanations=cached_result["explanations"],
                screenshot_dpi=params.get("screenshot_dpi", 150),
                title=title,
                font_name=params.get("cjk_font_name", "SimHei"),
                font_size=params.get("font_size", 14),
                line_spacing=params.get("line_spacing", 1.2),
                column_count=params.get("html_column_count", 2),
                column_gap=params.get("html_column_gap", 20),
                show_column_rule=params.get("html_show_column_rule", True)
            )
            return {
                "status": "completed",
                "html_content": html_content,
                "explanations": cached_result["explanations"],
                "failed_pages": cached_result["failed_pages"]
            }
        except Exception as e:
            st.warning(f"缓存重新生成失败，尝试重新处理: {str(e)}")
            # Fall through to reprocessing
    
    # Process from scratch
    with st.spinner(f"处理 {filename} 中..."):
        # First get explanations (reuse markdown processing for explanation generation)
        explanations, preview_images, failed_pages = pdf_processor.generate_explanations(
            src_bytes=src_bytes,
            api_key=params["api_key"],
            model_name=params["model_name"],
            user_prompt=params["user_prompt"],
            temperature=params["temperature"],
            max_tokens=params["max_tokens"],
            dpi=params["dpi"],
            concurrency=params["concurrency"],
            rpm_limit=params["rpm_limit"],
            tpm_budget=params["tpm_budget"],
            rpd_limit=params["rpd_limit"],
            on_progress=on_progress,
            use_context=params.get("use_context", False),
            context_prompt=params.get("context_prompt", None),
            llm_provider=params.get("llm_provider", "gemini"),
            api_base=params.get("api_base"),
            on_page_status=on_page_status,
        )
        
        if explanations:
            # Generate HTML screenshot document
            try:
                base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
                # Use user-configured title if provided, otherwise use filename
                title = params.get("markdown_title", "").strip() or base_name
                html_content = pdf_processor.generate_html_screenshot_document(
                    src_bytes=src_bytes,
                    explanations=explanations,
                    screenshot_dpi=params.get("screenshot_dpi", 150),
                    title=title,
                    font_name=params.get("cjk_font_name", "SimHei"),
                    font_size=params.get("font_size", 14),
                    line_spacing=params.get("line_spacing", 1.2),
                    column_count=params.get("html_column_count", 2),
                    column_gap=params.get("html_column_gap", 20),
                    show_column_rule=params.get("html_show_column_rule", True)
                )
                result = {
                    "status": "completed",
                    "html_content": html_content,
                    "explanations": explanations,
                    "failed_pages": failed_pages
                }
                save_result_to_file(file_hash, result)
                return result
            except Exception as e:
                return {
                    "status": "failed",
                    "html_content": None,
                    "explanations": {},
                    "failed_pages": [],
                    "error": f"HTML生成失败: {str(e)}"
                }
        else:
            return {
                "status": "failed",
                "html_content": None,
                "explanations": {},
                "failed_pages": [],
                "error": "生成讲解失败"
            }


def process_single_file_html_pdf2htmlex(
    uploaded_file: Optional[Any],
    filename: str,
    src_bytes: bytes,
    params: Dict[str, Any],
    cached_result: Optional[Dict[str, Any]],
    file_hash: str,
    on_progress: Optional[Callable[[int, int], None]] = None,
    on_page_status: Optional[Callable[[int, str, Optional[str]], None]] = None,
) -> Dict[str, Any]:
    """
    Process a single file in HTML pdf2htmlEX mode.
    
    Args:
        uploaded_file: Uploaded file object (optional, not used if src_bytes provided)
        filename: File name
        src_bytes: PDF file bytes
        params: Processing parameters
        cached_result: Cached result if available
        file_hash: File hash for cache
        on_progress: Progress callback
        on_page_status: Page status callback
        
    Returns:
        Processing result dictionary
    """
    from app.cache_processor import save_result_to_file
    
    # Try to use cached result
    if cached_result and cached_result.get("status") == "completed":
        st.info(f"📋 {filename} 使用缓存结果")
        try:
            base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
            title = params.get("markdown_title", "").strip() or base_name
            html_content = pdf_processor.generate_html_pdf2htmlex_document(
                src_bytes=src_bytes,
                explanations=cached_result["explanations"],
                title=title,
                font_name=params.get("cjk_font_name", "SimHei"),
                font_size=params.get("font_size", 14),
                line_spacing=params.get("line_spacing", 1.2),
                column_count=params.get("html_column_count", 2),
                column_gap=params.get("html_column_gap", 20),
                show_column_rule=params.get("html_show_column_rule", True)
            )
            return {
                "status": "completed",
                "html_content": html_content,
                "explanations": cached_result["explanations"],
                "failed_pages": cached_result["failed_pages"]
            }
        except Exception as e:
            st.warning(f"缓存重新生成失败，尝试重新处理: {str(e)}")
            # Fall through to reprocessing
    
    # Process from scratch
    with st.spinner(f"处理 {filename} 中..."):
        # First get explanations
        explanations, preview_images, failed_pages = pdf_processor.generate_explanations(
            src_bytes=src_bytes,
            api_key=params["api_key"],
            model_name=params["model_name"],
            user_prompt=params["user_prompt"],
            temperature=params["temperature"],
            max_tokens=params["max_tokens"],
            dpi=params["dpi"],
            concurrency=params["concurrency"],
            rpm_limit=params["rpm_limit"],
            tpm_budget=params["tpm_budget"],
            rpd_limit=params["rpd_limit"],
            on_progress=on_progress,
            use_context=params.get("use_context", False),
            context_prompt=params.get("context_prompt", None),
            llm_provider=params.get("llm_provider", "gemini"),
            api_base=params.get("api_base"),
            on_page_status=on_page_status,
        )
        
        if explanations:
            try:
                base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
                title = params.get("markdown_title", "").strip() or base_name
                html_content = pdf_processor.generate_html_pdf2htmlex_document(
                    src_bytes=src_bytes,
                    explanations=explanations,
                    title=title,
                    font_name=params.get("cjk_font_name", "SimHei"),
                    font_size=params.get("font_size", 14),
                    line_spacing=params.get("line_spacing", 1.2),
                    column_count=params.get("html_column_count", 2),
                    column_gap=params.get("html_column_gap", 20),
                    show_column_rule=params.get("html_show_column_rule", True)
                )
                result = {
                    "status": "completed",
                    "html_content": html_content,
                    "explanations": explanations,
                    "failed_pages": failed_pages
                }
                save_result_to_file(file_hash, result)
                return result
            except Exception as e:
                return {
                    "status": "failed",
                    "html_content": None,
                    "explanations": {},
                    "failed_pages": [],
                    "error": f"HTML生成失败: {str(e)}"
                }
        else:
            return {
                "status": "failed",
                "html_content": None,
                "explanations": {},
                "failed_pages": [],
                "error": "生成讲解失败"
            }


def process_single_file(
    src_bytes: bytes,
    filename: str,
    params: Dict[str, Any],
    file_hash: str,
    cached_result: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Process a single uploaded file.
    
    Args:
        src_bytes: PDF file bytes (already read)
        filename: File name
        params: Processing parameters
        file_hash: File hash for cache
        cached_result: Cached result if available
        
    Returns:
        Processing result dictionary
    """
    try:
        # Validate PDF file
        is_valid, validation_error = pdf_processor.validate_pdf_file(src_bytes)
        if not is_valid:
            return {
                "status": "failed",
                "pdf_bytes": None,
                "explanations": {},
                "failed_pages": [],
                "error": f"PDF文件验证失败: {validation_error}"
            }
        
        # Process based on output mode
        output_mode = params.get("output_mode", "PDF讲解版")
        if output_mode == "Markdown截图讲解":
            return process_single_file_markdown(
                None, filename, src_bytes, params, cached_result, file_hash
            )
        elif output_mode == "HTML截图版":
            return process_single_file_html_screenshot(
                None, filename, src_bytes, params, cached_result, file_hash
            )
        elif output_mode == "HTML-pdf2htmlEX版":
            return process_single_file_html_pdf2htmlex(
                None, filename, src_bytes, params, cached_result, file_hash
            )
        else:
            return process_single_file_pdf(
                None, filename, src_bytes, params, cached_result, file_hash
            )
            
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error processing file {filename}: {e}", exc_info=True)
        return {
            "status": "failed",
            "pdf_bytes": None,
            "explanations": {},
            "failed_pages": [],
            "error": str(e)
        }


def process_single_file_with_progress(
    src_bytes: bytes,
    filename: str,
    params: Dict[str, Any],
    file_hash: str,
    cached_result: Optional[Dict[str, Any]],
    on_progress: Optional[Callable[[int, int], None]] = None,
    on_page_status: Optional[Callable[[int, str, Optional[str]], None]] = None,
) -> Dict[str, Any]:
    """
    Process a single uploaded file with progress callbacks.
    
    Args:
        src_bytes: PDF file bytes (already read)
        filename: File name
        params: Processing parameters
        file_hash: File hash for cache
        cached_result: Cached result if available
        on_progress: Progress callback (done, total)
        on_page_status: Page status callback (page_index, status, error)
        
    Returns:
        Processing result dictionary
    """
    try:
        # Validate PDF file
        is_valid, validation_error = pdf_processor.validate_pdf_file(src_bytes)
        if not is_valid:
            return {
                "status": "failed",
                "pdf_bytes": None,
                "explanations": {},
                "failed_pages": [],
                "error": f"PDF文件验证失败: {validation_error}"
            }
        
        # Process based on output mode
        output_mode = params.get("output_mode", "PDF讲解版")
        if output_mode == "Markdown截图讲解":
            return process_single_file_markdown(
                None, filename, src_bytes, params, cached_result, file_hash,
                on_progress=on_progress, on_page_status=on_page_status
            )
        elif output_mode == "HTML截图版":
            return process_single_file_html_screenshot(
                None, filename, src_bytes, params, cached_result, file_hash,
                on_progress=on_progress, on_page_status=on_page_status
            )
        elif output_mode == "HTML-pdf2htmlEX版":
            return process_single_file_html_pdf2htmlex(
                None, filename, src_bytes, params, cached_result, file_hash,
                on_progress=on_progress, on_page_status=on_page_status
            )
        else:
            return process_single_file_pdf(
                None, filename, src_bytes, params, cached_result, file_hash,
                on_progress=on_progress, on_page_status=on_page_status
            )
            
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error processing file {filename}: {e}", exc_info=True)
        return {
            "status": "failed",
            "pdf_bytes": None,
            "explanations": {},
            "failed_pages": [],
            "error": str(e)
        }


def display_file_result(filename: str, result: Dict[str, Any]):
    """
    Display processing result for a single file.
    
    Args:
        filename: File name
        result: Processing result dictionary
    """
    if result.get("status") == "completed":
        st.success(f"✅ {filename} 处理完成！")
        if result.get("failed_pages"):
            st.warning(f"⚠️ {filename} 中 {len(result['failed_pages'])} 页生成讲解失败")
    elif result.get("status") == "failed":
        st.error(f"❌ {filename} 处理失败: {result.get('error', '未知错误')}")


def build_zip_cache_pdf(batch_results: Dict[str, Dict[str, Any]]) -> Optional[bytes]:
    """Build ZIP file containing PDFs and JSONs from batch results."""
    import zipfile
    import io
    import json
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, result in batch_results.items():
            if result.get("status") == "completed":
                base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
                
                # Add PDF
                if result.get("pdf_bytes"):
                    zip_file.writestr(
                        f"{base_name}讲解版.pdf",
                        result["pdf_bytes"]
                    )
                
                # Add JSON
                if result.get("explanations"):
                    json_bytes = json.dumps(
                        result["explanations"],
                        ensure_ascii=False,
                        indent=2
                    ).encode("utf-8")
                    zip_file.writestr(
                        f"{base_name}.json",
                        json_bytes
                    )
    
    zip_buffer.seek(0)
    return zip_buffer.read() if zip_buffer.getvalue() else None


def build_zip_cache_markdown(batch_results: Dict[str, Dict[str, Any]]) -> Optional[bytes]:
    """Build ZIP file containing Markdown files and JSONs from batch results."""
    import zipfile
    import io
    import json
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, result in batch_results.items():
            if result.get("status") == "completed":
                base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
                
                # Add Markdown
                if result.get("markdown_content"):
                    zip_file.writestr(
                        f"{base_name}讲解文档.md",
                        result["markdown_content"].encode("utf-8")
                    )
                
                # Add JSON
                if result.get("explanations"):
                    json_bytes = json.dumps(
                        result["explanations"],
                        ensure_ascii=False,
                        indent=2
                    ).encode("utf-8")
                    zip_file.writestr(
                        f"{base_name}.json",
                        json_bytes
                    )
    
    zip_buffer.seek(0)
    return zip_buffer.read() if zip_buffer.getvalue() else None
