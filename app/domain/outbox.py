from dataclasses import dataclass,field
from datetime import datetime
from uuid import UUID
from json import dumps

@dataclass
class Outbox:
    id : UUID|str 
    aggregate_type : str
    payload :dict
    create_dt : datetime = field(init=False)
    is_processed : bool = False
    
    def __post_init__(self):
        self.create_dt = datetime.now()
        



    

    