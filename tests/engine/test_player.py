"""Test cases for the Player class.

This module tests the core player mechanics including:
- State management (active/folded, all-in)
- Chip management (betting, calling, raising)
- Hand management (receiving cards)
- Action generation (Fold, Call, Raise)
"""

import pytest
from poker_bot.engine.player import Player
from poker_bot.engine.pot import Pot
from poker_bot.engine.card import Card
from poker_bot.engine.actions import Call, Fold, Raise


class ConcretePlayer(Player):
    """Concrete implementation of Player for testing."""

    def take_action(self, game_state):
        pass


@pytest.fixture
def pot():
    """Create a fresh pot for each test."""
    return Pot()


@pytest.fixture
def player(pot):
    """Create a default player with 1000 chips."""
    return ConcretePlayer(name="Test Player", initial_chips=1000, pot=pot)


class TestPlayerInitialization:
    """Test player initialization and state properties."""

    def test_initial_state(self, player, pot):
        """Verify player starts with correct initial state."""
        assert player.name == "Test Player"
        assert player.n_chips == 1000
        assert player.cards == []
        assert player.is_active is True
        assert player.is_all_in is False
        assert player.pot is pot
        assert player.n_bet_chips == 0

    def test_is_all_in_property(self, player):
        """Verify is_all_in property works correctly."""
        # Not all-in initially
        assert player.is_all_in is False

        # Reduce chips to 0 but stay active
        player.n_chips = 0
        assert player.is_all_in is True

        # If folded (inactive), is_all_in should be False even with 0 chips?
        # Logic in Player.is_all_in: return self._is_active and self.n_chips == 0
        player.is_active = False
        assert player.is_all_in is False


class TestChipManagement:
    """Test chip transactions and betting limits."""

    def test_add_chips(self, player):
        """Verify adding chips increases the stack."""
        player.add_chips(500)
        assert player.n_chips == 1500

    def test_add_to_pot(self, player, pot):
        """Verify chips move from player stack to pot."""
        amount_bet = player.add_to_pot(100)

        assert amount_bet == 100
        assert player.n_chips == 900
        assert pot.total == 100
        assert pot[player] == 100

    def test_bet_capped_at_stack_size(self, player, pot):
        """Verify player cannot bet more chips than they own."""
        # Try to bet 2000 when only having 1000
        amount_bet = player.add_to_pot(2000)

        # Should be capped at 1000
        assert amount_bet == 1000
        assert player.n_chips == 0
        assert player.is_all_in
        assert pot[player] == 1000

    def test_negative_bet_raises_error(self, player):
        """Verify negative bets raise ValueError."""
        with pytest.raises(ValueError, match="Can not subtract chips"):
            player.add_to_pot(-100)


class TestGameActions:
    """Test player actions (Fold, Call, Raise)."""

    def test_fold_action(self, player):
        """Verify fold() deactivates player and returns Fold action."""
        action = player.fold()

        assert isinstance(action, Fold)
        assert player.is_active is False
        assert player.is_all_in is False  # Should be False if inactive

    def test_call_action_initial_bet(self, player, pot):
        """Verify calling a bet from 0 contribution."""
        # Setup: Another player has bet 100
        opponent = ConcretePlayer("Opponent", 1000, pot)
        opponent.add_to_pot(100)

        # Action: Player calls
        action = player.call([opponent])

        assert isinstance(action, Call)
        assert player.n_chips == 900
        assert pot[player] == 100
        assert pot.total == 200

    def test_call_action_partial_contribution(self, player, pot):
        """Verify calling when already partially invested."""
        # Setup: Player put 20 in (e.g. blind), Opponent raised to 100
        player.add_to_pot(20)

        opponent = ConcretePlayer("Opponent", 1000, pot)
        opponent.add_to_pot(100)

        # Action: Player calls
        action = player.call([player, opponent])

        assert isinstance(action, Call)
        # Should put in 80 more to match 100
        assert player.n_chips == 900  # 1000 - 20 - 80
        assert pot[player] == 100
        assert pot.total == 200

    def test_call_while_all_in(self, player, pot):
        """Verify call() does nothing if player is already all-in."""
        player.n_chips = 0

        opponent = ConcretePlayer("Opponent", 1000, pot)
        opponent.add_to_pot(100)

        action = player.call([opponent])

        assert player.is_all_in is True
        assert isinstance(action, Call)
        assert pot[player] == 0  # No chips added

    def test_raise_to_action(self, player, pot):
        """Verify raise_to() raises total bet to target amount."""
        # Raise TO 300 (total contribution)
        action = player.raise_to(300)

        assert isinstance(action, Raise)
        assert action.amount == 300

        # Should add exactly 300 since starting from 0
        assert player.n_chips == 700  # 1000 - 300
        assert pot[player] == 300

    def test_raise_to_incremental(self, player, pot):
        """Verify raise_to() accounts for existing contribution."""
        # Already put in 50
        player.add_to_pot(50)

        # Raise TO 200 (Target Total = 200)
        # Should add only 150 more chips (200 - 50)
        action = player.raise_to(200)

        assert player.n_chips == 800  # 1000 - 50 (initial) - 150 (raise)
        assert pot[player] == 200  # Total contribution
        assert action.amount == 150

    def test_raise_to_invalid_amount(self, player):
        """Verify raise_to() raises error if target is less than current bet."""
        player.add_to_pot(100)

        with pytest.raises(ValueError):
            player.raise_to(50)


class TestHandManagement:
    """Test managing player's private hand."""

    def test_add_private_card(self, player):
        """Verify cards are added correctly."""
        card1 = Card("ace", "spades")
        card2 = Card("king", "hearts")

        player.add_private_card(card1)
        assert len(player.cards) == 1
        assert player.cards[0] == card1

        player.add_private_card(card2)
        assert len(player.cards) == 2
        assert card2 in player.cards
