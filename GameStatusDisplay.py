from enum import Enum


class GameStatusDisplay(Enum):
    ALWAYS_OPEN = 'ALWAYS_OPEN'
    STARTING = 'STARTING'
    VOTING = 'VOTING'
    WAITING = 'WAITING'
    IN_PROGRESS = 'IN_PROGRESS'
    CLOSING = 'CLOSING'
