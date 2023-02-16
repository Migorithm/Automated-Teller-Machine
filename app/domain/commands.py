from dataclasses import dataclass
from uuid import UUID

@dataclass(slots=True,frozen=True)
class OpenAccount: 
    user_id : UUID



@dataclass(slots=True,frozen=True)
class IssueCard: 
    user_id : UUID


@dataclass(slots=True,frozen=True)
class AppendTransaction:
    amount : int
    pin_number : UUID
    user_id : UUID