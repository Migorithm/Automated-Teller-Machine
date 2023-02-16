from app.domain import commands
from app.domain import models,outbox

from app.service_layer import exceptions,unit_of_work



def open_account(uow:unit_of_work.UnitOfWork, cmd:commands.OpenAccount):
    with uow:
        account:models.Account|None=uow.accounts.get(cmd.user_id)
        if account:
            raise exceptions.AccountAlreadyExists
        account = models.Account.open(cmd)
        uow.accounts.put(account)
        uow.commit()

def issue_card(uow:unit_of_work.UnitOfWork,cmd:commands.IssueCard):
    with uow:
        account:models.Account= uow.accounts.get(cmd.user_id)
        if not account:
            raise exceptions.AccountNotFound
        account.issue_card()
        uow.accounts.put(account)
        uow.commit()
        return account.latest_card_pin_number
        

def append_transaction(uow:unit_of_work.UnitOfWork, cmd:commands.AppendTransaction):
    with uow:
        account:models.Account = uow.accounts.get(cmd.user_id)
        if not account:
            raise exceptions.AccountNotFound(dict(user_id=cmd.user_id))
        try:
            account.append_transaction(cmd)
        except models.Account.InvalidPinNumberGiven:
            raise
        except models.Account.NotEnoughMoney:
            raise
        
        #If Successful, record that transaction in outbox model
        ob = outbox.Outbox(
            id=account.id,
            aggregate_type="account",
            payload=account.pending_events[-1].dict())
        
        uow.accounts.put(account)
        uow.outboxes.put(ob)
        uow.commit()

    
