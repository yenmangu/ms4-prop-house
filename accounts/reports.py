from typing import Any

from reportlab.platypus import Paragraph, Spacer, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from core.utils import BasePDFGenerator


class UserInventoryPDF(BasePDFGenerator):
    """
    Generates a secure, consumer-branded inventory manifest for a client's dashboard.
    Specififes an __init__ method for IDE guidance that delegates to base.
    """

    filename: str = "my_hire_manifest.pdf"
    title = "Your Hire History & Asset Manifest"

    def __init__(
        self,
        filename: str | None,
        headers: list[str],
        data_rows: list[list[Any]],
        context: dict[str, Any] | None = None,
    ):
        """
        Explicitly define parameter types and
        forward args to `BasePDFGenerator.__init__`
        """

        super().__init__(
            filename=filename,
            headers=headers,
            data_rows=data_rows,
            context=context,
        )

    def get_table_style(self):
        # Clients get a premium, dark aesthetic for their summary charts
        return TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1e293b"),
                ),  # Slate 800
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "LINEBELOW",
                    (0, 1),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e2e8f0"),
                ),  # Slate 200 grid
            ]
        )

    def build_story(self):
        # Customizes the top header metadata before rendering the main grid table
        story = []

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=self.styles["Heading1"],
            fontSize=20,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6,
        )
        meta_style = ParagraphStyle(
            "MetaStyle",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#475569"),
        )

        story.append(Paragraph(self.title, title_style))
        story.append(
            Paragraph(
                f"Account Holder: {self.context.get('client_name')}",
                meta_style,
            )
        )
        story.append(
            Paragraph(
                f"Generated On: {self.context.get('generated_at')}",
                meta_style,
            )
        )
        story.append(Spacer(1, 18))

        # Build and attach the formatted table rows securely
        from reportlab.platypus import Table

        table_data = [self.headers] + self.data_rows
        report_table = Table(table_data, hAlign="LEFT")
        report_table.setStyle(self.get_table_style())
        story.append(report_table)

        # Standard client footer T&Cs
        story.append(Spacer(1, 30))
        tc_style = ParagraphStyle(
            "TCStyle",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#94a3b8"),
        )
        story.append(
            Paragraph(
                "This document is an automatic live snapshot of assets in your possession. For modifications, please contact fulfillment directly.",
                tc_style,
            )
        )
        return story
