"""Invoice PDF layout and exclusive output allocation."""
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .models import Invoice

def _render(invoice, stream, invoice_number, issued_on):
    customer, description = invoice.customer, invoice.description
    quantity, price, tax_rate = invoice.quantity, invoice.unit_price, invoice.tax_rate
    subtotal, tax_amount, total = invoice.subtotal, invoice.tax_amount, invoice.total
    styles = getSampleStyleSheet()
    styles["Normal"].wordWrap = "CJK"
    story = [
        Paragraph("INVOICE", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"<b>Invoice number:</b> {invoice_number}", styles["Normal"]),
        Paragraph(f"<b>Date:</b> {issued_on.isoformat()}", styles["Normal"]),
        Paragraph(f"<b>Bill to:</b> {escape(customer)}", styles["Normal"]),
        Spacer(1, 20),
    ]

    table_data = [
        ["Description", "Quantity", "Unit price", "Amount"],
        [Paragraph(escape(description), styles["Normal"]), Paragraph(f"{quantity:g}", styles["Normal"]), Paragraph(f"{price:,.2f}", styles["Normal"]), Paragraph(f"{subtotal:,.2f}", styles["Normal"])],
        ["", "", "Subtotal", Paragraph(f"{subtotal:,.2f}", styles["Normal"])],
        ["", "", f"Tax ({tax_rate:g}%)", Paragraph(f"{tax_amount:,.2f}", styles["Normal"])],
        ["", "", "TOTAL", Paragraph(f"{total:,.2f}", styles["Normal"])],
    ]

    table = Table(table_data, colWidths=[200, 65, 105, 105], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B53")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (2, -1), (-1, -1), colors.HexColor("#E8F1F8")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(table)

    SimpleDocTemplate(stream, pagesize=A4, title=invoice_number).build(story)

def generate_invoice_pdf(invoice: Invoice, output_folder: Path, issued_on=None) -> Path:
    issued_on = issued_on or date.today()
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    sequence = 1
    while True:
        number = f"INV-{issued_on:%Y%m%d}-{sequence:03d}"
        path = output_folder / f"{number}.pdf"
        try:
            stream = path.open("xb")
            break
        except FileExistsError:
            sequence += 1
    try:
        with stream:
            _render(invoice, stream, number, issued_on)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return path.resolve()
