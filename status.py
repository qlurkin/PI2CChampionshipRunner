from enum import Enum


class ClientStatus(Enum):
    PENDING = 1
    READY = 2
    LOST = 3


class MatchStatus(Enum):
    PENDING = 1
    RUNNING = 2
    DONE = 3
