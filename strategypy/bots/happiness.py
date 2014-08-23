import random
import sys
from copy import deepcopy

from api import BaseBot

from happines_base import Bot as HappinessBaseBot


"""
...........
.....3.....
....323....
...32123...
..321H123..
...32X23...
....323....
.....3.....
...........
...........
...........
"""


class Bot(HappinessBaseBot):

    MAX_SHELL_OCC = 0.74
    ENEMY_MUL = 0.5
    DIST_MUL = 1.
    

    def calc_happiness(self, friend_dist, enemy_dist):
        
        happiness = 0. #+ random.random()/100.

        # occupied cells are unhappy
        if friend_dist[0] or enemy_dist[0]:
            return happiness

        # friends make me happy
        for distance in range(1, 100):

            max_per_shell = 4 * distance
            shell_occupancy = (friend_dist[distance] * 1. / max_per_shell)
            happiness += min(shell_occupancy, self.MAX_SHELL_OCC) / (distance * self.DIST_MUL)

        # enemiess make me happy, but not as much
        for distance in range(1, 100):

            max_per_shell = 4 * distance
            shell_occupancy = (enemy_dist[distance] * 1. / max_per_shell)
            happiness += self.ENEMY_MUL * min(shell_occupancy, self.MAX_SHELL_OCC) / (distance * self.DIST_MUL)
        
        return happiness
