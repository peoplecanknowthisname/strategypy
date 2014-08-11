import math
import random
import sys
import json

import numpy
from pybrain.tools.shortcuts import buildNetwork

from api import BaseBot


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

    
class Bot(BaseBot):
    """Robs' Bot"""
    filenames = ['{n}.json'.format(n=n) for n in range(50)]       

    max_age = 1000
    
    local_size = 7
    hidden_fraction = 0.5
    
    input_size = (local_size * 2 + 1 ) ** 2
    output_size = 5
    hidden_size = int((input_size + output_size) * hidden_fraction)

    sys.stderr.write('net shape {p}\n'.format(p=(input_size, hidden_size, output_size)))
    
    dna_size = (input_size * hidden_size) + \
               (output_size * hidden_size) + \
                         (1 * hidden_size) + \
                         (1 * output_size)   # thresholds

    parent_prob = ((0, 0.0), (1, 0.05), (2, 0.85), (3, 0.1))
    num_genes_that_mutate = int(0.0001 * dna_size)
    
    sys.stderr.write('dna size {p} genes that mutate {q}\n'.format(p=dna_size, q=num_genes_that_mutate))
                
    allowed_actions = [
        'move up',
        'move left',
        'move right',
        'move down',
        None,
    ]

    
    def __init__(self, unit, respawn):
        super(Bot, self).__init__(unit, respawn)
        self.unit = unit
        self.num_kills = 1

        self.age = 0

        self.net = buildNetwork(self.input_size, self.hidden_size, self.output_size)
        self.dna = None
        

        if respawn:
            self.filename = self.filenames.pop()
            self.set_new_dna()
            f = file(self.filename, 'w')
            json.dump(list(self.dna), f)
            f.close()
        else:
            
            self.filename = self.filenames.pop()

            try:
                f = open(self.filename, 'r')
                self.dna = json.load(f)
    #            sys.stderr.write('loaded bot {b}\n'.format(b=self.filename))
                f.close()
            except IOError:
                self.set_random_dna()
                f = file(self.filename, 'w')
       #         sys.stderr.write('saved bot {b}\n'.format(b=self.filename))
                json.dump(list(self.dna), f)
                f.close()
            

        self.net.params[:] = numpy.array(self.dna)

        
    def set_new_dna(self):

        num_parents = weighted_choice(self.parent_prob)

        if num_parents == 0:
            self.set_random_dna()
   #         sys.stderr.write('new random\n')

        elif num_parents == 1:
            self.dna = random.choice(self.unit.player.units).bot.dna[:]
 #           sys.stderr.write('new clone\n')

        else:
#            sys.stderr.write('new child weighted parents {p}\n'.format(p=[(u,u.bot.num_kills) for u in self.unit.player.units]))
#            parents = random.sample(self.unit.player.units, num_parents)
            parents = weighted_sample([(u,u.bot.num_kills) for u in self.unit.player.units], num_parents)
 #           for parent in parents:
  #              sys.stderr.write('new child parent {p} {q}\n'.format(q=len(parent.bot.dna), p=parent))
                
            self.dna = []        
            for i in range(self.dna_size):
                try:
                    doner_parent = random.choice([p for p in parents if p is not self.unit])
                    self.dna.append(doner_parent.bot.dna[i])
                except IndexError:
   #                 sys.stderr.write(' {p} {q}\n'.format(q=len(doner_parent.bot.dna), p=i))
                    raise



    #    sys.stderr.write('{p} mutations\n'.format(p=self.num_genes_that_mutate))
        for i in random.sample(range(self.dna_size), self.num_genes_that_mutate):
            self.dna[i] = random.uniform(-1, 1)

        assert 0 not in self.dna


    def set_random_dna(self):
        self.dna = [random.uniform(-1, 1) for i in range(self.dna_size)]
  
        

    def action(self):

        self.age += 1

        if self.age > self.max_age:
            sys.stderr.write('BRAIN WIPE\n')
            self.set_new_dna()
            self.net.params[:] = numpy.array(self.dna)
            self.age=0
            f = file(self.filename, 'w')
   #         sys.stderr.write('saved bot {b}\n'.format(b=self.filename))
            json.dump(list(self.dna), f)
            f.close()
       
        local_grid_shape = self.local_size * 2 + 1, self.local_size * 2 + 1 
        
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
         
        choices = zip(self.allowed_actions, res)
       
        return weighted_choice(choices)

    def you_are_dead(self):
        self.filenames.append(self.filename)
        sys.stderr.write('put back fn {b}\n'.format(b=self.filename))

    def you_killed(self):
        self.num_kills+=1
