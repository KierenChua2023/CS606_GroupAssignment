import os
import argparse

import numpy.random as rnd
# from operators import destroy_1, repair_1
from rcjsp import SMJSP, Parser
from src.alns import ALNS
from src.alns.criteria import *
from disruptions import *
from src.helper import save_output
from src.settings import DATA_PATH
import sys
import random

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='load data')
    parser.add_argument(dest='attraction_data', type=str, help='attraction data')
    parser.add_argument(dest='tourist_data', type=str, help='tourist data')
    parser.add_argument(dest='seed', type=int, help='seed')
    args = parser.parse_args()
    
    # instance file and random seed
    tourist_loc = args.tourist_data
    attraction_loc = args.attraction_data
    seed = int(args.seed)
    random.seed(seed)

    # Add disruptions
    attraction_disruptions_disruptions = [rainy_day, 
                                            sick_day]

    # load data and random seed
    parsed = Parser(attraction_loc, tourist_loc)

    # Choose a random tourist from the location
    chosen_tourist = random.choice(parsed.tourists)

    smjsp = SMJSP(chosen_tourist, parsed.attractions)

    sys.exit()

    # construct random initialized solution
    smjsp.random_initialize(seed)

    print("Initial solution objective is {}.".format(psp.objective()))

    # Generate output file
    save_output("<YourName>_ALNS", smjsp, "initial")  # // Modify with your name

    # ALNS
    random_state = rnd.RandomState(seed)

    alns = ALNS(random_state)

    # -----------------------------------------------------------------
    # // Implement Code Here
    # You should add all your destroy and repair operators here
    # add destroy operators
    alns.add_destroy_operator(destroy_1)

    # // add repair operators
    alns.add_repair_operator(repair_1)
    # -----------------------------------------------------------------

    # run ALNS & Select Criterion
    criterion = HillClimbing()

    omegas = [7, 5, 2, 0.1]  # // Select the weights adjustment strategy
    lambda_ = 0.5  # // Select the decay parameter

    for i in range(chosen_tourist.days):
        # We iterate along the days to amend the issue
        result = alns.iterate(
            smjsp, omegas, lambda_, criterion, iterations=1000, collect_stats=True
        )  # // Modify number of ALNS iterations as you see fit

        # result
        solution = result.best_state
        objective = solution.objective()
        print("Best heuristic objective is {}.".format(objective))

        # visualize final solution and generate output file
        save_output("<YourName>_ALNS", solution, "solution")  # // Modify with your name

        # We then remove the days left using the remaining days
        del smjsp.tourist.touring_dict[i]

        # We add the current day events to the visited
        for loc in smjsp.tourist.locations[i]:
            smjsp.tourist.visited.append(loc)

        # Remove the data
        del smjsp.tourist.locations[i]
        del smjsp.tourist.start_times[i]

        # We then introduce a random disruption for the next day
        smjsp.attractions = smjsp.attractions
