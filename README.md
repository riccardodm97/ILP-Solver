# Integer Programming Solver

Implementation of a Two-Phase Revised Simplex algorithm and Branch and Bound algorithm for integer programming problems solving.

## Modeling

The project contains some example use cases, including a resource assignment problem aimed at the assignment of electric vehicle recharging stations distributed in different city blocks with several constrains on the placement.

![Example Output](https://github.com/alessandrostockman/cv-intrusion-detection-project-work/blob/master/res/input-example.gif)

## Usage

The class `DomainProblem` implements the method `solve` and returns the solution of the given problem.

The problem can be created either by instanciating `DomainProblem` and adding constraints to it or by importing a json file which contains the problem definition with `DomainProblem.from_json(filename)`.

### Example run

python main.py [-L/--logging LOGGING] [-v/--verbosity VERBOSITY] [-P/--plot] [-R/--run RUN]

--logging: Defines logging mode between file and console
--verbosity: Level of verbosity of logs
--plot: If specified plots the resulting image at the end of execution (when running map)
--run: Chooses the example to run
 