from textwrap import dedent, indent
from ast import literal_eval
from os.path import commonprefix
import re
from typing import Optional
from uuid import UUID

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from jinja2 import Template

from auto_class import intermediate_representation as ir


GENERATED_CLASSES = {}
CUSTOM_FIELDS = {}
EXTRA_CLASS_BODY = ''
REQUIRED_TYPES: set = set()

_tdre = re.compile(r'(\d+)$')
_uuid4hex = re.compile('[0-9a-f]{32}\Z', re.I)


def get_trailing_digits(cls_name: str) -> Optional[int]:
    m = _tdre.search(cls_name)
    if m:
        return int(m.group(1))
    else:
        return None


def is_hashtable(d: dict):
    """makes an educated guess about whether or not this given dictionary is a hash table
    (a keyed list where all the values are the same type).

    It does this by first determining if all keys have a common prefix, and then checking if all values are the
    same type"""

    def has_common_prefix(d: dict) -> bool:
        prefix = commonprefix(list(d.keys()))
        if len(prefix) > 0:
            return True
        return False

    def all_values_are_the_same(d: dict) -> bool:
        test_val = next(iter(d.values()))
        if all(isinstance(x, type(test_val)) for x in iter(d.values())):
            return True
        else:
            return False

    def all_keys_are_sequential(d: dict) -> bool:
        """`has_common_prefix() catches most instances of this, but sometimes hash tables have sets of keys like:
        {'00', '01', '02', ...}. This function identifies those"""
        key_digits = [get_trailing_digits(k) for k in d.keys()]
        if all([k is not None for k in key_digits]):
            return True
        return False

    def all_keys_are_uuids(d: dict) -> bool:
        try:
            for k in d:
                UUID(k)
        except ValueError:
            return False
        else:
            return True

    if len(d.keys()) < 2:
        # if a dict only has one key, it's safe to assume it's a dataclass
        return False

    if has_common_prefix(d) and all_values_are_the_same(d):
        return True

    if all_keys_are_sequential(d) and all_values_are_the_same(d):
        return True

    if all_keys_are_uuids(d) and all_values_are_the_same(d):
        return True

    return False

 
def get_type_name(t):
    if isinstance(t, type):
        # This condition covers base types (int, str, etc) as well as generated classes
        typename = str(t)[8:][:-2]
        return typename
    else:
        # The only things not covered by above condition should be abstract types from the typing module
        typename = repr(t)
        return typename


def get_class_name(cls_name, members):
    global GENERATED_CLASSES
    # at this point, we need to create a new class with a name that may already exist.
    # If the existing name doesn't have a number on the end of it, we wanna add a number to the end of it.
    # If it already has a number on the end of it, we wanna increment that number
    if cls_name in GENERATED_CLASSES and set(members) == GENERATED_CLASSES[cls_name]['members']:
        already_exists = True
        return cls_name, already_exists

    if cls_name not in GENERATED_CLASSES:
        already_exists = False
        return cls_name, already_exists

    cls_num = get_trailing_digits(cls_name)
    if cls_num:
        end_point = len(str(cls_num))
        cls_num += 1
        cls_name = cls_name[:-end_point] + str(cls_num)
    else:
        cls_name += '1'

    return get_class_name(cls_name, members)


def handle_tuple(t, name, comment):
    global REQUIRED_TYPES

    REQUIRED_TYPES.add('Tuple')
    if not t:
        # Empty tuple
        expr = 'Tuple'
    else:
        subtypes = [type_mapper(subt, name) for subt in t]
        expr = 'Tuple[{}]'.format(', '.join(subtypes))
    if comment is not None and 'Optional' in comment:
        REQUIRED_TYPES.add('Optional')
        expr = f'Optional[{expr}]'
    return expr


def handle_list(t, name, comment):
    global REQUIRED_TYPES
    REQUIRED_TYPES.add('List')
    if not t:
        # Empty list
        REQUIRED_TYPES.add('Any')
        return 'List[Any]'
    # return 'List'+ repr([type_mapper(sub_t) for sub_t in t])
    subtypes = set([type_mapper(subt, name) for subt in t])
    subtypes = list(subtypes)
    if len(subtypes) > 1:
        expr = 'List[Union[{}]]'.format(', '.join(subtypes))
        REQUIRED_TYPES.add('Union')
    else:
        expr = 'List[{}]'.format(subtypes[0])
    if comment is not None and 'Optional' in comment:
        expr = f'Optional[{expr}]'
        REQUIRED_TYPES.add('Optional')
    return expr


