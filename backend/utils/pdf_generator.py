import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.colors import navy, black
from backend.api.models import FullReport


def generate_interview_report_pdf(report_data: FullReport) -> io.BytesIO:
    """
    Генерирует PDF-отчет на основе данных анализа интервью.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='Heading1', fontSize=16, fontName='Helvetica-Bold', textColor=navy, spaceAfter=14,
                              alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Heading2', fontSize=14, fontName='Helvetica-Bold', textColor=navy, spaceAfter=10,
                              alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Normal_L', fontName='Helvetica', fontSize=11, alignment=TA_LEFT))
    styles.add(
        ParagraphStyle(name='Bullet', parent=styles['Normal_L'], firstLineIndent=0, spaceBefore=3, leftIndent=20))

    story = []

    # Заголовок
    story.append(Paragraph(f"Отчет по собеседованию: {report_data.candidate_info.full_name}", styles['Heading1']))
    story.append(Spacer(1, 24))

    # Общий вывод
    story.append(Paragraph("Краткий вывод (AI Summary)", styles['Heading2']))
    story.append(Paragraph(report_data.ai_summary, styles['Justify']))
    story.append(Spacer(1, 12))

    # Информация о кандидате
    story.append(Paragraph("Информация о кандидате", styles['Heading2']))
    info_text = f"""
        <b>Имя:</b> {report_data.candidate_info.full_name}<br/>
        <b>Опыт:</b> {report_data.candidate_info.experience_years}<br/>
        <b>Технологии:</b> {', '.join(report_data.candidate_info.tech_stack)}<br/>
        <b>Домены:</b> {', '.join(report_data.candidate_info.domains)}
    """
    story.append(Paragraph(info_text, styles['Normal_L']))
    story.append(Spacer(1, 12))

    # Анализ интервью
    story.append(Paragraph("Анализ интервью", styles['Heading2']))
    analysis_text = f"""
        <b>Техническая оценка:</b> {report_data.interview_analysis.tech_assessment}<br/><br/>
        <b>Оценка коммуникации:</b> {report_data.interview_analysis.comm_skills_assessment}
    """
    story.append(Paragraph(analysis_text, styles['Justify']))
    story.append(Spacer(1, 12))

    # Заключение
    story.append(Paragraph("Заключение и рекомендации", styles['Heading2']))
    conclusion_text = f"""
        <b>Рекомендация:</b> {report_data.conclusion.recommendation}<br/>
        <b>Оцененный уровень:</b> {report_data.conclusion.assessed_level}<br/><br/>
        <b>Финальное заключение:</b> {report_data.conclusion.summary}
    """
    story.append(Paragraph(conclusion_text, styles['Justify']))
    story.append(Spacer(1, 12))

    # Рекомендации для кандидата
    story.append(Paragraph("Рекомендации для кандидата", styles['Heading2']))
    for rec in report_data.recommendations_for_candidate:
        story.append(Paragraph(f"• {rec}", styles['Bullet']))

    doc.build(story)
    buffer.seek(0)
    return buffer