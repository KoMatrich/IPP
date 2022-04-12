from common import *
import xml.etree.ElementTree as ET
from vir_machine import *


class Argument:
    def __init__(self, arg: 'ET.Element'):
        self.type = arg.get('type')
        if(self.type is None):
            exit_error(f'Argument "{arg.tag}" has no type', 32)

        self.type = self.type.lower()

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
                    self.content = self.content
                else:
                    exit_error(
                        f'Argument "{arg.tag}" of type "{self.type}" has invalid value "{self.content}"', 32)

            elif(self.type == 'bool'):
                if(self.content in ['true', 'false']):
                    self.content = self.content
                else:
                    exit_error(
                        f'Argument "{arg.tag}" of type "{self.type}" has invalid value "{self.content}"', 32)

            elif(self.type == 'string'):
                self.content = self.content

            elif(self.type == 'type'):
                self.content = self.content.lower()

            elif(self.type == 'label'):
                if(self.content == ''):
                    exit_error(f'Label "{arg.tag}" has no name', 32)
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

    # executes the instruction
    # internally calls the correct method for the opcode
    def run(self, memory: 'Memory'):
        method_name = f'_case_{self.opcode}_run'
        method = getattr(self, method_name)
        if(method is None):
            exit_error(f'{self.opcode} is not valid instruction', 32)
        method(memory)
        memory.inccounter()
        return memory

    # gets the value of an argument from memory
    # or from the argument itself
    def getval(self, memory: 'Memory', arg_index: 'int'):
        if(self.args[arg_index].type == 'var'):
            var = memory.getvalue(
                self.args[arg_index].frame, self.args[arg_index].name)
        else:
            var = self.args[arg_index].content
        return var

    # sets the value of an argument in memory
    # protection against setting a value to constant
    def setval(self, memory: 'Memory', arg_index: 'int', value: 'str'):
        if(self.args[arg_index].type == 'var'):
            memory.setvalue(self.args[arg_index].frame,
                            self.args[arg_index].name, value)
        else:
            exit_error('cannot set value to non-variable argument', 32)

    # sets the arguments of the instruction and sorts them
    def _set_args(self, instruction: ET.Element):
        self.args: 'list[Argument]' = []
        args = sorted(instruction, key=lambda x: x.tag[3:])

        index_list: 'list[str]' = []
        max = len(args)+1
        for arg in args:
            # check if argument is valid
            name = arg.tag[:3].lower()
            if(name != 'arg'):
                exit_error(
                    f'"{self.opcode}" argument "{arg.tag}" does not have a valid tag prefix "{name}"', 32)
            number = arg.tag[3:]
            if(not number.isnumeric()):
                exit_error(
                    f'"{self.opcode}" argument "{arg.tag}" does not have a valid tag index "{number}"', 32)
            if not isInt(number):
                exit_error(
                    f'"{self.opcode}" argument index is not an integer', 32)
            number = int(number)
            if (number < 1) or (max < number):
                exit_error(
                    f'"{self.opcode}" argument "{arg.tag}" tag index "{number}" is not it <1:{max}>', 32)

            # check for duplicates
            if(arg.tag in index_list):
                exit_error('argument has duplicate tag index', 32)
            else:
                index_list.append(arg.tag)

        self.args = [Argument(arg) for arg in args]

    # calls the correct argument check method for the opcode
    def _check_args(self):
        method_name = f'_case_{self.opcode}_check_args'
        check_args = getattr((self), method_name,
                             lambda: exit_error(f'{self.opcode} is not valid instruction (while arg checking)', 32))
        check_args()

    # checks the number of arguments of the instruction
    def _check_number_args(self, arg_count: 'int'):
        if(len(self.args) != arg_count):
            exit_error(
                f'{self.opcode} has {len(self.args)} arguments, but {arg_count} are required', 32)

    ############################################################################
    # Instructions implementations
    ############################################################################
    def _case_move_check_args(self):
        self._check_number_args(2)
        if self.args[0].type != 'var':
            exit_error('Argument 1 is not of type var', 32)
        if not (self.args[1].type in symb):
            exit_error(f'Argument 2 is not of type {symb}', 32)

    def _case_move_run(self, memory: 'Memory'):
        val = self.getval(memory, 1)
        self.setval(memory, 0, val)
    ############################################################################
    def _case_createframe_check_args(self):
        count = len(self.args)
        if(count != 0):
            exit_error(
                f'createframe has no arguments, but recived {count}', 32)

    def _case_createframe_run(self, memory: 'Memory'):
        memory.createframe()
    ############################################################################
    def _case_pushframe_check_args(self):
        self._check_number_args(0)

    def _case_pushframe_run(self, memory: 'Memory'):
        memory.pushframe()
    ############################################################################
    def _case_popframe_check_args(self):
        self._check_number_args(0)

    def _case_popframe_run(self, memory: 'Memory'):
        memory.popframe()
    ############################################################################
    def _case_defvar_check_args(self):
        self._check_number_args(1)
        if self.args[0].type != 'var':
            exit_error('Argument 1 is not of type var', 32)

    def _case_defvar_run(self, memory: 'Memory'):
        memory.defvar(self.args[0].frame, self.args[0].name)
    ############################################################################
    def _case_call_check_args(self):
        self._check_number_args(1)
        if(self.args[0].type != 'label'):
            exit_error('Argument 1 is not type of label', 32)

    def _case_call_run(self, memory: 'Memory'):
        memory.stack.push(str(memory.index))
        memory.jump(self.args[0].content)
    ############################################################################
    def _case_return_check_args(self):
        self._check_number_args(0)

    def _case_return_run(self, memory: 'Memory'):
        index = memory.stack.pop()
        memory.jump(index)
    ############################################################################
    def _case_pushs_check_args(self):
        self._check_number_args(1)
        if(self.args[0].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 1 is not type of"{symb}"', 32)

    def _case_pushs_run(self, memory: 'Memory'):
        val = self.getval(memory, 0)
        memory.stack.push(val)
    ############################################################################
    def _case_pops_check_args(self):
        self._check_number_args(1)
        if(self.args[0].type != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)

    def _case_pops_run(self, memory: 'Memory'):
        val = memory.stack.pop()
        self.setval(memory, 0, val)
    ############################################################################
    def _case_add_check_args(self):
        self._check_number_args(3)
        if(self.args[0].type != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)
        if(self.args[1].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 2 is not type of "{symb}"', 32)
        if(self.args[2].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 2 is not type of "{symb}', 32)

    def _case_add_run(self, memory: 'Memory'):
        var1 = int(self.getval(memory, 2))
        var2 = int(self.getval(memory, 3))
        self.setval(memory, 0, str(var1 + var2))
    ############################################################################
    def _case_sub_check_args(self):
        self._check_number_args(3)
        if(self.args[0].type != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)
        if(self.args[1].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 2 is not type of "{symb}"', 32)
        if(self.args[2].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 2 is not type of "{symb}', 32)

    def _case_sub_run(self, memory: 'Memory'):
        var1 = int(self.getval(memory, 2))
        var2 = int(self.getval(memory, 3))
        self.setval(memory, 0, str(var1 - var2))
    ############################################################################
    def _case_mul_check_args(self):
        self._check_number_args(3)
        if(self.args[0].type != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)
        if(self.args[1].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 2 is not type of "{symb}"', 32)
        if(self.args[2].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 2 is not type of "{symb}', 32)

    def _case_mul_run(self, memory: 'Memory'):
        var1 = int(self.getval(memory, 2))
        var2 = int(self.getval(memory, 3))
        self.setval(memory, 0, str(var1 * var2))
    ############################################################################
    def _case_idiv_check_args(self):
        self._check_number_args(3)
        if(self.args[0].type != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)
        if(self.args[1].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 2 is not type of "{symb}"', 32)
        if(self.args[2].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 2 is not type of "{symb}', 32)

    def _case_idiv_run(self, memory: 'Memory'):
        var1 = int(self.getval(memory, 2))
        var2 = int(self.getval(memory, 3))
        self.setval(memory, 0, str(var1 / var2))
    ############################################################################
    def _case_read_check_args(self):
        self._check_number_args(2)
        if(self.args[0].type != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)
        if(self.args[1].type != 'type'):
            exit_error(f'"{self.opcode}" argument 2 is not type of type', 32)

    def _case_read_run(self, memory: 'Memory'):
        line = memory.getline()
        if(self.args[1].content == 'int'):
            val = str(int(line))
        elif(self.args[1].content == 'string'):
            val = line
        elif(self.args[1].content == 'bool'):
            val = str(bool(line))
        elif(self.args[1].content == 'nil'):
            val = 'nil'
        else:
            exit_error(
                f'"{self.args[1].content}" is not type of {self.args[1].type}', 32)

        # @todo line format check for string
        self.setval(memory, 0, val)
    ############################################################################
    def _case_write_check_args(self):
        self._check_number_args(1)
        if(self.args[0].type not in symb):
            exit_error(f'"{self.opcode}" argument 1 is not type of {symb}', 32)

    def _case_write_run(self, memory: 'Memory'):
        if(self.args[0].type == 'nil'):
            print('nil@nil')
        else:
            print(self.getval(memory, 0), end='')
