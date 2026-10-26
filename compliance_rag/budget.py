"""Cost / budget inputs: negatives are rejected, never clamped silently.

Clamping a negative cost to zero would hide a data error and corrupt any
total built on it. Every entry point that accepts a cost validates here.
"""

from __future__ import annotations


class BudgetError(ValueError):
    pass


def validate_cost(amount: float) -> float:
    if amount is None or not isinstance(amount, (int, float)):
        raise BudgetError("cost must be a number")
    if amount != amount:  # NaN
        raise BudgetError("cost must not be NaN")
    if amount < 0:
        raise BudgetError(f"negative cost rejected: {amount}")
    return float(amount)


class CostTracker:
    def __init__(self, budget: float):
        self.budget = validate_cost(budget)
        self.spent = 0.0

    def add(self, amount: float) -> float:
        amount = validate_cost(amount)
        self.spent += amount
        return self.spent

    def over_budget(self) -> bool:
        return self.spent > self.budget
