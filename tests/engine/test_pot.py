"""Test cases for the Pot class.

This module tests pot management including:
- Adding chips to the pot
- Side pot calculations
- Multi-player pot scenarios
"""

import pytest
from poker_bot.engine.pot import Pot
from poker_bot.engine.player import Player


class TestPotBasics:
    """Test basic pot functionality."""

    def test_create_empty_pot(self):
        """Test creating a new empty pot."""
        pot = Pot()
        assert pot.total == 0
        assert len(pot.side_pots) == 0

    def test_pot_has_unique_id(self):
        """Test that each pot has a unique identifier."""
        pot1 = Pot()
        pot2 = Pot()
        assert pot1.uid != pot2.uid
        assert isinstance(pot1.uid, str)

    def test_add_chips_to_pot(self):
        """Test adding chips from a player to the pot."""
        pot = Pot()
        player = Player(name="Alice", initial_chips=1000, pot=pot)

        pot.add_chips(player, 100)
        assert pot.total == 100
        assert pot[player] == 100

    def test_add_chips_multiple_times(self):
        """Test adding chips from same player multiple times accumulates."""
        pot = Pot()
        player = Player(name="Bob", initial_chips=1000, pot=pot)

        pot.add_chips(player, 50)
        pot.add_chips(player, 100)
        pot.add_chips(player, 150)

        assert pot.total == 300
        assert pot[player] == 300

    def test_pot_with_multiple_players(self):
        """Test pot with contributions from multiple players."""
        pot = Pot()
        player1 = Player(name="Alice", initial_chips=1000, pot=pot)
        player2 = Player(name="Bob", initial_chips=1000, pot=pot)
        player3 = Player(name="Charlie", initial_chips=1000, pot=pot)

        pot.add_chips(player1, 100)
        pot.add_chips(player2, 200)
        pot.add_chips(player3, 150)

        assert pot.total == 450
        assert pot[player1] == 100
        assert pot[player2] == 200
        assert pot[player3] == 150

    def test_pot_reset(self):
        """Test resetting the pot clears all contributions."""
        pot = Pot()
        player = Player(name="Alice", initial_chips=1000, pot=pot)

        pot.add_chips(player, 500)
        assert pot.total == 500

        pot.reset()
        assert pot.total == 0
        assert len(pot.side_pots) == 0

    def test_pot_repr(self):
        """Test the string representation of a pot."""
        pot = Pot()
        player = Player(name="Test", initial_chips=1000, pot=pot)
        pot.add_chips(player, 250)

        repr_str = repr(pot)
        assert "Pot" in repr_str
        assert "250" in repr_str


class TestSidePots:
    """
    Test side pot calculations for all-in scenarios.

    These tests cover the complex logic of splitting the main pot into
    side pots when players have different amounts of chips (all-in).
    """

    def test_equal_contributions_no_side_pots(self):
        """Test that equal contributions result in one main pot."""
        pot = Pot()
        player1 = Player(name="Alice", initial_chips=1000, pot=pot)
        player2 = Player(name="Bob", initial_chips=1000, pot=pot)

        pot.add_chips(player1, 100)
        pot.add_chips(player2, 100)

        side_pots = pot.side_pots
        assert len(side_pots) == 1
        assert side_pots[0][player1] == 100
        assert side_pots[0][player2] == 100

    def test_one_player_all_in_creates_side_pot(self):
        """Test side pot creation when one player is all-in for less."""
        pot = Pot()
        player1 = Player(name="Alice", initial_chips=1000, pot=pot)
        player2 = Player(name="Bob", initial_chips=1000, pot=pot)
        player3 = Player(name="Charlie", initial_chips=1000, pot=pot)

        # Player1 all-in for 50, others bet 200
        pot.add_chips(player1, 50)
        pot.add_chips(player2, 200)
        pot.add_chips(player3, 200)

        side_pots = pot.side_pots

        # Should be 2 side pots: main pot (3x50=150) and side pot (2x150=300)
        assert len(side_pots) == 2

        # Main pot: all three players contributed 50
        assert side_pots[0][player1] == 50
        assert side_pots[0][player2] == 50
        assert side_pots[0][player3] == 50

        # Side pot: only player2 and player3 contributed remaining 150 each
        assert player1 not in side_pots[1]
        assert side_pots[1][player2] == 150
        assert side_pots[1][player3] == 150

    def test_multiple_all_ins_multiple_side_pots(self):
        """Test complex scenario with multiple players all-in at different amounts."""
        pot = Pot()
        player1 = Player(name="Alice", initial_chips=1000, pot=pot)
        player2 = Player(name="Bob", initial_chips=1000, pot=pot)
        player3 = Player(name="Charlie", initial_chips=1000, pot=pot)
        player4 = Player(name="Diana", initial_chips=1000, pot=pot)

        # Different bet amounts simulating multiple all-ins
        pot.add_chips(player1, 100)  # All-in at 100
        pot.add_chips(player2, 300)  # All-in at 300
        pot.add_chips(player3, 500)  # All-in at 500
        pot.add_chips(player4, 500)  # Calls at 500

        side_pots = pot.side_pots

        # Should create 3 side pots
        assert len(side_pots) == 3

        # First pot: everyone contributed 100
        assert side_pots[0][player1] == 100
        assert side_pots[0][player2] == 100
        assert side_pots[0][player3] == 100
        assert side_pots[0][player4] == 100

        # Second pot: player2, 3, 4 contributed 200 more each
        assert player1 not in side_pots[1]
        assert side_pots[1][player2] == 200
        assert side_pots[1][player3] == 200
        assert side_pots[1][player4] == 200

        # Third pot: player3 and 4 contributed 200 more each
        assert player1 not in side_pots[2]
        assert player2 not in side_pots[2]
        assert side_pots[2][player3] == 200
        assert side_pots[2][player4] == 200

    def test_side_pots_total_equals_main_pot(self):
        """Test that sum of all side pots equals the main pot total."""
        pot = Pot()
        player1 = Player(name="Alice", initial_chips=1000, pot=pot)
        player2 = Player(name="Bob", initial_chips=1000, pot=pot)
        player3 = Player(name="Charlie", initial_chips=1000, pot=pot)

        pot.add_chips(player1, 75)
        pot.add_chips(player2, 250)
        pot.add_chips(player3, 500)

        total_from_side_pots = sum(sum(side_pot.values()) for side_pot in pot.side_pots)

        assert total_from_side_pots == pot.total
        assert pot.total == 825


class TestPlayerPotIntegration:
    """Test integration between Player and Pot classes."""

    def test_player_can_index_pot(self):
        """Test that players can query their contribution to the pot."""
        pot = Pot()
        player = Player(name="Test Player", initial_chips=1000, pot=pot)

        pot.add_chips(player, 250)

        # Player can directly index the pot
        assert pot[player] == 250

    def test_invalid_pot_index_raises_error(self):
        """Test that indexing pot with non-player raises ValueError."""
        pot = Pot()

        with pytest.raises(ValueError, match="Index the pot with the player"):
            _ = pot["not_a_player"]

    def test_player_pot_reference_consistency(self):
        """Test that player and pot reference the same pot object."""
        pot = Pot()
        player = Player(name="Alice", initial_chips=1000, pot=pot)

        # Player's pot should be the same object
        assert player.pot is pot
        assert player.pot.uid == pot.uid
