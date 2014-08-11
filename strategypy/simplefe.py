import json
import sys
import copy
from optparse import OptionParser


def print_frames(output_dict):
    grid_size = output_dict['grid_size']

    empty_grid = [
        [' '] * grid_size[0]
        for i in range(grid_size[1])
    ]
    
    print '-' * (grid_size[0] + 2)
    
    for frame in output_dict['frames']:
        grid = copy.deepcopy(empty_grid)
        for player_pk in frame:
            for unit_id in frame[player_pk]:
                x, y = frame[player_pk][unit_id]
                grid[x][y] = player_pk
    
        for row in grid:
            print '|'+''.join(row)+'|'
        
        print '-'*(grid_size[0]+2)         


def print_summary(output_dict):
    winner = output_dict['winner']
    players = output_dict['players']
         
    turns = output_dict['turns']
    
    initial_frame = output_dict['frames'][0]
    last_frame = output_dict['frames'][-1]
    
    initial_count = sum((len(x) for x in initial_frame.itervalues()))
    final_count = sum((len(x) for x in last_frame.itervalues()))

    winner = None if winner is None else players[str(winner)]
    if winner is None:
        print 'No player won and the game ended in {} turns'.format(turns)
    else:
        print 'Player {} won in {} turns'.format(winner, turns)
    print 'Initial unit count: {}'.format(initial_count)
    print 'Final unit count: {}'.format(final_count)
    
    
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--frames",
                      action="store_true", dest="show_frames", default=False,
                      help="Show the frames")

    (options, _) = parser.parse_args()


    output = sys.stdin.read()
    output_dict = json.loads(output)
    
    if options.show_frames:
        print_frames(output_dict)
    print_summary(output_dict)