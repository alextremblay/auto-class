from auto_class.intermediate_representation import DataClass, Member, Sequence, HashTable, Type

type_scalars = [
    (Type('str'), 'str'),
    (Type('int'), 'int'),
    (Type('float'), 'float'),
    (Type('bool'), 'bool'),
    (Type('bytes'), 'bytes'),
]

type_sequences = [
    (Sequence('list', [Type('str')]), 'List[str]'),
    (Sequence('list', [Type('str'), Type('int')]), 'List[str,int]'),
    (Sequence('list', [Type('str'), Type('int'), Type('None')]), 'List[str,int,None]'),
    (Sequence('set', [Type('str'), Type('int')]), 'Set[str,int]'),
    (Sequence('tuple', [Type('str'), Type('str'), Type('int')]), 'Tuple[str,str,int]'),
    (
        Sequence('list', [Type('str'), Type('int'), Sequence('set', [Type('str'), Type('int')])]),
        'List[str,int,Set[str,int]]'
    ),
]

# noinspection PyArgumentList
type_hashtables = [
    (HashTable(key=Type('str'), values=[Type('str')]), 'Dict[str,str]'),
    (HashTable(key=Type('str'), values=[Type('str'), Type('int')]), 'Dict[str,Union[str,int]]'),
    (
        HashTable(key=Type('str'), values=[
            Type('str'), Type('int'), Type('None')
        ]),
        'Dict[str,Optional[Union[str,int]]]'
    ),
    (
        HashTable(key=Type('str'), values=[
            Type('str'), Type('int'), Sequence('tuple', [Type('str'), Type('int')])
        ]),
        'Dict[str,Union[str,int,Tuple[str,int]]]'
    ),
]

members = [
    (
        Member('attribute1', [Type('str')]),
        "attribute1: str = field(default_factory=str)"
    ),
    (
        Member('attribute2', [Type('str')], default='hello'),
        "attribute2: str = 'hello'"
    ),
    (
        Member('attribute3', [Type('str'), Type('int')], default='hello'),
        "attribute3: Union[str,int] = 'hello'"
    ),
    (
        Member('attribute4', [Sequence('list', [Type('str')])]),
        "attribute4: List[str] = field(default_factory=list)"
    ),
    (
        Member('attribute5', [Sequence('list', [Type('str')])], optional=True),
        "attribute5: List[str] = field(default_factory=list, metadata=dict(default=list, missing=list, required=False))"
    ),
    (
        Member('attribute6', [Type('str')], default='hello', optional=True),
        "attribute6: str = field(default='hello', metadata=dict(default='hello', missing='hello', required=False))"
    ),
    (
        Member('attribute7', [Type('None')]),
        "attribute7: Any = None"
    ),
    (
        Member('attribute7', [Type('None')], optional=True),
        "attribute7: Any = field(default=None, metadata=dict(default=None, missing=None, required=False))"
    ),
    (
        Member('Attribute 8', [Type('str')]),
        "attribute_8: str = field(default_factory=str, metadata=dict(data_key='Attribute 8'))"
    ),
    (
        Member('Attribute 9', [Type('str')], default='hello'),
        "attribute_9: str = field(default='hello', metadata=dict(data_key='Attribute 9'))"
    ),
    (
        Member('10 Attribute 10', [Type('str')], default='hello', optional=True),
        "attribute_10: str = field(default='hello', metadata=dict(default='hello', missing='hello', required=False, data_key='10 Attribute 10'))"
    ),
    (
        Member('Attribute 11', [Sequence('list', [Type('str')])], optional=True),
        "attribute_11: List[str] = field(default_factory=list, metadata=dict(default=list, missing=list, required=False, data_key='Attribute 11'))"
    ),
    (
        Member('Attribute12', [Sequence('list', [Type('str')]), Type('None')], optional=True),
        "attribute12: Optional[List[str]] = field(default=None, metadata=dict(default=None, missing=None, required=False, data_key='Attribute12'))"
    ),
    (
        Member('attribute13', [type_sequences[1][0]], optional=True),
        "attribute13: List[str,int] = field(default_factory=list, metadata=dict(default=list, missing=list, required=False))"
    ),
    (
        Member('attribute14', [type_sequences[4][0]]),
        "attribute14: Tuple[str,str,int] = field(default_factory=tuple)"
    ),
    (
        Member('attribute15', [type_hashtables[1][0]]),
        "attribute15: Dict[str,Union[str,int]] = field(default_factory=dict)"
    ),
    (
        Member('attribute16', [Type('str')], default='email@address.com', custom_field='Email'),
        "attribute16: str = field(default='email@address.com', metadata=dict(marshmallow_field=Email))"
    ),
]

