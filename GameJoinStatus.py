from enum import Enum


class GameJoinStatus(Enum):
    OPEN = 'OPEN'
    RANKS_ONLY = 'RANKS_ONLY'
    CLOSED = 'CLOSED'
