"""生成 Phase 1 Eval fixtures（规格第 19 节）。

运行：python evals/fixtures/generate_fixtures.py
依赖：python-docx / openpyxl / python-pptx / fpdf2（均为 dev 依赖）。

生成的样例文件随仓库提交，保证 Eval 可离线复现；修改生成逻辑后需重新运行
并提交更新后的样例。
"""
from __future__ import annotations

import base64
import io
from pathlib import Path

HERE = Path(__file__).parent

# 1x1 红色 PNG，用于给 DOCX/PPTX 提供真实的图片引用
PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
    "AAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def make_docx_standard(path: Path) -> None:
    """标准 DOCX：三级标题结构、正文、一个表格、列表、图片引用（TC-DOCX-01）。"""
    from docx import Document
    from docx.shared import Inches

    doc = Document()
    doc.core_properties.title = "资产池需求方案"

    doc.add_heading("一、项目背景", level=1)
    doc.add_paragraph(
        "随着业务规模扩大，各类资产需要统一入池管理。本文档描述资产池建设的第一阶段需求。"
    )
    doc.add_heading("二、业务流程", level=1)
    doc.add_heading("2.1 申请流程", level=2)
    doc.add_paragraph("业务部门提交入池申请，系统自动采集材料并生成资产档案。")
    doc.add_heading("2.2 审批流程", level=2)
    doc.add_paragraph("审批岗对入池材料进行复核，复核通过后资产正式进入资产池。")
    doc.add_heading("三、系统架构", level=1)
    doc.add_paragraph("系统由采集服务、解析服务与存储服务组成，均部署在内网环境。")

    table = doc.add_table(rows=4, cols=3)
    table.style = "Table Grid"
    data = [
        ["阶段", "操作", "责任主体"],
        ["采集", "上传材料并OCR识别", "系统"],
        ["审核", "人工复核材料完整性", "运营部"],
        ["入库", "资产写入资产池", "系统"],
    ]
    for row_index, row_data in enumerate(data):
        for col_index, cell_text in enumerate(row_data):
            table.rows[row_index].cells[col_index].text = cell_text

    for item in [
        "支持 DOCX/PDF/XLSX/PPTX 四种格式",
        "保留标题、表格等结构",
        "提供统一 Artifact 模型",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_picture(io.BytesIO(PNG_1PX), width=Inches(1))
    doc.save(str(path))


def make_docx_complex(path: Path) -> None:
    """复杂 DOCX：三级标题、两个普通表格 + 一个合并单元格表格 + 嵌套表格（TC-DOCX-01 补充）。"""
    from docx import Document
    from docx.shared import Inches

    doc = Document()
    doc.core_properties.title = "资产池建设总体方案（复杂样例）"

    doc.add_heading("一、总述", level=1)
    doc.add_paragraph("本方案覆盖资产池系统的总体设计、接口与风险。")
    doc.add_heading("二、需求详述", level=1)
    doc.add_heading("2.1 功能需求", level=2)
    doc.add_heading("2.1.1 文件发现", level=3)
    doc.add_paragraph("系统应递归扫描工作目录并忽略临时文件。")
    for item in ["递归遍历", "类型识别", "稳定 ID"]:
        doc.add_paragraph(item, style="List Bullet")
    doc.add_heading("2.1.2 统一读取", level=3)
    doc.add_paragraph("上层统一通过 read_artifact 读取，不感知具体格式。")
    doc.add_heading("2.2 非功能需求", level=2)
    doc.add_paragraph("50MB 以内的常规文件应能稳定解析，超限明确报错。")

    doc.add_heading("三、接口设计", level=1)
    table1 = doc.add_table(rows=4, cols=2)
    table1.style = "Table Grid"
    for row_index, row_data in enumerate(
        [
            ["接口", "说明"],
            ["list_artifacts", "扫描工作区文件"],
            ["read_artifact", "统一读取入口"],
            ["artifact_to_context", "构造 LLM 上下文"],
        ]
    ):
        for col_index, cell_text in enumerate(row_data):
            table1.rows[row_index].cells[col_index].text = cell_text

    doc.add_heading("四、风险与对策", level=1)
    table2 = doc.add_table(rows=3, cols=3)
    table2.style = "Table Grid"
    # 表头第一行前两列合并（colspan=2，用于验证合并单元格识别）
    merged_header = table2.cell(0, 0).merge(table2.cell(0, 1))
    merged_header.text = "风险类别"
    table2.cell(0, 2).text = "应对策略"
    table2.cell(1, 0).text = "扫描版 PDF"
    table2.cell(1, 1).text = "无文本层"
    table2.cell(1, 2).text = "标记 requires_ocr，暂不 OCR"
    table2.cell(2, 0).text = "超大表格"
    table2.cell(2, 1).text = "渲染溢出"
    table2.cell(2, 2).text = "截断并标注"

    doc.add_heading("五、嵌套结构示例", level=1)
    outer_table = doc.add_table(rows=1, cols=1)
    outer_table.style = "Table Grid"
    outer_cell = outer_table.cell(0, 0)
    outer_cell.text = "以下为部门联系人嵌套表格："
    inner_table = outer_cell.add_table(rows=2, cols=2)
    inner_table.style = "Table Grid"
    inner_table.cell(0, 0).text = "姓名"
    inner_table.cell(0, 1).text = "电话"
    inner_table.cell(1, 0).text = "张伟"
    inner_table.cell(1, 1).text = "13800000000"

    doc.add_paragraph("以上风险在第一阶段以标注和截断方式处理，不引入复杂管线。")
    doc.add_picture(io.BytesIO(PNG_1PX), width=Inches(1))
    doc.save(str(path))


def _find_cjk_ttf() -> str | None:
    """找一个系统里可内嵌的中文字体（TTF）。"""
    candidates = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simfang.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for font_path in candidates:
        if Path(font_path).exists():
            return font_path
    return None


def make_pdf_standard(path: Path) -> None:
    """标准 PDF：2 页有文本层，第 2 页含中文段落（TC-PDF-01）。

    使用 fpdf2 内嵌 TTF 字体：reportlab 的 TTF 子集化对 CJK 会写出
    错误的 ToUnicode CMap，导致提取结果乱码（实际观察到的失败）。
    """
    from fpdf import FPDF

    pdf = FPDF(format="A4")
    pdf.add_page()
    font_path = _find_cjk_ttf()
    if font_path is None:
        raise RuntimeError(
            "no CJK TTF font found for PDF fixture generation; "
            "install a Chinese font (e.g. simhei.ttf) or adjust _find_cjk_ttf()"
        )
    pdf.add_font("hmbuddycjk", "", font_path)
    pdf.set_font("hmbuddycjk", size=12)
    pdf.set_title("Quarterly Risk Report 2025 Q3")

    y = 20
    for line in [
        "Quarterly Risk Report 2025 Q3",
        "1. Market Risk",
        "Interest rate volatility increased in Q3.",
        "2. Credit Risk",
        "Overall credit quality remains stable.",
    ]:
        pdf.text(20, y, line)
        y += 10
    pdf.add_page()

    y = 20
    for line in [
        "3. 主要风险结论",
        "报告认为主要风险来自流动性紧张与利率波动，",
        "建议维持现金流缓冲并缩短资产久期。",
    ]:
        pdf.text(20, y, line)
        y += 10
    pdf.output(str(path))


def make_xlsx_standard(path: Path) -> None:
    """标准 XLSX：单 Sheet、公式、合并单元格（TC-XLSX-01）。"""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "资产负债表"
    for row in [
        ["项目", "2024", "2025", "变动"],
        ["营业收入", 1200, 1500, "=C2-B2"],
        ["营业成本", 800, 900, "=C3-B3"],
        ["毛利润", 400, 600, "=C4-B4"],
    ]:
        ws.append(row)
    ws["A6"] = "备注"
    ws["B6"] = "单位：万元"
    ws["A8"] = "注：数据为示例数据"
    ws.merge_cells("A8:D8")
    wb.save(str(path))


def make_xlsx_multisheet(path: Path) -> None:
    """多 Sheet XLSX：3 个 Sheet，含公式与合并单元格（TC-XLSX-01）。"""
    import openpyxl

    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "利润表"
    for row in [
        ["项目", "2024", "2025"],
        ["营业收入", 1200, 1500],
        ["营业成本", 800, 900],
        ["净利润", "=B2-B3", "=C2-C3"],
    ]:
        ws1.append(row)

    ws2 = wb.create_sheet("现金流量表")
    for row in [
        ["项目", "Q1", "Q2"],
        ["经营现金流", 300, 420],
        ["投资现金流", -150, -200],
    ]:
        ws2.append(row)

    ws3 = wb.create_sheet("预算对比")
    for row in [
        ["科目", "预算", "实际"],
        ["差旅费", 50, 63],
        ["会议费", 30, 21],
    ]:
        ws3.append(row)
    ws3["A5"] = "口径：万元"
    ws3.merge_cells("A5:C5")
    wb.save(str(path))


def make_pptx_standard(path: Path) -> None:
    """标准 PPTX：4 页，含标题页、正文页、问题页与表格页（TC-PPTX-01）。"""
    from pptx import Presentation
    from pptx.util import Inches

    prs = Presentation()

    slide1 = prs.slides.add_slide(prs.slide_layouts[0])
    slide1.shapes.title.text = "2025年度经营计划"
    slide1.placeholders[1].text = "战略规划部"

    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "年度目标"
    frame = slide2.placeholders[1].text_frame
    frame.text = "营收增长 20%"
    paragraph = frame.add_paragraph()
    paragraph.text = "成本下降 5%"

    slide3 = prs.slides.add_slide(prs.slide_layouts[1])
    slide3.shapes.title.text = "当前面临的问题"
    frame = slide3.placeholders[1].text_frame
    frame.text = "问题一：文档分散在多个共享目录，查找困难"
    for line in [
        "问题二：格式不统一，难以批量理解",
        "问题三：版本混乱，无法追踪变化",
    ]:
        paragraph = frame.add_paragraph()
        paragraph.text = line

    slide4 = prs.slides.add_slide(prs.slide_layouts[5])
    slide4.shapes.title.text = "季度目标"
    data = [
        ["季度", "目标(亿元)", "负责人"],
        ["Q1", "4.5", "张伟"],
        ["Q2", "5.0", "李娜"],
    ]
    graphic_frame = slide4.shapes.add_table(
        3, 3, Inches(1), Inches(2), Inches(8), Inches(2.5)
    )
    table = graphic_frame.table
    for row_index, row_data in enumerate(data):
        for col_index, cell_text in enumerate(row_data):
            table.cell(row_index, col_index).text = cell_text

    prs.save(str(path))


def make_pdf_table(path: Path) -> None:
    """带边框表格的 PDF：第 1 页表头 + 2 行数据，第 2 页同表头续表（跨页续表验证）。

    用描边矩形画单元格边框（Word/Excel 导出 PDF 的常见做法），供矢量表格
    引擎从几何线条重建表格。
    """
    from fpdf import FPDF

    pdf = FPDF(format="A4")
    pdf.set_title("部门季度费用明细表")
    font_path = _find_cjk_ttf()
    if font_path is None:
        raise RuntimeError("no CJK TTF font found for PDF fixture generation")
    pdf.add_font("hmbuddycjk", "", font_path)
    pdf.set_font("hmbuddycjk", size=12)
    pdf.set_line_width(0.2)

    col_x = [20.0, 80.0, 130.0, 180.0]  # 三列：宽 60 / 50 / 50
    row_height = 12.0

    def draw_table_row(top: float, values: list[str]) -> None:
        for column_index, (x0, x1) in enumerate(zip(col_x[:-1], col_x[1:])):
            pdf.rect(x0, top, x1 - x0, row_height, style="D")
            pdf.text(x0 + 2.0, top + row_height - 3.5, values[column_index])

    # 第 1 页：标题 + 表头 + 两行数据
    pdf.add_page()
    pdf.text(20, 20, "部门季度费用明细表")
    draw_table_row(30.0, ["项目", "2024", "2025"])
    draw_table_row(30.0 + row_height, ["营业收入", "1200", "1500"])
    draw_table_row(30.0 + 2 * row_height, ["营业成本", "800", "900"])
    pdf.text(20, 80, "注：本表在第 2 页继续。")

    # 第 2 页：同表头续表 + 两行数据
    pdf.add_page()
    draw_table_row(20.0, ["项目", "2024", "2025"])
    draw_table_row(20.0 + row_height, ["毛利润", "400", "600"])
    draw_table_row(20.0 + 2 * row_height, ["净利润", "350", "520"])
    pdf.output(str(path))


def make_xls_standard(path: Path) -> None:
    """标准 XLS（xlwt 生成）：单 Sheet、数值、合并单元格（遗留格式验证）。"""
    import xlwt

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("部门费用")
    for column_index, header in enumerate(["项目", "2024", "2025"]):
        sheet.write(0, column_index, header)
    sheet.write(1, 0, "营业收入")
    sheet.write(1, 1, 1200)
    sheet.write(1, 2, 1500)
    sheet.write(2, 0, "营业成本")
    sheet.write(2, 1, 800)
    sheet.write(2, 2, 900)
    sheet.write(4, 0, "注：数据为示例数据")
    sheet.merge(4, 4, 0, 2)
    workbook.save(str(path))


def main() -> None:
    generators = {
        "sample.docx": make_docx_standard,
        "complex.docx": make_docx_complex,
        "sample.pdf": make_pdf_standard,
        "sample_table.pdf": make_pdf_table,
        "sample.xlsx": make_xlsx_standard,
        "sample_multisheet.xlsx": make_xlsx_multisheet,
        "sample.xls": make_xls_standard,
        "sample.pptx": make_pptx_standard,
    }
    for filename, generator in generators.items():
        target = HERE / filename
        generator(target)
        print(f"generated: {target}  ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
