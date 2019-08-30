from auto_class.intermediate_representation import DataClass, Field, Scalar, Union, Sequence, HashTable

a_complete_example_ir = DataClass('DataClass', [
    Field('a_field', value=Scalar(type='str')),
    Field('a_default_value', value=Scalar('str', default='a default value')),
    Field('a_number', Scalar('int')),
    Field('a_list', Sequence('list', values=[
        Scalar('str', default='string'),
        Scalar('int', default=2)
    ])),
    Field('an_optional_value', Scalar('None')),
    Field('a_union', Union([
        Scalar('str'),
        Scalar('int')
    ])),
    Field('a_key_with_spaces', data_key='A Key With Spaces', value=Scalar('str')),
    Field('optional_field_with_type', Scalar('str', optional=True)),
    Field('implicit_optional', Scalar('str', optional=True)),
    Field('an_optional_union', Union(optional=True, values=[Scalar('str'), Scalar('int')])),
    Field('optional_field_with_default', Scalar('str', optional=True, default='hello')),
    Field('allow_missing', Scalar('str', allow_missing=True)),
    Field('optional_and_allow_missing', Scalar('str', optional=True, allow_missing=True)),
    Field('custom_field', Scalar('str', default='email@address.com', mm_field='Email')),
    Field('sub_class', DataClass('SubClass', [
        Field('subkey', Scalar('str')),
        Field('another_subkey', Scalar('str')),
        Field('sub_sub_class', DataClass('SubSubClass', [
            Field('so_nested', Scalar('bool', default=True)),
            Field('so_nested', Scalar('bool', default=True)),
        ])),
    ])),
    Field('optional_sub_class', DataClass('OptionalSubClass', optional=True, fields=[
        Field('subkey', Scalar('str')),
        Field('another_subkey', Scalar('str')),
    ])),
    Field('implicit_hashtable', HashTable(key=Scalar('int'), values=[Scalar('int')])),
    Field('explicit_hashtable', HashTable(key=Scalar('str'), values=[
        Scalar('int'), Scalar('str'), Scalar('bool')
    ])),
    Field('a_class_list', Sequence('list', values=[
        DataClass('NamedClass', [
            Field('a_subkey', Scalar('int', default=1)),
            Field('one_more', Scalar('str', default='hello'))
        ])
    ]))
])


def test_from_ir_to_dataclass_complete():
    # The code in this test should always be kept up to date with the code in the "A Complete Example" section of
    # the README



    expected_result = """
@dataclass
class TopLevelClass:
    string: str
    number: int
    optional: Optional[str] = field(default_factory=None, metadata=dict(missing=None, default=None, required=False))
    other_optional: Optional[str] = field(default=hello, metadata=dict(missing=hello, default=hello, required=False))
    with_spaces: str = field(metadata=dict(data_key="With Spaces"))
    list: List[str]
    union: Union[int,str]
    union_list: List[str,int]
    custom_field: str
    hash_table: Dict[int,Union[str,int]]
    explicit_hash_table: Dict[str,int]

    @dataclass
    class DataClass:
        string: str
        number: int
        optional: Optional[str] = field(default_factory=None, metadata=dict(missing=None, default=None, required=False))
        other_optional: Optional[str] = field(default=hello, metadata=dict(missing=hello, default=hello, required=False))
        with_spaces: str = field(metadata=dict(data_key="With Spaces"))
        list: List[int]

    data_class: DataClass
    data_class_list: List[DataClassList]
    list_of_lists: List[List[int]]
    """

    from pprint import pprint
    #pprint(intermediate.type)