# =============================================
#  utils/pdf_generator.py — PDF generatsiya
#  Ramis Arabic.otf fonti bilan (arab yozuvi)
# =============================================

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config import PDF_FILENAME

# ── RTL (Arab) yozuvi qo'llab-quvvatlash ──────────────────────────────────────
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _BIDI_OK = True
except ImportError:
    _BIDI_OK = False


def _fix_rtl(text: str) -> str:
    """Arab harflarini to'g'ri yo'nalishda ko'rsatish uchun qayta shakllantiradi."""
    if not text:
        return text
    has_arabic = any('\u0600' <= ch <= '\u06FF' for ch in text)
    if not has_arabic or not _BIDI_OK:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


# ── Ranglar ────────────────────────────────────────────────────────────────────
PRIMARY   = colors.HexColor("#1a3a5c")
SECONDARY = colors.HexColor("#2e7bcf")
ACCENT    = colors.HexColor("#e8f4fd")
WHITE     = colors.white
DARK_TEXT = colors.HexColor("#1e1e1e")
BORDER    = colors.HexColor("#b0c4de")
GOLD      = colors.HexColor("#b8860b")


# ── Font ro'yxatdan o'tkazish ──────────────────────────────────────────────────
_FONT_REGISTERED = False
_FONT_REGULAR    = "Helvetica"
_FONT_BOLD       = "Helvetica-Bold"


