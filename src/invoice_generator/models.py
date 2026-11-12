"""Input validation and decimal invoice arithmetic."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")

def _number(text: str, label: str, maximum: str) -> Decimal:
    try:
        value = Decimal(text.strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{label} must be a valid number.") from exc
    if not value.is_finite() or not 0 <= value <= Decimal(maximum):
        raise ValueError(f"{label} must be between 0 and {maximum}.")
    if value.as_tuple().exponent < -6:
        raise ValueError(f"{label} may have at most 6 decimal places.")
    return value

@dataclass(frozen=True)
class Invoice:
    customer: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal

    @classmethod
    def from_inputs(cls, customer, description, quantity, unit_price, tax_rate):
        customer, description = customer.strip(), description.strip()
        if not customer or not description:
            raise ValueError("Enter both customer name and product/service.")
        if len(customer) > 200 or len(description) > 2000:
            raise ValueError("Maximum lengths: customer 200, description 2000 characters.")
        qty = _number(quantity, "Quantity", "1000000000")
        if qty == 0:
            raise ValueError("Quantity must be greater than zero.")
        return cls(customer, description, qty,
                   _number(unit_price, "Unit price", "1000000000000"),
                   _number(tax_rate, "Tax percentage", "100"))

    @property
    def subtotal(self):
        return (self.quantity * self.unit_price).quantize(CENT, rounding=ROUND_HALF_UP)

    @property
    def tax_amount(self):
        return (self.subtotal * self.tax_rate / 100).quantize(CENT, rounding=ROUND_HALF_UP)

    @property
    def total(self):
        return self.subtotal + self.tax_amount
