"""OCR 子包纯逻辑 Eval（不依赖 paddleocr，任何环境可运行）。

真实 OCR 推理链路需要 paddleocr + 本地模型目录（默认关闭，见 adapters/ocr/engine.py），
此处验证移植过来的几何/分片/后处理规则本身。
"""
from adapters.ocr.geometry import (
    extract_ocr_text_boxes,
    group_ocr_text_boxes_into_rows,
    sort_ocr_text_boxes_reading_order,
)
from adapters.ocr.postprocess import (
    normalize_ocr_dash_candidates,
    normalize_ocr_english_spacing,
    postprocess_ocr_text_boxes_with_report,
)
from adapters.ocr.tiling import (
    build_ocr_owner_spans,
    build_ocr_tile_spans,
    tile_owns_text_box,
)
from adapters.ocr.types import OcrTextBox


def _box(text, x0, top, x1, bottom, score=0.9):
    x, t, x2, b = float(x0), float(top), float(x1), float(bottom)
    return OcrTextBox(
        text=text,
        score=score,
        box=[x, t, x2, b],
        polygon=[[x, t], [x2, t], [x2, b], [x, b]],
    )


# ---------------------------------------------------------------------------
# 破折号还原（fce: normalize_ocr_dash_candidates）
# ---------------------------------------------------------------------------

def test_dash_confusion_restored_between_cjk():
    assert normalize_ocr_dash_candidates("第一一章") == "第——章"


def test_dash_confusion_kept_for_lexical_usage():
    assert normalize_ocr_dash_candidates("状态一一对应") == "状态一一对应"


# ---------------------------------------------------------------------------
# 英文间距（fce: normalize_ocr_english_spacing）
# ---------------------------------------------------------------------------

def test_english_spacing_added_around_cjk():
    assert normalize_ocr_english_spacing("在Python和Go之间") == "在 Python 和 Go 之间"


def test_compact_english_phrase_expanded():
    assert normalize_ocr_english_spacing("googlereader") == "Google Reader"


# ---------------------------------------------------------------------------
# 分片（fce: build_ocr_tile_spans / tile_owns_text_box）
# ---------------------------------------------------------------------------

def test_tile_spans_cover_full_length_with_overlap():
    spans = build_ocr_tile_spans(7000)
    assert spans == [(0, 3000), (2744, 5744), (5488, 7000)]
    assert spans[1][0] - spans[0][1] == -256  # 相邻分片重叠 256


def test_tile_spans_single_when_small():
    assert build_ocr_tile_spans(1500) == [(0, 1500)]


def test_owner_spans_partition_space():
    spans = [(0, 100), (80, 200)]
    owners = build_ocr_owner_spans(spans)
    assert owners == [(0.0, 90.0), (90.0, 200.0)]


def test_tile_ownership_deduplicates_overlap_zone():
    spans = build_ocr_tile_spans(4000)
    owners = build_ocr_owner_spans(spans)
    tiles = _make_tiles(spans, owners)
    # 重叠区中心点（绝对坐标 x≈3000）只应被一个分片认领。
    # tile_owns_text_box 接收分片局部坐标（内部再加 tile.left 偏移）。
    absolute_center = 3000.0
    owners_count = sum(
        1
        for tile in tiles
        if tile_owns_text_box(
            tile,
            _box("词", absolute_center - tile.left, 0, absolute_center - tile.left + 100, 20),
        )
    )
    assert owners_count == 1


def _make_tiles(spans, owners):
    from pathlib import Path
    from adapters.ocr.types import OcrImageTile

    tiles = []
    for index, ((start, end), (owner_start, owner_end)) in enumerate(
        zip(spans, owners), start=1
    ):
        tiles.append(
            OcrImageTile(
                path=Path(f"tile-{index}.png"),
                left=start,
                top=0,
                right=end,
                bottom=100,
                owner_left=owner_start,
                owner_top=0.0,
                owner_right=owner_end,
                owner_bottom=100.0,
            )
        )
    return tiles


# ---------------------------------------------------------------------------
# 行分组与阅读顺序（fce: group_ocr_text_boxes_into_rows）
# ---------------------------------------------------------------------------

def test_boxes_grouped_into_rows_by_y_center():
    boxes = [
        _box("右", 100, 0, 140, 20),
        _box("左", 0, 0, 40, 20),
        _box("下行", 0, 40, 40, 60),
    ]
    rows = group_ocr_text_boxes_into_rows(boxes)
    assert [[item.text for item in row] for row in rows] == [
        ["左", "右"],
        ["下行"],
    ]
    ordered = sort_ocr_text_boxes_reading_order(boxes)
    assert [item.text for item in ordered] == ["左", "右", "下行"]


# ---------------------------------------------------------------------------
# 结果解析（fce: extract_ocr_text_boxes，PaddleOCR 3.x Mapping 风格）
# ---------------------------------------------------------------------------

def test_extract_text_boxes_from_mapping_result():
    page_result = {
        "rec_texts": ["季度", "1200"],
        "rec_scores": [0.98, 0.91],
        "rec_polys": [
            [[0, 0], [50, 0], [50, 20], [0, 20]],
            [[0, 30], [50, 30], [50, 50], [0, 50]],
        ],
        "rec_boxes": [],
    }
    boxes = extract_ocr_text_boxes(page_result)
    assert [item.text for item in boxes] == ["季度", "1200"]
    assert boxes[0].score == 0.98
    assert boxes[0].box == [0.0, 0.0, 50.0, 20.0]


# ---------------------------------------------------------------------------
# 后处理报告（fce: postprocess_ocr_text_boxes_with_report）
# ---------------------------------------------------------------------------

def test_postprocess_reports_transformations():
    boxes = [_box("第一一章", 0, 0, 100, 20)]
    processed, transformations = postprocess_ocr_text_boxes_with_report(boxes)
    assert processed[0].text == "第——章"
    dash_rule = next(t for t in transformations if t.rule_id == "ocr.dash-confusion")
    assert dash_rule.count == 1


def test_postprocess_infers_list_markers():
    boxes = [
        _box("• 已识别项", 100, 0, 300, 20),
        _box("缩进项一", 140, 30, 340, 50),
        _box("缩进项二", 140, 60, 340, 80),
    ]
    processed, transformations = postprocess_ocr_text_boxes_with_report(boxes)
    texts = [item.text for item in processed]
    assert texts[1] == "• 缩进项一"
    assert texts[2] == "• 缩进项二"
    list_rule = next(t for t in transformations if t.rule_id == "ocr.list-marker")
    assert list_rule.count == 2
