from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from invoice_generator.models import Invoice
from invoice_generator.pdf import generate_invoice_pdf


class InvoiceTests(unittest.TestCase):
    def test_decimal_money_and_rounding(self):
        invoice = Invoice.from_inputs("C", "D", "3", "0.10", "14")
        self.assertEqual(invoice.subtotal, Decimal("0.30"))
        self.assertEqual(invoice.tax_amount, Decimal("0.04"))
        self.assertEqual(invoice.total, Decimal("0.34"))
        self.assertEqual(Invoice.from_inputs("C", "D", "1", "1.005", "0").total, Decimal("1.01"))

    def test_invalid_numbers(self):
        cases = [("NaN", "1", "14"), ("1", "Infinity", "14"),
                 ("1", "1", "NaN"), ("0", "1", "0"), ("1", "-1", "0"),
                 ("1", "1", "101"), ("bad", "1", "0"),
                 ("1e100", "1", "0"), ("1", "0.0000001", "0")]
        for values in cases:
            with self.subTest(values=values), self.assertRaises(ValueError):
                Invoice.from_inputs("C", "D", *values)

    def test_required_and_bounded_text(self):
        for customer, description in [(" ", "D"), ("C", ""), ("C" * 201, "D")]:
            with self.subTest(customer=customer), self.assertRaises(ValueError):
                Invoice.from_inputs(customer, description, "1", "1", "0")

    def test_unique_files_and_literal_markup(self):
        invoice = Invoice.from_inputs("Alex <b> & Co", "<invoice> & consulting " * 25, "2", "100", "14")
        with TemporaryDirectory() as folder:
            first = generate_invoice_pdf(invoice, Path(folder), date(2026, 11, 12))
            original = first.read_bytes()
            second = generate_invoice_pdf(invoice, Path(folder), date(2026, 11, 12))
            self.assertEqual(first.name, "INV-20261112-001.pdf")
            self.assertEqual(second.name, "INV-20261112-002.pdf")
            self.assertEqual(first.read_bytes(), original)
            self.assertTrue(second.read_bytes().startswith(b"%PDF-"))

    def test_failed_render_preserves_existing_invoices(self):
        invoice = Invoice.from_inputs("C", "D", "1", "100", "14")
        with TemporaryDirectory() as folder:
            first = generate_invoice_pdf(invoice, Path(folder), date(2026, 11, 12))
            original = first.read_bytes()
            with patch("invoice_generator.pdf._render", side_effect=OSError("Disk full")):
                with self.assertRaises(OSError):
                    generate_invoice_pdf(invoice, Path(folder), date(2026, 11, 12))
            self.assertEqual(list(Path(folder).iterdir()), [first])
            self.assertEqual(first.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
