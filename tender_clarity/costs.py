"""Small, transparent cost and margin calculations for the Tender Clarity worksheet."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Mapping, Any

_CENT = Decimal("0.01")
_ZERO = Decimal("0.00")


def _money(value: Any, field_name: str) -> Decimal:
    """Convert a contractor-entered amount to non-negative ZAR cents."""
    if value is None or value == "":
        return _ZERO
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{field_name} must be a valid amount.") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{field_name} must be a non-negative amount.")
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def calculate_costs(cost_items: Mapping[str, Any], expected_contract_value: Any) -> dict[str, Any]:
    """Calculate estimated totals, remainder, and margin from user-entered amounts.

    Margin percentage is (expected contract value - estimated costs) divided by
    expected contract value, multiplied by 100. A zero value has no defined
    percentage, so ``margin_percent`` is None in that case.
    """
    costs = {name: _money(value, name) for name, value in cost_items.items()}
    total = sum(costs.values(), _ZERO).quantize(_CENT, rounding=ROUND_HALF_UP)
    expected = _money(expected_contract_value, "Expected contract value")
    remaining = (expected - total).quantize(_CENT, rounding=ROUND_HALF_UP)
    margin = None if expected == 0 else (remaining / expected * Decimal("100")).quantize(_CENT, rounding=ROUND_HALF_UP)
    return {
        "cost_items": costs,
        "total_estimated_costs": total,
        "expected_contract_value": expected,
        "amount_remaining": remaining,
        "margin_percent": margin,
        "below_estimated_cost": expected < total,
    }