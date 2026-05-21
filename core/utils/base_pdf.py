import io
from typing import Any
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class BasePDFGenerator:
    """
    A reusable, parameter-driven PDF generator utility class

    :param filename: Str name of the downloaded file.
    :param title: Str main header of the document.
    :param headers: List of strings for table columns.
    :param data_rows: List of lists representing table rows.
    :param user_context: Dict containing metadata (e.g., {'request_user': 'rob', 'type': 'client'})
    """

    def __init__(
        self,
        filename: str,
        headers: list[str],
        data_rows: list[list[Any]],
        context: dict[str, Any] | None = None,
    ):
        self.filename = (
            filename
            or f"pdf_{timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )
        self.headers = headers
        self.data_rows = data_rows
        self.context = context or {}
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()

    def get_document_settings(self):
        """
        Override to adjust page settings
        """
        return {
            "pagesize": letter,
            "rightMargin": 36,
            "leftMargin": 36,
            "topMargin": 36,
            "bottomMargin": 36,
        }

    def get_table_styles(self):
        return TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#111111"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#cccccc"),
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
            ]
        )

    def build_story(self):
        story = []

        # Title
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=self.styles["Heading1"],
            fontSize=18,
            spaceAfter=12,
        )
        story.append(Paragraph(self.title.upper(), title_style))
        story.append(Spacer(1, 12))

        # Table
        table_data = [self.headers] + self.data_rows
        report_table = Table(table_data, hAlign="LEFT")
        report_table.setStyle(self.get_table_style())
        story.append(report_table)

        return story

    def render(self) -> HttpResponse:
        """
        Compiles the story into raw bytes
        and returns it as a Django HttpResponse.
        """

        doc = SimpleDocTemplate(
            self.buffer, **self.get_document_settings()
        )
        story = self.build_story()

        doc.build(story)
        self.buffer.seek(0)

        response = HttpResponse(
            self.buffer, content_type="application/pdf"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{self.filename}"'
        )
        return response
