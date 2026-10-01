"""Cost worksheet arithmetic and boundary tests."""
import unittest
from decimal import Decimal

from tender_clarity.costs import calculate_costs


class CostCalculationTests(unittest.TestCase):
    def test_known_costs_calculate_total_remaining_and_margin(self):
        result = calculate_costs(
            {"labour": 1000, "materials": 500, "transport": 100, "equipment": 200, "overheads": 150, "other": 50},
            2500,
        )
        self.assertEqual(result["total_estimated_costs"], Decimal("2000.00"))
        self.assertEqual(result["amount_remaining"], Decimal("500.00"))
        self.assertEqual(result["margin_percent"], Decimal("20.00"))
        self.assertFalse(result["below_estimated_cost"])

    def test_value_below_costs_shows_negative_remainder_and_margin(self):
        result = calculate_costs({"labour": 1000, "materials": 500}, 1000)
        self.assertEqual(result["total_estimated_costs"], Decimal("1500.00"))
        self.assertEqual(result["amount_remaining"], Decimal("-500.00"))
        self.assertEqual(result["margin_percent"], Decimal("-50.00"))
        self.assertTrue(result["below_estimated_cost"])

    def test_zero_or_blank_contract_value_has_no_percentage_margin(self):
        result = calculate_costs({"labour": 100}, "")
        self.assertEqual(result["amount_remaining"], Decimal("-100.00"))
        self.assertIsNone(result["margin_percent"])
        self.assertTrue(result["below_estimated_cost"])

    def test_zero_value_and_zero_costs_are_valid(self):
        result = calculate_costs({}, 0)
        self.assertEqual(result["total_estimated_costs"], Decimal("0.00"))
        self.assertEqual(result["amount_remaining"], Decimal("0.00"))
        self.assertIsNone(result["margin_percent"])
        self.assertFalse(result["below_estimated_cost"])

    def test_negative_cost_or_value_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            calculate_costs({"labour": -1}, 100)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            calculate_costs({}, -1)

    def test_non_finite_amount_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            calculate_costs({"labour": float("inf")}, 100)


if __name__ == "__main__":
    unittest.main()