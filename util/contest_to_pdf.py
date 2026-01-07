import base64
import os
import re
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import ImageFont, ImageDraw, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.colors import HexColor, toColor, Color
from reportlab.graphics.shapes import String
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Image as RLImage
from reportlab.pdfgen import canvas

from model.contest_model.contest_model import DifficultyEnum, ContestDetailResponse
# from model.contest.conte import DifficultyEnum, ContestDetailResponse
from util.html_image_extractor import HTMLImageExtractor
from datetime import datetime

from util.watermask import WatermarkCanvas


def download_image(url):
    """Download image from URL or decode base64"""
    try:
        if url.startswith('data:image'):
            header, encoded = url.split(',', 1)
            image_data = base64.b64decode(encoded)
            return BytesIO(image_data)
        else:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return BytesIO(response.read())
    except Exception as e:
        print(f"Lỗi tải ảnh: {e}")
        return None


def html_to_reportlab(html_content, style):
    """Convert HTML content to ReportLab elements"""
    elements = []

    if not html_content:
        return elements

    parser = HTMLImageExtractor()
    try:
        parser.feed(str(html_content))
    except:
        pass

    image_placeholders = {}
    for idx, img_src in enumerate(parser.images):
        placeholder = f"[[[IMAGE_{idx}]]]"
        image_placeholders[placeholder] = img_src

    html_clean = str(html_content)
    for idx, img_src in enumerate(parser.images):
        placeholder = f"[[[IMAGE_{idx}]]]"
        pattern = r'<img[^>]*src\s*=\s*["\']?' + re.escape(img_src) + r'["\']?[^>]*>'
        html_clean = re.sub(pattern, placeholder, html_clean, flags=re.IGNORECASE)

    html_clean = html_clean.replace('<strong>', '<b>').replace('</strong>', '</b>')
    html_clean = html_clean.replace('<em>', '<i>').replace('</em>', '</i>')
    html_clean = html_clean.replace('<br>', '<br/>').replace('<br/>', '<br/>')

    html_clean = re.sub(r'<ul[^>]*>', '', html_clean)
    html_clean = html_clean.replace('</ul>', '')
    html_clean = re.sub(r'<ol[^>]*>', '', html_clean)
    html_clean = html_clean.replace('</ol>', '')
    html_clean = re.sub(r'<li[^>]*>', '• ', html_clean)
    html_clean = html_clean.replace('</li>', '<br/>')

    html_clean = re.sub(r'<p[^>]*>', '', html_clean)
    html_clean = html_clean.replace('</p>', '<br/><br/>')
    html_clean = re.sub(r'<div[^>]*>', '', html_clean)
    html_clean = html_clean.replace('</div>', '<br/>')

    html_clean = re.sub(r'<h[1-6][^>]*>', '<b>', html_clean)
    html_clean = re.sub(r'</h[1-6]>', '</b><br/>', html_clean)

    html_clean = re.sub(r'<(?!/?(?:b|i|u|br/?)(?:\s|>))[^>]+>', '', html_clean)
    html_clean = re.sub(r'(<br/>){3,}', '<br/><br/>', html_clean)

    parts = re.split(r'(\[\[\[IMAGE_\d+\]\]\])', html_clean)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if part.startswith('[[[IMAGE_') and part.endswith(']]]'):
            img_src = image_placeholders.get(part)
            if img_src:
                img_data = download_image(img_src)
                if img_data:
                    try:
                        img = Image(img_data)
                        img_width = img.drawWidth
                        img_height = img.drawHeight

                        max_width = 15 * cm
                        if img_width > max_width:
                            ratio = max_width / img_width
                            img_width = max_width
                            img_height = img_height * ratio

                        img.drawWidth = img_width
                        img.drawHeight = img_height

                        elements.append(img)
                        elements.append(Spacer(1, 0.3 * cm))
                    except Exception as e:
                        print(f"Lỗi thêm ảnh: {e}")
        else:
            if part:
                try:
                    para = Paragraph(part, style)
                    elements.append(para)
                    elements.append(Spacer(1, 0.1 * cm))
                except Exception as e:
                    safe_text = part.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    elements.append(Paragraph(safe_text, style))
                    elements.append(Spacer(1, 0.1 * cm))

    return elements


