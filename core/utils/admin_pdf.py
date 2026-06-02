from typing import Any

# =========================================================================
# EXTERNAL DEPENDENCY ATTRIBUTION
# Source: ReportLab PDF Library (https://www.reportlab.com/)
# Purpose: Plautypus structural layout classes and custom color properties
#          used to generate granular invoice design tables.
# Localisation: Controls internal spacing configurations and line-item formatting.
# =========================================================================
from reportlab.platypus import Paragraph, Spacer, TableStyle, Table
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from core.utils.base_pdf import BasePDFGenerator


class UserInvoicePDF(BasePDFGenerator):
    """
    Generate a professional, admin-only billing invoice for a client.
    """

    title = "TAX INVOICE / RECEIPT"

    def get_table_styles(self) -> TableStyle:

        # =========================================================================
        # EXTERNAL DEPENDENCY ATTRIBUTION
        # Class: TableStyle / colors.HexColor
        # Purpose: Formats the commercial tax table grid cells with precise custom
        #          hexadecimal brand colours matching the system theme palette.
        # =========================================================================
        return TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#0f172a"),
                    # Slate 900
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "LINEBELOW",
                    (0, 1),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#cbd5e1"),
                    # Slate 300
                ),
            ]
        )

    def build_story(self) -> list[Any]:
        story: list[Any] = []

        # Typography Profiles
        title_style = ParagraphStyle(
            "InvoiceTitle",
            parent=self.styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4,
        )
        meta_style = ParagraphStyle(
            "InvoiceMeta",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#334155"),
            leading=14,
        )

        story.append(Paragraph(self.title, title_style))
        story.append(Spacer(1, 10))

        # Meta blocks derived from context dict parameters
        story.append(
            Paragraph(
                f"<b>Invoice Reference:</b> INV-{self.context.get('order_id', 'N/A')}",
                meta_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Issue Date:</b> {self.context.get('date', 'N/A')}",
                meta_style,
            )
        )
        story.append(
            Paragraph(
                f"<b>Billed To:</b> {self.context.get('client_name', 'N/A')} ({self.context.get('client_email', 'N/A')})",
                meta_style,
            )
        )
        story.append(Spacer(1, 20))

        # Build itemised table matrix
        table_data = [self.headers] + self.data_rows
        report_table = Table(
            table_data, hAlign="LEFT", colWidths=[300, 80, 140]
        )
        report_table.setStyle(self.get_table_styles())
        story.append(report_table)

        # Bottom Pricing Summaries block
        story.append(Spacer(1, 15))
        total_style = ParagraphStyle(
            "InvoiceTotal",
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#0f172a"),
            # Right-aligned text flow
            alignment=2,
        )

        story.append(
            Paragraph(
                f"<b>TOTAL AMOUNT PAID:</b> ${self.context.get('total_amount', '0.00')}",
                total_style,
            )
        )

        # Standard Legal disclaimer line
        story.append(Spacer(1, 40))

        # Create own distinct ParagraphStyle (footer_style)
        footer_style = ParagraphStyle(
            "InvFooter",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#94a3b8"),
        )
        story.append(
            Paragraph(
                "This document serves as an official proof of transaction payment. Prop House Management System.",
                footer_style,
            )
        )

        return story
