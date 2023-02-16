from uuid import uuid4
from app.service_layer.unit_of_work import UnitOfWork
from app.service_layer import handlers
from app.domain import commands,models, outbox
import pytest

    


def test_open_account():
    #GIVEN
    uow = UnitOfWork()
    user_id = uuid4()
    cmd = commands.OpenAccount(user_id = user_id)

    #WHEN
    handlers.open_account(uow=uow,cmd=cmd)
    account:models.Account = uow.accounts.get(user_id)
    
    assert account.id == user_id
    assert not account.cards 
    assert account.balance == 0
    
    
def test_issue_card(account_factory:models.Account):
    #GIVEN
    account = account_factory
    user_id = account.id
    uow = UnitOfWork()

    #WHEN
    cmd = commands.IssueCard(user_id=user_id)
    pin_number = handlers.issue_card(uow=uow,cmd=cmd)

    #Then
    account:models.Account = uow.accounts.get(user_id)
    assert account.id == user_id
    assert account.cards 
    assert account.balance == 0
    latest_card = next(c for c in account.cards)
    assert latest_card.pin_number == pin_number
    


def test_append_transaction_deposit(account_factory:models.Account):
    #GIVEN
    account = account_factory
    user_id = account.id
    uow = UnitOfWork()
    cmd = commands.IssueCard(user_id=user_id)
    pin_number = handlers.issue_card(uow=uow,cmd=cmd)

    #WHEN
    cmd = commands.AppendTransaction(pin_number=pin_number,user_id=user_id,amount=100)
    handlers.append_transaction(uow=uow,cmd=cmd)
    account:models.Account = uow.accounts.get(user_id)

    #THEN
    assert account.balance == 100
    box :outbox.Outbox = uow.outboxes.get(user_id)
    assert box
    assert box.payload
    assert box.payload["id"] == user_id
    assert box.payload["amount"] == 100



def test_append_transaction_withdraw(account_factory:models.Account):
    #GIVEN - create account, issue card, deposit 100 to account with the given card
    account = account_factory
    user_id = account.id
    uow = UnitOfWork()
    cmd = commands.IssueCard(user_id=user_id)
    pin_number = handlers.issue_card(uow=uow,cmd=cmd)
    cmd = commands.AppendTransaction(pin_number=pin_number,user_id=user_id,amount=100)
    handlers.append_transaction(uow=uow,cmd=cmd)

    #WHEN 
    cmd = commands.AppendTransaction(pin_number=pin_number,user_id=user_id,amount=-50)    
    handlers.append_transaction(uow=uow,cmd=cmd)


    #THEN
    assert account.balance == 50
    box :outbox.Outbox = uow.outboxes.get(user_id)
    assert box
    assert box.payload
    assert box.payload["id"] == user_id
    assert box.payload["amount"] == -50

    #When in second trial where the amount of money asked to be withdrawn is higher than overdraft -> reject
    with pytest.raises(models.Account.NotEnoughMoney):
        cmd = commands.AppendTransaction(pin_number=pin_number,user_id=user_id,amount=-60)    
        handlers.append_transaction(uow=uow,cmd=cmd)



