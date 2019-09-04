from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Any
from textwrap import indent

from ordered_set import OrderedSet


@dataclass
class Type:
    name: str

    @property
    def definition(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


@dataclass
class Sequence(Type):
    types: List[Type]

    @property
    def definition(self):
        type_name = self.name.capitalize()  # Ex. `list` become `List`, `set` become `Set`, etc
        contained_types = ','.join([t.definition for t in self.types])
        return f"{type_name}[{contained_types}]"

    def __hash__(self):
        return hash(self.name)


@dataclass
class HashTable(Type):
    name: str = field(default='dict', init=False)
    key: Type
    values: List[Type]

    @property
    def definition(self):
        k = self.key.definition
        v = get_type_definition(self.values)
        return f"Dict[{k},{v}]"

    def __hash__(self):
        return hash(self.name)


@dataclass
class DataClass(Type):
    """Will become a Dataclass definition"""
    members: List['Member']
    methods = None

    @property
    def dataclass_definition(self):
        return '\n' + self.header + indent(self.body, prefix=' '*4) + '\n'*2

    @property
    def body(self):
        if self.members:
            return '\n'.join([m.definition for m in self.members])
        else:
            return 'pass'

    @property
    def header(self):
        return f"@dataclass\n" \
            f"class {self.name}:\n"

    def __hash__(self):
        return hash(self.name)


@dataclass
class Member:
    name: str

    types: List[Type]
    # The strings in this set are string representations of python types (ie `str`, `int`, `bool`, `None`).
    # This can also include names of generated data classes (ie)

    default: Any = None

    optional: bool = False

    custom_field: str = None

    def __post_init__(self):
        try:
            # only immutable defaults are supported
            hash(self.default)
        except TypeError:
            raise Exception(f'only immutable default values are supported. Member {self.name} was called with mutable '
                            f'default: {self.default}')

    @property
    def definition(self):
        lines = []
        lines.extend(self.get_embedded_dataclass_defs(self.types))
        lines.append(f"{self.attribute}: {self.type_definition} = {self.expression}")
        return "\n".join(lines)

    def get_embedded_dataclass_defs(self, types: List[Type]) -> List[str]:
        lines = []
        for type in types:
            if isinstance(type, DataClass):
                lines.append(type.dataclass_definition)
            if isinstance(type, Sequence):
                lines.extend(self.get_embedded_dataclass_defs(type.types))
            if isinstance(type, HashTable):
                lines.extend(self.get_embedded_dataclass_defs(type.values))
        return lines

    @property
    def attribute(self):
        attribute_name = self.name.lower().replace(' ', '_').replace('-', '_')
        while not attribute_name[0].isalpha():
            attribute_name = attribute_name[1:]
        return attribute_name

    @property
    def type_definition(self):
        return get_type_definition(self.types)

    @property
    def expression(self):
        if self.default_value and not self.metadata:
            # If we can get away with it, we always want to try and return a non-field expression
            # field expression is `= field(default='blah')`
            # non-field expression is `= 'blah'`.
            # field expression is only required when there is no default AND when there is metadata to capture
            return self.default_value

        elements = []
        if self.default_value:
            elements.append(f'default={self.default_value}')
        else:
            elements.append(f"default_factory={self.default_factory}")
        if self.metadata:
            elements.append(f"metadata={self.metadata}")
        elements = ', '.join(elements)
        return f"field({elements})"

    @property
    def metadata(self):
        items = []
        if self.optional:
            if self.default_value:
                d = self.default_value
            else:
                d = self.default_factory
            items.append(f"default={d}")
            items.append(f"missing={d}")
            items.append(f"required=False")
        if self.attribute != self.name:
            items.append(f"data_key='{self.name}'")
        if self.custom_field:
            items.append(f"marshmallow_field={self.custom_field}")
        if items:
            items = ', '.join(items)
            return f"dict({items})"
        else:
            return None

    @property
    def default_value(self):
        if self.default:
            d = self.default
            if isinstance(d, str):
                d = f"'{d}'"
            return d
        elif Type('None') in self.types:
            return 'None'
        else:
            return None

    @property
    def default_factory(self):
        # Get the first type in the set, excluding NoneType
        t = OrderedSet(self.types)
        t = next(iter(t - {Type('None')}))
        return t.name

    def __hash__(self):
        return hash((self.name, self.attribute))


def get_type_definition(types: List[Type]) -> str:
    t = OrderedSet(types)
    if Type('None') in t:
        if len(t) is 1:
            return 'Any'
        t = t - {Type('None')}
        optional = True
    else:
        optional = False
    d = ','.join([v.definition for v in t])
    if len(t) > 1:
        d = f'Union[{d}]'
    if optional:
        d = f'Optional[{d}]'
    return d
