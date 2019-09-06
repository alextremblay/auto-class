from dataclasses import dataclass, field
from typing import List, Any, Optional


@dataclass()
class Type:
    """
    Abstract base representation of a data type.
    All intermediate representations of data types will either be instances of Type, or instances of subclasses of Type.
    All scalar data types are instances of Type (ex. Type('str') represents a `str`, Type('float') represents a `float`
    All complex data types are instances of subclasses of Type (ex Sequence('list', types=[Type('str')]) represents a
    list which holds strings... a List[str])
    """
    name: str

    def __hash__(self):
        return hash(self.name)


@dataclass
class Sequence(Type):
    types: List[Type]


@dataclass(init=False)
class HashTable(Type):
    name: str = field(default='dict', init=False)
    key: Type
    values: List[Type]

    def __init__(self, key: Type, values: List[Type]):
        self.name = 'dict'
        self.key = key
        self.values = values


@dataclass
class DataClass(Type):
    """Will become a Dataclass definition"""
    members: List['Member']
    methods = None


@dataclass
class Member:
    name: str

    types: List[Type]
    # The strings in this set are string representations of python types (ie `str`, `int`, `bool`, `None`).
    # This can also include names of generated data classes (ie)

    default: Any = None
    # Default value to give to new instances of the dataclass

    optional: bool = False
    # whether to treat serializer a null value for this member or a missing instance of this member as acceptable

    custom_field: Optional[str] = None
    # custom marshmallow serializer field to use for handling this member


@dataclass
class ResultSet:
    """
    A ResultSet is an object which holds all the data and metadata necessary to generate a complete output artifact
    for a given backend (all the info necessary to create a python module using the py_dataclass backend, for example
    """
    dataclasses: List[DataClass]

    preamble: str = ''
    # preamble is the stuff that goes in between the import statements
