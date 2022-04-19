#!/usr/bin/python
# coding: latin-1

import sys
import getopt
from typing import TextIO
import xml.etree.ElementTree as ET

from common import *
from virtual_mc import *
from instruction import *

# opens file and returns it's content
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

# from input string creates xml tree
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

# checks instruction tag and order and returns instruction order
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

# returns sorted instructions by order from xml tree
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

# add labels to memory
def addlabels(memory: 'Memory', instructions: 'list[Instruction]'):
    memory.pc = 0
    for inst in instructions:
        if inst.opcode == 'label':
            inst.run(memory)
        memory.inccounter()

# runs whole program
def run(xml_tree: 'ET.Element', input: 'TextIO'):
    if(xml_tree.tag != 'program'):
        exit_error('root tag is not program', 32)
    if(xml_tree.get('language') != 'IPPcode22'):
        exit_error('language is not IPPcode22', 32)

    instructions = get_instructions(xml_tree)
    codelen = len(instructions)
    memory = Memory(input)

    addlabels(memory, instructions)

    memory.pc = 0
    while(memory.pc < codelen):
        eprint(f'Memory:\n{memory}')  # for debugging
        if(instructions[memory.pc].opcode != 'label'):
            instructions[memory.pc].run(memory)
        memory.inccounter()


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
            if(sourcefile != ''):
                exit_error('--source argument is already used', 10)
            sourcefile = arg
        elif opt in ("--input"):
            if(inputfile != ''):
                exit_error('--input argument is already used', 10)
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