def register_vietnamese_fonts():
    """Register fonts that support Vietnamese characters"""
    try:
        font_paths = [
            'DejaVuSans.ttf',
            'DejaVuSans-Bold.ttf',
            'DejaVuSans-Oblique.ttf',
            'DejaVuSans-BoldOblique.ttf'
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                if 'Bold' in font_path and 'Oblique' in font_path:
                    pdfmetrics.registerFont(TTFont('DejaVu-BoldOblique', font_path))
                elif 'Bold' in font_path:
                    pdfmetrics.registerFont(TTFont('DejaVu-Bold', font_path))
                elif 'Oblique' in font_path:
                    pdfmetrics.registerFont(TTFont('DejaVu-Oblique', font_path))
                else:
                    pdfmetrics.registerFont(TTFont('DejaVu', font_path))

        if all(os.path.exists(fp) for fp in font_paths):
            registerFontFamily(
                'DejaVu',
                normal='DejaVu',
                bold='DejaVu-Bold',
                italic='DejaVu-Oblique',
                boldItalic='DejaVu-BoldOblique'
            )
            return 'DejaVu'
    except Exception as e:
        print(f"Không thể load font DejaVu: {e}")

    return 'Helvetica'


def format_datetime(dt: Optional[datetime]) -> str:
    """Format datetime to Vietnamese format"""
    if not dt:
        return "N/A"
    return dt.strftime("%d/%m/%Y %H:%M")


def get_difficulty_text(difficulty: Optional[DifficultyEnum]) -> str:
    """Convert difficulty enum to Vietnamese text"""
    if not difficulty:
        return ""

    mapping = {
        DifficultyEnum.EASY: "Dễ",
        DifficultyEnum.MEDIUM: "Trung bình",
        DifficultyEnum.HARD: "Khó"
    }
    return mapping.get(difficulty, "")


def add_watermark_corner(canvas, doc):
    canvas.saveState()

    text = "HocCode.io"
    font_size = 40
    opacity = 0.2
    color = (180, 180, 180)

    try:
        canvas.setFont("DejaVu-Bold", font_size)
    except:
        canvas.setFont("Helvetica-Bold", font_size)

    try:
        canvas.setFillAlpha(opacity)
    except:
        pass

    canvas.setFillColorRGB(*[c / 255 for c in color])

    width, height = A4

    canvas.drawString(40, height - 60, text)  # trên trái
    canvas.drawRightString(width - 40, 40, text)  # dưới phải

    canvas.restoreState()


def create_pdf_from_contest(contest: ContestDetailResponse, output_file):
    base_font = register_vietnamese_fonts()

    # Use custom canvas with watermark
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    elements = []

    # Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName=base_font + '-Bold' if base_font == 'DejaVu' else 'Helvetica-Bold'
    )

    contest_info_style = ParagraphStyle(
        'ContestInfo',
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName=base_font
    )

    problem_title_style = ParagraphStyle(
        'ProblemTitle',
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=10,
        spaceBefore=15,
        fontName=base_font + '-Bold' if base_font == 'DejaVu' else 'Helvetica-Bold'
    )

    section_style = ParagraphStyle(
        'Section',
        fontSize=11,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=6,
        spaceBefore=8,
        fontName=base_font + '-Bold' if base_font == 'DejaVu' else 'Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'Body',
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        fontName=base_font,
        leading=14
    )

    # Header - Contest Information
    elements.append(Paragraph(contest.title, title_style))
    elements.append(Spacer(1, 0.3 * cm))

    if contest.description:
        elements.append(Paragraph(contest.description, contest_info_style))

    date_info = f"Bắt đầu: {format_datetime(contest.startTime)} | Kết thúc: {format_datetime(contest.endTime)}"
    elements.append(Paragraph(date_info, contest_info_style))
    elements.append(Spacer(1, 0.5 * cm))

    # Separator line
    line_table = Table([['']], colWidths=[16 * cm])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#3498db')),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.5 * cm))

    # Problems
    problem_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for idx, problem in enumerate(contest.problems):
        if idx > 0:
            elements.append(PageBreak())

        letter = problem_letters[idx] if idx < len(problem_letters) else str(idx + 1)

        # Problem Title (without metadata)
        problem_header = f"Câu {letter}. {problem.title}"
        elements.append(Paragraph(problem_header, problem_title_style))

        # Metadata on separate line (Difficulty and Points)
        if problem.difficulty or problem.point:
            metadata = []
            if problem.difficulty:
                metadata.append(f"Độ khó: {get_difficulty_text(problem.difficulty)}")
            if problem.point:
                metadata.append(f"Điểm: {problem.point}")

            metadata_text = " | ".join(metadata)
            metadata_para = Paragraph(f"<i>{metadata_text}</i>", body_style)
            elements.append(metadata_para)
            # elements.append(Spacer(1, 0.2 * cm))

        # Time and Memory limits
        if problem.timeLimit or problem.memoryLimit:
            limits = []
            if problem.timeLimit:
                limits.append(f"Giới hạn thời gian: {problem.timeLimit}ms")
            if problem.memoryLimit:
                limits.append(f"Giới hạn bộ nhớ: {problem.memoryLimit}MB")
            elements.append(Paragraph(f"<i>{' | '.join(limits)}</i>", body_style))
            # elements.append(Spacer(1, 0.2 * cm))

        # Description (HTML content with images)
        if problem.description:
            elements.append(Paragraph('<b>Mô tả đề bài</b>', section_style))
            html_elements = html_to_reportlab(problem.description, body_style)
            if html_elements:
                elements.extend(html_elements)
            else:
                elements.append(Paragraph(problem.description, body_style))
            # elements.append(Spacer(1, 0.2 * cm))

        # Constraints
        if problem.constrains:
            elements.append(Paragraph('<b>Ràng buộc</b>', section_style))
            # Parse constrains if it's a list or string
            constrains_list = problem.constrains.split('\n') if isinstance(problem.constrains, str) else [
                problem.constrains]
            for constraint in constrains_list:
                if constraint.strip():
                    elements.append(Paragraph(f"• {constraint.strip()}", body_style))
            # elements.append(Spacer(1, 0.2 * cm))

        # Hints
        if problem.hints:
            elements.append(Paragraph('<b>Gợi ý</b>', section_style))
            for hint in problem.hints:
                elements.append(Paragraph(f"• {hint.description}", body_style))
            # elements.append(Spacer(1, 0.2 * cm))

        # Test Cases (only non-hidden ones)
        visible_testcases = [tc for tc in problem.allTestCases if not tc.isHidden]
        if visible_testcases:
            elements.append(Paragraph('<b>Test Case Mẫu</b>', section_style))
            # elements.append(Spacer(1, 0.2 * cm))

            table_data = [['ID', 'Đầu vào', 'Đầu ra mong đợi']]

            count = 1
            for tc in visible_testcases:
                tc_id = str(count)
                input_para = Paragraph(tc.input.replace('\n', '<br/>'), body_style)
                output_para = Paragraph(tc.expectedOutput.replace('\n', '<br/>'), body_style)
                table_data.append([tc_id, input_para, output_para])
                count += 1
            col_widths = [1.5 * cm, 7 * cm, 7 * cm]
            testcase_table = Table(table_data, colWidths=col_widths, repeatRows=1)

            testcase_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), base_font + '-Bold' if base_font == 'DejaVu' else 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 1), (-1, -1), base_font),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2c3e50')),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))

            elements.append(testcase_table)
            elements.append(Spacer(1, 0.3 * cm))

        # Follow Up
        if problem.followUp:
            elements.append(Paragraph('<b>Câu hỏi mở rộng</b>', section_style))
            followup_list = problem.followUp.split('\n') if isinstance(problem.followUp, str) else [problem.followUp]
            for followup in followup_list:
                if followup.strip():
                    elements.append(Paragraph(f"• {followup.strip()}", body_style))
            elements.append(Spacer(1, 0.2 * cm))

    # Build PDF with watermark
    doc.build(
        elements,
        onFirstPage=add_watermark_corner,
        onLaterPages=add_watermark_corner,
    )


PDF_STORAGE_DIR = Path("contest_pdfs")


def get_pdf_path(contest_id: int) -> Path:
    """Get the file path for a contest PDF"""
    return PDF_STORAGE_DIR / f"contest_{contest_id}.pdf"


def pdf_exists(contest_id: int) -> bool:
    """Check if PDF file exists for given contest ID"""
    return get_pdf_path(contest_id).exists()


def delete_pdf(contest_id: int) -> bool:
    """Delete PDF file if exists"""
    pdf_path = get_pdf_path(contest_id)
    if pdf_path.exists():
        pdf_path.unlink()
        return True
    return False
