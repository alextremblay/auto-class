# auto-class

>> This project is in early alpha. Until it is complete, this document should be treated as more of a design document than an actual README

**auto-class** (not to be confused with the excellent but unrelated [python-autoclass] library) is a too that allows you to 
automatically generate a set of nested dataclasses with built-in (de)serializers from a given YAML manifest ~~or set of api responses (json objects)~~

> Generating dataclasses from a set of objects is not  yet implemented, but it's the first thing on the [TODO](#todo) list

[python-autoclass]:https://smarie.github.io/python-autoclass/

## Description

This tool allows you, for a given data structure, to generate python source code for a set of nested dataclasses which 
can load and dump (deserialize and serialize) that data structure. 
The data structure you supply can either be a YAML manifest 
describing the nested data you want to work with (manual mode),
~~or it can be a set of objects (a JSON string array of objects, or a python literal list of dictionaries) representing 
all possible variations of your 
data structure (auto mode)~~(Not Yet Implemented)

Manual mode allows you to define data classes with serializers from a data structure of your choice. Example:
```yaml
MyDataClass: 
    a_string: ''
    a_number: 0 
    a_bool: False
    a_list:
      - a string
      - 1
    A Key With Spaces: ''
    default_value: sweet!
    optional_field_without_type: 
    optional_field_with_type:  # t:str Optional
    allow_missing: '' # AllowMissing
    optional_and_allow_missing: # t:str Optional AllowMissing
    a_union: 0  # t:str,int
    sub_class:
      subkey: ''
      another_subkey: ''
      sub_sub_class:
        so_nested: True
        much_wow: True
    a_class_list:
      - a_subkey: 1
        one_more: hello
```
Becomes:
```python
from typing import List, Any, Union, Optional, ClassVar, Type
from dataclasses import field
from marshmallow import Schema
from marshmallow_dataclass import dataclass

@dataclass
class MyDataClass:
    a_string: str = field(default_factory=str)
    a_number: int = field(default_factory=int)
    a_bool: bool = field(default_factory=bool)
    a_list: List[str,int] = field(default_factory=list)
    a_key_with_spaces: str = field(default_factory=str, metadata=dict(data_key='A Key With Spaces'))
    default_value: str = field(default='sweet!')
    optional_field_without_type: Any = field(default=None)
    optional_field_with_type: Optional[str] = field(default=None)
    allow_missing: str = field(default_factory=str, metadata=dict(missing=str, default=str, required=False))
    optional_and_allow_missing: Optional[str] = field(default=None, metadata=dict(missing=None, default=None, required=False))
    a_union: Union[str,int] = field(default_factory=str)
    
    @dataclass
    class SubClass:
        subkey: str = field(default_factory=str)
        another_subkey: str = field(default_factory=str)
        
        @dataclass
        class SubSubClass:
            so_nested: bool = field(default_factory=bool)
            much_wow: bool = field(default_factory=bool)
            Schema: ClassVar[Type[Schema]] = Schema
        
        sub_sub_class: SubSubClass = field(default_factory=SubSubClass)
        Schema: ClassVar[Type[Schema]] = Schema
        
    sub_class: SubClass = field(default_factory=SubClass)
    
    @dataclass
    class AClassList:
        a_subkey: int = field(default_factory=int)
        one_more: str = field(default='hello')
        Schema: ClassVar[Type[Schema]] = Schema
        
    a_class_list: List[AClassList] = field(default_factory=list)
    Schema: ClassVar[Type[Schema]] = Schema
    
# and can be used to transform this:
    
input_dict = {
    'a_string': 'hello',
    'a_number': 24,
    'a_bool': True,
    'a_list': ['hello', 1, 2, 'world'],
    'A Key With Spaces': 'nice!',
    'default_value': None,
    'optional_field_without_type': None,
    'optional_field_with_type': None,
    # allow_missing key is missing
    # optional_and_allow_missing is also missing
    'a_union': 0,
    'sub_class': {
        'subkey': 'hello',
        'another_subkey': 'world',
        'sub_sub_class': {
            'so_nested': True, 
            'much_wow': True
        }
    },
    'a_class_list': [
        {'a_subkey': 1, 'one_more': 'hello'}
    ]
}

# into this:

output_object = MyDataClass.Schema().load({})
assert output_object == MyDataClass(
    a_string='hello',
    a_number=24,
    a_bool=True,
    a_list=['hello', 1, 2, 'world'],
    a_key_with_spaces='nice!',
    default_value='sweet!',
    optional_field_without_type=None,
    optional_field_with_type=None,
    allow_missing='',
    optional_and_allow_missing=None,
    a_union=0,
    sub_class=MyDataClass.SubClass(
        subkey='hello', 
        another_subkey='world',
        sub_sub_class=MyDataClass.SubClass.SubSubClass(
            so_nested=True,
            much_wow=True
        )
    ),
    a_class_list=[
        MyDataClass.AClassList(a_subkey=1, one_more='hello')
    ]
)

# And accessing nested data goes from this:

input_dict['sub_class']['sub_sub_class']['so_nested'] == True

# To this:

output_object.sub_class.sub_sub_class.so_nested == True
```

