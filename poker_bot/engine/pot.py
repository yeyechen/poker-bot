from __future__ import annotations

import uuid
from collections import Counter
from poker_bot.engine.player import Player


class Pot:

    def __init__(self):
        self._pot = Counter()
        self._uid = str(uuid.uuid4().hex)

    def __repr__(self):
        return f"<Pot n_chips={self.total}>"

    def __getitem__(self, player: Player) -> int:
        return self._pot[player]

    def add_chips(self, player: Player, amount: int):
        self._pot[player] += amount

    def reset(self):
        self._pot = Counter()

    @property
    def side_pots(self):
        side_pots = []
        if not len(self._pot):
            return []
        pot = {k: v for k, v in self._pot.items()}
        while len(pot):
            side_pots.append({})
            min_n_chips = min(pot.values())
            players_to_pop = []
            for player, n_chips in pot.items():
                side_pots[-1][player] = min_n_chips
                pot[player] -= min_n_chips
                if pot[player] == 0:
                    players_to_pop.append(player)
            for player in players_to_pop:
                pot.pop(player)
        return side_pots

    @property
    def uid(self):
        return self._uid

    @property
    def total(self):
        return sum(self._pot.values())
