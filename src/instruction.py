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

    def _argument_order_check(self, args: 'list[ET.Element]'):
        for arg in args:
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
            max = len(args)+1
            if (number < 1) or (max < number):
                exit_error(
                    f'"{self.opcode}" argument "{arg.tag}" tag index "{number}" is not it <1:{max}>', 32)

    def _xml_argument_order(self, arg: 'ET.Element'):
        return arg.tag[3:]

    def _set_args(self, instruction: ET.Element):
        self.args: 'list[Argument]' = []
        args = sorted(instruction, key=self._xml_argument_order)
        self._argument_order_check(args)
        index_list: 'list[str]' = []

        for arg in args:
            if(arg.tag in index_list):
                exit_error('argument has duplicate tag index', 32)
            else:
                index_list.append(arg.tag)

        self.args = [Argument(arg) for arg in args]

    def _check_args(self):
        method_name = f'_case_{self.opcode}_check_args'
        check_args = getattr((self), method_name,
                             lambda: exit_error(f'{self.opcode} is not valid instruction (while arg checking)', 32))
        check_args()

    def _check_number_args(self, arg_count: 'int'):
        if(len(self.args) != arg_count):
            exit_error(
                f'{self.opcode} has {len(self.args)} arguments, but {arg_count} are required', 32)

    def run(self, memory: 'Memory'):
        method_name = f'_case_{self.opcode}_run'
        method = getattr(self, method_name)
        if(method is None):
            exit_error(f'{self.opcode} is not valid instruction', 32)
        method(memory)
        memory.inccounter()
        return memory

    def _case_move_check_args(self):
        self._check_number_args(2)
        if self.args[0].type != 'var':
            exit_error('Argument 1 is not of type var', 32)
        if not (self.args[1].type in symb):
            exit_error(f'Argument 2 is not of type {symb}', 32)

    def _case_move_run(self, memory: 'Memory'):
        if(self.args[0].type is None):
            exit_error('Argument 1 is not of type var', 99)

        if(self.args[1].type == 'var'):
            val = memory.getvalue(self.args[0].frame, self.args[0].name)
        if(self.args[1].type in symb):
            memory.setvalue(self.args[1].frame, self.args[1].name, val)
        else:
            exit_error(
                f'"{self.opcode}" argument 2 is not of type "{symb}"', 32)

    def _getvalue(self, memory: 'Memory', arg_index: 'int'):
        if(self.args[arg_index].type == 'var'):
            var = memory.getvalue(self.args[1].frame, self.args[1].name)
        else:
            var = self.args[arg_index].content
        return var

    def _case_createframe_check_args(self):
        count = len(self.args)
        if(count != 0):
            exit_error(
                f'createframe has no arguments, but recived {count}', 32)

    def _case_createframe_run(self, memory: 'Memory'):
        memory.createframe()

    def _case_pushframe_check_args(self):
        self._check_number_args(0)

    def _case_pushframe_run(self, memory: 'Memory'):
        memory.pushframe()

    def _case_popframe_check_args(self):
        self._check_number_args(0)

    def _case_popframe_run(self, memory: 'Memory'):
        memory.popframe()

    def _case_defvar_check_args(self):
        self._check_number_args(1)
        if self.args[0].type != 'var':
            exit_error('Argument 1 is not of type var', 32)

    def _case_defvar_run(self, memory: 'Memory'):
        memory.defvar(self.args[0].frame, self.args[0].name)

    def _case_call_check_args(self):
        self._check_number_args(1)
        if(self.args[0].type != 'label'):
            exit_error('Argument 1 is not type of label', 32)

    def _case_call_run(self, memory: 'Memory'):
        memory.stack.push(str(memory.index))
        memory.jump(self.args[0].content)

    def _case_return_check_args(self):
        self._check_number_args(0)

    def _case_return_run(self, memory: 'Memory'):
        index = memory.stack.pop()
        memory.jump(index)

    def _case_pushs_check_args(self):
        self._check_number_args(1)
        if(self.args[0].type not in symb):
            exit_error(
                f'"{self.opcode}" argument 1 is not type of"{symb}"', 32)

    def _case_pushs_run(self, memory: 'Memory'):
        if(self.args[0].type == 'var'):
            val = self._getvalue(memory, 0)
            memory.stack.push(val)
        elif(self.args[0].type in symb):
            memory.stack.push(self.args[0].content)

    def _case_pops_check_args(self):
        self._check_number_args(1)
        if(self.args[0].type != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)

    def _case_pops_run(self, memory: 'Memory'):
        val = memory.stack.pop()
        memory.setvalue(self.args[0].frame, self.args[0].name, val)

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
        var1 = int(self._getvalue(memory, 2))
        var2 = int(self._getvalue(memory, 3))
        memory.setvalue(self.args[0].frame,
                        self.args[0].name, str(var1 + var2))

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
        var1 = int(self._getvalue(memory, 2))
        var2 = int(self._getvalue(memory, 3))
        memory.setvalue(self.args[0].frame,
                        self.args[0].name, str(var1 - var2))

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
        var1 = int(self._getvalue(memory, 2))
        var2 = int(self._getvalue(memory, 3))
        memory.setvalue(self.args[0].frame,
                        self.args[0].name, str(var1 * var2))

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
        var1 = int(self._getvalue(memory, 2))
        var2 = int(self._getvalue(memory, 3))
        memory.setvalue(self.args[0].frame,
                        self.args[0].name, str(var1 / var2))

    def _case_read_check_args(self):
        self._check_number_args(2)
        if(self.args[0].type != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)
        if(self.args[1].type != 'type'):
            exit_error(f'"{self.opcode}" argument 2 is not type of type', 32)

    def _case_read_run(self, memory: 'Memory'):
        line = memory.getline()
        #@todo line format check
        memory.setvalue(self.args[0].frame, self.args[0].name, line)

    def _case_write_check_args(self):
        self._check_number_args(1)
        if(self.args[0].type not in symb):
            exit_error(f'"{self.opcode}" argument 1 is not type of {symb}', 32)

    def _case_write_run(self, memory: 'Memory'):
        if(self.args[0].type == 'nil'):
            print('nil@nil')
        else:
            print(self._getvalue(memory, 0), end='')
