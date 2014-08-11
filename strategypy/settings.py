"""
All the settings/constants of the game
"""

GRID_SIZE = (60, 60)
UNITS = 50
MAX_TURNS = 500
RESPAWN = True

try:
    from local_settings import *
except ImportError:
    pass
