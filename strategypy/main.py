import sys

from game import Game

if __name__ == "__main__":
    game = Game(*sys.argv[1:])
    result = game.main_loop()
    sys.stdout.write(result)
