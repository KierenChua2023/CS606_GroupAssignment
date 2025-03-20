import os
import argparse

import numpy.random as rnd
# from operators import destroy_1, repair_1
from rcjsp import JSP, Parser
from src.alns import ALNS
from src.alns.criteria import *
from src.helper import save_output
from src.settings import DATA_PATH
import sys

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
    
    # load data and random seed
    parsed = Parser(attraction_loc, tourist_loc)

    sys.exit()

    psp = JSP(parsed.tourists, parsed.attractions)

    # construct random initialized solution
    psp.random_initialize(seed)

    print("Initial solution objective is {}.".format(psp.objective()))

    # Generate output file
    save_output("<YourName>_ALNS", psp, "initial")  # // Modify with your name

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

    omegas = [...]  # // Select the weights adjustment strategy
    lambda_ = ...  # // Select the decay parameter
    result = alns.iterate(
        psp, omegas, lambda_, criterion, iterations=1000, collect_stats=True
    )  # // Modify number of ALNS iterations as you see fit

    # result
    solution = result.best_state
    objective = solution.objective()
    print("Best heuristic objective is {}.".format(objective))

    # visualize final solution and generate output file
    save_output("<YourName>_ALNS", solution, "solution")  # // Modify with your name
