




import numpy

from pybrain.tools.shortcuts import buildNetwork






import math
import random
from api import BaseBot

def weighted_choice(choices):
    
    choices = dict([(c, max(w, 0)) for (c, w) in choices])
    
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w > r:
            return c
        upto += w
    assert False, "Shouldn't get here"

    
class Bot(BaseBot):
    """Robs' Bot"""
    
    local_size = 7
    hidden_fraction = 0.5
    
    input_size = (local_size * 2 + 1 ) ** 2
    output_size = 5
    hidden_size = int((input_size + output_size) * hidden_fraction)
    
    dna_size = (input_size * self.hidden_size) + \
               (output_size * self.hidden_size) + \
                         (1 * self.hidden_size) + \
                         (1 * self.output_size)   # thresholds
                
    allowed_actions = [
        'move up',
        'move left',
        'move right',
        'move down',
        None,
    ]
    
    
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.net = buildNetwork(input_size, hidden_size, output_size)
        self.dna = None
        
        self.create_new_dna()

        self.net.params[:] = numpy.array(dna)

        
    def create_new_dna(self):
        self.dna = self.random_dna()
    
    def random_dna(self):
        return [-1 + 2 * random.random() for i in range(self.dna_size)]
    
  

    def action(self):
       
        local_grid_shape = local_size * 2 + 1, local_size * 2 + 1 
        
        local_data = numpy.zeros(local_grid_shape)
        
        current_frame = self.current_data

        x, y = self.position
        
        for player_pk in current_frame:
            
            code = 1 if player_pk == self.player_pk else -1
            
            for tx,ty in current_frame[player_pk].values():
                dx = x - tx
                dy = y - ty
                
                if not ( -7 <= dx <= 7 and -7 <= dy <=7):
                    continue
                
                local_data[7 + dx, 7 + dy] = code
        
        
        res = self.net.activate(local_data.flat)
        
        choices = dict(zip(self.allowed_actions, res))
        
        return weighted_choice(choices)
        