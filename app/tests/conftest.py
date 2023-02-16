from uuid import uuid4
import pytest
from app.domain import commands, models
from app.service_layer import handlers
from app.service_layer.unit_of_work import UnitOfWork


@pytest.fixture
def account_factory():
    uow = UnitOfWork()
    user_id = uuid4()
    cmd = commands.OpenAccount(user_id = user_id)
    handlers.open_account(uow=uow,cmd=cmd)
    account:models.Account = uow.accounts.get(user_id)
    return account