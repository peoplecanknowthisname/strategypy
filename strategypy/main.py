import sys
import json
import shutil
import random
import os, errno
import glob
import random
import re

from game import Game


rex = re.compile('happiness_evo_w-(?P<won>.*)_s-(?P<score>.*)_hk-(?P<has_killed>.*)_wk-(?P<was_killed>.*)_d0')


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def weighted_sample(choices, num):

    if num == 0:
        return []

    choice = weighted_choice(choices)
    choices = [c for c in choices if c[0] != choice]
    return [choice] + weighted_sample(choices, num-1)

def weighted_choice(choices):

    choices = [(c, max(w, 0)) for (c, w) in choices]

    total = sum(w for c, w in choices)
    if total <= 0:
        return None
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w > r:
            return c
        upto += w
    assert False, "Shouldn't get here"


class Evolver(object):

    def __init__(self, dir_root, bot_name, GAMES_PER_EVAL, POP_SIZE, game_args):
        self.dir_root = dir_root
        self.BOT_NAME = bot_name
        self.GAMES_PER_EVAL = GAMES_PER_EVAL
        self.POP_SIZE = POP_SIZE
        self.game_args = game_args

        self.gen = 0
        self.source_dir = None
        self.dest_dir = None
        self.mutate_amount = 0.01

    def run_games(self):

        wins = 0
        was_killed = 0
        killed = 0

        for attempt in range(self.GAMES_PER_EVAL):
            game = Game(*self.game_args)
            result = game.main_loop()

            winner = game.get_winner()
            if winner and winner.get_bot_class_module_name() == self.BOT_NAME:
                wins += 1

            player = [p for p in game.all_players if p.get_bot_class_module_name() == self.BOT_NAME][0]

            was_killed += sum(player.was_killed_by.values())
            killed += sum(player.has_killed.values())

        return wins, killed, was_killed

    def rank_bots(self, filenames):
        files = []
        for filename in filenames:
            res = rex.search(filename)
            fitness = self.score_bot(
                int(res.group('won')),
                int(res.group('has_killed')),
                int(res.group('was_killed')),
            )
            files.append((filename, fitness))

        files = sorted(files)

        return files

    def score_bot(self, wins, killed, was_killed):
        return ((wins * 40 )+ killed - was_killed * 3) ** 2

    def choose_parents(self, parents):
        return weighted_sample(parents, 2)

    def splice_dna(self, dna_1, dna_2):
        new_dna = []
        for i in range(len(dna_1)):
            new_dna.append(random.choice([dna_1[i], dna_2[i]]))

        for i in random.sample(range(len(dna_1)), int(len(dna_1)*self.mutate_amount)):
            new_dna[i] = random.random()

        return new_dna

    def get_dna(self):
        filenames = glob.glob('{}/*.json'.format(self.source_dir))

        files = self.rank_bots(filenames)

        parent_files = self.choose_parents(files)

        print 'parent 1', parent_files[0]
        print 'parent 2', parent_files[1]

        with open(parent_files[0], 'r') as f:
            dna_1 = json.load(f)
        with open(parent_files[1], 'r') as f:
            dna_2 = json.load(f)

        new_dna = self.splice_dna(dna_1, dna_2)

        return new_dna


    def go(self):
        while 1:

            self.dest_dir = '{}/gen_{}'.format(self.dir_root, self.gen)
            mkdir_p(self.dest_dir)

            while 1:
                print 'gen {}: {} bots'.format(
                    self.gen,
                    len(glob.glob('%s/*.json'%self.dest_dir)),
                )

                if len(glob.glob('%s/*.json'%self.dest_dir)) >= self.POP_SIZE:
                    break

                with open('{}.json'.format(self.BOT_NAME), 'w') as f:
                    if not self.source_dir:
                        d = [random.random() for i in range(292)]
                    else:
                        d = self.get_dna()

                    json.dump(d, f)

                wins, killed, was_killed = self.run_games()

                fn = '{}/happiness_evo_w-{:03d}_s-{:03d}_hk-{:03d}_wk-{:03d}_d0-{}_rand-{}.json'.format(
                    self.dest_dir,
                    wins,
                    killed - was_killed,
                    killed,
                    was_killed,
                    d[0],
                    random.random(),
                )

                print fn

                shutil.copy('{}.json'.format(self.BOT_NAME), fn)

            self.source_dir = self.dest_dir
            self.gen += 1


if __name__ == "__main__":

    evo = Evolver(
        dir_root='happiness_dna',
        bot_name='happiness_evo',
        GAMES_PER_EVAL = 10,
        POP_SIZE = 1000,
        game_args = sys.argv[1:],
    )

    evo.go()

if __name__ == "__main__" and False:
    game = Game(*sys.argv[1:])
    result = game.main_loop()
    sys.stdout.write(result)
