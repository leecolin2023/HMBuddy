from __future__ import annotations

import os
import platform
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .geometry import extract_ocr_text_boxes
from .tiling import create_ocr_image_tiles, shift_ocr_text_box, tile_owns_text_box
from .types import OcrTextBox


OCR_IMAGE_EXTENSIONS = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
_OCR_INSTANCES: Dict[tuple[str, str], Any] = {}

# OCR 模型档位（沿用 fce 的档案划分；模型文件须预先放置在模型目录内）
OCR_MODEL_PROFILES = {
    "v4": {
        "label": "PP-OCRv4 mobile（基线/回退）",
        "det": "PP-OCRv4_mobile_det_infer",
        "rec": "PP-OCRv4_mobile_rec_infer",
        "det_model_name": "PP-OCRv4_mobile_det",
        "rec_model_name": "PP-OCRv4_mobile_rec",
    },
    "v6-small": {
        "label": "PP-OCRv6 small（默认）",
        "det": "PP-OCRv6_small_det_infer",
        "rec": "PP-OCRv6_small_rec_infer",
        "det_model_name": "PP-OCRv6_small_det",
        "rec_model_name": "PP-OCRv6_small_rec",
    },
    "v6-medium": {
        "label": "PP-OCRv6 medium（高精度）",
        "det": "PP-OCRv6_medium_det_infer",
        "rec": "PP-OCRv6_medium_rec_infer",
        "det_model_name": "PP-OCRv6_medium_det",
        "rec_model_name": "PP-OCRv6_medium_rec",
    },
}
DEFAULT_OCR_MODEL_PROFILE = "v6-small"
# 表格结构识别模型（SLANet_plus，经 paddlex table_recognition 管线调用）
TABLE_STRUCTURE_MODEL_SUBDIR = "SLANet_plus_infer"


def resolve_enable_mkldnn() -> Optional[bool]:
    """Linux CPU 推理在 Paddle 3.3/PaddleOCR 3.7 下可能落入不兼容的 oneDNN 路径。

    默认在 Linux 上关闭 MKLDNN；可用环境变量 HMBUDDY_OCR_ENABLE_MKLDNN
    （兼容 FCE_OCR_ENABLE_MKLDNN）显式覆盖。
    """
    configured = (
        os.environ.get("HMBUDDY_OCR_ENABLE_MKLDNN")
        or os.environ.get("FCE_OCR_ENABLE_MKLDNN")
        or ""
    ).strip().lower()
    if configured in {"1", "true", "yes", "on"}:
        return True
    if configured in {"0", "false", "no", "off"}:
        return False
    if platform.system() == "Linux":
        return False
    return None


def resolve_model_root(custom_model_dir=None) -> Optional[Path]:
    """解析 OCR 模型根目录：显式参数 > 环境变量 > 项目 ./models。

    不会触发任何模型下载。
    """
    candidates: List[Path] = []

    if custom_model_dir:
        candidates.append(Path(custom_model_dir).expanduser())

    env_model_dir = (
        os.environ.get("HMBUDDY_MODEL_DIR") or os.environ.get("FCE_MODEL_DIR")
    )
    if env_model_dir:
        candidates.append(Path(env_model_dir).expanduser())

    # adapters/ocr/engine.py -> 项目根
    project_root = Path(__file__).resolve().parent.parent.parent
    candidates.append(project_root / "models")

    if getattr(sys, "frozen", False):
        executable_dir = Path(sys.executable).resolve().parent
        candidates.insert(0, executable_dir / "models")
        if getattr(sys, "_MEIPASS", None):
            candidates.append(Path(getattr(sys, "_MEIPASS")) / "models")

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def normalize_ocr_model_profile(
    ocr_model: str = DEFAULT_OCR_MODEL_PROFILE,
) -> str:
    profile = str(ocr_model or DEFAULT_OCR_MODEL_PROFILE).strip().lower()
    if profile not in OCR_MODEL_PROFILES:
        raise ValueError(
            "未知 OCR 模型档位：{0}；可选值：{1}".format(
                ocr_model,
                ", ".join(OCR_MODEL_PROFILES),
            )
        )
    return profile