complete_dataclass_example = DataClass('DataClass', [
    Member('a_field', [Type('str')]),
    Member('a_default_value', [Type('str')], default='a default value'),
    Member('a_number', [Type('int')]),
    Member('a_list', [Sequence('list', types=[
        Type('str'),
        Type('int')
    ])]),
    Member('an_optional_value', [Type('None')]),
    Member('a_union', [
        Type('str'),
        Type('int')
    ]),
    Member('A Key With Spaces', [Type('str')]),
    Member('optional_field_with_type', [Type('str'), Type('None')]),
    Member('implicit_optional', [Type('str'), Type('None')]),
    Member('an_optional_union', [Type('str'), Type('int'), Type('None')]),
    Member('optional_field_with_default', [Type('str')], default='hello'),
    Member('allow_missing', [Type('str')], optional=True),
    Member('optional_and_allow_missing', [Type('str'), Type('None')], optional=True),
    Member('custom_field', [Type('str')], default='email@address.com', custom_field='Email'),
    Member('sub_class', [DataClass('SubClass', [
        Member('subkey', [Type('str')]),
        Member('another_subkey', [Type('str')]),
        Member('sub_sub_class', [DataClass('SubSubClass', [
            Member('so_nested', [Type('bool')], default=True),
            Member('much_wow', [Type('bool')], default=True),
        ])]),
    ])]),
    Member('optional_sub_class', [Type('None'), DataClass('OptionalSubClass', [
        Member('subkey', [Type('str')]),
        Member('another_subkey', [Type('str')]),
    ])]),
    Member('implicit_hashtable', [HashTable(key=Type('int'), values=[Type('int')])]),
    Member('explicit_hashtable', [HashTable(key=Type('str'), values=[
        Type('int'), Type('str'), Type('bool')
    ])]),
    Member('a_class_list', [Sequence('list', [
        DataClass('NamedClass', [
            Member('a_subkey', [Type('int')], default=1),
            Member('one_more', [Type('str')], default='hello')
        ])
    ])])
])


def test_type_scalars():
    input_output = type_scalars
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.definition}\n")
        assert data_in.definition == expected_output


def test_type_sequences():
    input_output = type_sequences
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.definition}\n")
        assert data_in.definition == expected_output


def test_type_hashtables():
    input_output = type_hashtables
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.definition}\n")
        assert data_in.definition == expected_output


def test_members():
    input_output = members
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.definition}\n")
        assert expected_output in data_in.definition


