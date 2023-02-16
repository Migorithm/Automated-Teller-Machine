from typing import Protocol
from uuid import UUID
from app.domain import models,outbox


class AggregateModel(Protocol):
    id : UUID

class Repository:
    """
    Repository to abstract persistent layer.
    The implementation below is sheerly for test purposes.
    """
    outbox_db = {}
    account_db = {}
    def __init__(self,model):
        self.model = model

    def get(self,ref):
        if self.model == models.Account:
            return self.account_db.get(ref)
        if self.model == outbox.Outbox:
            return self.outbox_db.get(ref)

    def put(self,model:AggregateModel):
        if self.model == models.Account:
            self.account_db[model.id] = model
        if self.model == outbox.Outbox:
            self.outbox_db[model.id] = model
        
    

