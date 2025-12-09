from __future__ import annotations

from typing import List, TYPE_CHECKING

from poker_bot.engine.deck import Deck

if TYPE_CHECKING:
    from poker_bot.engine.table import PokerTable
    from poker_bot.engine.player import Player
    from poker_bot.engine.card import Card


class Dealer:
    """The dealer is in charge of handling the cards on a poker table."""

    HAND_SIZE = 2
    FLOP_SIZE = 3
    TURN_SIZE = 1
    RIVER_SIZE = 1

    def __init__(self, **deck_kwargs):
        self.deck = Deck(**deck_kwargs)

    def deal_hands_to_players(self, players: List[Player]):
        for _ in range(self.HAND_SIZE):
            for player in players:
                card = self.deal_card()
                player.add_private_card(card)

    def deal_flop(self, table: PokerTable):
        return self._deal_community_cards(table, self.FLOP_SIZE)

    def deal_turn(self, table: PokerTable):
        return self._deal_community_cards(table, self.TURN_SIZE)

    def deal_river(self, table: PokerTable):
        return self._deal_community_cards(table, self.RIVER_SIZE)

    def deal_card(self) -> Card:
        return self.deck.pick_random_card()

    def _deal_community_cards(self, table: PokerTable, n_cards: int):
        if n_cards <= 0:
            raise ValueError(
                f"Positive n of cards must be specified, but got {n_cards}"
            )
        for _ in range(n_cards):
            card = self.deal_card()
            table.add_community_card(card)
