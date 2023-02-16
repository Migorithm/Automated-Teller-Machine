from __future__ import annotations
from dataclasses import dataclass, field
from uuid import UUID,uuid4
from app.utils import domain_util
from app.domain import commands

@dataclass
class Account(domain_util.Aggregate):
    balance: int # amount of money in the account at any given time
    cards : list[Card] = field(default_factory=list)

    #Exceptions
    class NotEnoughMoney(Exception):
        pass
    
    class InvalidPinNumberGiven(Exception):
        pass
    
    #Possible Events
    class Opened(domain_util.Aggregate.Created):
        id : UUID
        balance :int = 0

    class CardIssued(domain_util.Aggregate.Event):
        pin_number : UUID
        def apply(self,account:Account)->None:
            account.cards.append(Card(pin_number=self.pin_number))

    class TransactionAppended(domain_util.Aggregate.Event):
        amount:int
        def apply(self,account:Account)->None:
            account.balance += self.amount
    
    @property
    def latest_card_pin_number(self):
        return self.cards[-1].pin_number

    @classmethod
    def open(cls,cmd:commands.OpenAccount):
        return super()._create_(
        cls.Opened,
        id=cmd.user_id
        )

    def issue_card(self)-> UUID:
        self._trigger_(
            self.CardIssued,
            pin_number = uuid4(),
        )

    def append_transaction(self,cmd:commands.AppendTransaction)->None:
        """
        Either deposit or withdraw money from the account
        """
        self._check_if_valid_pin_number(cmd.pin_number)
        self._check_has_sufficient_money(cmd.amount)
        self._trigger_(
            self.TransactionAppended,
            amount=cmd.amount
        )
    
    #Invariants
    def _check_has_sufficient_money(self,amount:int)->None:
        if self.balance + amount < 0:
            raise self.NotEnoughMoney(dict(account_id=self.id))
    def _check_if_valid_pin_number(self,pin_number:UUID):
        is_valid= bool(next((c for c in self.cards if c.pin_number == pin_number),None))
        if not is_valid:
            raise self.InvalidPinNumberGiven(dict(pin_number=pin_number))

    
            
@dataclass
class Card:
    """
    Users may have multiple ways to access an account. 
    Therefore, one-to-many relationship should be made between Account - Card
    """
    account_id : UUID = field(init=False)
    account: Account =field(init=False)
    pin_number:UUID