from typing import List, Dict, Any, Union
from uuid import UUID
from os.path import commonprefix
import re


class HashTable(list):
    keys: list

    def __init__(self, d: dict):
        self.keys = list(d)
        super().__init__(list(d.values()))


class ResultSet(list):
    types: set = None
    type: Any = None
    optional: bool = False


_td_re = re.compile(r'(\d+)$')


def get_opts(options: Dict = None) -> Dict:
    if options is None:
        options = dict()
    default_options = dict(threshold=10)
    default_options.update(options)
    options = default_options
    return options


def all_keys_have_common_prefix(d) -> bool:
    prefix = commonprefix(list(d.keys()))
    if len(prefix) > 0:
        return True
    return False


def all_keys_are_have_numbers(d) -> bool:
    """`has_common_prefix() catches most instances of this, but sometimes hash tables have sets of keys like:
    {'00', '01', '02', ...}. This function identifies those"""
    for k in d.keys():
        m = _td_re.search(k)
        if not m:
            # This key does not end in a number, therefore not all keys end in numbers
            return False
    return True

def all_keys_are_numbers(d) -> bool:
    return all([isinstance(k, int) for k in d])

def all_keys_are_uuids(d) -> bool:
    try:
        for k in d:
            UUID(k)
    except ValueError:
        return False
    else:
        return True


def is_hashtable(d: dict, threshold=10):
    """makes an educated guess about whether or not this given dictionary is a hash table
    (a keyed list where all the values are the same type).

    It does this by identifying if one of the following conditions are true:
        All keys have a common prefix (ex. keys like 'group-1737', 'group-8572', 'group-0439')
        All keys have numeric suffixes
        All keys are actually numbers
        All keys are UUIDs
    It only identifies dicts as hash tables if one of these conditions has been met, and the size of the dict exceeds
    the threshold"""

    if len(d.keys()) < threshold:
        # dictionary size below threshold, not considered a hashtable
        return False

    if all_keys_are_numbers(d):
        return True

    if all_keys_have_common_prefix(d):
        return True

    if all_keys_are_uuids(d):
        return True

    if all_keys_are_have_numbers(d):
        return True

    return False


def convert_hash_tables(t: Any, options: Dict) -> Any:
    options = get_opts(options)

    if isinstance(t, list):
        for i, v in enumerate(t):
            t[i] = convert_hash_tables(v, options)

    if isinstance(t, dict):
        if is_hashtable(t, options['threshold']):
            table = HashTable(t)
            return convert_hash_tables(table, options)

        else:
            for k, v in t.items():
                t[k] = convert_hash_tables(v, options)

    return t


def reduce(t: Any, options: Dict) -> Any:
    """recursively applies itself to a nested data structure. if given a list of dicts, will reduce those down to a
    list of a single dict, whose values are ResultSets of the values from the dicts in the original list

     Example:
        [
            {
                'hello': 1
            },
            {
                'hello': 'one',
                'world': 'two'
            },
            {
                'hello':3,
                'world': None
            }
        ]
        Becomes:
        {
            'hello': ResultSet([1, 'one', 3]),
            'world': ResultSet(['two', None])

    :param t: the input data to operate on
    :param options: a dictionary of options to be passed around where needed
    :return: the original data `t`, or a list containing a single Dict whose values are ResultSets
    """
    options = get_opts(options)

    if isinstance(t, list):
        # Handle the 'list-of-dicts' case
        dicts = [v for v in t if isinstance(v, dict)]
        remainder = [v for v in t if not isinstance(v, dict)]
        reduced_dict: Dict[Any, ResultSet] = {}
        if dicts:
            for d in dicts:
                for k in d:
                    # This is inefficient, i know, but it covers the case where keys only exist in some of the dicts in
                    # the list
                    reduced_dict.setdefault(k, ResultSet()).append(d[k])

            # Now we want to replace original dicts in the list with the reduced dict. We need to do the replacement in
            # place so that we can preserve custom list subclasses like HashTable
            t.clear()
            t.extend(remainder)
            t.append(reduced_dict)

        # recurse into all lists, regardless of what's in them
        for i, v in enumerate(t):
            t[i] = reduce(v, options)

    if isinstance(t, dict):
        for k, v in t.items():
            t[k] = reduce(v, options)

    return t


def annotate(t: Any, options: Dict) -> Any:
    options = get_opts(options)

    if isinstance(t, list):
        for i, v in enumerate(t):
            t[i] = annotate(v, options)

    if isinstance(t, dict):
        for k, v in t.items():
            t[k] = annotate(v, options)

    if isinstance(t, ResultSet):
        t.types = {type(v).__name__ for v in t}
        if 'NoneType' in t.types:
            t.optional = True
            t.types.remove('NoneType')

        if len(t.types) > 1:
            t.type = 'Union'
        elif len(t.types) < 1:
            t.type = 'Any'
        else:
            t.type = next(iter(t.types))

    return t



# def idontknow(output_dict, options):
#         # now we've got our output_dict populated, we need to recurse into every value that is itself a list of dicts
#         # first we need to identify which values are lists of dicts. We also need to handle the case where the value
#         # list might contain dicts AND something else.
#         for k, val_list in output_dict.items():
#             dicts = [val for val in val_list if isinstance(val, dict)]
#             remainder = [val for val in val_list if not isinstance(val, dict)]
#             if dicts:
#                 if all([is_hashtable(d, threshold=options['threshold']) for d in dicts]):
#                     # Dicts which are hash tables should be converted into hash tables, not reduced
#                     hash_tables = []
#                     for d in dicts:
#                         hash_tables.append(HashTable(d))
#                     output_dict[k] = remainder + hash_tables
#                 else:
#                     # Dicts which are not hash tables should be reduced
#                     result = reduce(dicts, options)
#
#                     # If val_list only contained dicts, it will now be a list of a single dict, which is fine
#                     # If val_list also contained other values, it will now contain at least one of every type of value
#                     remainder.append(result)
#                     output_dict[k] = remainder
#
#     # Next we need to handle the case where some of our value lists might be lists of lists. if those sub lists are
#     # lists of dicts, we need to reduce them too. This will also capture hash tables (which are a form of list), so we
#     # need to make sure to preserve those (and not accidentally turn them into plain lists)
#     for k, val_list in output_dict.items():
#         sub_lists = [l for l in val_list if isinstance(l, list)]
#         remainder = [l for l in val_list if not isinstance(l, list)]
#         for index, sl in enumerate(sub_lists):
#             sl_dicts = [val for val in sl if isinstance(val, dict)]
#             sl_remainder = [val for val in sl if not isinstance(val, dict)]
#             if sl_dicts:
#                 if all([is_hashtable(d, threshold=options['threshold']) for d in sl_dicts]):
#                     # Dicts which are hash tables should be converted into hash tables, not reduced
#                     hash_tables = []
#                     for d in sl_dicts:
#                         hash_tables.append(HashTable(d))
#                     sub_lists[index] = sl_remainder + hash_tables
#                 else:
#                     # Dicts which are not hash tables should be reduced
#                     result = reduce(sl_dicts, options)
#
#                     # If val_list only contained dicts, it will now be a list of a single dict, which is fine
#                     # If val_list also contained other values, it will now contain at least one of every type of value
#                     sl_remainder.append(result)
#                     sub_lists[index] = sl_remainder
#         output_dict[k] = remainder + sub_lists
