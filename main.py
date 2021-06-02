import json
from lib import logger
from lib.logger import LogTarget, LogVerbosity

import numpy as np
from lib.utils import DomainConstraintType, DomainOptimizationType, plot_map
from lib.domain import DomainConstraint, DomainProblem
from argparse import ArgumentParser
import time

def run_map_example(blocks_filename, columns_filename, image_filename=None, plot=False, log_target=LogTarget.NONE, log_verbose=LogVerbosity.LOW):
    start_time = time.time()
    logger.set_target(log_target)
    logger.set_verbosity(log_verbose)

    budget = 100000

    with open(blocks_filename) as json_blocks, open(columns_filename) as json_columns:
        blocks = json.load(json_blocks)
        columns = json.load(json_columns)

    blocks_num = len(blocks)
    cols_num = len(columns)
    var_number = blocks_num * cols_num
    c = np.array([columns[i % cols_num]['power'] for i in range(var_number)])

    int_probl = DomainProblem(c, DomainOptimizationType.MAX, is_integer=True)

    # area
    for index, block in enumerate(blocks):
        int_probl.add_constraint(DomainConstraint([columns[i % cols_num]['area'] if index * cols_num <= i < (index + 1) * cols_num else 0 for i in range(var_number)], block['area'], DomainConstraintType.LESS_EQUAL))

    # minim 
    for index, block in enumerate(blocks):
        int_probl.add_constraint(DomainConstraint([1 if index * cols_num <= i < (index + 1) * cols_num else 0 for i in range(var_number)], block['min_number'], DomainConstraintType.GREAT_EQUAL))

    # price 
    int_probl.add_constraint(DomainConstraint([columns[i % cols_num]['cost'] for i in range(var_number)], budget, DomainConstraintType.LESS_EQUAL))

    # availability 
    for index, column in enumerate(columns):
        int_probl.add_constraint(DomainConstraint([1 if i % cols_num == index else 0 for i in range(var_number)], column['availability'], DomainConstraintType.LESS_EQUAL))

    ret, opt, sol = int_probl.solve()
    end_time = time.time()
    
    if plot:
        plot_map(image_filename, blocks, columns, sol)

    return end_time - start_time

def run_toy_example(example_filename, plot=False, log_target=LogTarget.NONE, log_verbose=LogVerbosity.LOW):
    start_time = time.time()
    logger.set_target(log_target)
    logger.set_verbosity(log_verbose)

    int_probl = DomainProblem.from_json(example_filename)
    ret, opt, sol = int_probl.solve()
    print("\nsolution : ",opt, sol)
    end_time = time.time()

    return end_time - start_time


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-L", "--logging", dest="logging", help="Defines logging mode", default="none", choices=['none', 'console', 'file'])
    parser.add_argument('-V', '--verbosity', dest="verbosity", help="Defines verbosity level", default="low", choices=['low', 'high'])
    parser.add_argument('-P', '--plot', dest="plot", help="If specified plots the resulting image at the end of execution", default=False, action='store_true')
    parser.add_argument('-R', '--run', dest="run", help="Chooses the example to run", default="linear", choices=['linear', 'integer', 'map'])
    args = parser.parse_args()

    log_target = {
        "none": LogTarget.NONE,
        "console": LogTarget.CONSOLE,
        "file": LogTarget.FILE,
    }[args.logging]

    log_verbose = {
        "low": LogVerbosity.LOW,
        "high": LogVerbosity.HIGH,
    }[args.verbosity]

    if args.run == "map":
        execution_time = run_map_example("res/rome.json", "res/columns.json", "res/rome.png", plot=args.plot, log_target=log_target, log_verbose=log_verbose)
    elif args.run == "linear":
        execution_time = run_toy_example("res/linear_example.json", plot=args.plot, log_target=log_target, log_verbose=log_verbose)
    elif args.run == "integer":
        execution_time = run_toy_example("res/integer_example.json", plot=args.plot, log_target=log_target, log_verbose=log_verbose)

    print("Execution finished in " + str(execution_time) + "s")
