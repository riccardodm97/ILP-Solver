import json
from lib import logger
from lib.logger import LogTarget, LogVerbosity

import numpy as np
from lib.utils import DomainConstraintType, DomainOptimizationType, plot_map
from lib.domain import DomainConstraint, DomainProblem
from argparse import ArgumentParser
import time

image_path = "res/rome2.png"
blocks_data_path = "res/rome2.json"
columns_data_path = "res/columns.json"

def run_example(blocks_filename, columns_filename, image_filename=None, plot=False, log_target=LogTarget.NONE, log_verbose=LogVerbosity.LOW):
    start_time = time.time()
    logger.set_target(log_target)
    logger.set_verbosity(log_verbose)

    with open(blocks_filename) as json_blocks, open(columns_filename) as json_columns:
        blocks = json.load(json_blocks)
        columns = json.load(json_columns)

    blocks_num = len(blocks)
    cols_num = len(columns)
    var_number = blocks_num * cols_num
    c = np.array([columns[i % 3]['power'] for i in range(var_number)])

    int_probl = DomainProblem(c, DomainOptimizationType.MAX, is_integer=True)

    # area
    for index, block in enumerate(blocks):
        int_probl.add_constraint(DomainConstraint([columns[i % cols_num]['area'] if index * cols_num <= i < (index + 1) * cols_num else 0 for i in range(var_number)], block['area'], DomainConstraintType.LESS_EQUAL))

    # minim 
    for index, block in enumerate(blocks):
        int_probl.add_constraint(DomainConstraint([1 if index * cols_num <= i < (index + 1) * cols_num else 0 for i in range(var_number)], block['min_number'], DomainConstraintType.LESS_EQUAL))

    # price 
    int_probl.add_constraint(DomainConstraint([columns[i % cols_num]['cost'] for i in range(var_number)], 600, DomainConstraintType.LESS_EQUAL))

    # availability 
    for index, column in enumerate(columns):
        int_probl.add_constraint(DomainConstraint([1 if index % cols_num == 0 else 0 for i in range(var_number)], column['availability'], DomainConstraintType.LESS_EQUAL))

    ret, opt, sol = int_probl.solve()
    end_time = time.time()

    if plot:
        plot_map(image_filename, blocks, columns, sol)

    return end_time - start_time

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-B", "--blocks", dest="blocks", help="TODO", default="res/rome.json")
    parser.add_argument("-C", "--columns", dest="columns", help="TODO", default="res/columns.json")
    parser.add_argument("-I", "--image", dest="image", help="TODO", default=None)
    parser.add_argument("-L", "--logging", dest="logging", help="TODO", default="none", choices=['none', 'console', 'file'])
    parser.add_argument('-V', '--verbosity', dest="verbosity", help="TODO", default="low", choices=['low', 'high'])
    parser.add_argument('-P', '--plot', dest="plot", help="TODO", default=False, action='store_true')
    args = parser.parse_args()

    execution_time = run_example(args.blocks, args.columns, args.image, 
        plot=args.plot, 
        log_target={
            "none": LogTarget.NONE,
            "console": LogTarget.CONSOLE,
            "file": LogTarget.FILE,
        }[args.logging], 
        log_verbose={
            "low": LogVerbosity.LOW,
            "high": LogVerbosity.HIGH,
        }[args.verbosity])

    print("Execution finished in " + str(execution_time) + "s")
