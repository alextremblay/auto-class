from auto_class import intermediate_representation as ir

from typing import List, Set
from textwrap import indent, dedent

from ordered_set import OrderedSet


class ImportRegistry:
    """This class acts as a global registry of all external names which need to be imported from external modules.
    This includes all type names which need to be imported from the `typing` module in the
    generated dataclass definition module (ie List, Dict, Any, etc)"""
    types: Set[str] = {'ClassVar', 'Type'}
    dc_field = False

    @classmethod
    def register_type(cls, typ: str):
        cls.types.add(typ)

    @classmethod
    def get_types_import_string(cls):
        """Returns a string like `from typing import List, Set, Union`"""
        type_str = ', '.join(cls.types)
        return f"from typing import {type_str}"

    @classmethod
    def get_import_stmts(cls):
        statements = f"""
            {cls.get_types_import_string()}
            {'from dataclasses import field' if cls.dc_field else ''}
            from marshmallow import Schema
            from marshmallow_dataclass import dataclass
            
            """
        statements = dedent(statements)
        return statements


class Type(ir.Type):

    def __init__(self, name: str = ''):
        self.name = name

    @classmethod
    def from_ir(cls, base: ir.Type) -> 'Type':
        obj = cls()
        obj.__dict__.update(base.__dict__)
        return obj

    @property
    def type_definition(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class Sequence(ir.Sequence, Type):

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            raise Exception('This subclass should not be instantiated directly. Use the `from_ir` class method instead')

    @classmethod
    def from_ir(cls, base: ir.Sequence) -> 'Sequence':
        obj = cls()
        obj.__dict__.update(base.__dict__)
        obj.types = list(map(from_ir, obj.types))
        return obj

    @property
    def type_definition(self):
        self.types: List[Type]
        type_name = self.name.capitalize()  # Ex. `list` become `List`, `set` become `Set`, etc
        contained_types = ','.join([t.type_definition for t in self.types])
        ImportRegistry.register_type(type_name)
        return f"{type_name}[{contained_types}]"

    def __hash__(self):
        return hash(self.name)


class HashTable(ir.HashTable, Type):

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            raise Exception('This subclass should not be instantiated directly. Use the `from_ir` class method instead')

    @classmethod
    def from_ir(cls, base: ir.HashTable) -> 'HashTable':
        obj = cls()
        obj.__dict__.update(base.__dict__)
        obj.key = from_ir(base.key)
        obj.values = list(map(from_ir, obj.values))
        return obj

    @property
    def type_definition(self):
        self.key: Type
        self.values: List[Type]
        k = self.key.type_definition
        v = get_type_definition(self.values)
        ImportRegistry.register_type('Dict')
        return f"Dict[{k},{v}]"

    def __hash__(self):
        return hash(self.name)


class DataClass(ir.DataClass, Type):
    """Will become a Dataclass definition"""

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            raise Exception('This subclass should not be instantiated directly. Use the `from_ir` class method instead')

    @classmethod
    def from_ir(cls, base: ir.DataClass) -> 'DataClass':
        obj = cls()
        obj.__dict__.update(base.__dict__)
        obj.members = list(map(from_ir, obj.members))
        return obj

    @property
    def definition(self):
        dfn = f"\n{self.header}\n{self.body}\n"
        return dfn

    @property
    def body(self):
        bod = ''
        if self.members:
            self.members: List['Member']
            bod = '\n'.join([m.definition for m in self.members]) + '\n'
        bod += 'Schema: ClassVar[Type[Schema]] = Schema'
        return indent(bod, prefix=' ' * 4)

    @property
    def header(self):
        return f"@dataclass\nclass {self.name}:"

    def __hash__(self):
        return hash(self.name)


class Member(ir.Member):

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            raise Exception('This subclass should not be instantiated directly. Use the `from_ir` class method instead')

    @classmethod
    def from_ir(cls, base: ir.Member) -> 'Member':
        obj = cls()
        obj.__dict__.update(base.__dict__)
        obj._validate_default()
        obj.types = list(map(from_ir, obj.types))
        return obj

    def _validate_default(self):
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
        lines.append(f"{self.attribute}: {get_type_definition(self.types)} = {self.expression}")
        return "\n".join(lines)

    def get_embedded_dataclass_defs(self, types: List[Type]) -> List[str]:
        lines = []
        for type in types:
            if isinstance(type, DataClass):
                lines.append(type.definition)
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
        ImportRegistry.dc_field = True
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
            ImportRegistry.register_type('Any')
            return 'Any'
        t = t - {Type('None')}
        optional = True
    else:
        optional = False
    d = ','.join([v.type_definition for v in t])
    if len(t) > 1:
        ImportRegistry.register_type('Union')
        d = f'Union[{d}]'
    if optional:
        ImportRegistry.register_type('Optional')
        d = f'Optional[{d}]'
    return d


def from_ir(base):
    """Convert instances of ir base classes to instances of py_dataclass subclasses
    This is very hacky, and relies on all base classes in ir having equivalents in this module with the same name.
    """
    class_name = base.__class__.__name__
    local_equivalent = globals()[class_name]

    new = local_equivalent.from_ir(base)

    return new


def generate_dataclass_definitions(rs: ir.ResultSet) -> str:
    dataclasses = [from_ir(dc) for dc in rs.dataclasses]

    # We need to include import statements at the top of our result stack, but we need to generate dataclass definitions
    # in order to populate the import statements.
    # To get around this, we'll build our result stack in reverse
    result = [dc.definition for dc in dataclasses]
    if rs.preamble:
        result.insert(0, rs.preamble)
    result.insert(0, ImportRegistry.get_import_stmts())

    return '\n'.join(result)
