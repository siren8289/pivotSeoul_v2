"""Minimal .xlsx writer (stdlib only) for date-folder test_sheet.xlsx."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

_ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _cell(ref: str, value: object) -> str:
    text = _ILLEGAL.sub("", "" if value is None else str(value))
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(text)}</t></is></c>'


def _col(index: int) -> str:
    name = ""
    n = index
    while True:
        n, rem = divmod(n, 26)
        name = chr(65 + rem) + name
        if n == 0:
            break
        n -= 1
    return name


def write_xlsx(path: Path, sheets: dict[str, list[list[object]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet_items = list(sheets.items()) or [("Results", [["empty"]])]
    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
    ]
    workbook_sheets: list[str] = []
    workbook_rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for index, (title, _rows) in enumerate(sheet_items, start=1):
        safe = re.sub(r"[\\/*?:\[\]]", "_", title)[:31] or f"Sheet{index}"
        workbook_sheets.append(f'<sheet name="{escape(safe)}" sheetId="{index}" r:id="rId{index}"/>')
        workbook_rels.append(
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
        content_types.append(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    content_types.append("</Types>")
    workbook_rels.append("</Relationships>")
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets>{"".join(workbook_sheets)}</sheets></workbook>'
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/></Relationships>'
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "\n".join(content_types))
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", "\n".join(workbook_rels))
        for index, (_title, rows) in enumerate(sheet_items, start=1):
            row_xml = []
            for r_idx, row in enumerate(rows, start=1):
                cells = "".join(
                    _cell(f"{_col(c_idx)}{r_idx}", value) for c_idx, value in enumerate(row)
                )
                row_xml.append(f'<row r="{r_idx}">{cells}</row>')
            sheet_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f'<sheetData>{"".join(row_xml)}</sheetData></worksheet>'
            )
            archive.writestr(f"xl/worksheets/sheet{index}.xml", sheet_xml)
