import json
import sys

if __name__ == "__main__":
    output = sys.stdin.read()
    output_dict = json.loads(output)
    winner = output_dict['winner']
    players = output_dict['players']
    turns = output_dict['turns']
    initial_frame = output_dict['frames'][0]
    last_frame = output_dict['frames'][-1]
    initial_count = sum((len(x) for x in initial_frame.itervalues()))
    final_count = sum((len(x) for x in last_frame.itervalues()))

    winner = None if winner is None else players[str(winner)]
    if winner is None:
        print 'No player won and the game ended in {turns} turns'.format(turns=turns)
    else:
        print 'Player {winner} won in {turns} turns'.format(winner=winner, turns=turns)
    print 'Initial unit count: {initial_count}'.format(initial_count=initial_count)
    print 'Final unit count: {final_count}'.format(final_count=final_count)
