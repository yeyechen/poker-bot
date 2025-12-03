from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from poker_bot.engine.actions import Action, Call, Fold, Raise
from poker_bot.engine.state import PokerGameState

if TYPE_CHECKING:
    from poker_bot.engine.card import Card
    from poker_bot.engine.pot import Pot


logger = logging.getLogger(__name__)


class Player:
    """Abstract base class for all poker-playing agents.

    All agents should inherit from this class and implement the take_action
    method.

    A poker player has a name, holds chips to bet with, and has private cards
    to play with. The n_chips of contributions to the pot for a given hand of
    poker are stored cumulative, as the total pot to cash out is just the sum
    of all players' contributions.
    """

    def __init__(self, name: str, initial_chips: int, pot: Pot):
        self.name: str = name
        self.n_chips: int = initial_chips
        self.cards: List[Card] = []
        self._is_active: bool = True
        self.id = int(uuid.uuid4().hex, 16)
        self.pot: Pot = pot
        self.order: int = None
        self.is_small_blind = False
        self.is_big_blind = False
        self.is_dealer = False

    def __repr__(self):
        return (
            '<Player name="{}" n_chips={:05d} n_bet_chips={:05d} '
            "folded={}>".format(
                self.name, self.n_chips, self.n_bet_chips, int(not self._is_active)
            )
        )

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, x):
        self._is_active = x

    @property
    def is_all_in(self) -> bool:
        return self._is_active and self.n_chips == 0

    @property
    def n_bet_chips(self) -> int:
        return self.pot[self]

    def _get_min_valid_amount_to_call(self, chips_to_call: int) -> int:
        return min(self.n_chips, chips_to_call)

    def _call_with_best_effort(self, players: List[Player]) -> None:
        biggest_bet = max(p.n_bet_chips for p in players)
        amount_to_call = self._get_min_valid_amount_to_call(
            biggest_bet - self.n_bet_chips
        )
        self.add_chips_to_pot(amount_to_call)

    def _check_valid_bet_amount(self, amount: int) -> None:
        if amount < 0:
            raise ValueError(f"Can not subtract chips from pot.")
        if amount > self.n_chips:
            raise ValueError(f"Can not bet more chips than you have.")

    def _raise_by(self, amount: int) -> Action:
        self.add_chips_to_pot(amount)
        action = Raise()
        action(amount)
        return action

    def add_chips(self, amount: int) -> None:
        self.n_chips += amount

    def add_chips_to_pot(self, amount: int) -> None:
        self._check_valid_bet_amount(amount)
        self.n_chips -= amount
        self.pot.add_chips(self, amount)

    def fold(self) -> Action:
        self.is_active = False
        return Fold()

    def call(self, players: List[Player]) -> Action:
        if not self.is_all_in:
            self._call_with_best_effort(players)
        return Call()

    def raise_to(self, amount: int) -> Action:
        amount_to_add = amount - self.n_bet_chips
        return self._raise_by(amount_to_add)

    def add_private_card(self, card: Card) -> None:
        self.cards.append(card)

    # @abstractmethod
    def take_action(self, game_state: PokerGameState) -> PokerGameState:
        """All poker strategy is implemented here.

        Smart agents have to implement this method to compete. To take an
        action, agents receive the current game state and have to emit the next
        state.
        """
        pass