def _register_fonts() -> tuple[str, str]:
    """
    Shriftlarni bir marta ro'yxatdan o'tkazadi.
    Ustuvorlik tartibi:
      1. fonts/RamisArabic.otf  (arab + boshqa barcha harflar)
      2. Windows Arial
      3. Linux DejaVu
      4. Helvetica (standart fallback)
    """
    global _FONT_REGISTERED, _FONT_REGULAR, _FONT_BOLD
    if _FONT_REGISTERED:
        return _FONT_REGULAR, _FONT_BOLD

    # Bot papkasidagi fonts/ katalogi
    base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ramis_otf = os.path.join(base_dir, "fonts", "RamisArabic.otf")

    candidates = [
        # (regular_name, regular_path, bold_name, bold_path)
        ("RamisArabic", ramis_otf,                          "RamisArabic", ramis_otf),
        ("Arial",       r"C:\Windows\Fonts\arial.ttf",      "Arial-Bold",  r"C:\Windows\Fonts\arialbd.ttf"),
        ("DejaVu",      "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                        "DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]

    for reg_name, reg_path, bold_name, bold_path in candidates:
        if not os.path.exists(reg_path):
            continue
        try:
            pdfmetrics.registerFont(TTFont(reg_name, reg_path))
            if bold_path != reg_path and os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
            else:
                bold_name = reg_name  # OTF faylida bold alohida yo'q
            _FONT_REGULAR    = reg_name
            _FONT_BOLD       = bold_name
            _FONT_REGISTERED = True
            return _FONT_REGULAR, _FONT_BOLD
        except Exception:
            continue

    _FONT_REGISTERED = True
    return _FONT_REGULAR, _FONT_BOLD


# ── Asosiy generatsiya funksiyasi ──────────────────────────────────────────────
def generate_pdf(rows: list) -> str:
    """
    Foydalanuvchilar ro'yxatidan A4 PDF hisobot yaratadi.
    Qaytaradi: PDF fayl yo'lini.
    """
    font_name, font_bold = _register_fonts()
    filepath = PDF_FILENAME

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title="Ijoza uchun ro'yxat",
        author="Certificate Bot",
    )

    styles = getSampleStyleSheet()
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")

    # ── Uslublar ──────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Normal"],
        fontSize=20, textColor=PRIMARY, alignment=TA_CENTER,
        fontName=font_bold, leading=26, spaceAfter=4,
    )
    meta_style = ParagraphStyle(
        "MetaStyle", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER, fontName=font_name, spaceAfter=14,
    )
    section_style = ParagraphStyle(
        "SectionStyle", parent=styles["Normal"],
        fontSize=13, textColor=PRIMARY, fontName=font_bold,
        spaceBefore=14, spaceAfter=6, leading=18,
    )
    # Arab harflar uchun o'ngga hizalangan uslub
    cell_rtl = ParagraphStyle(
        "CellRTL", parent=styles["Normal"],
        fontSize=9, textColor=DARK_TEXT, fontName=font_name,
        leading=13, alignment=TA_RIGHT, wordWrap="CJK",
    )
    cell_ltr = ParagraphStyle(
        "CellLTR", parent=styles["Normal"],
        fontSize=9, textColor=DARK_TEXT, fontName=font_name,
        leading=13, alignment=TA_LEFT, wordWrap="CJK",
    )
    cell_center = ParagraphStyle(
        "CellCenter", parent=styles["Normal"],
        fontSize=9, textColor=DARK_TEXT, fontName=font_name,
        leading=13, alignment=TA_CENTER,
    )
    header_style = ParagraphStyle(
        "HeaderStyle", parent=styles["Normal"],
        fontSize=10, textColor=WHITE, fontName=font_bold,
        alignment=TA_CENTER, leading=13,
    )
    empty_style = ParagraphStyle(
        "EmptyStyle", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#888888"),
        fontName=font_name, alignment=TA_LEFT, spaceAfter=10,
    )

    # Ustun kengliklari (jami 18 sm)
    col_w = [1.2*cm, 5.8*cm, 3.2*cm, 7.8*cm]

    def _cell_name(text: str) -> Paragraph:
        """Ism uchun — arab bo'lsa RTL, bo'lmasa LTR."""
        has_ar = any('\u0600' <= ch <= '\u06FF' for ch in text)
        fixed  = _fix_rtl(text) if has_ar else text
        style  = cell_rtl if has_ar else cell_ltr
        return Paragraph(fixed, style)

    def build_table(student_rows: list, gender_icon: str) -> Table:
        header = [
            Paragraph("<b>№</b>",           header_style),
            Paragraph("<b>Ism Familiya</b>", header_style),
            Paragraph("<b>Guruh</b>",        header_style),
            Paragraph("<b>Kitob</b>",        header_style),
        ]
        data = [header]
        for idx, r in enumerate(student_rows, 1):
            data.append([
                Paragraph(str(idx),                    cell_center),
                _cell_name(str(r.get("full_name", ""))),
                Paragraph(_fix_rtl(str(r.get("group_name", ""))), cell_center),
                Paragraph(_fix_rtl(str(r.get("book_name", ""))),  cell_ltr),
            ])

        t = Table(data, colWidths=col_w, repeatRows=1)
        ts = TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
            ("LINEBELOW",     (0, 0), (-1, 0),  1.5, SECONDARY),
            ("BOX",           (0, 0), (-1, -1), 1.2, PRIMARY),
        ])
        for i in range(1, len(data)):
            bg = ACCENT if i % 2 == 0 else WHITE
            ts.add("BACKGROUND", (0, i), (-1, i), bg)
        t.setStyle(ts)
        return t

    # ── Sahifani to'ldirish ───────────────────────────────────────────────────
    erkaklar = [r for r in rows if r.get("gender") == "Erkak"]
    ayollar  = [r for r in rows if r.get("gender") == "Ayol"]

    story = []

    story.append(Paragraph("IJOZA UCHUN RO'YXAT", title_style))
    story.append(Paragraph(
        f"Hisobot sanasi: <b>{now_str}</b> &nbsp;|&nbsp; "
        f"Jami: <b>{len(rows)}</b> nafar "
        f"(👨 {len(erkaklar)} erkak + 👩 {len(ayollar)} ayol)",
        meta_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    # Erkaklar
    story.append(Paragraph("👨 ERKAK O'QUVCHILAR", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=6))
    if erkaklar:
        story.append(build_table(erkaklar, "👨"))
    else:
        story.append(Paragraph("<i>Erkak o'quvchilar ro'yxatdan o'tmagan</i>", empty_style))

    story.append(Spacer(1, 0.8 * cm))

    # Ayollar
    story.append(Paragraph("👩 AYOL O'QUVCHILAR", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=6))
    if ayollar:
        story.append(build_table(ayollar, "👩"))
    else:
        story.append(Paragraph("<i>Ayol o'quvchilar ro'yxatdan o'tmagan</i>", empty_style))

    # ── Sahifa raqami ─────────────────────────────────────────────────────────
    def add_page_number(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont(font_name, 8)
        canvas.setFillColor(colors.HexColor("#777777"))
        num = canvas.getPageNumber()
        canvas.drawRightString(A4[0] - 1.5*cm, 0.8*cm, f"Sahifa {num}")
        canvas.drawString(1.5*cm, 0.8*cm, f"Certificate Bot | {now_str}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return filepath
