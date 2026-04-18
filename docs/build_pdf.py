# -*- coding: utf-8 -*-
"""사용설명서.md → 사용설명서.pdf (PyQt6 기반)"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qt_bootstrap import prepare_qt_runtime
prepare_qt_runtime()

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextDocument, QPageLayout, QPageSize
from PyQt6.QtCore import QMarginsF, QSizeF
from PyQt6.QtPrintSupport import QPrinter


def md_to_html(md: str) -> str:
    """간단한 마크다운 → HTML 변환 (제목/리스트/표/코드/굵게/기울임)"""
    lines = md.splitlines()
    out = []
    in_table = False
    in_code = False
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def close_table():
        nonlocal in_table
        if in_table:
            out.append("</table>")
            in_table = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # 코드 블록
        if line.startswith("```"):
            close_list(); close_table()
            if not in_code:
                out.append('<pre style="background:#f4f4f4;padding:10px;border-radius:4px;font-family:monospace;font-size:11pt;">')
                in_code = True
            else:
                out.append("</pre>")
                in_code = False
            i += 1; continue
        if in_code:
            out.append(escape(line))
            i += 1; continue

        # 헤딩
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            close_list(); close_table()
            level = len(m.group(1))
            sizes = {1: "26pt", 2: "20pt", 3: "16pt", 4: "13pt"}
            size = sizes.get(level, "11pt")
            out.append(f'<h{level} style="font-size:{size};color:#1a3a5f;margin-top:18pt;margin-bottom:8pt;">{inline(m.group(2))}</h{level}>')
            i += 1; continue

        # 가로선
        if line.strip() == "---":
            close_list(); close_table()
            out.append('<hr style="border:none;border-top:1px solid #ccc;margin:14pt 0;">')
            i += 1; continue

        # 표 (헤더 포함 처리)
        if "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|?[\s\-|:]+\|?\s*$", lines[i+1]):
            close_list()
            if not in_table:
                out.append('<table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse;margin:8pt 0;width:100%;">')
                in_table = True
            cells = [c.strip() for c in line.strip("|").split("|")]
            row = "".join(f'<th style="background:#1a3a5f;color:white;text-align:left;">{inline(c)}</th>' for c in cells)
            out.append(f"<tr>{row}</tr>")
            i += 2  # skip separator
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                row = "".join(f"<td>{inline(c)}</td>" for c in cells)
                out.append(f"<tr>{row}</tr>")
                i += 1
            close_table()
            continue

        # 인용
        if line.startswith("> "):
            close_list(); close_table()
            out.append(f'<blockquote style="border-left:3px solid #1a3a5f;margin:6pt 0;padding:4pt 10pt;background:#f4f7fb;color:#444;">{inline(line[2:])}</blockquote>')
            i += 1; continue

        # 리스트
        if re.match(r"^\s*[-*]\s+", line):
            close_table()
            if not in_list:
                out.append('<ul style="margin:4pt 0;padding-left:20pt;">')
                in_list = True
            stripped = re.sub(r"^\s*[-*]\s+", "", line)
            out.append(f"<li>{inline(stripped)}</li>")
            i += 1; continue

        # 빈 줄
        if not line.strip():
            close_list(); close_table()
            out.append("<br/>")
            i += 1; continue

        # 단락
        close_list(); close_table()
        out.append(f"<p>{inline(line)}</p>")
        i += 1

    close_list(); close_table()
    if in_code:
        out.append("</pre>")

    return "\n".join(out)


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s: str) -> str:
    """굵게 / 기울임 / 인라인 코드 / 링크"""
    s = escape(s)
    # 인라인 코드
    s = re.sub(r"`([^`]+)`", r'<code style="background:#f4f4f4;padding:1pt 4pt;border-radius:2pt;font-family:monospace;">\1</code>', s)
    # 굵게
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    # 기울임
    s = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", s)
    # 링크
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    # 이모지 ⭐ 그대로 둠
    return s


def main():
    app = QApplication(sys.argv)

    here = os.path.dirname(os.path.abspath(__file__))
    md_path = os.path.join(here, "사용설명서.md")
    pdf_path = os.path.join(here, "사용설명서.pdf")

    with open(md_path, "r", encoding="utf-8") as f:
        md = f.read()

    body = md_to_html(md)
    html = f"""
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:'AppleSDGothicNeo','Apple SD Gothic Neo','Malgun Gothic','Nanum Gothic',sans-serif;font-size:11pt;line-height:1.6;color:#222;">
    {body}
    </body>
    </html>
    """

    doc = QTextDocument()
    doc.setHtml(html)

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(pdf_path)
    layout = QPageLayout(QPageSize(QPageSize.PageSizeId.A4),
                         QPageLayout.Orientation.Portrait,
                         QMarginsF(20, 20, 20, 20),
                         QPageLayout.Unit.Millimeter)
    printer.setPageLayout(layout)

    doc.print(printer)
    print(f"PDF 생성 완료: {pdf_path}")


if __name__ == "__main__":
    main()