def resolve_ocr_model_paths(model_root: Path, ocr_model: str) -> Dict[str, Path]:
    profile = OCR_MODEL_PROFILES[normalize_ocr_model_profile(ocr_model)]
    return {
        "det": model_root / str(profile["det"]),
        "rec": model_root / str(profile["rec"]),
    }


def get_ocr_instance(
    model_root: Optional[Path],
    ocr_model: str = DEFAULT_OCR_MODEL_PROFILE,
):
    if model_root is None:
        raise RuntimeError("未找到 OCR 模型目录。请设置 HMBUDDY_MODEL_DIR 或放入 ./models。")

    profile_name = normalize_ocr_model_profile(ocr_model)
    resolved_root = str(model_root.resolve())
    cache_key = (resolved_root, profile_name)
    if cache_key in _OCR_INSTANCES:
        return _OCR_INSTANCES[cache_key]

    try:
        from paddleocr import PaddleOCR  # type: ignore
    except ImportError as exc:
        raise RuntimeError("缺少 paddleocr，无法执行扫描件 OCR。") from exc

    model_paths = resolve_ocr_model_paths(model_root, profile_name)
    det_model = model_paths["det"]
    rec_model = model_paths["rec"]
    missing_paths = [str(path) for path in model_paths.values() if not path.exists()]
    if missing_paths:
        raise RuntimeError(
            "OCR 模型档位 {0} 目录不完整：{1}".format(
                profile_name,
                ", ".join(missing_paths),
            )
        )

    profile = OCR_MODEL_PROFILES[profile_name]
    instance_options = {
        "text_detection_model_name": str(profile["det_model_name"]),
        "text_detection_model_dir": str(det_model),
        "text_recognition_model_name": str(profile["rec_model_name"]),
        "text_recognition_model_dir": str(rec_model),
        "use_doc_orientation_classify": False,
        "use_doc_unwarping": False,
        "use_textline_orientation": False,
        "device": "cpu",
    }
    enable_mkldnn = resolve_enable_mkldnn()
    if enable_mkldnn is not None:
        instance_options["enable_mkldnn"] = enable_mkldnn
    instance = PaddleOCR(
        **instance_options,
    )
    _OCR_INSTANCES[cache_key] = instance
    return instance


def run_ocr_without_tiling(path: Path, ocr: Any) -> List[List[OcrTextBox]]:
    page_text_boxes: List[List[OcrTextBox]] = []
    predict = getattr(ocr, "predict", None)
    if callable(predict):
        raw_results = predict(str(path)) or []
    else:
        raw_results = ocr.ocr(str(path), cls=True) or []
    for page_result in raw_results:
        page_text_boxes.append(extract_ocr_text_boxes(page_result))
    return page_text_boxes


def run_ocr_on_path(
    path: Path,
    ocr: Any,
    *,
    progress_func=None,
    progress_label: str = "",
) -> List[List[OcrTextBox]]:
    """对单张图片执行 OCR；超长/超大图片自动分片后合并文本框。"""
    if path.suffix.lower() not in OCR_IMAGE_EXTENSIONS:
        if progress_func:
            progress_func("OCR：{0}".format(progress_label or path.name))
        return run_ocr_without_tiling(path, ocr)

    with tempfile.TemporaryDirectory(prefix="hmbuddy-ocr-tiles-") as temp_dir:
        tiles = create_ocr_image_tiles(path, Path(temp_dir))
        if not tiles:
            if progress_func:
                progress_func("OCR：{0}".format(progress_label or path.name))
            return run_ocr_without_tiling(path, ocr)

        merged_boxes: List[OcrTextBox] = []
        for tile_index, tile in enumerate(tiles, start=1):
            if progress_func:
                progress_func(
                    "OCR 分片 {0}/{1}：{2}".format(
                        tile_index,
                        len(tiles),
                        progress_label or path.name,
                    )
                )
            for page_text_boxes in run_ocr_without_tiling(tile.path, ocr):
                merged_boxes.extend(
                    shift_ocr_text_box(text_box, tile.left, tile.top)
                    for text_box in page_text_boxes
                    if tile_owns_text_box(tile, text_box)
                )
        return [sort_ocr_text_boxes_reading_order(merged_boxes)]
