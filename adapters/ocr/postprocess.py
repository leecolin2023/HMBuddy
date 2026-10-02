from __future__ import annotations

import re
from typing import List

from ..textnorm import TextTransformation, merge_transformations
from .types import OcrTextBox


OCR_BULLET_PREFIX_PATTERN = re.compile(r"^\s*[•●▪◦]\s*")
OCR_LATIN_WORD_PATTERN = re.compile(r"[A-Za-z]+")
OCR_COMPACT_ENGLISH_PHRASES = {
    "googlereader": "Google Reader",
}
OCR_DASH_LEXICAL_SUFFIXES = (
    "对应",
    "列举",
    "说明",
    "核实",
    "答复",
    "回复",
    "记录",
    "查看",
    "检查",
    "确认",
    "介绍",
    "呈现",
    "列出",
    "解决",
    "落实",
    "兑现",
    "告知",
    "询问",
    "解答",
    "分析",
    "比较",
    "匹配",
    "排查",
    "处理",
    "展示",
    "验证",
    "罗列",
)


def median_number(values: List[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def normalize_ocr_dash_candidates(text: str) -> str:
    """OCR 常把破折号"——"识别成"一一"：按上下文判断是否需要还原。"""
    if "一一" not in text:
        return text

    parts: List[str] = []
    cursor = 0
    for match in re.finditer("一一", text):
        parts.append(text[cursor : match.start()])
        previous = text[match.start() - 1] if match.start() > 0 else ""
        following = text[match.end() :]
        next_character = following[:1]
        lexical_usage = any(
            following.startswith(suffix) for suffix in OCR_DASH_LEXICAL_SUFFIXES
        )
        left_context = (
            not previous
            or "\u3400" <= previous <= "\u9fff"
            or previous in "）】》”’"
        )
        right_context = bool(next_character) and (
            "\u3400" <= next_character <= "\u9fff"
            or next_character in "（【《“‘"
        )
        parts.append(
            "一一" if lexical_usage or not (left_context and right_context) else "——"
        )
        cursor = match.end()
    parts.append(text[cursor:])
    return "".join(parts)


def normalize_ocr_english_spacing(text: str) -> str:
    normalized = text
    for compact, expanded in OCR_COMPACT_ENGLISH_PHRASES.items():
        normalized = re.sub(
            r"(?i)(?<![A-Za-z]){0}(?![A-Za-z])".format(re.escape(compact)),
            expanded,
            normalized,
        )
    contains_cjk = bool(re.search(r"[\u3400-\u9fff]", normalized))
    if contains_cjk and len(normalized.strip()) >= 5:
        normalized = OCR_LATIN_WORD_PATTERN.sub(split_ocr_camel_case_word, normalized)
        normalized = re.sub(r"(?<=[\u3400-\u9fff])(?=[A-Za-z])", " ", normalized)
        normalized = re.sub(r"(?<=[A-Za-z])(?=[\u3400-\u9fff])", " ", normalized)
    return normalized


def split_ocr_camel_case_word(match: re.Match[str]) -> str:
    word = match.group(0)
    if not word[:1].isupper():
        return word
    return re.sub(r"(?<=[a-z])(?=[A-Z][a-z])", " ", word)


def normalize_ocr_text(text: str) -> str:
    return normalize_ocr_english_spacing(normalize_ocr_dash_candidates(text))


def replace_ocr_text(text_box: OcrTextBox, text: str) -> OcrTextBox:
    return OcrTextBox(
        text=text,
        score=text_box.score,
        box=list(text_box.box),
        polygon=[list(point) for point in text_box.polygon],
    )


def restore_split_ocr_english_phrases(
    text_boxes: List[OcrTextBox],
) -> List[OcrTextBox]:
    restored = list(text_boxes)
    for index in range(len(restored) - 1):
        current = restored[index]
        following = restored[index + 1]
        current_match = re.search(r"([A-Za-z]+)$", current.text)
        following_match = re.match(r"^([A-Za-z]+)", following.text)
        if current_match is None or following_match is None:
            continue
        compact_value = (current_match.group(1) + following_match.group(1)).lower()
        expanded = OCR_COMPACT_ENGLISH_PHRASES.get(compact_value)
        if expanded is None:
            continue
        current_text = current.text[: current_match.start()].rstrip()
        following_text = following.text[following_match.end() :].lstrip()
        restored[index] = replace_ocr_text(
            current,
            normalize_ocr_english_spacing(
                "{0} {1}".format(current_text, expanded).strip()
            ),
        )
        restored[index + 1] = replace_ocr_text(
            following,
            normalize_ocr_english_spacing(following_text),
        )
    return restored


def restore_ocr_list_markers(text_boxes: List[OcrTextBox]) -> List[OcrTextBox]:
    """根据已识别的"• "行推断同列缩进的列表项，补回丢失的列表符号。"""
    if not text_boxes:
        return []

    normalized_boxes = [
        replace_ocr_text(
            text_box,
            OCR_BULLET_PREFIX_PATTERN.sub("• ", text_box.text),
        )
        for text_box in text_boxes
    ]
    explicit_indices = [
        index
        for index, text_box in enumerate(normalized_boxes)
        if text_box.text.startswith("• ")
    ]
    if not explicit_indices:
        return normalized_boxes

    heights = [max(item.box[3] - item.box[1], 1.0) for item in normalized_boxes]
    median_height = median_number(heights)
    explicit_width = median_number(
        [
            normalized_boxes[index].box[2] - normalized_boxes[index].box[0]
            for index in explicit_indices
        ]
    )
    search_distance = max(240.0, median_height * 32.0)
    indent_distance = max(24.0, median_height * 1.4)
    x_tolerance = max(10.0, median_height * 0.75)

    candidate_indices: List[int] = []
    for index, text_box in enumerate(normalized_boxes):
        if index in explicit_indices or not text_box.text.strip():
            continue
        y_center = (text_box.box[1] + text_box.box[3]) / 2.0
        nearest_explicit_index = min(
            explicit_indices,
            key=lambda item_index: abs(
                y_center
                - (
                    normalized_boxes[item_index].box[1]
                    + normalized_boxes[item_index].box[3]
                )
                / 2.0
            ),
        )
        explicit_box = normalized_boxes[nearest_explicit_index]
        explicit_y_center = (explicit_box.box[1] + explicit_box.box[3]) / 2.0
        box_width = text_box.box[2] - text_box.box[0]
        if (
            abs(y_center - explicit_y_center) <= search_distance
            and text_box.box[0] >= explicit_box.box[0] + indent_distance
            and box_width >= explicit_width * 0.55
        ):
            candidate_indices.append(index)

    x_clusters: List[List[int]] = []
    for index in sorted(
        candidate_indices, key=lambda item: normalized_boxes[item].box[0]
    ):
        if x_clusters:
            cluster_x = median_number(
                [normalized_boxes[item].box[0] for item in x_clusters[-1]]
            )
            if abs(normalized_boxes[index].box[0] - cluster_x) <= x_tolerance:
                x_clusters[-1].append(index)
                continue
        x_clusters.append([index])

    inferred_indices = {
        index for cluster in x_clusters if len(cluster) >= 2 for index in cluster
    }
    return [
        replace_ocr_text(text_box, "• {0}".format(text_box.text.lstrip()))
        if index in inferred_indices
        else text_box
        for index, text_box in enumerate(normalized_boxes)
    ]


def postprocess_ocr_text_boxes(text_boxes: List[OcrTextBox]) -> List[OcrTextBox]:
    processed, _transformations = postprocess_ocr_text_boxes_with_report(text_boxes)
    return processed


def postprocess_ocr_text_boxes_with_report(
    text_boxes: List[OcrTextBox],
) -> tuple[List[OcrTextBox], List[TextTransformation]]:
    dash_count = sum(
        max(
            item.text.count("一一")
            - normalize_ocr_dash_candidates(item.text).count("一一"),
            0,
        )
        for item in text_boxes
    )
    dash_normalized = [
        replace_ocr_text(item, normalize_ocr_dash_candidates(item.text))
        for item in text_boxes
    ]
    english_normalized = [
        replace_ocr_text(item, normalize_ocr_english_spacing(item.text))
        for item in dash_normalized
    ]
    restored_english = restore_split_ocr_english_phrases(english_normalized)
    english_count = sum(
        1
        for before, after in zip(dash_normalized, restored_english)
        if before.text != after.text
    )
    restored_lists = restore_ocr_list_markers(restored_english)
    list_count = sum(
        1
        for before, after in zip(restored_english, restored_lists)
        if not before.text.startswith("• ") and after.text.startswith("• ")
    )
    transformations = merge_transformations(
        [
            TextTransformation("ocr.dash-confusion", count=dash_count),
            TextTransformation("ocr.english-spacing", count=english_count),
            TextTransformation("ocr.list-marker", count=list_count),
        ]
    )
    return restored_lists, transformations
