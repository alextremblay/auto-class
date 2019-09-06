#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for auto_class.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

import pytest
from auto_class.intermediate_representation import DataClass, Member, Sequence, HashTable, Type


class irTestData:
    type_scalars = [
        Type('str'),
        Type('int'),
        Type('float'),
        Type('bool'),
        Type('bytes'),
    ]

    type_sequences =  [
        Sequence(name='list', types=[Type(name='str')]),
        Sequence(name='list', types=[Type(name='str'), Type(name='int')]),
        Sequence(name='list', types=[Type(name='str'), Type(name='int'), Type(name='None')]),
        Sequence(name='set', types=[Type(name='str'), Type(name='int')]),
        Sequence(name='tuple', types=[Type(name='str'), Type(name='str'), Type(name='int')]),
        Sequence(name='list', types=[Type(name='str'), Type(name='int'), Sequence(name='set', types=[
            Type(name='str'), Type(name='int')
        ])])
    ]

    type_hashtables = [
        HashTable(key=Type(name='str'), values=[Type(name='str')]),
        HashTable(key=Type(name='str'), values=[Type(name='str'), Type(name='int')]),
        HashTable(key=Type(name='str'), values=[Type(name='str'), Type(name='int'), Type(name='None')]),
        HashTable(key=Type(name='str'), values=[
            Type(name='str'), Type(name='int'), Sequence(name='tuple', types=[Type(name='str'), Type(name='int')])
        ])]

    members = [
        Member(name='attribute1', types=[Type(name='str')]),
        Member(name='attribute2', types=[Type(name='str')], default='hello'),
        Member(name='attribute3', types=[Type(name='str'), Type(name='int')], default='hello'),
        Member(name='attribute4', types=[Sequence(name='list', types=[Type(name='str')])]),
        Member(name='attribute5', types=[Sequence(name='list', types=[Type(name='str')])], optional=True),
        Member(name='attribute6', types=[Type(name='str')], default='hello', optional=True),
        Member(name='attribute7', types=[Type(name='None')]),
        Member(name='attribute7', types=[Type(name='None')], optional=True),
        Member(name='Attribute 8', types=[Type(name='str')]),
        Member(name='Attribute 9', types=[Type(name='str')], default='hello'),
        Member(name='10 Attribute 10', types=[Type(name='str')], default='hello', optional=True),
        Member(name='Attribute 11', types=[Sequence(name='list', types=[Type(name='str')])], optional=True),
        Member(name='Attribute12', types=[Sequence(name='list', types=[Type(name='str')]), Type(name='None')],
               optional=True),
        Member(name='attribute13', types=[Sequence(name='list', types=[Type(name='str'), Type(name='int')])],
               optional=True),
        Member(name='attribute14', types=[
            Sequence(name='tuple', types=[Type(name='str'), Type(name='str'), Type(name='int')])
        ]),
        Member(name='attribute15', types=[
            HashTable(key=Type(name='str'), values=[Type(name='str'), Type(name='int')])
        ]),
        Member(name='attribute16', types=[Type(name='str')], default='email@address.com', custom_field='Email')]

    dataclasses = [
        DataClass(name='MyDataClass', members=[]),
        DataClass(name='MyDataClass', members=members),
        DataClass(name='MyDataClass', members=[
            Member(name='sub-class', types=[
                DataClass(name='MySubClass', members=[
                    Member(name='attribute1', types=[Type(name='str')])
                ])
            ])
        ]),
        DataClass(name='MyDataClass', members=[
            Member(name='sub-class', optional=True, types=[
                DataClass(name='MySubClass', members=[
                    Member(name='attribute1', types=[Type(name='str')])
                ])
            ])
        ]),
        DataClass(name='MyDataClass', members=[
            Member(name='sub-class', optional=True, types=[
                DataClass(name='MySubClass', members=[
                    Member(name='attribute1', types=[Type(name='str')])
                ])
            ]),
            Member(name='a_class_list', types=[
                Sequence(name='list', types=[
                    DataClass(name='AClassList', members=[
                        Member(name='attribute1', types=[Type(name='str')])
                    ])
                ])
            ], optional=True)
        ])
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


@pytest.fixture(scope='session')
def ir_test_data():
    return irTestData