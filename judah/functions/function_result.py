from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FunctionSignal(Enum):
    STOP_CONVERSATION = 1


@dataclass
class FunctionResult:
    signal: Optional[FunctionSignal] = None
    context: Optional[str] = None
