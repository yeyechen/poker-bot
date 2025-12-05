from __future__ import annotations

import random
from typing import List

import numpy as np

from poker_bot.engine.card import Card, get_all_suits

default_include_suits: List[str] = list(get_all_suits())
default_include_ranks: List[int] = list(range(2, 15))


class Deck:

    def __init__(
        self,
        include_suits: List[str] = default_include_suits,
        include_ranks: List[int] = default_include_ranks,
    ):
        self._include_suits = include_suits
        self._include_ranks = include_ranks
        self.reset()

    def __len__(self) -> int:
        """Return number of cards remaining in the deck."""
        return len(self._cards_in_deck)

    @property
    def dealt_count(self) -> int:
        """Return the number of cards that have been dealt."""
        return len(self._dealt_cards)

    @property
    def total_count(self) -> int:
        """Return the total number of cards (remaining + dealt)."""
        return len(self._cards_in_deck) + len(self._dealt_cards)

    def reset(self):
        """Reset the deck and shuffle it, ready for use."""
        self._cards_in_deck: List[Card] = [
            Card(rank, suit)
            for suit in self._include_suits
            for rank in self._include_ranks
        ]
        self._dealt_cards: List[Card] = []
        random.shuffle(self._cards_in_deck)

    def pick_random_card(self) -> Card:
        return self._next_card(random=True)

    def pick_sequential_card(self) -> Card:
        return self._next_card(random=False)

    def _check_deck_not_empty(self) -> None:
        if not self._cards_in_deck:
            raise ValueError("Deck is empty - please use Deck.reset()")

    def _next_card(self, random: bool = True) -> Card:
        self._check_deck_not_empty()
        if random:
            index = np.random.randint(len(self._cards_in_deck), size=None)
        else:
            index = len(self._cards_in_deck) - 1
        return self._pick_card_using_index(index)

    def _pick_card_using_index(self, index: int) -> Card:
        picked_card = self._cards_in_deck.pop(index)
        self._dealt_cards.append(picked_card)
        return picked_card
