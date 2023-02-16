from __future__ import annotations
from collections import deque
from typing import Type
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field,asdict
import importlib

#Helper functions
def get_topic(cls:type) -> str:
    """
    Returns a string that locates the given class
    """
    return f"{cls.__module__}#{cls.__qualname__}"

def resolve_topic(topic:str):
    """
    Returns a class located by the given string
    """
    module_name, _,class_name =topic.partition("#")
    module = importlib.import_module(module_name)
    return resolve_attr(module,class_name)

def resolve_attr(obj,path:str) -> type:
    #Base Case
    if not path:
        return obj

    #Recursive Case
    else:
        head,_,tail = path.partition(".")
        obj = getattr(obj,head)
        return resolve_attr(obj,tail)


#Event Metaclass
class EventMetaclass(type):
    def __new__(cls,*args,**kwargs):
        new_cls = super().__new__(cls,*args,**kwargs)
        return dataclass(frozen=True,kw_only=True)(new_cls)

    
class DomainEvent(metaclass=EventMetaclass):
    id: UUID
    version: int
    timestamp : datetime

    def dict(self):
        return asdict(self)


@dataclass
class Aggregate:
    """
    Base Class For Aggregate.
    """

    #Exceptions
    class NotAggregateError(Exception):
        pass
    class VersionError(Exception):
        pass

    #Events For Base Aggregate 
    class Event(DomainEvent):
        def mutate(self,obj:Aggregate|None) -> "Aggregate":
            """
            Changes the state of the aggregate
            according to domain event attriutes. 
            """
            #Check sequence
            if not isinstance(obj,Aggregate):
                raise Aggregate.NotAggregateError
            next_version = obj.version +1 
            if self.version != next_version:
                raise obj.VersionError(
                    self.version, next_version
                )
            #Update aggregate version 
            obj.version = next_version

            obj.timestamp = self.timestamp
            #Project obj 
            self.apply(obj)
            return obj 
        def apply(self,obj) -> None:
            pass

    class Created(Event):
        """
        Domain event for creation of aggregate
        """

        topic : str
        def mutate(self, obj: "Aggregate"|None) -> "Aggregate":
            #Copy the event attributes
            kwargs = self.__dict__.copy()
            id = kwargs.pop("id")
            version = kwargs.pop("version")

            #Get the root class from topicm, using helper function
            aggregate_class = resolve_topic(kwargs.pop("topic"))

            return aggregate_class(id=id,version=version,**kwargs)


    @classmethod
    def _create_(
        cls,
        event_class: Type["Aggregate.Event"], 
        **kwargs,
    ):
        id = kwargs["id"] if "id" in kwargs else uuid4()
        if "id" in kwargs:
            del kwargs["id"]
        
        event = event_class(
            id = id, # Should it be managed on application?
            version = 1,
            topic = get_topic(cls),
            timestamp=datetime.now(),
            **kwargs
        )

        #Call Aggregate.Created.mutate
        aggregate = event.mutate(None)
        aggregate.pending_events.append(event)
        return aggregate

    def _trigger_(
        self,
        event_class: Type["Aggregate.Event"],
        **kwargs,
    )->None:
        """
        Triggers domain event of given type,
        extending the sequence of domain events for this aggregate object
        """
        next_version = self.version +1
        try:
            event = event_class(
                id = self.id,
                version = next_version,
                timestamp= datetime.now(),
                **kwargs,
            )
        except AttributeError:
            raise
        #Mutate aggregate with domain event
        event.mutate(self)

        #Append the domain event to pending events
        self.pending_events.append(event)

    def _collect_(self) -> list[Event]:
        """
        Collect pending events
        """
        collected = []
        while self.pending_events:
            collected.append(self.pending_events.popleft())
        return collected

    id:UUID
    version:int
    timestamp:datetime
    pending_events: deque[Event] = field(init=False)
    def __post_init__(self):
        self.pending_events = deque()
