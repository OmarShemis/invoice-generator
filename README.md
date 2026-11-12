# Invoice Generator

[![Tests](https://github.com/OmarShemis/invoice-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/OmarShemis/invoice-generator/actions/workflows/tests.yml)

A Python/PySide6 desktop app for creating single-item PDF invoices with ReportLab.

## Features

- Customer, description, quantity, unit price and editable tax percentage.
- Decimal arithmetic: subtotal and tax rounded separately, half-up, to two places.
- Validation rejects invalid numbers, NaN and infinity.
- Unique daily invoice numbers prevent overwriting previous PDFs.
- Customer text is escaped and long descriptions wrap in the PDF.

## Setup

Requires Python 3.13+. With uv:

```powershell
uv sync
uv run invoice-generator
```

Or with pip:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\invoice-generator
```

After installation, `python -m invoice_generator` also works. The original `python src/main.py` launcher is retained.

PDFs are saved in `invoices/` under the working directory. Generated invoices, environments and editor files are excluded from Git.

## Development

```powershell
uv run python -m unittest discover -s tests -v
```

- `models.py`: validation and decimal calculations.
- `pdf.py`: PDF layout and unique file allocation.
- `ui.py`: desktop interface.

## Scope

Learning/portfolio project: one item and one currency per invoice, basic Latin-font output. No currency conversion, accounting integrations or electronic tax submission. The default 14% tax is editable and is not tax advice. Jurisdiction-specific invoice requirements are not implemented.

## Architecture and verification

[Architecture](docs/architecture.md) · [MIT licence](LICENSE). Unit tests and CI are reproducible with the commands above. Live API/model quality requires separate evaluation.
