from auto_class.backends import py_dataclass as pd
from auto_class.intermediate_representation import ResultSet
from textwrap import dedent

import pytest


@pytest.fixture(scope='module')
def py_dataclass_test_data(ir_test_data):
    """Tests whether all ir (intermediate representation) base classes can successfully be converted in-place into
    instances of their respective subclasses from the pd module
    All other tests in this suite implicitly require these global objects to be instances of pd subclasses, so this
    test must always run before any other test in this suite
    """
    class ConvertedData:
        type_scalars = [pd.from_ir(o) for o in ir_test_data.type_scalars]
        type_sequences = [pd.from_ir(o) for o in ir_test_data.type_sequences]
        type_hashtables = [pd.from_ir(o) for o in ir_test_data.type_hashtables]
        members = [pd.from_ir(o) for o in ir_test_data.members]
        dataclasses = [pd.from_ir(o) for o in ir_test_data.dataclasses]
        complete_dataclass_example = pd.from_ir(ir_test_data.complete_dataclass_example)

    class ExpectedResults:
        type_scalars = ['str', 'int', 'float', 'bool', 'bytes']

        type_sequences = [
            'List[str]',
            'List[str,int]',
            'List[str,int,None]',
            'Set[str,int]',
            'Tuple[str,str,int]',
            'List[str,int,Set[str,int]]'
        ]

        type_hashtables = [
            'Dict[str,str]',
            'Dict[str,Union[str,int]]',
            'Dict[str,Optional[Union[str,int]]]',
            'Dict[str,Union[str,int,Tuple[str,int]]]'
        ]

        members = [
            "attribute1: str = field(default_factory=str)",
            "attribute2: str = 'hello'",
            "attribute3: Union[str,int] = 'hello'",
            "attribute4: List[str] = field(default_factory=list)",
            "attribute5: List[str] = field(default_factory=list, metadata=dict(default=list, missing=list, "
            "required=False))",

            "attribute6: str = field(default='hello', metadata=dict(default='hello', missing='hello', required=False))",
            "attribute7: Any = None",
            "attribute7: Any = field(default=None, metadata=dict(default=None, missing=None, required=False))",
            "attribute_8: str = field(default_factory=str, metadata=dict(data_key='Attribute 8'))",
            "attribute_9: str = field(default='hello', metadata=dict(data_key='Attribute 9'))",
            "attribute_10: str = field(default='hello', metadata=dict(default='hello', missing='hello', "
            "required=False, data_key='10 Attribute 10'))",

            "attribute_11: List[str] = field(default_factory=list, metadata=dict(default=list, missing=list, "
            "required=False, data_key='Attribute 11'))",

            "attribute12: Optional[List[str]] = field(default=None, metadata=dict(default=None, missing=None, "
            "required=False, data_key='Attribute12'))",

            "attribute13: List[str,int] = field(default_factory=list, metadata=dict(default=list, missing=list, "
            "required=False))",

            "attribute14: Tuple[str,str,int] = field(default_factory=tuple)",
            "attribute15: Dict[str,Union[str,int]] = field(default_factory=dict)",
            "attribute16: str = field(default='email@address.com', metadata=dict(marshmallow_field=Email))"
        ]

        dataclasses = [
            """
            @dataclass
            class MyDataClass:
                Schema: ClassVar[Type[Schema]] = Schema
            
            """,

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
                Schema: ClassVar[Type[Schema]] = Schema
            
            """,

            """
            @dataclass
            class MyDataClass:
            
                @dataclass
                class MySubClass:
                    attribute1: str = field(default_factory=str)
                    Schema: ClassVar[Type[Schema]] = Schema
            
                sub_class: MySubClass = field(default_factory=MySubClass, metadata=dict(data_key='sub-class'))
                Schema: ClassVar[Type[Schema]] = Schema
            
            """,

            """
            @dataclass
            class MyDataClass:

                @dataclass
                class MySubClass:
                    attribute1: str = field(default_factory=str)
                    Schema: ClassVar[Type[Schema]] = Schema

                sub_class: MySubClass = field(default_factory=MySubClass, metadata=dict(default=MySubClass, missing=MySubClass, required=False, data_key='sub-class'))
                Schema: ClassVar[Type[Schema]] = Schema

            """,

            """
            @dataclass
            class MyDataClass:

                @dataclass
                class MySubClass:
                    attribute1: str = field(default_factory=str)
                    Schema: ClassVar[Type[Schema]] = Schema

                sub_class: MySubClass = field(default_factory=MySubClass, metadata=dict(default=MySubClass, missing=MySubClass, required=False, data_key='sub-class'))

                @dataclass
                class AClassList:
                    attribute1: str = field(default_factory=str)
                    Schema: ClassVar[Type[Schema]] = Schema

                a_class_list: List[AClassList] = field(default_factory=list, metadata=dict(default=list, missing=list, required=False))
                Schema: ClassVar[Type[Schema]] = Schema

            """,

        ]
        dataclasses = [dedent(t) for t in dataclasses]

        complete_dataclass_example = """
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
                        Schema: ClassVar[Type[Schema]] = Schema
            
                    sub_sub_class: SubSubClass = field(default_factory=SubSubClass)
                    Schema: ClassVar[Type[Schema]] = Schema
            
                sub_class: SubClass = field(default_factory=SubClass)
            
                @dataclass
                class OptionalSubClass:
                    subkey: str = field(default_factory=str)
                    another_subkey: str = field(default_factory=str)
                    Schema: ClassVar[Type[Schema]] = Schema
            
                optional_sub_class: Optional[OptionalSubClass] = None
                implicit_hashtable: Dict[int,int] = field(default_factory=dict)
                explicit_hashtable: Dict[str,Union[int,str,bool]] = field(default_factory=dict)
            
                @dataclass
                class NamedClass:
                    a_subkey: int = 1
                    one_more: str = 'hello'
                    Schema: ClassVar[Type[Schema]] = Schema
            
                a_class_list: List[NamedClass] = field(default_factory=list)
                Schema: ClassVar[Type[Schema]] = Schema
            
            """
        complete_dataclass_example = dedent(complete_dataclass_example)

    class PyDataClassTestData:
        type_scalars = zip(ConvertedData.type_scalars, ExpectedResults.type_scalars)
        type_sequences = zip(ConvertedData.type_sequences, ExpectedResults.type_sequences)
        type_hashtables = zip(ConvertedData.type_hashtables, ExpectedResults.type_hashtables)
        members = zip(ConvertedData.members, ExpectedResults.members)
        dataclasses = zip(ConvertedData.dataclasses, ExpectedResults.dataclasses)
        complete_dataclass_example = (ConvertedData.complete_dataclass_example,
                                      ExpectedResults.complete_dataclass_example)
    return PyDataClassTestData


def test_type_scalars(py_dataclass_test_data):
    input_output = py_dataclass_test_data.type_scalars
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.type_definition}\n")
        assert data_in.type_definition == expected_output


def test_type_sequences(py_dataclass_test_data):
    input_output = py_dataclass_test_data.type_sequences
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.type_definition}\n")
        assert data_in.type_definition == expected_output


def test_type_hashtables(py_dataclass_test_data):
    input_output = py_dataclass_test_data.type_hashtables
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.type_definition}\n")
        assert data_in.type_definition == expected_output


def test_members(py_dataclass_test_data):
    input_output = py_dataclass_test_data.members
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.definition}\n")
        assert data_in.definition in expected_output


def test_dataclasses(py_dataclass_test_data):
    input_output = py_dataclass_test_data.dataclasses
    print()  # pytest test suite status doesn't end with a new line, so we add one here
    for data_in, expected_output in input_output:
        print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.definition}\n")
        lines = zip(expected_output.splitlines(), data_in.definition.splitlines())
        for expected_line, generated_line in lines:
            assert generated_line == expected_line


def test_dataclass_complete_example(py_dataclass_test_data):
    # The code in this test should always be kept up to date with the code in the "A Complete Example" section of
    # the README

    data_in, expected_output = py_dataclass_test_data.complete_dataclass_example

    print(f"Data in: \n\t{data_in}\nResult:\n\t{data_in.definition}\n")
    lines = zip(expected_output.splitlines(), data_in.definition.splitlines())
    for expected_line, generated_line in lines:
        assert generated_line == expected_line


def test_generate_module_code(py_dataclass_test_data):
    dataclass, expected_dataclass_definition = py_dataclass_test_data.complete_dataclass_example

    preamble = "from marshmallow.fields import Email\n"

    resultset = ResultSet([dataclass], preamble)
    result = pd.generate_dataclass_definitions(resultset)

    print(f"Data in: \n\t{dataclass}\nResult:\n\t{result}\n")

    expected_output = """
from typing import Type, Union, List, Any, Tuple, Optional, Set, Dict, ClassVar
from dataclasses import field
from marshmallow import Schema
from marshmallow_dataclass import dataclass


from marshmallow.fields import Email

""" + expected_dataclass_definition

    lines = zip(expected_output.splitlines(), result.splitlines())
    for expected_line, generated_line in lines:
        if expected_line.startswith('from typing import'):
            expected_types = expected_line[19:].split(', ')
            for type in expected_types:
                assert type in generated_line
        else:
            assert generated_line == expected_line
