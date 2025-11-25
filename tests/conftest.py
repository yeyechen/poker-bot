"""Pytest configuration and shared fixtures."""

import pytest
from poker_bot.engine.evaluation.evaluator import Evaluator


@pytest.fixture(scope="session")
def evaluator():
    """Create a session-scoped Evaluator instance.

    Initializing the hand rank lookup table is expensive, so it should
    only happen once per test run.
    """
    return Evaluator()


@pytest.fixture(autouse=True)
def reset_random_seed():
    """Reset random seed before each test for reproducibility"""
    import random
    import numpy as np

    random.seed(42)
    np.random.seed(42)