def test_dataclasses():
    input_output = [
        (
            DataClass('MyDataClass', members=[]),
            """
@dataclass
class MyDataClass:
    pass

"""
        ),
        (
            DataClass('MyDataClass', members=[tup[0] for tup in members]),
            """
@dataclass
class MyDataClass:
    attribute1: str = field(default_factory=str)
    attribute2: str = 'hello'
    attribute3: Union[str,int] = 'hello'
    attribute4: List[str] = field(default_factory=list)
    attribute5: List[str] = field(default_factory=list, metadata=dict(default=list, missing=list, required=False))
    attribute6: str = field(default='hello', metadata=dict(default='hello', missing='hello', required=False))
    attribute7: Any = None
    attribute7: Any = field(default=None, metadata=dict(default=None, missing=None, required=False))
    attribute_8: str = field(default_factory=str, metadata=dict(data_key='Attribute 8'))
    attribute_9: str = field(default='hello', metadata=dict(data_key='Attribute 9'))
    attribute_10: str = field(default='hello', metadata=dict(default='hello', missing='hello', required=False, data_key='10 Attribute 10'))
    attribute_11: List[str] = field(default_factory=list, metadata=dict(default=list, missing=list, required=False, data_key='Attribute 11'))
    attribute12: Optional[List[str]] = field(default=None, metadata=dict(default=None, missing=None, required=False, data_key='Attribute12'))
    attribute13: List[str,int] = field(default_factory=list, metadata=dict(default=list, missing=list, required=False))
    attribute14: Tuple[str,str,int] = field(default_factory=tuple)
    attribute15: Dict[str,Union[str,int]] = field(default_factory=dict)
    attribute16: str = field(default='email@address.com', metadata=dict(marshmallow_field=Email))

"""
        ),
        (
            DataClass('MyDataClass', members=[
                Member('sub-class', types=[DataClass('MySubClass', members=[Member('attribute1', [Type('str')])])])
            ]),
            """
@dataclass
class MyDataClass:

    @dataclass
    class MySubClass:
        attribute1: str = field(default_factory=str)


    sub_class: MySubClass = field(default_factory=MySubClass, metadata=dict(data_key='sub-class'))

"""
        ),
        (
            DataClass('MyDataClass', members=[
                Member('sub-class', optional=True, types=[
                    DataClass('MySubClass', members=[Member('attribute1', [Type('str')])])
                ])
            ]),
            """
@dataclass
class MyDataClass:

    @dataclass
    class MySubClass:
        attribute1: str = field(default_factory=str)


    sub_class: MySubClass = field(default_factory=MySubClass, metadata=dict(default=MySubClass, missing=MySubClass, required=False, data_key='sub-class'))

"""
        ),
        (
            DataClass('MyDataClass', members=[
                Member('sub-class', optional=True, types=[
                    DataClass('MySubClass', members=[Member('attribute1', [Type('str')])])
                ]),
                Member('a_class_list', optional=True, types=[
                    Sequence('list', [DataClass('AClassList', members=[Member('attribute1', [Type('str')])])])
                ]),
            ]),
            """
@dataclass
class MyDataClass:

    @dataclass
    class MySubClass:
        attribute1: str = field(default_factory=str)


    sub_class: MySubClass = field(default_factory=MySubClass, metadata=dict(default=MySubClass, missing=MySubClass, required=False, data_key='sub-class'))

    @dataclass
    class AClassList:
        attribute1: str = field(default_factory=str)


    a_class_list: List[AClassList] = field(default_factory=list, metadata=dict(default=list, missing=list, required=False))

"""
        ),
    ]
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.dataclass_definition}\n")
        assert expected_output in data_in.dataclass_definition


def test_dataclass_complete_example():
    # The code in this test should always be kept up to date with the code in the "A Complete Example" section of
    # the README

    data_in = complete_dataclass_example

    expected_output = """
@dataclass
class DataClass:
    a_field: str = field(default_factory=str)
    a_default_value: str = 'a default value'
    a_number: int = field(default_factory=int)
    a_list: List[str,int] = field(default_factory=list)
    an_optional_value: Any = None
    a_union: Union[str,int] = field(default_factory=str)
    a_key_with_spaces: str = field(default_factory=str, metadata=dict(data_key='A Key With Spaces'))
    optional_field_with_type: Optional[str] = None
    implicit_optional: Optional[str] = None
    an_optional_union: Optional[Union[str,int]] = None
    optional_field_with_default: str = 'hello'
    allow_missing: str = field(default_factory=str, metadata=dict(default=str, missing=str, required=False))
    optional_and_allow_missing: Optional[str] = field(default=None, metadata=dict(default=None, missing=None, required=False))
    custom_field: str = field(default='email@address.com', metadata=dict(marshmallow_field=Email))

    @dataclass
    class SubClass:
        subkey: str = field(default_factory=str)
        another_subkey: str = field(default_factory=str)

        @dataclass
        class SubSubClass:
            so_nested: bool = True
            much_wow: bool = True


        sub_sub_class: SubSubClass = field(default_factory=SubSubClass)


    sub_class: SubClass = field(default_factory=SubClass)

    @dataclass
    class OptionalSubClass:
        subkey: str = field(default_factory=str)
        another_subkey: str = field(default_factory=str)


    optional_sub_class: Optional[OptionalSubClass] = None
    implicit_hashtable: Dict[int,int] = field(default_factory=dict)
    explicit_hashtable: Dict[str,Union[int,str,bool]] = field(default_factory=dict)

    @dataclass
    class NamedClass:
        a_subkey: int = 1
        one_more: str = 'hello'


    a_class_list: List[NamedClass] = field(default_factory=list)
"""

    print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.dataclass_definition}\n")
    assert expected_output in data_in.dataclass_definition
