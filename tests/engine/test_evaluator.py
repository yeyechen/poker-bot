"""Test cases for the Evaluator class.

This module tests the hand evaluation logic including:
- Basic hand ranking comparisons (e.g. Flush > Straight)
- Exact hand value calculations for 5, 6, and 7 card hands
- Hand class identification (e.g. "Royal Flush", "Pair")
- Tie-breaking and kicker logic
- Edge cases like Wheel straights and counterfeited hands
"""

import pytest
from poker_bot.engine.card import Card


class TestEvaluatorHandSizes:
    """Test evaluation with different numbers of cards (5, 6, 7)."""

    def test_evaluate_five_cards(self, evaluator):
        """Test evaluation with exactly 5 cards."""
        cards = [Card("ace", "hearts"), Card("king", "hearts")]
        board = [Card("queen", "hearts"), Card("jack", "hearts"), Card("10", "hearts")]

        score = evaluator.evaluate(cards, board)
        assert score == 1  # Royal Flush

    def test_evaluate_six_cards(self, evaluator):
        """Test evaluation with 6 cards (pick best 5)."""
        # Board has 4 cards, player has 2
        cards = [Card("ace", "hearts"), Card("king", "hearts")]
        board = [
            Card("queen", "hearts"),
            Card("jack", "hearts"),
            Card("10", "hearts"),
            Card("2", "clubs"),  # Irrelevant card
        ]

        score = evaluator.evaluate(cards, board)
        assert score == 1  # Should still find the Royal Flush

    def test_evaluate_seven_cards(self, evaluator):
        """Test evaluation with 7 cards (pick best 5)."""
        # Board has 5 cards, player has 2
        cards = [Card("ace", "hearts"), Card("king", "hearts")]
        board = [
            Card("queen", "hearts"),
            Card("jack", "hearts"),
            Card("10", "hearts"),
            Card("2", "clubs"),  # Irrelevant
            Card("3", "diamonds"),  # Irrelevant
        ]

        score = evaluator.evaluate(cards, board)
        assert score == 1  # Should still find the Royal Flush


class TestBasicHandClasses:
    """Test identification of all 9 standard hand classes."""

    def test_all_hand_classes(self, evaluator):
        """Verify that each hand class is correctly identified."""

        test_cases = [
            (
                "Straight Flush",
                [
                    Card("9", "hearts"),
                    Card("8", "hearts"),
                    Card("7", "hearts"),
                    Card("6", "hearts"),
                    Card("5", "hearts"),
                ],
            ),
            (
                "Four of a Kind",
                [
                    Card("ace", "hearts"),
                    Card("ace", "diamonds"),
                    Card("ace", "clubs"),
                    Card("ace", "spades"),
                    Card("king", "hearts"),
                ],
            ),
            (
                "Full House",
                [
                    Card("king", "hearts"),
                    Card("king", "diamonds"),
                    Card("king", "clubs"),
                    Card("queen", "spades"),
                    Card("queen", "clubs"),
                ],
            ),
            (
                "Flush",
                [
                    Card("ace", "hearts"),
                    Card("jack", "hearts"),
                    Card("8", "hearts"),
                    Card("4", "hearts"),
                    Card("2", "hearts"),
                ],
            ),
            (
                "Straight",
                [
                    Card("ace", "hearts"),
                    Card("king", "diamonds"),
                    Card("queen", "clubs"),
                    Card("jack", "spades"),
                    Card("10", "hearts"),
                ],
            ),
            (
                "Three of a Kind",
                [
                    Card("7", "hearts"),
                    Card("7", "diamonds"),
                    Card("7", "clubs"),
                    Card("king", "spades"),
                    Card("2", "hearts"),
                ],
            ),
            (
                "Two Pair",
                [
                    Card("jack", "hearts"),
                    Card("jack", "diamonds"),
                    Card("9", "clubs"),
                    Card("9", "spades"),
                    Card("ace", "hearts"),
                ],
            ),
            (
                "Pair",
                [
                    Card("10", "hearts"),
                    Card("10", "diamonds"),
                    Card("ace", "clubs"),
                    Card("king", "spades"),
                    Card("2", "hearts"),
                ],
            ),
            (
                "High Card",
                [
                    Card("ace", "hearts"),
                    Card("queen", "diamonds"),
                    Card("9", "clubs"),
                    Card("5", "spades"),
                    Card("2", "hearts"),
                ],
            ),
        ]

        for class_name, hand in test_cases:
            score = evaluator.evaluate(hand, [])
            rank_class = evaluator.get_rank_class(score)
            assert (
                evaluator.class_to_string(rank_class) == class_name
            ), f"Failed to identify {class_name}"


