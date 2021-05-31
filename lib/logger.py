from datetime import datetime
from enum import Enum

class LogVerbosity(Enum):
    NOTHING = 1
    LOW = 2
    HIGH = 3

class LogTarget(Enum):
    FILE = 1
    CONSOLE = 2
    NONE = 3

_verbosity = LogVerbosity.HIGH
_target = LogTarget.FILE
_target_initialized = False
_target_file = None

def set_verbosity(level: LogVerbosity):
    global _verbosity
    _verbosity = level

def set_target(target: LogTarget):
    global _target
    _target = target

def write(*message: list, verbosity: LogVerbosity=LogVerbosity.LOW):
    global _target_initialized, _target_file, _target
    if not _target_initialized:
        if _target is LogTarget.FILE:
            _target_file = open("logs/" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".log", "w")

        _target_initialized = True
    if _verbosity.value >= verbosity.value:
        _print_to_target(*message)

def _print_to_target(*message: list):
    global _target_file, _target
    if _target is LogTarget.CONSOLE:
        print(message)
    elif _target is LogTarget.FILE:
        _target_file.write(" ".join(str(x) for x in message) + "\n")
