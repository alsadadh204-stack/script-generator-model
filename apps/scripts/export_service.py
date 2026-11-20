import io
from django.http import HttpResponse

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import docx
    from docx.shared import Inches, Pt, RGBColor
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


class ScriptExportService:
    """
    Exports scripts into PDF, DOCX, TXT, and Markdown formats.
    """

    @staticmethod
    def export_txt(script):
        content = f"TITLE: {script.title}\n"
        content += f"PLATFORM: {script.get_platform_display()} | DURATION: {script.duration} | TONE: {script.tone}\n"
        content += f"VERSION: v{script.version} | WORDS: {script.word_count} | EST. TIME: {script.estimated_speaking_minutes} min\n"
        content += "=" * 60 + "\n\n"
        content += script.get_full_text()

        response = HttpResponse(content, content_type='text/plain; charset=utf-8')
        filename = f"{script.title.replace(' ', '_').lower()}_v{script.version}.txt"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def export_markdown(script):
        content = f"""# {script.title}

> **Platform:** {script.get_platform_display()} | **Duration:** {script.duration} | **Tone:** {script.tone}  
> **Version:** v{script.version} | **Word Count:** {script.word_count} words | **Estimated Reading Time:** {script.estimated_speaking_minutes} min

---

"""
        text = script.get_full_text()
        for line in text.splitlines():
            line_s = line.strip()
            if line_s in ['HOOK', 'INTRODUCTION', 'MAIN CONTENT', 'CONCLUSION', 'CALL TO ACTION', 'OUTRO']:
                content += f"\n## {line_s}\n\n"
            elif line_s.startswith('[VISUAL:') or line_s.startswith('[CAMERA:'):
                content += f"> *{line_s}*\n\n"
            else:
                content += f"{line}\n"

        response = HttpResponse(content, content_type='text/markdown; charset=utf-8')
        filename = f"{script.title.replace(' ', '_').lower()}_v{script.version}.md"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def export_pdf(script):
        if not HAS_REPORTLAB:
            return ScriptExportService.export_txt(script)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ScriptTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#FF7A3D'),
            spaceAfter=6,
        )

        meta_style = ParagraphStyle(
            'ScriptMeta',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#6E675F'),
            spaceAfter=14,
        )

        section_heading = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#FF7A3D'),
            spaceBefore=14,
            spaceAfter=6,
            textTransform='uppercase',
        )

        body_style = ParagraphStyle(
            'ScriptBody',
            parent=styles['BodyText'],
            fontSize=10.5,
            leading=16,
            textColor=colors.HexColor('#1E1B18'),
            spaceAfter=8,
        )

        visual_style = ParagraphStyle(
            'VisualStyle',
            parent=styles['Italic'],
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor('#555555'),
            spaceAfter=6,
            leftIndent=15,
        )

        story = []

        story.append(Paragraph(script.title, title_style))
        meta_line = (
            f"<b>Platform:</b> {script.get_platform_display()} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Duration:</b> {script.duration} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Tone:</b> {script.tone} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Words:</b> {script.word_count} (~{script.estimated_speaking_minutes} min)"
        )
        story.append(Paragraph(meta_line, meta_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E1DC'), spaceAfter=14))

        full_text = script.get_full_text()
        for block in full_text.split('\n\n'):
            block = block.strip()
            if not block:
                continue

            lines = block.split('\n')
            first_line = lines[0].strip().upper()

            if first_line in ['HOOK', 'INTRODUCTION', 'MAIN CONTENT', 'CONCLUSION', 'CALL TO ACTION', 'OUTRO']:
                story.append(Paragraph(first_line, section_heading))
                body_content = "<br/>".join(lines[1:])
                if body_content:
                    story.append(Paragraph(body_content, body_style))
            elif block.startswith('[VISUAL:') or block.startswith('[CAMERA:'):
                story.append(Paragraph(block, visual_style))
            else:
                story.append(Paragraph(block.replace('\n', '<br/>'), body_style))

            story.append(Spacer(1, 4))

        doc.build(story)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"{script.title.replace(' ', '_').lower()}_v{script.version}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def export_docx(script):
        if not HAS_DOCX:
            return ScriptExportService.export_txt(script)

        doc = docx.Document()

        # Add Title
        h = doc.add_heading(script.title, level=1)
        for run in h.runs:
            run.font.color.rgb = RGBColor(255, 122, 61)  # Warm coral/orange
            run.font.size = Pt(22)

        # Meta paragraph
        p = doc.add_paragraph()
        p.add_run(f"Platform: {script.get_platform_display()} | Duration: {script.duration} | Tone: {script.tone}\n").bold = True
        p.add_run(f"Version: v{script.version} | Words: {script.word_count} | Est. Reading Time: {script.estimated_speaking_minutes} min\n")

        doc.add_paragraph("-" * 50)

        # Content
        text = script.get_full_text()
        for block in text.split('\n\n'):
            block = block.strip()
            if not block:
                continue
            lines = block.split('\n')
            first = lines[0].strip().upper()
            if first in ['HOOK', 'INTRODUCTION', 'MAIN CONTENT', 'CONCLUSION', 'CALL TO ACTION', 'OUTRO']:
                sh = doc.add_heading(first, level=2)
                for r in sh.runs:
                    r.font.color.rgb = RGBColor(255, 122, 61)
                body = "\n".join(lines[1:])
                if body:
                    doc.add_paragraph(body)
            elif block.startswith('[VISUAL:') or block.startswith('[CAMERA:'):
                vp = doc.add_paragraph()
                r = vp.add_run(block)
                r.italic = True
                r.font.color.rgb = RGBColor(100, 100, 100)
            else:
                doc.add_paragraph(block)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        filename = f"{script.title.replace(' ', '_').lower()}_v{script.version}.docx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
