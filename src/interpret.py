#!/usr/bin/python
# coding: latin-1


import sys
import getopt
from typing import TextIO
import xml.etree.ElementTree as ET

"""
10 - chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů;
11 - chyba při otevírání vstupních souborů (např. neexistence, nedostatečné oprávnění);
12 - chyba při otevření výstupních souborů pro zápis (např. nedostatečné oprávnění, chyba při zápisu);
20 – 69 - návratové kódy chyb specifických pro jednotlivé skripty;
99 - interní chyba (neovlivněná vstupními soubory či parametry příkazové řádky; např. chyba
alokace paměti).

interpret.py
31 - chybný XML formát ve vstupním souboru (soubor není tzv. dobře formátovaný, angl.
    well-formed, viz [1]);
32 - neočekávaná struktura XML (např. element pro argument mimo element pro instrukci,
    instrukce s duplicitním pořadím nebo záporným pořadím);

52 - chyba při sémantických kontrolách vstupního kódu v IPPcode22 (např. použití nedefino-
    vaného návěští, redefinice proměnné);
53 - běhová chyba interpretace – špatné typy operandů;
54 - běhová chyba interpretace – přístup k neexistující proměnné (rámec existuje);
55 - běhová chyba interpretace – rámec neexistuje (např. čtení z prázdného zásobníku rámců);
10
56 - běhová chyba interpretace – chybějící hodnota (v proměnné, na datovém zásobníku nebo
    zásobníku volání);
57 - běhová chyba interpretace – špatná hodnota operandu (např. dělení nulou, špatná návra-
    tová hodnota instrukce EXIT);
58 - běhová chyba interpretace – chybná práce s řetězcem.
"""


def exit_error(error_message: 'str', rc: 'int'):
    print(f'interpret.py: {error_message}')
    exit(rc)


def print_help():
    print('Usage: interpret.py [--help] [--source=<source>] [--input=<input>]')
    print('\t--help                 Print this help')
    print('Inputs:')
    print('\t--source=<source>      Input XML file')
    print('\t--input=<input>        Input file with inputs for interpretetation')
    print('\t\t At least one of the two inputs is required')
    print('\t\t If one input file is missing, the input will be read from stdin')
    exit()


def open_file(filepath: 'str'):
    if(filepath != ''):
        try:
            input = open(filepath, 'r')
        except FileNotFoundError:
            exit_error(f'{filepath} file not found', 11)
        except Exception as e:
            exit_error(f'{e}', 99)
    else:
        input = sys.stdin
    return input


def get_xml(sourcefile: 'str'):
    try:
        if(sourcefile != ''):
            xml_tree = ET.parse(sourcefile)
        else:
            xml_tree = ET.parse(sys.stdin)
    except FileNotFoundError:
        exit_error(f'{sourcefile} file not found', 11)
    except ET.ParseError:
        exit_error(f'{sourcefile} is not well-formed', 31)
    except Exception as e:
        exit_error(f'{e}', 99)
    return xml_tree.getroot()


class Argument:
    def __init__(self, arg: 'ET.Element'):
        if(arg.get('type') is None):
            exit_error(f'Argument {arg.tag} has no type', 32)
        self.type = arg.get('type')
        if(self.type not in ['int', 'bool', 'string']):
            pass
        if(arg.text is None):
            exit_error(f'Argument {arg.tag} has no value', 32)
        self.frame = arg.text[:2]
        if(self.frame not in ['GF', 'LF', 'TF']):
            exit_error(f'Argument {arg.tag} has invalid frame', 32)
        self.name = arg.text[3:]
        if(self.name == ''):
            exit_error(f'Argument {arg.tag} has no name', 32)


class Instruction(object):
    def __init__(self, instruction: ET.Element):
        self.opcode = instruction.get('opcode')
        if(self.opcode is None):
            exit_error('opcode is missing', 32)
        self.opcode = self.opcode.lower()
        if(self.opcode not in
           [
               'move', 'createframe', 'pushframe', 'popframe', 'defvar', 'call', 'return',  # frames
               'pushs', 'pops',  # stack
               'add', 'sub', 'mul', 'idiv', 'lt', 'gt', 'eq',  # arithmetic
               'and', 'or', 'not', 'int2char', 'string2int',
               'read', 'write',  # io
               'concat', 'strlen', 'getchar', 'setchar',  # strings
               'type',  # type
               'label', 'jump', 'jumpifeq', 'jumpifneq', 'exit',  # labels
               'dprint', 'break'  # debug
           ]):
            exit_error(f'{self.opcode} is not a valid opcode', 32)

        self.arguments = [Argument]*len(instruction)
        for arg in instruction:
            name = arg.tag[:3].lower()
            if(name != 'arg'):
                exit_error('argument does not have a valid tag (prefix)', 32)
            number = arg.tag[3:]
            if(not number.isnumeric()):
                exit_error('argument does not have a valid tag (index)', 32)
            number = int(number)-1
            if (number < 0) or (len(self.arguments) <= number):
                exit_error(
                    'argument does not have a valid tag (index out of bounds)', 32)
            if(self.arguments[number] is not None):
                exit_error(
                    'argument does not have a valid tag (index already used)', 32)
            self.arguments[number] = Argument(arg)

        # @todo switch of function based on opcode

    def _get_method(self):
        method_name = f'_case_{self.opcode}'
        method = getattr(self, method_name,
                         lambda: exit_error(f'{self.opcode} is not a valid case', 32))
        return method()

    def run(self):
        method = self._get_method()
        method()

    def _case_pushs(self):
        pass


def run(xml_tree: 'ET.Element', input: 'TextIO'):
    instuctions = []
    if(xml_tree.tag != 'program'):
        exit_error('root tag is not program', 32)
    if(xml_tree.get('language') != 'IPPcode22'):
        exit_error('language is not IPPcode22', 32)

    #@todo discord
    for inst in xml_tree:
        if(inst.tag != 'instruction'):
            exit_error('instruction tag is not instruction', 32)
        index = inst.get('order')
        if(index is None):
            exit_error('Instruction has no order', 32)
        index = str(index)
        if(not index.isnumeric()):
            exit_error('Instruction has no order', 32)
        index = int(index)-1
        if(index < 0) or (len(xml_tree) <= index):
            exit_error('Instruction has invalid order (out of bounds)', 32)
        if(instuctions[index] is not None):
            exit_error('Instruction index is already used', 32)

        instuctions[index] = Instruction(inst)

    # @todo: check if all instructions are defined
    # @todo: frames are defined


def main(argv: 'list[str]'):
    inputfile = ''
    sourcefile = ''

    try:
        opts, args = getopt.getopt(argv, '', ['help', 'source=', 'input='])
    except getopt.GetoptError:
        exit_error(f'Invalid argument/s {argv}', 10)

    for opt, arg in opts:
        if opt in ("--help"):
            print_help()
        elif opt in ("--source"):
            sourcefile = arg
        elif opt in ("--input"):
            inputfile = arg

    if(len(args) > 0):
        exit_error(f'Invalid argument/s {args}', 10)

    if(sourcefile == '') and (inputfile == ''):
        exit_error('No input files specified', 10)

    input = open_file(inputfile)
    xml_tree = get_xml(sourcefile)
    run(xml_tree, input)


if __name__ == "__main__":
    main(sys.argv[1:])
