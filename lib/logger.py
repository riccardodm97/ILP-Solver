

from enum import Enum


class Verbosity(Enum):
    NOTHING = 1
    LOW = 2
    HIGH = 3

_verbosity = Verbosity.HIGH

def set_verbosity(level: Verbosity):
    _verbosity = level

def write(*message: list, verbosity: Verbosity=Verbosity.LOW):
    if _verbosity.value >= verbosity.value:
        print(*message)