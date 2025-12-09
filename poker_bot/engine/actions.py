from __future__ import annotations


__all__ = ["Call", "Fold", "Raise"]


class Action:
    def __init__(self):
        pass


class Call(Action):
    def __repr__(self):
        return "call"


class Fold(Action):
    def __repr__(self):
        return "fold"


class Raise(Action):
    def __call__(self, amount):
        self.amount = amount

    def __repr__(self):
        return f"raise by {self.amount}"
