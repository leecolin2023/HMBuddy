"""OCR 子包（移植自 fce/ocr）。

边界约束（沿用 fce/AGENTS.md）：PaddleOCR / paddlex 等重依赖一律懒加载，
模型只从本地目录解析（环境变量 HMBUDDY_MODEL_DIR / FCE_MODEL_DIR 或 ./models），
绝不隐式下载模型。默认链路（enable_ocr=False）完全不触碰本包的重依赖。
"""
from .engine import (
    OCR_IMAGE_EXTENSIONS,
    get_ocr_instance,
    resolve_enable_mkldnn,
    resolve_model_root,
    resolve_ocr_model_paths,
    run_ocr_on_path,
    run_ocr_without_tiling,
)
from .geometry import (
    extract_ocr_text_boxes,
    group_ocr_text_boxes_into_rows,
    normalize_ocr_polygon,
    polygon_to_box,
    sort_ocr_text_boxes_reading_order,
)
from .postprocess import (
    median_number,
    normalize_ocr_dash_candidates,
    normalize_ocr_english_spacing,
    normalize_ocr_text,
    postprocess_ocr_text_boxes,
    postprocess_ocr_text_boxes_with_report,
    replace_ocr_text,
    restore_ocr_list_markers,
    restore_split_ocr_english_phrases,
    split_ocr_camel_case_word,
)
from .tiling import (
    build_ocr_owner_spans,
    build_ocr_tile_spans,
    create_ocr_image_tiles,
    shift_ocr_text_box,
    tile_owns_text_box,
)
from .types import OcrImageTile, OcrTextBox

__all__ = [
    "OCR_IMAGE_EXTENSIONS",
    "OcrImageTile",
    "OcrTextBox",
    "build_ocr_owner_spans",
    "build_ocr_tile_spans",
    "create_ocr_image_tiles",
    "extract_ocr_text_boxes",
    "get_ocr_instance",
    "group_ocr_text_boxes_into_rows",
    "median_number",
    "normalize_ocr_dash_candidates",
    "normalize_ocr_english_spacing",
    "normalize_ocr_polygon",
    "normalize_ocr_text",
    "polygon_to_box",
    "postprocess_ocr_text_boxes",
    "postprocess_ocr_text_boxes_with_report",
    "replace_ocr_text",
    "resolve_enable_mkldnn",
    "resolve_model_root",
    "resolve_ocr_model_paths",
    "restore_ocr_list_markers",
    "restore_split_ocr_english_phrases",
    "run_ocr_on_path",
    "run_ocr_without_tiling",
    "shift_ocr_text_box",
    "sort_ocr_text_boxes_reading_order",
    "split_ocr_camel_case_word",
    "tile_owns_text_box",
]
