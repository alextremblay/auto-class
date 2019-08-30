from string import hexdigits

import pyperclip
from prompt_toolkit import prompt as ptprompt
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.completion import FuzzyWordCompleter, WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import click

from .generate import from_dict_literal_str, from_yaml


def prompt(options, prompt, include_opts_str=True, completer_type='word') -> str:
    if include_opts_str:
        opts_str = "".join([f"\t{o}\n" for o in options])
        prompt += "\n" + opts_str

    print(prompt)

    if completer_type == 'fuzzy':
        completer = FuzzyWordCompleter(options)
    elif completer_type == 'word':
        completer = WordCompleter(options, match_middle=True, ignore_case=True, sentence=True)
    else: # default to 'word'
        completer = WordCompleter(options, match_middle=True, ignore_case=True, sentence=True)

    choice = ptprompt('> ', completer=completer, complete_while_typing=True)
    return choice


def select(options, prompt=''):
    if len(options) > (len(hexdigits)-1):
        raise Exception(f'select() called with too many options. select() supports a maximum of '
                        f'{len(hexdigits)-1} options.')
    opts = {}
    text = '<bold>Choose one</bold>:\n'
    for i, val in enumerate(options):
        key = hexdigits[i+1]
        opts[key] = val
        text += f'<bold>{key})</bold> {val}\n'
    prompt = HTML(prompt + '> ')
    text = HTML(text)
    print_formatted_text(text)
    keys = list(opts.keys())

    completer = WordCompleter(keys, meta_dict=opts)
    choice = ptprompt(prompt, completer=completer)
    return opts[choice]

def main():
    type = select(['Python Dict Literal', 'YAML "Manifest"'],
                    'What input type would you like to create dataclasses from?')
    if 'Python' in type:
        source = select(['Text Input', 'Clipboard'], 'Where are we pulling the source data from?')
        if 'Text Input' in source:
            data = click.edit(extension='.py')
            name = input("What do you want to call the top-level class?> ")
            result = from_dict_literal_str(data, name)
            print(result)
        if 'Clipboard' in source:
            data = pyperclip.paste()
            name = input("What do you want to call the top-level class?> ")
            result = from_dict_literal_str(data, name)
            print(result)
    if 'YAML' in type:
        source = select(['Text Input', 'Clipboard'], 'Where are we pulling the source data from?')
        if 'Text Input' in source:
            data = click.edit(extension='.yaml')
            name = input("What do you want to call the top-level class?> ")
            result = from_yaml(data, name)
            print(result)
        if 'Clipboard' in source:
            data = pyperclip.paste()
            name = input("What do you want to call the top-level class?> ")
            result = from_yaml(data, name)
            print(result)


if __name__ == '__main__':
    main()