def handle_dict(t, name: str, comment:str):
    """Generate a dataclass for a given dict, with field names equal to the normalized key names from the input dict,
    Unless the dict is a hashtable, in which case, return a proper Dict[] definition"""
    global GENERATED_CLASSES
    global CUSTOM_FIELDS
    global EXTRA_CLASS_BODY
    global REQUIRED_TYPES

    if is_hashtable(t):
        # should return something like Dict[<key type>,<val type>]
        key_type = get_type_name(type(next(iter(t.keys()))))
        key_name = commonprefix(list(t.keys()))
        example_value = next(iter(t.values()))
        val_type = type_mapper(example_value, name=name)

        result = f'Dict[{key_type},{val_type}]'
        REQUIRED_TYPES.add('Dict')
        return result
    fields = []
    members = []
    for key in t:
        normalized_key = key.lower().replace(' ', '_').replace('-', '_')
        value = t[key]
        fcomment = None
        custom_field = None
        if isinstance(t, CommentedMap):
            fcomment = t.ca.items.get(key, [None, None, None])[2]
            if fcomment:
                fcomment: str = fcomment.value
                field_token = [token for token in fcomment.split() if token.startswith('f:')]
                custom_field = field_token[0][2:] if field_token else None

        value_type = type_mapper(value, name=key, comment=fcomment)

        if custom_field:
            cfs = f"'marshmallow_field': {custom_field},"
            if custom_field not in CUSTOM_FIELDS:
                new_field_def = """
                class {name}(Field):
                    def _serialize(self, value, attr, obj, **kwargs):
                        return value
                
                    def _deserialize(self, value, attr, data, **kwargs):
                        return value
                
                
                """
                new_field_def = dedent(new_field_def)
                new_field_def = new_field_def.format(name=custom_field)
                CUSTOM_FIELDS[custom_field] = new_field_def

        else:
            cfs = ''
        dks = f"'data_key': '{key},'" if key != normalized_key else ''
        metadata = f"metadata={{{cfs}{dks}}}," if cfs or dks else ''
        field_fn = f"= field({metadata})" if metadata else ''
        members.append(normalized_key)
        fields.append(f"{normalized_key}: {value_type} {field_fn}")

    cls_name = ''.join([s.capitalize() for s in name.replace('-', ' ').split()])

    cls_name, already_exists = get_class_name(cls_name, members)

    if already_exists:
        return cls_name

    tmpl = """
    @dataclass
    class {{cls_name}}:
        {% for field in fields -%}
            {{field}}
        {% endfor %}
        Schema: ClassVar[Type[Schema]] = Schema
        {%- if extra_class_body %}
            {{extra_class_body}}
        {%- endif %}
    
    
    """.lstrip('\n')

    REQUIRED_TYPES.add('ClassVar')
    REQUIRED_TYPES.add('Type')
    tmpl = dedent(tmpl)
    tmpl = Template(tmpl)
    class_def = tmpl.render(cls_name=cls_name, fields=fields, extra_class_body=EXTRA_CLASS_BODY)
    print(class_def)
    GENERATED_CLASSES[cls_name] = {'members': set(members), 'def': class_def}
    if comment is not None and 'Optional' in comment:
        REQUIRED_TYPES.add('Optional')
        return f'Optional[{cls_name}]'
    else:
        return cls_name


def type_mapper(t, name: str = None, comment: str = None):
    global GENERATED_CLASSES
    global REQUIRED_TYPES
    if isinstance(t, tuple):
        return handle_tuple(t, name, comment)
    if isinstance(t, list):
        return handle_list(t, name, comment)
    if isinstance(t, dict):
        return handle_dict(t, name, comment)
    if isinstance(t, type(None)):
        REQUIRED_TYPES.add('Any')
        return 'Any'
    else:
        expr = get_type_name(type(t))
        if comment is not None and 'Optional' in comment:
            REQUIRED_TYPES.add('Optional')
            expr = f'Optional[{expr}]'
        return expr


def compile_module(generated_fields: list, generated_class_list: list, return_list: bool):
    typing_imports = ', '.join(REQUIRED_TYPES)
    typing_imports = f'from typing import {typing_imports}'
    head = f"""
    from dataclasses import field
    {typing_imports}
    
    from marshmallow import Schema
    from marshmallow.fields import Field
    from marshmallow_dataclass import dataclass
    """
    head = dedent(head)
    body = generated_fields + generated_class_list

    if return_list:
        return [head] + body
    else:
        body = ''.join(body)
        return '\n'.join([head, body])


def from_dict(data: dict, name: str, append_code: str, as_list: bool = False):
    global EXTRA_CLASS_BODY
    append_code = append_code.rstrip()
    EXTRA_CLASS_BODY = indent(append_code, '    ')
    type_mapper(data, name,)
    generated_fields = list(CUSTOM_FIELDS.values())
    generated_class_list = [cls['def'] for cls in GENERATED_CLASSES.values()]
    return compile_module(generated_fields, generated_class_list, as_list)


def from_yaml(document: str, name: str, append_code: str = '', as_list: bool = False):
    y = YAML()
    y.indent(mapping=2, sequence=4, offset=2)
    data = y.load(document)
    return from_dict(data, name, append_code, as_list)


def from_dict_literal_str(text: str, name):
    """Expects `text` to be a string representation of a python literal.
    Can also include pycharm type tag prefix (like what you seen when you copy a value out of the pycharm debugger),
    which will be stripped before processing. Copied value must be a dictionary"""
    # strip out "<class 'dict'>:"
    if text.startswith("<class"):
        text = text.split(':', maxsplit=1)[1].strip()

    # escape newlines in embedded string literals before parsing
    text = text.replace('\r', '\\r').replace('\n', '\\n')
    try:
        d = literal_eval(text)
    except (SyntaxError, ValueError) as e:
        raise Exception(f'Provided text does not appear to be a valid ast-parseable python dict literal.'
                        f'Text starts with "{text[:10]}"')
    generated_code = from_dict(d, name, append_code='')
    return generated_code


class Generate:
    def __init__(self):
        self.classes = dict()
        self.required_types = set()
        self.custom_fields = set()

    def from_ir(self, manifest: ir.DataClass):
        print()