This gives you type checking capability, IDE autocomplete, easy data validation, and a whole bunch of other features!


## Installation

\# TODO: deploy to PyPI
```bash
$ pip3 install auto-class
```


## Usage

This tool was primarily designed to be a command-line tool, but can also be used directly in python

### Command Line Usage

\# TODO: flesh this out
```bash
$ auto-class generate --from yaml --in-clipboard
$ auto-class generate --from yaml --in-file file.yaml
$ auto-class generate --from python --in-clipboard
$ auto-class generate --from python --in-file file.py  # Haven't quite figured out how this one's gonna work
```

### Python Usage

\# TODO: flesh this out
```python
from auto_class import generate

generated_source_code = generate.from_yaml('''
MyDataClass:
    test_field: ''
    Another Test Field: 2
''')
```


## YAML Manifest Spec

The YAML manifest is a YAML document with the following rules:
 - All Dataclasses to be generated should be expressed as YAML mappings (aka dictionaries) attached to CapitalCased 
   top-level variables, like so:
   ```yaml
   MyDataClass:
     field: blah
     other_field: blah
   MyOtherDataClass:
     field: blah
     other_field: blah
   ```
   All top-level variables starting with lower-case letters as reserved for future use (like global settings to 
   modify dataclass generation, for example)
 - All fields in each top-level dataclass declaration must be one of three types: 
    - **Scalars** (int, float, str, null, bool)
    - **Sequences** (list, [hash table](#hash-table)) 
    - **Objects** (dictionaries)
 - All field values are optional. If a field has a value, the type of that value will be used to define the type of the 
   dataclass definition for that field. If the value is "truthy", it will be used as the default value for the 
   dataclass definition for that field.
 - All fields can contain YAML comments. Those comments can contain any of the following tokens:
    - `Optional`: (only valid for **Scalar** and **Object** fields) Marks the field's type annotation as Optional and sets default value to None, if a default value has not been explicitly set
    
    - `HashTable`: (only valid for **Object** fields) Instructs the generator to create a [hash table](#hash-table) definition from this object, instead of generating a dataclass definition. 
      This field will effectively become a special kind of **Sequence** type, and so only tokens which are valid for **Sequence** fields can be used in combination with this token. 
      
    - `AllowMissing`: (valid on all field types) Configures the marshmallow serializer for this field to create a default value when this field is missing from an input dict / json payload
    
    - `t:{*type}`: (only valid for **Scalar** fields) Overrides the field's derived type. `*type` is a comma-separated list of one or more types (ex. `t:str` or `t:int,bool`). 
      The types must only be separated by commas, and cannot be separated by spaces. 
      When used on **Scalar** fields, the types listed in this token will replace the derived type of the field(ex `field_name: '' # t:str,int` will become `field_name: Union[str,int]`). 
      Although it's possible to override a derived type with a completely different type (Ex. `field: '' # t:int`), it's ill advised and should be avoided. 
      It will make your manifest unintuitive and difficult to read. 
      Also, please note, this comment token is incompatible with the `f:{field}` comment token shown below. 
      These two tokens cannot be used in the same field of your schema definition.
      
    - `f:{mm_field_name}`: (only valid for **Scalar** fields. [see note](#custom-field-name)) Overrides the Marshmallow [Field] to use for serialization / deserialization of the field. 
      Can be an existing Marshmallow field, or a [Custom Field].
      For example: `field_name: '' # f:Url` will generate a field definition of `field_name: str = field(default_factory=str, metadata={'marshmallow_field': Url})`. 
      Note: You will be responsible for either defining a custom field called `Url` or importing the `Url` field from the `marshmallow.fields` module into the generated dataclass module.
      
    - `n:{class_name}`: (Only valid for **Object** fields) Override the derived class name of a nested dataclass. 
      Generally, the class name is derived from the name of the field that the nested object is attached to (ie: `field_name: {}` becomes `field_name: FieldName = field(default_factory=FieldName)`). 
      With this token, you can specify the name of the generated data class (ex: `field_name: {} # n:MyNamedClass` becomes `field_name: MyNamedClass = field(default_factory=MyNamedClass)`)
      
[Field]:https://marshmallow.readthedocs.io/en/3.0/api_reference.html#module-marshmallow.fields
[Custom Field]:https://marshmallow.readthedocs.io/en/3.0/custom_fields.html


## A Complete Example:

```yaml
DataClass:
# ^^^^^^^ 
# All top-level keys will be used as names for dataclass definitions, 
# and must contain YAML maps (aka dictionaries).
    
    a_field: ''
#            ^^ 
#            this value is a string, so the generator will define 
#            this as a str type, and tell marshmallow to validate 
#            it as a Str() field.
    
    a_default_value: a default value
#                    ^^^^^^^^^^^^^^^ 
#                    this string is not an empty string (''), 
#                    so it will be treated as a default value
    
    a_number: 0
#             ^ 
#             this value is a number, so the generator will define 
#             this as an int type, and tell marshmallow to validate
#             it as a Int() field. Since this number is falsy, 
#             it will not be treated as a default value
    
    a_list:
      - string  # Lists can contain any combination of types and will generate appropriate definitions
      - 2       # Lists should not contain more than one instance of a given type
    
    an_optional_value: 
#                      ^ a blank value will translate into type Any with default value None
    
    a_union: 0  # t:str,int
#                 ^^^^^^^^^
#                 There is no way in YAML to define a value that 
#                 has more than one type, so we introduce metadata 
#                 into our manifest in the form of a YAML comment token. 
#                 The 't:' token stands for type, and can be used to override
#                 the type information which this library derives from the 
#                 YAML value itself
    
    
    A Key With Spaces: ''
#   ^^^^^^^^^^^^^^^^^
#   This key is not a valid python attribute name. 
#   The dataclass field generated from this key will use a normalized 
#   version of this key as its field name, and will configure 
#   marshmallow field options to treat this key name as its 
#   data key (to serialize from and deserialize to this key name)
    
    optional_field_with_type: ''  # Optional
#                                   ^^^^^^^^
#                                   This flag will mark the type definition of 
#                                   the generated dataclass field as Optional[]
#                                   and set its default value to None 
    
    implicit_optional:  # t:str
#                      ^^^^^^^^
#                      Any field that has a value of None (ie. a blank field) 
#                      with an explicit type override (t:str) will be implicitly
#                      treated as if it had an `Optional` comment token. 
    
    an_optional_union:  # t:str,int
#                       ^^^^^^^^^^^ 
#                       As with the `a_union` and `implicit_optional` examples
#                       above, this will create a field definition that is
#                       Optional[Union[str,int]] and has a default value of None
    
    optional_field_with_default: 'hello' # Optional
#                                ^^^^^^^   ^^^^^^^^
#                                This field will be marked Optional[] as above, 
#                                but its default value will not be set to None,
#                                because it already has a default value.
    
    allow_missing: '' # AllowMissing
#                       ^^^^^^^^^^^^
#                       With this flag, the dataclass generator will configure the 
#                       marshmallow serializer/deserializer(Field) for this field 
#                       to set the value of this field to an empty string if this
#                       field is missing from the input dictionary / json payload
    
    optional_and_allow_missing: '' # Optional AllowMissing
#                                    ^^^^^^^^ ^^^^^^^^^^^^
#                                    Same as above, but if the field is missing from 
#                                    the input dictionary / json payload, it will be 
#                                    set to None instead of an empty string (because 
#                                    of the `Optional` comment token)
    
    custom_field: email@address.com  # f:Email
#                                     ^^^^^^^
#                                     This tells the generator not to use the default marshmallow 
#                                     field for a given type (in this case String for a str) 
#                                     and instead use this specific marshmallow field. 
#                                     Note: If you do this, you will be repsonsible for importing 
#                                     an Email field into the generated dataclass module.
    
    sub_class:
#   ^^^^^^^^^
#   This field is a YAML map (equivalent to a python dictionary). 
#   The generator will create a nested dataclass definition named 
#   after this key (sub_class) and the type of this field will be 
#   set to that data class. Since not all key names are guaranteed
#   to be valid python class names, the generated dataclass name 
#   will be normalized (all spaces, dashes, and underscores will be
#   removed, and all letters following spaces, dashes, and underscores 
#   will be capitalized. The first letter will also be capitalized).
#   In this case, a nested dataclass will be generated and named `SubClass`, 
#   and the generated field definition for  this `sub_class` field will
#   be `sub_class: SubClass = field(default_factory=SubClass)`
      subkey: ''
      another_subkey: ''
      sub_sub_class:
        so_nested: True
        much_wow: True
    
    optional_sub_class: # Optional
      subkey: ''
      another_subkey: ''
    
    implicit_hashtable:
      1: 1  # The keys in this object are not and cannot be made to be valid  python dataclass
      2: 2  # field names, and so it is safe to assume that this particular object is not meant 
      3: 3  # to be a dataclass instance. auto-class will pick up on this and automatically mark
      4: 4  # this object as a `HashTable`. Instead of generating a dataclass definition for this
            # for this object, auto-class will treat `implicit_hashtable` as an ordinary field with 
            # a type of `Dict[int,int]`
    
    explicit_hashtable:  # HashTable
#                          ^^^^^^^^^
#                          An object can also be explicitly marked as a `HashTable`, in 
#                          which case a dataclass definition will not be created for it.
#                          This particular example will be treated as a regular field
#                          with a type of `Dict[str,Union[int,str,bool]]`
      a_subkey: 1
      one_more: hello
      and_another: True
    
    a_class_list:  # n:NamedClass
#                    ^^^^^^^^^^^^
#                    This object would have generated a dataclass called `AClassList`, but with
#                    the inclusion of the `n:{}` token, the generated dataclass will instead be 
#                    called `NamedClass` 
      - a_subkey: 1
        one_more: hello
```
Will generate the following python code:
```python
from typing import List, Any, Union, Optional, ClassVar, Type
from dataclasses import field
from marshmallow import Schema
from marshmallow_dataclass import dataclass

# TODO: flesh this out
```

as a side note, for those interested in the nuts and bolts, what happens behind the scenes is that the input manifest 
is converted into an intermediate representation, which is then used to generate the actual python code for the 
dataclass definitions. The above example produces the following intermediate representation:
```python
from auto_class.intermediate_representation import DataClass, Field, Scalar, Sequence, HashTable, Union

DataClass('DataClass', {
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
    Field('sub_class', DataClass('SubClass', {
        Field('subkey', Scalar('str')),
        Field('another_subkey', Scalar('str')),
        Field('sub_sub_class', DataClass('SubSubClass', {
            Field('so_nested', Scalar('bool', default=True)),
            Field('so_nested', Scalar('bool', default=True)),
        })),
    })),
    Field('optional_sub_class', DataClass('OptionalSubClass', optional=True, fields={
        Field('subkey', Scalar('str')),
        Field('another_subkey', Scalar('str')),
    })),
    Field('implicit_hashtable', HashTable(key=Scalar('int'), values=[Scalar('int')])),
    Field('explicit_hashtable', HashTable(key=Scalar('str'), values=[
        Scalar('int'), Scalar('str'), Scalar('bool')
    ])),
    Field('a_class_list', Sequence('list', values=[
        DataClass('NamedClass', {
            Field('a_subkey', Scalar('int', default=1)),
            Field('one_more', Scalar('str', default='hello'))
        })
    ]))
})
```


## Limitations
Currently, the following limitations apply:
 - Cannot support shared dataclasses:
     see [docs/shared_dataclasses](./docs/shared_dataclasses.md) for more info
 - Can only support `Union` types where all unioned types are **Scalar** values. (ie. can't support `Union[str,DataClass]`, `Union[int, List[int]]`, etc)


## TODO
Here is a list of features that I am either actively implementing in another branch, or hope to add to the library in the future:
 - Generate dataclass definitions from a set of objects, including the following sub-features:
   - Auto-identify fields that have different types in different objects within the set, and make those fields Unions
   - Auto-identify fields that are `null` in some of the objects in the set, and make those fields Optional
   - Auto-identify fields that are missing from some of the objects in the set and add the `AllowMissing` comment token 
     to those objects
   - Recursively reduce types from sub-objects (ie if a field in the object set is a nested object, merge all instances 
     of the nested sub-objects into a single set of objects and apply all the rules listed above to that set of 
     sub-objects, recursively)
   - Generate a YAML manifest of the identified data structure, and present that manifest to the user for tweaking prior 
     to generating dataclass definitions
 - Add support for Tuples and Sets (possible by adding a comment token to a list?)
 - Add the ability to define methods in the schema attached to the generated dataclasses (maybe define these methods as 
   fields on the dictionary with a special comment token?) (maybe also add token syntax to support decorators, to enable 
   [extending marshmallow schemas](https://marshmallow.readthedocs.io/en/stable/extending.html#schemavalidation))
 - Add options to the manifest to change defaults, for example: 
   - Instead of all fields being required by default and having an `Optional` comment token, make all fields optional 
     and have a `Required` comment token
   - Instead of causing validation errors when input dictionaries have missing keys and having an `AllowMissing` 
     comment token to override that, make all fields allow missing keys and have a `DontAllowMissing` comment token
   

## Inspiration
Time and time again I've found myself following the same basic patterns, and I suspect you probably have too:

### Pattern 1: Organic Data Structures

You're happily typing along, building some awesome library or tool, and you create a data structure to represent some state or 
important part of your project. It starts out as a simple dictionary, whose keys are strings, or numbers, or bools, or 
lists  containing strings, or numbers, or bools, and everything is fine.

Your project's complexity grows, and so too does the complexity of your data structure. you start grouping related 
values in your dictionary into nested dictionaries, turning those lists of strings into lists of dictionaries to store 
related data. Your data structure is a bit tricky to fully keep in your head, you write it down somewhere and start 
getting in the habit of checking that example every time you access or change a key, but still, mostly, everything is 
fine.

Your project's complexity grows some more. some of your nested dictionaries and lists of dictionaries start to ALSO 
contain nested dictionaries and lists of dictionaries. You start running into problems:
 - "Wait, is this subfield a dictionary in a list, or a list in a dictionary?"
 - "Wait, how did I spell this key name?"
 - "Wait, is this subfield supposed to be a string, or a number?"
 
You get to the point where you think to yourself "Ok, ok, this isn't working anymore. My data is too large to be an 
undocumented pile of dictionaries and lists. I need to implement structure!"

So you start implementing structure. You think to yourself "Well, I'll just make a set of classes to define my data 
structure. That's the best-practices way to go!"... except that class definitions are incredibly verbose and tedious 
to write. Especially if you've got nested data structure. Not only do you need to write out each field name 3-4 times 
(class body, \__init\__ signature, \__init\__ body x2), you also have to manually convert each field value that's a dict
or a list of dicts into class instances or lists of class instances. It gets to be a real pain.

So you think "OK, I'll just make my classes dataclasses! Then the dataclass library can auto-generate \__init\__ 
methods for me. Perfect!"... Well, yes and no. True, dataclasses conveniently auto-generate \__init\__ methods for you,
but those init methods don't handle converting nested dictionaries / lists of dictionaries into nested dataclass 
instances / lists of dataclass instances. You could achieve what you want by futzing around with dataclass InitVars and 
\__post_init\__ methods, but you'll probably find yourself fighting against the very thing you thought would save you 
time. You'll also find that omitting default values for fields, in order to mark them as required (as, for example, a 
rudimentary form of data validation) will cause you more headaches than it solves.

Also, if your python dictionary data structure has keys with spaces or dashes in them, turning them into dataclasses 
becomes an almost instant non-starter

The excellent marshmallow library has the ability to not only validate any data structure you want, but also has the 
ability to seemlessly transform data at the global level and on a per-node level (meaning you can give it a dictionary 
of dictionaries and have it transform the whole thing, or apply per-sub-dictionary transformations).

"Perfect!" you say to yourself, "I can use marshmallow to validate that my data is correct and transform each 
subdict into a dataclass instance, automatically attached to its parent dictionary / dataclass instance! (and rename 
keys with spaces / dashes in them into valid python field names)"... Well, as it turns out, yes! you can! 
Marshmallow and dataclasses fit so incredibly well together. Dataclasses are great if you have a very rigidly defined 
structure where none of the fields are either missing or `None`, and marshmallow (with it's ability to intelligently 
handle missing and null keys) is great at filling in that all-fields-should-be-required part of dataclasses 
mentioned above.

The only problem is that marshmallow can only do all of these wonderful things if you write custom marshmallow schemas 
to represent each of your nested dataclasses, like so:

```python
from marshmallow import Schema, fields, post_load, pre_dump
from dataclasses import dataclass, asdict

@dataclass
class NestedData:
    some_data: str
    more: bool
    
class NestedDataSchema(Schema):
    some_data = fields.Str(missing='')
    more = fields.Bool(missing=False)
    
    @post_load
    def post(self, data):
        return NestedData(**data)
    
    @pre_dump
    def pre(self, instance):
        return asdict(instance)

@dataclass
class ParentData:
    a_field: str
    another_field: int
    extra_data: NestedData
    
class ParentDataSchema(Schema):
    a_field = fields.Str(missing='')
    another_field = fields.Int(missing=0)
    
    @post_load
    def post(self, data):
        return ParentData(**data)
    
    @pre_dump
    def pre(self, instance):
        return asdict(instance)
```

So for each field in each dictionary / data class, you'd have to write each field name twice, and each field type twice,
in two different ways! (`str` vs `fields.Str`, etc)

Ick!

That's not fun. That's a lot of typing, a lot of verbosity. That's a lot of opportunities to create annoying bugs by 
accidentally having mismatches or typos between dataclasses and their associated schemas.

So maybe at this point you're thinking "Gosh, I wonder if there's a library that can autogenerate marshmallow schemas 
from dataclasses, or dataclasses from marshmallow schemas..." And there is! There are, in fact, several of them. All 
with different pros and cons. Maybe you dive deep into them all and find that some of them are too cumbersome to use and 
others involve too much python meta-magic (a python class that replaces itself with an auto-generated dataclass version 
of itself... what?) and decide (as i did) that marshmallow_dataclass strikes the best balance between hassle and magic 
and you think "Perfect! my quest for a data structure solution is finally complete! I now have something that can define 
an arbitrarily nested set of dataclasses and can optionally support input validation, key name transformation, and a 
whole bunch of other features! Yes!"

Well, yes, but the end result is still kind of verbose. To represent a data structure like:
```python
{
    'a_string': 'hello',
    'a_number': 24,
    'a_bool': True,
    'a_list': ['hello', 1, 2, 'world'],
    'A Key With Spaces': 'nice!',
    'default_value': None,
    'default_value_of_none': None,
    'default_none_with_explicit_type': None,
    'optional_field': None,
    'a_union': 0,
    'sub_class': {
        'subkey': 'hello',
        'another_subkey': 'world',
        'sub_sub_class': {
            'so_nested': True, 
            'much_wow': True
        }
    },
    'a_class_list': [
        {'a_subkey': 1, 'one_more': 'hello'}
    ]
}
```
You would need to write this:
```python
from typing import List, Any, Union, Optional, ClassVar, Type
from dataclasses import field
from marshmallow import Schema
from marshmallow_dataclass import dataclass

@dataclass
class MyDataClass:
    a_string: str = field(default_factory=str)
    a_number: int = field(default_factory=int)
    a_bool: bool = field(default_factory=bool)
    a_list: List[str,int] = field(default_factory=list)
    a_key_with_spaces: str = field(default_factory=str, metadata=dict(data_key='A Key With Spaces'))
    default_value: str = field(default='sweet!')
    default_value_of_none: Any = field(default=None)
    default_none_with_explicit_type: str = field(default=None)
    optional_field: Optional[str] = field(default=None)
    allow_missing: str = field(default_factory=str, metadata=dict(missing=str, default=str, required=False))
    a_union: Union[str,int] = field(default_factory=str)
    
    @dataclass
    class SubClass:
        subkey: str = field(default_factory=str)
        another_subkey: str = field(default_factory=str)
        
        @dataclass
        class SubSubClass:
            so_nested: bool = field(default_factory=bool)
            much_wow: bool = field(default_factory=bool)
        
        sub_sub_class: SubSubClass = field(default_factory=SubSubClass)
        
    sub_class: SubClass = field(default_factory=SubClass)
    
    @dataclass
    class AClassList:
        a_subkey: int = field(default_factory=int)
        one_more: str = field(default='hello')
        
    a_class_list: List[AClassList] = field(default_factory=list)
```
It's definitely better, but still verbose. We're no longer repetitively writing out field names again and again, but
we're still repetitively writing out types and a lot of boilerplate, which is not very fun.

Wouldn't it be great if we could just declare what we want our data structure to look like in as simple a way as 
possible and have the classes and schemas and various minutia taken care of for us?

That was the driving force behind this project.

The idea is to have a super simple and minimal YAML manifest, containing all the information needed to generate 
functional marshmallow_dataclass code. See the [Manifest Specification](#yaml-manifest-spec) and 
[A Complete Example](#a-complete-example)for details.

### Pattern 2: Undocumented APIs

You're working on a piece of software that makes use of an api endpoint that returns a JSON object. This JSON object 
is deeply nested, and not very well documented (or documented at all).

You grab an example api response object from the endpoint, and store it somewhere for reference, so you can look at 
key names and value types and whatnot.

You're typing along, working on your library, and you start to run into some of the same problems identified in pattern 1:
 - "Wait, is this subfield a dictionary in a list, or a list in a dictionary?"
 - "Wait, how did I spell this key name?"
 - "Wait, is this subfield supposed to be a string, or a number?"

You reference your stored api response object to correct these issue, but find it a hassle.

Maybe you also start to run into issues where sometimes the response from the api doesn't match the response object 
you're using as reference:
 - "Oh, sometimes when this field is blank it's an empty string, but sometimes its a `null`/`None`..."
 - "Huh, sometimes this field is a `float`, and sometimes it's a `str` of a float. Well that's just perfect..."
 - "Oh man, sometimes this nested dict is a null value, and I'm getting key errors trying to look up its values..."
 
Maybe you also start thinking you need to document this API in the form of a class.

Maybe you start with a dataclass, but then realize that writing out dataclass rules to handle all the variety this 
API endpoint throws at you is too much of a PITA (making everything a field with defaults, setting up default 
factories for values that need mutable defaults, figuring out how to handle nested data), etc.

Maybe you also discover marshmallow as I did and go down the rabbit hole of discovery as I did in Pattern 1 above

The problem is, you've got this API that you call and get a response from, and every time you think you know the shape 
of that response, the API surprises you. You make a bunch of calls to this API, and get a bunch of responses that all 
have a given field, and that field is always a string... until it isn't. Until you get a response where that field is 
a null value, or just doesn't exist at all.

So what do you do? You update your dataclass definition / schema. You didn't know that this field was optional, but 
now you do. You won't be surprised again... Or so you think. Then it happens again, with a different field. Maybe this 
time it's a nested dictionary that sometimes does and sometimes doesn't exist. Updating your dataclass / schema is 
more complicated, but still doable. But then it happens again, and again, and you start getting fed up. You wish you 
could just feed a list of every possible api response object into a tool and have that tool figure out what is and 
isn't optional, which fields are sometimes a string and sometimes an integer, and all that stuff...
 
Well now you can!

> Actually, you can't. This feature hasn't been implemented yet. Sorry!


## Notes

#### Custom Field Name
`f:{mm_field_name}` is technically valid for all field types except [hash table](#hash-table) and union types, but is 
currently only supported for **Scalar** fields

#### Hash Table
A hash table is a kind of dictionary, like a dataclass, but where a dataclass is a dictionary with a fixed set of keys 
that are all strings, a hash table is an arbitrarily-sized set of keyed values where both the keys and the values can 
be any type. Another common name ofr a hash table is a lookup table

#### Union Types
A quick note about unions: in python a union is a value type that can be one of a number of types. a Union[str,int] is a value that could be either a string or an integer. Marshmallow_dataclass (upon which this library is built) also support serializing and deserializing union types through the `marshmallow_union` library. The way this works is it maps each type in the union to a marshmallow field and tries the value to be serialized / deserialized against each of those marshmallow fields until one succeeds, or they all fail and you get a validation error

#### PyScaffold
This project has been set up using PyScaffold 3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