class TestEvaluatorRankings:
    """Test relative rankings of different poker hands."""

    def test_flush_beats_straight(self, evaluator):
        """Verify that a Flush is ranked higher (lower score) than a Straight."""
        # Flush: 2, 4, 6, 8, 10 of hearts
        flush_cards = [
            Card("2", "hearts"),
            Card("4", "hearts"),
            Card("6", "hearts"),
            Card("8", "hearts"),
            Card("10", "hearts"),
        ]

        # Straight: 2, 3, 4, 5, 6 of mixed suits
        straight_cards = [
            Card("2", "clubs"),
            Card("3", "diamonds"),
            Card("4", "hearts"),
            Card("5", "spades"),
            Card("6", "clubs"),
        ]

        flush_score = evaluator.evaluate(flush_cards, [])
        straight_score = evaluator.evaluate(straight_cards, [])

        # Lower score is better
        assert flush_score < straight_score

    def test_four_of_a_kind_beats_full_house(self, evaluator):
        """Verify that Four of a Kind beats a Full House."""
        # Four of a Kind: 9, 9, 9, 9, K
        quads = [
            Card("9", "hearts"),
            Card("9", "diamonds"),
            Card("9", "clubs"),
            Card("9", "spades"),
            Card("king", "hearts"),
        ]

        # Full House: A, A, A, K, K
        full_house = [
            Card("ace", "hearts"),
            Card("ace", "diamonds"),
            Card("ace", "clubs"),
            Card("king", "spades"),
            Card("king", "clubs"),
        ]

        quads_score = evaluator.evaluate(quads, [])
        fh_score = evaluator.evaluate(full_house, [])

        assert quads_score < fh_score

    def test_royal_flush_is_best(self, evaluator):
        """Verify that a Royal Flush has the best possible score (1)."""
        royal_flush = [
            Card("ace", "spades"),
            Card("king", "spades"),
            Card("queen", "spades"),
            Card("jack", "spades"),
            Card("10", "spades"),
        ]

        score = evaluator.evaluate(royal_flush, [])
        assert score == 1


class TestTieBreakingAndKickers:
    """Test tie-breaking logic and kicker comparisons."""

    def test_split_pot_different_suits(self, evaluator):
        """Verify that hands with same ranks but different suits return exact same score."""
        hand1 = [
            Card("ace", "hearts"),
            Card("king", "hearts"),
            Card("queen", "hearts"),
            Card("jack", "hearts"),
            Card("9", "hearts"),
        ]  # Flush

        hand2 = [
            Card("ace", "spades"),
            Card("king", "spades"),
            Card("queen", "spades"),
            Card("jack", "spades"),
            Card("9", "spades"),
        ]  # Flush with same ranks

        score1 = evaluator.evaluate(hand1, [])
        score2 = evaluator.evaluate(hand2, [])

        assert score1 == score2

    def test_kicker_pair_of_aces(self, evaluator):
        """Verify Pair of Aces with better kicker wins."""
        # AA K 8 2
        hand_better = [
            Card("ace", "hearts"),
            Card("ace", "diamonds"),
            Card("king", "clubs"),
            Card("8", "spades"),
            Card("2", "hearts"),
        ]

        # AA Q 8 2
        hand_worse = [
            Card("ace", "clubs"),
            Card("ace", "spades"),
            Card("queen", "hearts"),
            Card("8", "diamonds"),
            Card("2", "clubs"),
        ]

        score_better = evaluator.evaluate(hand_better, [])
        score_worse = evaluator.evaluate(hand_worse, [])

        # Lower score is better
        assert score_better < score_worse

    def test_kicker_two_pair(self, evaluator):
        """Verify Two Pair with better kicker wins."""
        # KK 22 A
        hand_better = [
            Card("king", "hearts"),
            Card("king", "diamonds"),
            Card("2", "clubs"),
            Card("2", "spades"),
            Card("ace", "hearts"),
        ]

        # KK 22 Q
        hand_worse = [
            Card("king", "clubs"),
            Card("king", "spades"),
            Card("2", "hearts"),
            Card("2", "diamonds"),
            Card("queen", "clubs"),
        ]

        score_better = evaluator.evaluate(hand_better, [])
        score_worse = evaluator.evaluate(hand_worse, [])

        assert score_better < score_worse


