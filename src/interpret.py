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


def isInt(s: str):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except Exception as e:
        exit_error(f'{e}', 99)


def open_file(filepath: 'str'):
    if(filepath != ''):
        try:
            input = open(filepath, 'r')
        except FileNotFoundError:
            exit_error(f'"{filepath}" file not found', 11)
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
        exit_error(f'"{sourcefile}" file not found', 11)
    except ET.ParseError:
        exit_error(f'"{sourcefile}" file is not well-formed', 31)
    except Exception as e:
        exit_error(f'{e}', 99)
    return xml_tree.getroot()


class Argument:
    def __init__(self, arg: 'ET.Element'):
        if(arg.get('type') is None):
            exit_error(f'Argument "{arg.tag}" has no type', 32)
        self.type = arg.get('type')
        if(arg.text is None):
            exit_error(f'Argument "{arg.tag}" has no value', 32)

        if(self.type == 'var'):
            self.frame = arg.text[:2]
            if(self.frame not in ['GF', 'LF', 'TF']):
                exit_error(
                    f'Argument "{arg.tag}" has invalid frame "{self.frame}"', 32)
            self.name = arg.text[3:]
            if(self.name == ''):
                exit_error(f'Argument "{arg.tag}" has no name', 32)
        else:
            self.content = arg.text
            if(self.type == 'int'):
                if(not isInt(self.content)):
                    self.content = int(self.content)
                else:
                    exit_error(
                        f'Argument "{arg.tag}" of type "{self.type}" has invalid value "{self.content}"', 32)
            elif(self.type == 'bool'):
                if(self.content in ['true', 'false']):
                    self.content = self.content == 'true'
                else:
                    exit_error(
                        f'Argument "{arg.tag}" of type "{self.type}" has invalid value "{self.content}"', 32)
            elif(self.type == 'string'):
                self.content = self.content
            elif(self.type == 'type'):
                self.content = self.content.lower()
            else:
                exit_error(
                    f'Argument "{arg.tag}" has invalid type "{self.type}"', 32)


class Instruction(object):
    def __init__(self, instruction: ET.Element):
        self.opcode = instruction.get('opcode')
        if(self.opcode is None):
            exit_error('opcode is missing', 32)
        self.opcode = self.opcode.lower()
        self._set_args(instruction)
        self._check_args()

    def xml_argument_order(self, arg: 'ET.Element'):
        name = arg.tag[:3].lower()
        if(name != 'arg'):
            exit_error(
                f'Argument "{arg.tag}" does not have a valid tag prefix "{name}"', 32)
        number = arg.tag[3:]
        if(not number.isnumeric()):
            exit_error(
                f'Argument "{arg.tag}" does not have a valid tag index "{number}"', 32)
        if(isInt(number)):
            number = int(number)-1
        else:
            exit_error('Argument index is not an integer', 32)
        if (number < 0) or (len(self.arguments) <= number):
            exit_error(
                f'argument "{arg.tag}" tag index "{number}" is not it <0,{len(self.arguments)})', 32)
        return number

    def _set_args(self, instruction: ET.Element):
        self.arguments = [Argument]*len(instruction)
        args = sorted(instruction, key=self.xml_argument_order)
        index_list: 'list[str]' = []
        for arg in args:
            if(arg.tag in index_list):
                exit_error('argument has duplicate tag index', 32)
            else:
                index_list.append(arg.tag)
        self.arguments = [Argument(arg) for arg in args]

    def _check_args(self):
        method_name = f'_case_{self.opcode}_check_args'
        check_args = getattr((self), method_name,
                             lambda: exit_error(f'{self.opcode} is not valid instruction (while arg checking)', 32))
        check_args()

    def run(self):
        method_name = f'_case_{self.opcode}_run'
        run = getattr(self, method_name,
                      lambda: exit_error(f'{self.opcode} is not valid instruction (selecting function)', 32),)
        run()

    def _case_move_check_args(self):
        if(len(self.arguments) != 2):
            exit_error(f'{self.opcode} has invalid number of arguments', 32)

    def _case_move_run(self):
        pass

    def _case_defvar_check_args(self):
        pass

    def _case_defvar_run(self):
        pass


def xml_instruction_order(instruction: 'ET.Element'):
    if(instruction.tag != 'instruction'):
        exit_error(f'{instruction.tag} tag is not instruction', 32)
    index = instruction.get('order')
    if(index is None):
        exit_error(f'Instruction "{instruction.tag}" has no order', 32)
    index = str(index)
    if(not isInt(index)):
        exit_error(
            f'Instruction "{instruction.tag}" order "{index}" is not a number', 32)
    index = int(index)-1
    if(index < 0):
        exit_error(
            f'Instruction "{instruction.tag}" order "{index}" is negative number', 32)
    return int(instruction.attrib["order"])


def get_instructions(xml_tree: 'ET.Element'):
    sorted_inst = sorted(xml_tree, key=xml_instruction_order)
    index_list: 'list[str]' = []
    instuctions: 'list[Instruction]' = []

    for inst in sorted_inst:
        order = inst.get('order')
        if(order is None):
            exit_error('Instruction has no order', 32)
        if(order in index_list):
            exit_error('Instruction index is already used', 32)
        index_list.append(order)

        instuctions.append(Instruction(inst))
    return instuctions


class frame:
    def __init__(self):
        self.variables = {}
        self.lables = {}


def run(xml_tree: 'ET.Element', input: 'TextIO'):
    if(xml_tree.tag != 'program'):
        exit_error('root tag is not program', 32)
    if(xml_tree.get('language') != 'IPPcode22'):
        exit_error('language is not IPPcode22', 32)

    instructions = get_instructions(xml_tree)
    index = 0

    GF: 'frame' = frame()
    LF: 'frame' = frame()
    TF: 'list[frame]' = []

    while(index < len(instructions)):
        pass
        #index = instructions[index].run(index, GF, LF, TF, input)


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
