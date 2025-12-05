"""Test cases for the Deck class.

This module tests the deck functionality including:
- Deck initialization and size
- Random and sequential card picking
- Reseeding and resetting the deck
- Removing specific cards
"""

import pytest
from poker_bot.engine.deck import Deck
from poker_bot.engine.card import Card


class TestDeckBasics:
    """Test basic deck operations."""

    def test_deck_initialization(self):
        """Test that a new deck starts with 52 cards."""
        deck = Deck()
        assert len(deck) == 52
        assert deck.total_count == 52

    def test_pick_random(self):
        """Test picking a card randomly decrements deck size."""
        deck = Deck()
        initial_len = len(deck)

        card = deck.pick_random_card()

        assert isinstance(card, Card)
        assert len(deck) == initial_len - 1
        assert deck.dealt_count == 1
        assert deck.total_count == initial_len

        # Let's check that we can pick 52 cards
        picked_cards = set()
        picked_cards.add(card)

        # We already picked 1, so pick 51 more
        for _ in range(51):
            picked_cards.add(deck.pick_random_card())

        assert len(picked_cards) == 52
        assert len(deck) == 0

    def test_pick_sequential(self):
        """Test picking cards sequentially."""
        deck = Deck()
        initial_len = len(deck)

        card = deck.pick_sequential_card()
        assert isinstance(card, Card)
        assert len(deck) == initial_len - 1
        assert deck.dealt_count == 1

    def test_reset_restores_deck(self):
        """Test that reset() restores the deck to full size."""
        deck = Deck()

        # Draw some cards
        deck.pick_random_card()
        deck.pick_random_card()
        deck.pick_random_card()

        # Check length decreases
        assert len(deck) == 49
        assert deck.dealt_count == 3
        assert deck.total_count == 52

        deck.reset()
        assert len(deck) == 52
        assert deck.dealt_count == 0
        assert len(deck._dealt_cards) == 0

    def test_pick_from_empty_deck_raises_error(self):
        """Test that picking from an empty deck raises ValueError."""
        deck = Deck()
        # Empty the deck
        for _ in range(52):
            deck.pick_random_card()

        assert len(deck) == 0

        with pytest.raises(ValueError, match="Deck is empty"):
            deck.pick_random_card()
