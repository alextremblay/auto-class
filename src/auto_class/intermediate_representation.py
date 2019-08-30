from dataclasses import dataclass, field, InitVar
from typing import List, Set, Dict, Optional, Any
from textwrap import indent
from abc import abstractmethod


@dataclass
class Value:

    optional: bool = False
    # Control the python typing / dataclass optionality mechanism. If true, the type will be
    # wrapped in 'Optional[]' and the implicit default value will be None

    allow_missing: bool = False
    # Control whether marshmallow field should be set to required and whether or not to
    # generate marshmallow field defaults

    mm_field: str = ''  # Custom marshmallow field

    default: Any = None
    # must be string form of a factory function (Ex. 'list' for the list() function,
    # 'DataClass' to call DataClass() initializer)

    @property
    @abstractmethod
    def type_def(self):
        raise NotImplemented


# noinspection PyDataclass
@dataclass(init=False)
class Scalar(Value):
    type: str  # Can be one of [ bool, int, float, complex, str, bytes, None ]

    def __init__(self, type: str, optional: bool = False, allow_missing: bool = False,
                 mm_field: str = '', default: Any = None):
        self.type = type
        super().__init__(optional, allow_missing, mm_field, default)

    @property
    def type_def(self):
        t = self.type
        if t == 'None':
            # Scalar types are derived from values. A value can be None, but a typ cannot be.
            # The best valid type for `None` Scalars is Any. Dataclass fields of 'None' are inherently optional
            t = 'Any'
            self.optional = True
        elif self.optional:
            # `Optional[Any] is not a valid type def, so this bit of logic is mutually exclusive with the None/Any
            # logic above
            t = 'Optional[{}]'.format(t)
        return t


# noinspection PyDataclass
@dataclass(init=False)
class Sequence(Value):
    """Will become a List[*{Type}], Tuple[*{Type}], or Set[*{Type}] definition"""
    type: str  # Can be one of [ list, tuple, set ]

    values: List[Value] = field(default_factory=list)

    def __init__(self, type: str, values: list, optional: bool = False, allow_missing: bool = False,
                 mm_field: str = '', default: Any = None):
        self.type = type
        self.values = values
        super().__init__(optional, allow_missing, mm_field, default)

    @property
    def contained_types(self):
        if self.type == 'list' or self.type == 'set':
            return set(v.type_def for v in self.values)
        else:
            assert self.type == 'tuple'
            return list(v.type_def for v in self.values)

    @property
    def type_def(self):
        t = '[{}]'.format(','.join(iter(self.contained_types)))
        t = self.type.capitalize() + t
        return t


# noinspection PyDataclass
@dataclass(init=False)
class Union(Value):
    """Will become a Union[*{Type}] definition"""
    # Note: a Union is conceptually similar to a Sequence, except that it has no variable type, and its
    # contained values must inherently be a set

    values: List[Value]

    def __init__(self, values: List[Value], optional: bool = False, allow_missing: bool = False,
                 mm_field: str = '', default: Any = None):
        self.values = values
        super().__init__(optional, allow_missing, mm_field, default)

    @property
    def type_def(self):
        return 'Union[{}]'.format(','.join(set(v.type_def for v in self.values)))

    @classmethod
    def convert_val_to_union(cls, val: Value):
        u = cls(values=[val])
        u.default = val.default
        u.allow_missing = val.allow_missing
        u.optional = val.optional
        u.mm_field = val.mm_field
        return u


# noinspection PyDataclass
@dataclass(init=False)
class HashTable(Sequence):
    # TODO: override default marshmallow field `Nested`, replace with marshmallow field `Dict`
    """Will become a Dict[{KeyType},{ValType}] definition"""
    key: Scalar

    def __init__(self, key: Scalar, values: List[Value], optional: bool = False, allow_missing: bool = False,
                 mm_field: str = '', default: Any = None):
        self.key = key
        super().__init__('list', values, optional, allow_missing, mm_field, default)

    @property
    def type_def(self):
        t = 'Dict[{},{}]'.format(self.key.type, self.contained_types)
        if self.optional:
            t = 'Optional[{}]'.format(t)
        return t


@dataclass
class Field:
    """Will become a {attribute}: {type} or {attribute}: {type} = field({props}) definition"""
    attribute: str  # The name of this key in the generated dataclass
    value: Value
    data_key: Optional[str] = None  # The json-encodable key name. Only needed if different from attribute

    @property
    def default(self):
        if self.value.default:
            d = self.value.default
        elif self.value.optional:
            d = 'None'
        elif isinstance(self.value, HashTable):
            d = 'dict'
        elif isinstance(self.value, Sequence):
            d = 'list'
        elif isinstance(self.value, Scalar):
            d = next(iter(self.value.type))
            # Scalars can be single types or unions, but defaults cannot be unions.
            # in the event of an optional union scalar, default will be the factory function
            # of the first type in the scalar.
            # Ex for Optional[Union[str,int]], default factory function will be str
        else:
            assert isinstance(self.value, DataClass)
            # This is the only remaining condition. if value is not a Dataclass at this point,
            # then something has gone terribly wrong
            d = self.value.name  # default factory should be
        return d

    @property
    def metadata(self):
        """Generates the `metadata={*stuff}` part of the field body, if applicable.
        Otherwise returns empty str"""
        items = []
        if self.data_key:
            items.append('data_key="{}"'.format(self.data_key))
        if self.value.mm_field:
            items.append('marshmallow_field={}'.format(self.value.mm_field))
        if self.value.optional:
            items.append('missing={0}, default={0}, required=False'.format(self.default))

        result = ', '.join(items)
        if result:
            return 'metadata=dict({})'.format(result)
        else:
            return ''

    @property
    def body(self):
        """Generates a field({*stuff}) definition, if applicable. Otherwise returns empty str

        This is the stuff on the right side of the '=' in a dataclass field definition.

        Possible outputs are:
            'field(default="default_val")
                    # field is required, there is a default and no metadata

            'field(default="default_val")
                    # field is required, there is a default and no metadata

            'field(metadata=dict(data_key="key"))'
                    # field is required, there is metadata, but no default

            'field(default="default_val", metadata=dict(data_key="key"))
                    # field is required, there is metadata, and a default

            'field(default_factory=list, metadata=dict(missing=list, default=list, required=False))'
                    # field is optional, but there is no default

            'field(default="default_value", metadata=dict(missing="default_value",
                default="default_value", required=False))'
                    # field is optional, and there is a default
        """
        items = []
        if self.value.default:
            items.append('default={}'.format(self.value.default))
        else:
            items.append('default_factory={}'.format(self.default))
        if self.metadata:
            items.append(self.metadata)

        result = ', '.join(items)
        if result:
            return '= field({})'.format(result)
        else:
            return ''

    @property
    def definition(self):
        defn = f"{self.attribute}: {self.value.type_def} {self.body}"
        if isinstance(self.value, DataClass):
            defn = f"\n{self.value.body}\n\n{defn}"

        return defn


# noinspection PyDataclass
@dataclass(init=False)
class DataClass(Value):
    """Will become a Dataclass definition"""
    name: str  # The name of this dataclass
    fields: List[Field]

    def __init__(self, name: str, fields: List[Field], optional: bool = False, allow_missing: bool = False,
                 mm_field: str = '', default: Any = None):
        self.name = name
        self.fields = fields
        super().__init__(optional, allow_missing, mm_field, default)

    @property
    def type_def(self):
        return self.name

    @property
    def body(self):
        b = f"@dataclass\n" \
            f"class {self.name}:\n"
        b += indent('\n'.join([f.definition for f in self.fields]), prefix=' '*4)
        return b
