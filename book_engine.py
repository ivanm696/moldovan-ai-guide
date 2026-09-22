# -*- coding: utf-8 -*-
"""
Полноценный движок для сборки книг библиотеки:
- Единый визуальный стиль
- Поддержка кириллицы (DejaVu)
- Колонтитулы и нумерация страниц (с пропуском обложки)
- Блоки кода, заметки и бейджи уровней
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# Путь к шрифтам (стандартный для Linux, при необходимости измените)
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
try:
    pdfmetrics.registerFont(TTFont("DejaVu", f"{FONT_DIR}/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVu-Oblique", f"{FONT_DIR}/DejaVuSans-Oblique.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVuMono", f"{FONT_DIR}/DejaVuSansMono.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVuMono-Bold", f"{FONT_DIR}/DejaVuSansMono-Bold.ttf"))
except Exception as e:
    print(f"⚠️ Внимание: Не удалось загрузить системные шрифты DejaVu. Ошибка: {e}")

# ── Палитра цветов ────────────────────────────────────────────────────────
INK      = colors.HexColor("#1a1d24")
INK2     = colors.HexColor("#4a5266")
ACCENT   = colors.HexColor("#2c5aa0")
ACCENT2  = colors.HexColor("#7a3fb8")
CODE_BG  = colors.HexColor("#f4f4f8")
CODE_LN  = colors.HexColor("#d8dae8")
NOTE_BG  = colors.HexColor("#fff8e6")
NOTE_LN  = colors.HexColor("#e0c268")

LEVEL_BEGINNER = colors.HexColor("#2e8b57")
LEVEL_INTER    = colors.HexColor("#c07a1e")
LEVEL_ADVANCED = colors.HexColor("#b8392c")


def make_styles():
    return {
        "BookTitle": ParagraphStyle("BookTitle", fontName="DejaVu-Bold", fontSize=28, leading=34,
            textColor=INK, alignment=TA_LEFT, spaceAfter=6),
        "BookSubtitle": ParagraphStyle("BookSubtitle", fontName="DejaVu", fontSize=13, leading=18,
            textColor=INK2, alignment=TA_LEFT, spaceAfter=4),
        "VolTag": ParagraphStyle("VolTag", fontName="DejaVuMono-Bold", fontSize=10, leading=14,
            textColor=ACCENT, spaceAfter=14),
        "H1": ParagraphStyle("H1", fontName="DejaVu-Bold", fontSize=18, leading=24,
            textColor=INK, spaceBefore=22, spaceAfter=10),
        "H2": ParagraphStyle("H2", fontName="DejaVu-Bold", fontSize=13.5, leading=18,
            textColor=ACCENT, spaceBefore=16, spaceAfter=8),
        "H3": ParagraphStyle("H3", fontName="DejaVu-Bold", fontSize=11, leading=14,
            textColor=INK, spaceBefore=10, spaceAfter=4),
        "Body": ParagraphStyle("Body", fontName="DejaVu", fontSize=10, leading=15,
            textColor=INK, alignment=TA_JUSTIFY, spaceAfter=8),
        "Bullet": ParagraphStyle("Bullet", fontName="DejaVu", fontSize=10, leading=14,
            textColor=INK, leftIndent=10, spaceAfter=3),
        "Code": ParagraphStyle("Code", fontName="DejaVuMono", fontSize=8.5, leading=12,
            textColor=INK, backColor=CODE_BG, borderColor=CODE_LN, borderWidth=0.5,
            borderPadding=8, spaceBefore=6, spaceAfter=10),
        "Note": ParagraphStyle("Note", fontName="DejaVu-Oblique", fontSize=9, leading=13,
            textColor=colors.HexColor("#6b5a1e"), backColor=NOTE_BG, borderColor=NOTE_LN,
            borderWidth=0.5, borderPadding=8, spaceBefore=6, spaceAfter=10),
        "Small": ParagraphStyle("Small", fontName="DejaVu", fontSize=8, leading=10,
            textColor=INK2),
    }

S = make_styles()


def level_badge(text, color):
    """Мини-бейджик уровня сложности в виде таблички."""
    t = Table([[text]], colWidths=[30*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
        ("FONTNAME", (0,0), (-1,-1), "DejaVuMono-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 7.5),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    return t


def code_block(code_text):
    """Безопасный блок кода с экранированием спецсимволов."""
    escaped = (code_text.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\n", "<br/>")
                        .replace(" ", "&nbsp;"))
    return Paragraph(escaped, S["Code"])


def note_block(text, label="Заметка"):
    """Информационный блок (заметка/совет)."""
    return Paragraph(f"<b>{label}:</b> {text}", S["Note"])


def h_section(number, title, level_color=None, level_text=None):
    """Заголовок раздела с опциональным бейджем сложности."""
    if level_text and level_color:
        header_table = Table(
            [[Paragraph(f"{number}  {title}", S["H2"]), level_badge(level_text, level_color)]],
            colWidths=[130*mm, 30*mm],
            style=TableStyle([
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("ALIGN", (1,0), (1,0), "RIGHT"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 0),
            ])
        )
        return KeepTogether([header_table])
    return Paragraph(f"{number}  {title}", S["H2"])


class PageNumCanvas:
    """Генератор колонтитулов и нумерации страниц."""
    def __init__(self, book_tag):
        self.book_tag = book_tag

    def __call__(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("DejaVu", 8)
        canvas.setFillColor(INK2)
        # Нижний колонтитул
        canvas.drawString(20*mm, 12*mm, self.book_tag)
        canvas.drawRightString(A4[0]-20*mm, 12*mm, f"стр. {doc.page}")
        canvas.setStrokeColor(CODE_LN)
        canvas.setLineWidth(0.5)
        canvas.line(20*mm, 16*mm, A4[0]-20*mm, 16*mm)
        canvas.restoreState()


def cover_page(vol_num, title, subtitle, level_range, color):
    """Генерация титульного листа (обложки)."""
    elems = []
    elems.append(Spacer(1, 25*mm))
    
    tag_table = Table([[f"КНИГА {vol_num}"]], colWidths=[35*mm])
    tag_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
        ("FONTNAME", (0,0), (-1,-1), "DejaVuMono-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 5), 
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    elems.append(tag_table)
    elems.append(Spacer(1, 8*mm))
    elems.append(Paragraph(title, S["BookTitle"]))
    elems.append(Paragraph(subtitle, S["BookSubtitle"]))
    elems.append(Spacer(1, 4*mm))
    elems.append(Paragraph(f"Уровень: {level_range}", S["VolTag"]))
    elems.append(HRFlowable(width="100%", thickness=1.2, color=color, spaceBefore=4, spaceAfter=20))
    return elems


def build_book(filename, title, subtitle, vol_tag, story):
    """Сборка PDF-документа с автоматическим пропуском колонтитула на обложке."""
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm,
        title=title, author="Независимая библиотека ИИ",
    )
    footer = PageNumCanvas(vol_tag)
    # onFirstPage ничего не делает (обложка чистая), onLaterPages добавляет колонтитул
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=footer)
    print(f"✅ Успешно собрано: {filename}")


# ── Демонстрация использования ────────────────────────────────────────────
if __name__ == "__main__":
    story = []
    
    # 1. Добавляем обложку
    story.extend(cover_page(
        vol_num="01",
        title="Архитектура ИИ-систем",
        subtitle="Практическое руководство по созданию автономных агентов",
        level_range="Базовый — Средний",
        color=ACCENT
    ))
    
    # 2. Основное содержание
    story.append(h_section("1.", "Введение в экосистему", LEVEL_BEGINNER, "BEGINNER"))
    story.append(Paragraph("В этой книге мы рассмотрим основные концепции построения надежных пайплайнов для работы с большими языковыми моделями.", S["Body"]))
    
    story.append(note_block("Все примеры кода протестированы на Python 3.10+", "Важно"))
    
    story.append(h_section("2.", "Базовый пример кода", LEVEL_INTER, "INTERMEDIATE"))
    story.append(Paragraph("Ниже представлен минимальный пример функции для отправки запроса:", S["Body"]))
    
    sample_code = '''def generate_response(prompt: str) -> str:
    # Инициализация клиента
    client = AIClient(api_key="secret")
    response = client.complete(prompt)
    return response.text'''
    
    story.append(code_block(sample_code))
    
    # Сборка книги в файл
    build_book("output_book.pdf", "Архитектура ИИ-систем", "Практическое руководство", "AI-LIB VOL. 1", story)
