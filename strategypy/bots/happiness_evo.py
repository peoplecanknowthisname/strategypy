import random
import sys
from copy import deepcopy
import json

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

FRIENDS = 0
ENEMIES = 0


class Bot(HappinessBaseBot):

    OCCUPANCE_LIMIT = 20

    # distance range : num cells in that range
    SHELL_BANDS = {
        (0, 1): 0, # 1
        (1, 2): 0, # 4
        (2, 3): 0, # 8
        (3, 4): 0, # 12
        (4, 5): 0, # 16
        (5, 7): 0, 
        (7, 10): 0, 
        (10, 15): 0, 
        (15, 25): 0, 
        (25, 100): 0, 
    }

    for shell_band in SHELL_BANDS:
        for distance in range(shell_band[0], shell_band[1]):
            if distance:
                SHELL_BANDS[shell_band] += 4 * distance
            else:
                SHELL_BANDS[shell_band] += 1

    filename = 'happiness_evo.json'

    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        
        with open(self.filename, 'r') as f:
            self.dna = json.load(f)

        dna_copy = self.dna[:]

     #   sys.stderr.write(' len dna - {} \n'.format(len(dna_copy)))

        self.friendly_lookup = {'friends': {}, 'enemies': {}}

      #  i = 0
        
        for shell_band, max_per_band in self.SHELL_BANDS.items():
                
            values_in_band = min(max_per_band + 1, 20)

            for aligence in ('friends', 'enemies'):
                self.friendly_lookup[aligence][shell_band] = dna_copy[:values_in_band]
                dna_copy = dna_copy[values_in_band:]
     #           i += values_in_band
    #            sys.stderr.write('needed {} remaining {}\n'.format(i, len(dna_copy)))

        assert not len(dna_copy)

    def calc_happiness(self, friend_dist, enemy_dist):
        
        def _band_summing(shell_band):
            friends_in_band = 0
            enemies_in_band = 0

            friends_in_band += sum(friend_dist[shell_band[0]: shell_band[1]])
            enemies_in_band += sum(enemy_dist[shell_band[0]: shell_band[1]])

            return friends_in_band, enemies_in_band

        def _scale_to_limit(x_in_band, max_per_band):
            return int(x_in_band * 1. * self.OCCUPANCE_LIMIT / max_per_band)

        def lookup_happiness(a, b, c):
            return self.friendly_lookup[a][b][c]

        happiness = 0.

        for shell_band, max_per_band in self.SHELL_BANDS.items():
            friends_in_band, enemies_in_band = _band_summing(shell_band)

            if max_per_band >= self.OCCUPANCE_LIMIT:
                friends_in_band = _scale_to_limit(friends_in_band, max_per_band)
                enemies_in_band = _scale_to_limit(enemies_in_band, max_per_band)

     #       sys.stderr.write('fib {} feb {} shell_band {}\n'.format(friends_in_band, enemies_in_band, shell_band))
      #      sys.stderr.write(' - {} \n'.format(self.friendly_lookup['friends'][shell_band]))

            happiness += lookup_happiness('enemies', shell_band, friends_in_band) 
            happiness += lookup_happiness('enemies', shell_band, enemies_in_band) 
        
        return happiness