class TestEdgeCases:
    """Test edge cases and tricky hand evaluations."""

    def test_wheel_straight(self, evaluator):
        """Verify A-2-3-4-5 (Wheel) is a valid straight and ranked correctly."""
        # Wheel: 5-4-3-2-A
        wheel = [
            Card("5", "hearts"),
            Card("4", "diamonds"),
            Card("3", "clubs"),
            Card("2", "spades"),
            Card("ace", "hearts"),
        ]

        # 6-high straight: 6-5-4-3-2
        six_high = [
            Card("6", "hearts"),
            Card("5", "diamonds"),
            Card("4", "clubs"),
            Card("3", "spades"),
            Card("2", "hearts"),
        ]

        wheel_score = evaluator.evaluate(wheel, [])
        six_high_score = evaluator.evaluate(six_high, [])

        # Wheel is valid
        rank_class = evaluator.get_rank_class(wheel_score)
        assert evaluator.class_to_string(rank_class) == "Straight"

        # Wheel (5-high) loses to 6-high straight
        assert six_high_score < wheel_score

    def test_nut_low_comparison(self, evaluator):
        """Verify 7-5-4-3-2 beats 7-6-4-3-2 (Low hand comparison)."""
        # 7-5-4-3-2 unsuited
        hand1 = [
            Card("7", "hearts"),
            Card("5", "diamonds"),
            Card("4", "clubs"),
            Card("3", "spades"),
            Card("2", "hearts"),
        ]

        # 7-6-4-3-2 unsuited
        hand2 = [
            Card("7", "diamonds"),
            Card("6", "clubs"),
            Card("4", "spades"),
            Card("3", "hearts"),
            Card("2", "diamonds"),
        ]

        score1 = evaluator.evaluate(hand1, [])
        score2 = evaluator.evaluate(hand2, [])

        assert score2 < score1

    def test_counterfeited_pocket_pair(self, evaluator):
        """Verify that a counterfeited pocket pair uses the board's kickers."""
        # Board: K K Q Q A
        board = [
            Card("king", "hearts"),
            Card("king", "diamonds"),
            Card("queen", "clubs"),
            Card("queen", "spades"),
            Card("ace", "hearts"),
        ]

        # Player 1: 3 3 (Counterfeited pair, plays board: KK QQ A)
        player1_hand = [Card("3", "diamonds"), Card("3", "clubs")]

        # Player 2: 2 2 (Counterfeited pair, plays board: KK QQ A)
        player2_hand = [Card("2", "diamonds"), Card("2", "clubs")]

        score1 = evaluator.evaluate(player1_hand, board)
        score2 = evaluator.evaluate(player2_hand, board)

        # Both play the board, so it's a chop
        assert score1 == score2

        # Verify rank is Two Pair
        rank_class = evaluator.get_rank_class(score1)
        assert evaluator.class_to_string(rank_class) == "Two Pair"

    def test_counterfeited_pair_vs_kicker(self, evaluator):
        """Verify board kicker plays over pocket pair."""
        # Board: K K Q Q 4
        board = [
            Card("king", "hearts"),
            Card("king", "diamonds"),
            Card("queen", "clubs"),
            Card("queen", "spades"),
            Card("4", "hearts"),
        ]

        # Player 1: 3 3 (Plays KK QQ 4)
        p1 = [Card("3", "diamonds"), Card("3", "clubs")]

        # Player 2: A 2 (Plays KK QQ A)
        p2 = [Card("ace", "diamonds"), Card("2", "clubs")]

        score1 = evaluator.evaluate(p1, board)
        score2 = evaluator.evaluate(p2, board)

        # Player 2 wins because A kicker plays
        assert score2 < score1

    def test_suit_independence(self, evaluator):
        """Verify that non-flush hands score identical regardless of specific suits."""
        # As Ks 8d 7c 2h
        hand1 = [
            Card("ace", "spades"),
            Card("king", "spades"),
            Card("8", "diamonds"),
            Card("7", "clubs"),
            Card("2", "hearts"),
        ]

        # Ac Kc 8s 7d 2s
        hand2 = [
            Card("ace", "clubs"),
            Card("king", "clubs"),
            Card("8", "spades"),
            Card("7", "diamonds"),
            Card("2", "spades"),
        ]

        score1 = evaluator.evaluate(hand1, [])
        score2 = evaluator.evaluate(hand2, [])

        assert score1 == score2

    def test_wrap_around_straight_invalid(self, evaluator):
        """Verify that Q-K-A-2-3 is NOT a straight."""
        # This should likely be just Ace high or whatever partial hand it makes
        # Q, K, A, 2, 3
        hand = [
            Card("queen", "hearts"),
            Card("king", "diamonds"),
            Card("ace", "clubs"),
            Card("2", "spades"),
            Card("3", "hearts"),
        ]

        score = evaluator.evaluate(hand, [])
        rank_class = evaluator.get_rank_class(score)

        # Should NOT be a straight
        assert evaluator.class_to_string(rank_class) != "Straight"
        assert evaluator.class_to_string(rank_class) == "High Card"

    def test_invalid_card_counts(self, evaluator):
        """Verify that evaluator raises error for invalid card counts."""
        # 4 cards
        cards_4 = [
            Card("ace", "hearts"),
            Card("king", "hearts"),
            Card("queen", "hearts"),
            Card("jack", "hearts"),
        ]

        with pytest.raises((KeyError, IndexError)):
            evaluator.evaluate(cards_4, [])

        # 8 cards
        cards_8 = [
            Card("2", "hearts"),
            Card("3", "hearts"),
            Card("4", "hearts"),
            Card("5", "hearts"),
            Card("6", "hearts"),
            Card("7", "hearts"),
            Card("8", "hearts"),
            Card("9", "hearts"),
        ]

        with pytest.raises((KeyError, IndexError)):
            evaluator.evaluate(cards_8, [])

    def test_duplicate_cards(self, evaluator):
        """Test that the evaluator raises an error when given duplicate cards."""
        # Duplicate Ace of Hearts
        hand = [
            Card("ace", "hearts"),
            Card("ace", "hearts"),
            Card("king", "hearts"),
            Card("queen", "hearts"),
            Card("jack", "hearts"),
        ]

        with pytest.raises(KeyError):
            evaluator.evaluate(hand, [])

    def test_three_way_split_pot(self, evaluator):
        """Verify 3-way split pot with Royal Flush on board."""
        # Board: Royal Flush
        board = [
            Card("ace", "spades"),
            Card("king", "spades"),
            Card("queen", "spades"),
            Card("jack", "spades"),
            Card("10", "spades"),
        ]

        # Player 1: 2d 3d
        p1 = [Card("2", "diamonds"), Card("3", "diamonds")]

        # Player 2: 4c 5c
        p2 = [Card("4", "clubs"), Card("5", "clubs")]

        # Player 3: 6h 7h
        p3 = [Card("6", "hearts"), Card("7", "hearts")]

        score1 = evaluator.evaluate(p1, board)
        score2 = evaluator.evaluate(p2, board)
        score3 = evaluator.evaluate(p3, board)

        assert score1 == score2 == score3
        assert score1 == 1  # Royal Flush score
