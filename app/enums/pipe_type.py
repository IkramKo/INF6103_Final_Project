from enum import Enum

class PipeType(Enum):
    TREATED_OUTPUT = 'treated_output'
    UNTREATED_INPUT = 'untreated_input'
    UNTREATED_OUTPUT = 'untreated_output'
    RETREATEMENT = 'retreatment'