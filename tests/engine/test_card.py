"""Test cases for the Card class.

This module tests the card representation and functionality including:
- Card creation with different rank/suit inputs
- Card comparison operations
- Card validation
"""

import pytest
from poker_bot.engine.card import Card, get_all_suits, get_all_ranks


class TestCardCreation:
    """Test card instantiation and basic properties."""

    def test_create_card_with_string_rank(self):
        """Test creating a card with a string rank like 'ace' or 'king'."""
        card = Card(rank="ace", suit="spades")
        assert card.rank == "ace"
        assert card.suit == "spades"
        assert card.rank_int == 14

    def test_create_card_with_integer_rank(self):
        """Test creating a card with an integer rank (2-14)."""
        card = Card(rank=10, suit="hearts")
        assert card.rank == "10"
        assert card.suit == "hearts"
        assert card.rank_int == 10

    def test_create_card_with_shorthand_rank(self):
        """Test creating cards with shorthand notation (J, Q, K, A, T)."""
        jack = Card(rank="j", suit="diamonds")
        assert jack.rank == "jack"
        assert jack.rank_int == 11

        ace = Card(rank="a", suit="clubs")
        assert ace.rank == "ace"
        assert ace.rank_int == 14

    def test_invalid_rank_raises_error(self):
        """Test that invalid ranks raise ValueError."""
        with pytest.raises(ValueError, match="rank should be between 2 and 14"):
            Card(rank=1, suit="hearts")

        with pytest.raises(ValueError, match="rank should be between 2 and 14"):
            Card(rank=15, suit="spades")

    def test_invalid_suit_raises_error(self):
        """Test that invalid suits raise ValueError."""
        with pytest.raises(ValueError, match="suit .* must be in"):
            Card(rank="ace", suit="invalid_suit")

    def test_card_repr(self):
        """Test the string representation of a card."""
        card = Card(rank="king", suit="hearts")
        repr_str = repr(card)
        assert "king" in repr_str
        assert "hearts" in repr_str
        assert "♥" in repr_str  # Unicode heart symbol


class TestCardComparison:
    """Test card comparison operations."""

    def test_card_equality(self):
        """Test that two cards with same rank and suit are equal."""
        card1 = Card(rank="ace", suit="spades")
        card2 = Card(rank="ace", suit="spades")
        assert card1 == card2

    def test_card_inequality(self):
        """Test that cards with different properties are not equal."""
        card1 = Card(rank="ace", suit="spades")
        card2 = Card(rank="king", suit="spades")
        assert card1 != card2

    def test_card_comparisons(self):
        """Test greater/less than and equal comparisons."""
        two = Card(rank=2, suit="hearts")
        five = Card(rank=5, suit="diamonds")
        king = Card(rank="king", suit="diamonds")
        ace = Card(rank="ace", suit="hearts")
        ace2 = Card(rank="ace", suit="spades")

        # Less than / Greater than
        assert two < ace
        assert ace > two
        assert five < king
        assert king > five

        # Less than or equal
        assert two <= ace
        assert two <= two
        assert ace <= ace2  # Same rank

        # Greater than or equal
        assert ace >= two
        assert ace >= ace
        assert ace >= ace2  # Same rank

    def test_card_less_than_or_equal(self):
        """Test less than or equal comparison."""
        jack = Card(rank="jack", suit="clubs")
        queen = Card(rank="queen", suit="clubs")
        assert jack <= queen

        jack2 = Card(rank="jack", suit="spades")
        assert jack.rank_int <= jack2.rank_int

    def test_card_hash(self):
        """Test that cards can be used in sets and as dict keys."""
        card1 = Card(rank="ace", suit="spades")
        card2 = Card(rank="ace", suit="spades")
        card3 = Card(rank="king", suit="spades")

        # Same cards should have same hash
        assert hash(card1) == hash(card2)

        # Can use in set
        card_set = {card1, card2, card3}
        assert len(card_set) == 2  # card1 and card2 are same


class TestCardSerialization:
    """Test card serialization to/from dictionaries."""

    def test_card_to_dict(self):
        """Test converting a card to dictionary format."""
        card = Card(rank="queen", suit="diamonds")
        card_dict = card.to_dict()

        assert isinstance(card_dict, dict)
        assert card_dict["rank"] == 12
        assert card_dict["suit"] == "diamonds"

    def test_card_from_dict(self):
        """Test creating a card from dictionary format."""
        card_dict = {"rank": 14, "suit": "hearts"}
        card = Card.from_dict(card_dict)

        assert card.rank == "ace"
        assert card.suit == "hearts"

    def test_card_roundtrip(self):
        """Test that card -> dict -> card preserves data."""
        original = Card(rank="jack", suit="clubs")
        card_dict = original.to_dict()
        restored = Card.from_dict(card_dict)

        assert original == restored


class TestCardHelperFunctions:
    """Test module-level helper functions."""

    def test_get_all_suits(self):
        """Test that all suits are returned."""
        suits = get_all_suits()
        assert len(suits) == 4
        assert "hearts" in suits
        assert "diamonds" in suits
        assert "clubs" in suits
        assert "spades" in suits

    def test_get_all_ranks(self):
        """Test that all ranks are returned in order."""
        ranks = get_all_ranks()
        assert len(ranks) == 13
        assert ranks[0] == "2"
        assert ranks[-1] == "ace"
        assert "10" in ranks
        assert "jack" in ranks
