#!/usr/bin/env python

import numpy as np
from scipy.optimize import linear_sum_assignment
from pypdf import PdfReader
import re

# 1 = seed
# 2 = spacer
# 3 = double spacer
# 0 = empty

def get_needles(pdf_path):
    reader = PdfReader(pdf_path) # make pdf reader object
    num_pages = reader.get_num_pages()
    
    needles = {}
    retraction = {}
    hole = {} 
    seed_num = {} 

    for p in range(num_pages):
        page = reader.pages[p] # get page
    
        text = page.extract_text() # extract text

        lines = [line for line in text.splitlines() if re.match(r"^\d+\s+\d\.", line)] # gets all lines with a number followed by any number of spaces followed by a number and decimal place
        
        if len(lines) == 0:
            continue

        needle_loc = {}
        for line in lines:
            columns = line.split() # turn each line into a list deliminated by whitespace
            if len(columns) >= 5 and len(columns) <= 11: # double checks to make sure the line it grabbed was a needle
                needle_num = int(columns[0]) # sets the dictionary key 
                loc = [float(n) for n in columns[4:]] # gets the location of each needle
                needle_loc[needle_num] = loc
                
                retraction[needle_num] = columns[1] # get and set important info
                hole[needle_num] = columns[2]
                seed_num[needle_num] = columns[3]

        for i in needle_loc:
            needles[i] = [] 
            for j in range(len(needle_loc[i])):
                needles[i].append(1) # assign seed to each location (1)
                if j < len(needle_loc[i]) - 1:
                    spacer_count = int(needle_loc[i][j+1] - needle_loc[i][j]) # count number of spaces in between seeds
                    needles[i].extend([2] * spacer_count) # add spacers (2)
                else:
                    needles[i].append(2) # add trailing spacer

            needles[i].extend([0] * (11 - len(needles[i]))) # pad needle with zeros
            
            if len(needles[i]) > 11: # Redundancy to make sure it really read the needle
                print("Error, bad pdf")
                break

            needles[i] = np.array(needles[i]) 

    return needles, retraction, hole, seed_num

pp_file = input("Enter pre-plan file name with .pdf: ")
OR_file = input("Enter OR-plan file name with .pdf: ")

pp_needles, retract_pp, hole_loc_pp, num_seeds_pp = get_needles(pp_file) #needle, retraction length, hole location, number of seeds
or_needles, retract_OR, hole_loc_OR, num_seeds_OR = get_needles(OR_file)

# scalars for cost minimazation function
add_weight = float(input("Enter weight of adding a seed or spacer, between 0.1 and 2.0: "))
remove_weight = float(input("Enter weight of removing a seed or spacer, between 0.1 and 2.0: "))
distance_weight = float(input("Enter weight of moving a needle to a different location, between 0.1 and 2.0: "))

#print(pp_needles)
#print('')
#print(or_needles)

params = [add_weight, remove_weight, distance_weight]

# cost function to minimize
def cost_function(*params, num_add, num_remove, distance):
    return 1 + params[0] * num_add + params[1] * num_remove + params[2] * distance

instructions = {}

num_pp = len(pp_needles)
num_or = len(or_needles)

# pad arrays with zeros to make sure the matrix is square
if num_or > num_pp:
    for i in range(num_pp+1, num_or+1):
        pp_needles[i] = np.array([1,2,0,0,0,0,0,0,0,0,0]) # single seed needle
if num_pp > num_or:
    for i in range(num_or+1, num_pp+1):
        or_needles[i] = np.zeros(11) # empty needles
  
cost_matrix = np.zeros((len(pp_needles),len(or_needles))) # create a cost matrix

# loop through each needle, creating cost matrix based on how many moves required
for i in pp_needles:
    instructions[i] = {}
    for j in or_needles:
        
        #pp_needles[i] = double_spacer(pp_needles[i])
        #or_needles[j] = double_spacer(or_needles[j])
        
        initial = pp_needles[i].tolist() # create a temporary list
        target = or_needles[j].tolist()
       
        changes = np.where(pp_needles[i] != or_needles[j])[0] # Finds all locations needles differ
        
        popped = [] # create lists for cost function analysis
        appended = []
        
        spacer_num = 0 
        if len(changes) > 0: # makes sure the arrays are different
            while len(initial) > changes[0]:
                pop_val = initial.pop() # remove seeds or spacers until initial needle matches target needle
                
                # logic to deal with double spacers
                if pop_val == 2: # count spacer
                    spacer_num = 1
                    popped.append(pop_val)
                    
                if pop_val == 2 and spacer_num == 1: # if two spacers in a row, only count as one removal
                    popped.pop()
                    popped.append(3)
                    spacer_num = 0
                
                else:
                    popped.append(pop_val) # store removed values for cost function

            to_append = target[changes[0]:] # seeds and spacers to be added to initial needle to match target needle
            
            for k in range(len(to_append)):
                append_val = to_append[k]
                initial.append(append_val) # add seeds or spacers until initial needle matches target needle
                appended.append(append_val) # store added values for cost function
            
            distance = np.abs(i-j) # soft calculation to give an estimate of work required to move needle to different location 
            num_add = np.count_nonzero(appended) # don't care about zero values (adding or removing nothing)
            num_remove = np.count_nonzero(popped)
            
            cost_matrix[i-1][j-1] = cost_function(*params, num_add=num_add, num_remove=num_remove, distance = distance) # use cost function to create cost matrix
            cost_new = cost_function(*params, num_add=len(target), num_remove=0, distance = 0) # cost of making a new needle

            if cost_new < cost_matrix[i-1][j-1]: # check if it is easier to make a new needle
                cost_matrix[i-1][j-1] = cost_new
                appended = target

                # write instructions
                instructions[i][j] = { 
                'action': 'Make New Needle',
                'remove Following': [],
                'add Following': [x for x in appended if x != 0]
                }

            else:
                instructions[i][j] = {
                'action': 'Modify Existing Needle',
                'remove Following': [x for x in popped if x != 0],
                'add Following': [x for x in appended if x != 0]
                }
                
        else: # if arrays the same, cost value is 1
            cost_matrix[i-1][j-1] = 1
            instructions[i][j] = {
                'action': 'Move Current Needle',
                'remove Following': [],
                'add Following': []
                }



#print(cost_matrix)

if num_pp > num_or: # if there are more target needles than initial needles
    max_cost = cost_matrix.max()
    for i in range(num_pp):
        for j in range(num_or, num_pp):
            cost_matrix[i][j] = max_cost + 1 # overwrtie the cost matrix so padded needles are never prioritized in assignment

start, end = linear_sum_assignment(cost_matrix) # scipy optimizer Jonker-Volgenant algorithm (Hunagrian)

start = start + 1 
end = end + 1 

# print instructions
for i,j in zip(start, end):
    if j > num_or: # don't print instructions for padded needles
        continue

    instr = instructions[i].get(j)
    grid_loc = hole_loc_OR[j]
    print(f"Pre-plan needle {i} -> OR needle {j} ({grid_loc})| Instruction: {instr}")

