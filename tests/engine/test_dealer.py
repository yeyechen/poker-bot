"""Test cases for the Dealer class.

This module tests the dealer functionality including:
- Deck management and initialization
- Card distribution to players
- Community card dealing (Flop, Turn, River)
- Error handling
"""

import pytest
from unittest.mock import Mock, MagicMock
from poker_bot.engine.dealer import Dealer
from poker_bot.engine.card import Card
from poker_bot.engine.deck import Deck
from poker_bot.engine.player import Player
from poker_bot.engine.table import PokerTable


class TestDealerInitialization:
    """Test dealer initialization."""

    def test_dealer_init_default(self):
        """Verify dealer initializes with a standard full deck."""
        dealer = Dealer()
        assert isinstance(dealer.deck, Deck)
        assert len(dealer.deck) == 52

    def test_dealer_init_custom_deck(self):
        """Verify dealer passes kwargs to the internal deck."""
        # Create a dealer with a deck containing only Aces
        dealer = Dealer(include_ranks=[14])
        assert len(dealer.deck) == 4  # 4 suits * 1 rank


class TestBasicMechanics:
    """Test basic card dealing mechanics."""

    def test_deal_card_returns_card(self):
        """Verify deal_card returns a Card object."""
        dealer = Dealer()
        card = dealer.deal_card()
        assert isinstance(card, Card)

    def test_deal_card_reduces_deck_size(self):
        """Verify deal_card removes the card from the deck."""
        dealer = Dealer()
        initial_size = len(dealer.deck)

        dealer.deal_card()

        assert len(dealer.deck) == initial_size - 1


class TestPlayerDealing:
    """Test dealing cards to players."""

    @pytest.fixture
    def players(self):
        """Create a list of mock players."""
        p1 = Mock(spec=Player)
        p1.cards = []
        p1.add_private_card = MagicMock(side_effect=lambda c: p1.cards.append(c))

        p2 = Mock(spec=Player)
        p2.cards = []
        p2.add_private_card = MagicMock(side_effect=lambda c: p2.cards.append(c))

        p3 = Mock(spec=Player)
        p3.cards = []
        p3.add_private_card = MagicMock(side_effect=lambda c: p3.cards.append(c))

        return [p1, p2, p3]

    def test_deal_hands_to_players(self, players):
        """Verify dealing hands distributes 2 cards to each player."""
        dealer = Dealer()
        initial_deck_size = len(dealer.deck)
        num_players = len(players)

        dealer.deal_hands_to_players(players)

        # Verify deck size reduction (2 cards per player)
        expected_cards_dealt = num_players * Dealer.HAND_SIZE
        assert len(dealer.deck) == initial_deck_size - expected_cards_dealt

        # Verify each player received cards
        for player in players:
            assert player.add_private_card.call_count == Dealer.HAND_SIZE
            # If using side_effect to append, check list length too
            assert len(player.cards) == Dealer.HAND_SIZE


class TestCommunityCards:
    """Test dealing community cards (Flop, Turn, River)."""

    @pytest.fixture
    def table(self):
        """Create a mock PokerTable."""
        table = Mock(spec=PokerTable)
        table.community_cards = []
        table.add_community_card = MagicMock(
            side_effect=lambda c: table.community_cards.append(c)
        )
        return table

    def test_deal_flop(self, table):
        """Verify dealing flop adds 3 cards to the table."""
        dealer = Dealer()
        initial_deck_size = len(dealer.deck)

        dealer.deal_flop(table)

        assert len(table.community_cards) == 3
        assert len(dealer.deck) == initial_deck_size - 3
        assert table.add_community_card.call_count == 3

    def test_deal_turn(self, table):
        """Verify dealing turn adds 1 card to the table."""
        dealer = Dealer()
        initial_deck_size = len(dealer.deck)

        dealer.deal_turn(table)

        assert len(table.community_cards) == 1
        assert len(dealer.deck) == initial_deck_size - 1
        assert table.add_community_card.call_count == 1

    def test_deal_river(self, table):
        """Verify dealing river adds 1 card to the table."""
        dealer = Dealer()
        initial_deck_size = len(dealer.deck)

        dealer.deal_river(table)

        assert len(table.community_cards) == 1
        assert len(dealer.deck) == initial_deck_size - 1
        assert table.add_community_card.call_count == 1

    def test_deal_sequence(self, table):
        """Verify full dealing sequence (Flop -> Turn -> River)."""
        dealer = Dealer()

        dealer.deal_flop(table)
        assert len(table.community_cards) == 3

        dealer.deal_turn(table)
        assert len(table.community_cards) == 4

        dealer.deal_river(table)
        assert len(table.community_cards) == 5


class TestErrorHandling:
    """Test dealer error handling."""

    def test_deal_community_cards_invalid_count(self):
        """Verify dealing 0 or negative community cards raises ValueError."""
        dealer = Dealer()
        table = Mock(spec=PokerTable)

        with pytest.raises(ValueError, match="Positive n of cards must be specified"):
            dealer._deal_community_cards(table, 0)

        with pytest.raises(ValueError, match="Positive n of cards must be specified"):
            dealer._deal_community_cards(table, -1)

    def test_deal_from_empty_deck(self):
        """Verify dealing from an empty deck raises ValueError."""
        # Create a very small deck
        dealer = Dealer(include_ranks=[2], include_suits=["hearts"])  # 1 card

        # Pick the only card
        dealer.deal_card()
        assert len(dealer.deck) == 0

        # Try to pick again
        with pytest.raises(ValueError, match="Deck is empty"):
            dealer.deal_card()
