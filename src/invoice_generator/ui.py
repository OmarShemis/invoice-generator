"""Qt invoice entry window."""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QMessageBox
from .models import Invoice
from .pdf import generate_invoice_pdf

class InvoiceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Generator")
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h1>Invoice Generator</h1>"))
        layout.addWidget(QLabel("Enter the invoice details below."))

        form = QFormLayout()

        self.customer_input = QLineEdit()
        self.customer_input.setMaxLength(200)
        self.customer_input.setPlaceholderText("e.g. Alex Morgan")
        self.description_input = QLineEdit()
        self.description_input.setMaxLength(2000)
        self.description_input.setPlaceholderText("e.g. Consulting services")
        self.quantity_input = QLineEdit("1")
        self.unit_price_input = QLineEdit("100")
        self.tax_rate_input = QLineEdit("14")

        form.addRow("Customer name:", self.customer_input)
        form.addRow("Product / service:", self.description_input)
        form.addRow("Quantity:", self.quantity_input)
        form.addRow("Unit price:", self.unit_price_input)
        form.addRow("Tax (%):", self.tax_rate_input)
        layout.addLayout(form)

        self.total_label = QLabel("Total: 114.00")
        layout.addWidget(self.total_label)

        calculate_button = QPushButton("Calculate total")
        calculate_button.clicked.connect(self.calculate_total)
        layout.addWidget(calculate_button)

        pdf_button = QPushButton("Generate PDF invoice")
        pdf_button.clicked.connect(self.generate_pdf)
        layout.addWidget(pdf_button)

    def read_invoice(self):
        return Invoice.from_inputs(self.customer_input.text(), self.description_input.text(),
            self.quantity_input.text(), self.unit_price_input.text(), self.tax_rate_input.text())

    def calculate_total(self):
        try:
            self.total_label.setText(f"Total: {self.read_invoice().total:,.2f}")
        except ValueError as error:
            QMessageBox.warning(self, "Check your input", str(error))

    def generate_pdf(self):
        try:
            invoice = self.read_invoice()
        except ValueError as error:
            QMessageBox.warning(self, "Check your input", str(error))
            return
        try:
            path = generate_invoice_pdf(invoice, Path.cwd() / "invoices")
        except Exception as error:
            QMessageBox.warning(self, "Could not save invoice", f"Unable to generate PDF: {error}")
            return
        self.total_label.setText(f"Total: {invoice.total:,.2f}")
        QMessageBox.information(self, "Invoice created", f"Your PDF invoice was saved to:\n{path}")

def run():
    app = QApplication(sys.argv)
    window = InvoiceWindow()
    window.show()
    return app.exec()
