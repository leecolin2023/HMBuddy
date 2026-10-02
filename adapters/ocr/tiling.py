from __future__ import annotations

from pathlib import Path
from typing import List

from .types import OcrImageTile, OcrTextBox


OCR_TILE_MAX_SIDE = 3000
OCR_TILE_OVERLAP = 256


def build_ocr_tile_spans(
    length: int,
    *,
    max_side: int = OCR_TILE_MAX_SIDE,
    overlap: int = OCR_TILE_OVERLAP,
) -> List[tuple[int, int]]:
    if length <= 0:
        return []
    if max_side <= 0:
        raise ValueError("OCR 分片边长必须大于 0。")
    if overlap < 0 or overlap >= max_side:
        raise ValueError("OCR 分片重叠必须大于等于 0 且小于分片边长。")
    if length <= max_side:
        return [(0, length)]

    spans: List[tuple[int, int]] = []
    start = 0
    while start < length:
        end = min(start + max_side, length)
        spans.append((start, end))
        if end >= length:
            break
        start = end - overlap
    return spans


def build_ocr_owner_spans(
    spans: List[tuple[int, int]],
) -> List[tuple[float, float]]:
    owners: List[tuple[float, float]] = []
    for index, (start, end) in enumerate(spans):
        owner_start = float(start)
        owner_end = float(end)
        if index > 0:
            owner_start = (spans[index - 1][1] + start) / 2.0
        if index + 1 < len(spans):
            owner_end = (end + spans[index + 1][0]) / 2.0
        owners.append((owner_start, owner_end))
    return owners


def create_ocr_image_tiles(
    path: Path,
    output_dir: Path,
    *,
    max_side: int = OCR_TILE_MAX_SIDE,
    overlap: int = OCR_TILE_OVERLAP,
) -> List[OcrImageTile]:
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:
        raise RuntimeError("缺少 pillow，无法对超长图片执行 OCR 分片。") from exc

    with Image.open(path) as image:
        width, height = image.size
        x_spans = build_ocr_tile_spans(width, max_side=max_side, overlap=overlap)
        y_spans = build_ocr_tile_spans(height, max_side=max_side, overlap=overlap)
        if len(x_spans) == 1 and len(y_spans) == 1:
            return []

        x_owners = build_ocr_owner_spans(x_spans)
        y_owners = build_ocr_owner_spans(y_spans)
        tiles: List[OcrImageTile] = []
        tile_index = 1
        for y_index, (top, bottom) in enumerate(y_spans):
            for x_index, (left, right) in enumerate(x_spans):
                tile_path = output_dir / "ocr-tile-{0:04d}.png".format(tile_index)
                tile = image.crop((left, top, right, bottom))
                tile.save(tile_path)
                owner_left, owner_right = x_owners[x_index]
                owner_top, owner_bottom = y_owners[y_index]
                tiles.append(
                    OcrImageTile(
                        path=tile_path,
                        left=left,
                        top=top,
                        right=right,
                        bottom=bottom,
                        owner_left=owner_left,
                        owner_top=owner_top,
                        owner_right=owner_right,
                        owner_bottom=owner_bottom,
                    )
                )
                tile_index += 1
    return tiles


def shift_ocr_text_box(
    text_box: OcrTextBox, x_offset: int, y_offset: int
) -> OcrTextBox:
    return OcrTextBox(
        text=text_box.text,
        score=text_box.score,
        box=[
            text_box.box[0] + x_offset,
            text_box.box[1] + y_offset,
            text_box.box[2] + x_offset,
            text_box.box[3] + y_offset,
        ],
        polygon=[
            [point[0] + x_offset, point[1] + y_offset]
            for point in text_box.polygon
        ],
    )


def tile_owns_text_box(tile: OcrImageTile, text_box: OcrTextBox) -> bool:
    center_x = (text_box.box[0] + text_box.box[2]) / 2.0 + tile.left
    center_y = (text_box.box[1] + text_box.box[3]) / 2.0 + tile.top
    owns_right_edge = float(tile.right) == tile.owner_right
    owns_bottom_edge = float(tile.bottom) == tile.owner_bottom
    within_x = tile.owner_left <= center_x and (
        center_x < tile.owner_right
        or (owns_right_edge and center_x <= tile.owner_right)
    )
    within_y = tile.owner_top <= center_y and (
        center_y < tile.owner_bottom
        or (owns_bottom_edge and center_y <= tile.owner_bottom)
    )
    return within_x and within_y
