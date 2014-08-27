import sys
import json
import shutil
import random
import os, errno
import glob 
import random
import re

from main import Evolver as MainEvolver
from main import weighted_sample, weighted_choice


class Evolver(MainEvolver):
    pass


if __name__ == "__main__":

    evo = Evolver(
        dir_root='happiness_dna',
        bot_name='happiness_evo_4',
        GAMES_PER_EVAL = 10,
        POP_SIZE = 1000,
        game_args = sys.argv[1:],
    )

    evo.go()    
