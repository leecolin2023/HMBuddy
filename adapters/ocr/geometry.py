from __future__ import annotations

from collections.abc import Mapping
from typing import List, Optional

from .types import OcrTextBox


def normalize_ocr_polygon(raw_box: object) -> Optional[List[List[float]]]:
    if hasattr(raw_box, "tolist"):
        raw_box = raw_box.tolist()
    if not isinstance(raw_box, (list, tuple)) or len(raw_box) < 4:
        return None

    normalized: List[List[float]] = []
    for point in raw_box:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            return None
        try:
            normalized.append([float(point[0]), float(point[1])])
        except (TypeError, ValueError):
            return None
    return normalized


def polygon_to_box(polygon: List[List[float]]) -> List[float]:
    x_coords = [point[0] for point in polygon]
    y_coords = [point[1] for point in polygon]
    return [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]


def extract_ocr_text_boxes(page_result: object) -> List[OcrTextBox]:
    text_boxes: List[OcrTextBox] = []

    # PaddleOCR 3.x 返回 Mapping 风格的 OCRResult；字段均可能是 numpy 数组。
    if isinstance(page_result, Mapping):
        texts = page_result.get("rec_texts")
        scores = page_result.get("rec_scores")
        polygons = page_result.get("rec_polys")
        boxes = page_result.get("rec_boxes")
        texts = [] if texts is None else texts
        scores = [] if scores is None else scores
        polygons = [] if polygons is None else polygons
        boxes = [] if boxes is None else boxes
        for value_name, value in (
            ("texts", texts),
            ("scores", scores),
            ("polygons", polygons),
            ("boxes", boxes),
        ):
            if hasattr(value, "tolist"):
                converted = value.tolist()
                if value_name == "texts":
                    texts = converted
                elif value_name == "scores":
                    scores = converted
                elif value_name == "polygons":
                    polygons = converted
                else:
                    boxes = converted

        for index, raw_text in enumerate(texts):
            text = str(raw_text or "").strip()
            if not text:
                continue
            raw_polygon = polygons[index] if index < len(polygons) else None
            polygon = normalize_ocr_polygon(raw_polygon)
            if polygon is None and index < len(boxes):
                raw_box = boxes[index]
                if hasattr(raw_box, "tolist"):
                    raw_box = raw_box.tolist()
                if isinstance(raw_box, (list, tuple)) and len(raw_box) >= 4:
                    try:
                        x1, y1, x2, y2 = (float(raw_box[item]) for item in range(4))
                        polygon = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
                    except (TypeError, ValueError):
                        polygon = None
            if polygon is None:
                continue
            try:
                score = float(scores[index]) if index < len(scores) else 0.0
            except (TypeError, ValueError):
                score = 0.0
            text_boxes.append(
                OcrTextBox(
                    text=text,
                    score=score,
                    box=polygon_to_box(polygon),
                    polygon=polygon,
                )
            )
        return text_boxes

    # 保留 PaddleOCR 2.x 嵌套列表结果的兼容解析。
    if not isinstance(page_result, list):
        return text_boxes

    for line in page_result:
        if not isinstance(line, (list, tuple)) or len(line) < 2:
            continue
        polygon = normalize_ocr_polygon(line[0])
        recognition = line[1]
        if polygon is None or not isinstance(recognition, (list, tuple)) or not recognition:
            continue

        text = str(recognition[0] or "").strip()
        if not text:
            continue
        try:
            score = float(recognition[1]) if len(recognition) > 1 else 0.0
        except (TypeError, ValueError):
            score = 0.0

        text_boxes.append(
            OcrTextBox(
                text=text,
                score=score,
                box=polygon_to_box(polygon),
                polygon=polygon,
            )
        )

    return text_boxes


def group_ocr_text_boxes_into_rows(
    text_boxes: List[OcrTextBox],
) -> List[List[OcrTextBox]]:
    if not text_boxes:
        return []

    heights = [max(item.box[3] - item.box[1], 1.0) for item in text_boxes]
    average_height = sum(heights) / len(heights)
    row_tolerance = max(6.0, average_height * 0.6)

    rows: List[List[OcrTextBox]] = []
    for text_box in sorted(
        text_boxes,
        key=lambda item: ((item.box[1] + item.box[3]) / 2.0, item.box[0]),
    ):
        y_center = (text_box.box[1] + text_box.box[3]) / 2.0
        if rows:
            last_row = rows[-1]
            last_y_center = sum(
                (item.box[1] + item.box[3]) / 2.0 for item in last_row
            ) / len(last_row)
            if abs(y_center - last_y_center) <= row_tolerance:
                last_row.append(text_box)
                continue
        rows.append([text_box])

    for row in rows:
        row.sort(key=lambda item: item.box[0])
    return rows


def sort_ocr_text_boxes_reading_order(
    text_boxes: List[OcrTextBox],
) -> List[OcrTextBox]:
    return [item for row in group_ocr_text_boxes_into_rows(text_boxes) for item in row]
