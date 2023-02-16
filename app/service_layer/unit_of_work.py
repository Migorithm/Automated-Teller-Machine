from app.adapter.repository import Repository
from app.domain import models,outbox

class UnitOfWork:
    def __init__(self):
        ...

    
    def __enter__(self):
        self.accounts = Repository(models.Account)
        self.outboxes = Repository(outbox.Outbox)
    
    def __exit__(self,*args):
        self.rollback()

    def commit(self):
        """
        Commit the changes to repositories
        """
        pass

    def rollback(self):
        """
        Rollback the changes from repositories
        """
        