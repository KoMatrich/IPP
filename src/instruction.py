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
                if(self.content not in var_types):
                    exit_error(
                        f'Argument "{arg.tag}" type has invalid value "{self.content}"', 32)

            elif(self.type == 'label'):
                if(self.content == ''):
                    exit_error(f'Label "{arg.tag}" has no name', 32)
            elif(self.type == 'nil'):
                if(self.content != 'nil'):
                    exit_error(
                        f'Argument "{arg.tag}" type nil can have only value of nil', 32)
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
    def getvar(self, memory: 'Memory', arg_index: 'int') -> 'tuple[str, str]':
        if(self.args[arg_index].type == 'var'):
            type, var = memory.getvar(
                self.args[arg_index].frame, self.args[arg_index].name)
        else:
            var = self.args[arg_index].content
            type = self.args[arg_index].type
            if(type is None):
                exit_error('Invalid argument type', 32)

        return type, var

    # sets the value of an argument in memory
    # protection against setting a value to constant
    def setval(self, memory: 'Memory', arg_index: 'int', type: 'str', value: 'str'):
        if(self.args[arg_index].type == 'var'):
            memory.setvalue(self.args[arg_index].frame,
                            self.args[arg_index].name, value, type)
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

    def _check_type(self, arg_index: 'int', type: 'str'):
        if self.args[arg_index].type != type:
            exit_error(f'Instruction {self.opcode} arg{arg_index} is not of type "{type}"', 32)

    def _check_types(self, arg_index:'int', types: 'list[str]'):
        if not (self.args[arg_index].type in types):
            exit_error(f'Instruction {self.opcode} arg{arg_index} is not of type of {symb}', 32)

    ############################################################################
    # Instructions implementations
    ############################################################################
    def _case_move_check_args(self):
        self._check_number_args(2)
        self._check_type(0, 'var')
        self._check_types(1, symb)

    def _case_move_run(self, memory: 'Memory'):
        type, var = self.getvar(memory, 1)
        self.setval(memory, 0, type, var)
    ############################################################################
    def _case_createframe_check_args(self):
        self._check_number_args(0)

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
        self._check_type(0, 'var')

    def _case_defvar_run(self, memory: 'Memory'):
        memory.defvar(self.args[0].frame, self.args[0].name)
    ############################################################################
    def _case_call_check_args(self):
        self._check_number_args(1)
        self._check_type(0, 'label')

    def _case_call_run(self, memory: 'Memory'):
        memory.return_stack.push(memory.index)
        memory.jump(self.args[0].content)
    ############################################################################
    def _case_return_check_args(self):
        self._check_number_args(0)

    def _case_return_run(self, memory: 'Memory'):
        index = memory.return_stack.pop()
        memory.index = index
    ############################################################################
    def _case_pushs_check_args(self):
        self._check_number_args(1)
        self._check_types(0, symb)

    def _case_pushs_run(self, memory: 'Memory'):
        memory.stack.push(self.getvar(memory, 0))
    ############################################################################
    def _case_pops_check_args(self):
        self._check_number_args(1)
        self._check_type(0, 'var')

    def _case_pops_run(self, memory: 'Memory'):
        type,val = memory.stack.pop()
        self.setval(memory, 0, type, val)
    ############################################################################
    # checks the types of the arguments for aritmetic instructions
    def _check_arithmetic_args(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, numeric_types)
        self._check_types(2, numeric_types)
    ############################################################################

    def _case_add_check_args(self):
        self._check_arithmetic_args()

    def _case_add_run(self, memory: 'Memory'):
        type1,var1 = self.getvar(memory, 2)
        type2,var2 = self.getvar(memory, 3)
        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 32)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 3 is not type of int', 32)
        self.setval(memory, 0, 'int' ,str(int(var1) + int(var2)))
    ############################################################################
    def _case_sub_check_args(self):
        self._check_arithmetic_args()

    def _case_sub_run(self, memory: 'Memory'):
        type1,var1 = self.getvar(memory, 2)
        type2,var2 = self.getvar(memory, 3)
        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 32)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 3 is not type of int', 32)
        self.setval(memory, 0, 'int' ,str(int(var1) - int(var2)))
    ############################################################################

    def _case_mul_check_args(self):
        self._check_arithmetic_args()

    def _case_mul_run(self, memory: 'Memory'):
        type1,var1 = self.getvar(memory, 2)
        type2,var2 = self.getvar(memory, 3)
        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 32)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 3 is not type of int', 32)
        self.setval(memory, 0, 'int' ,str(int(var1) * int(var2)))
    ############################################################################

    def _case_idiv_check_args(self):
        self._check_arithmetic_args()

    def _case_idiv_run(self, memory: 'Memory'):
        type1,var1 = self.getvar(memory, 2)
        type2,var2 = self.getvar(memory, 3)
        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 32)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 3 is not type of int', 32)
        if(int(var2) == 0):
            exit_error('Division by zero', 32)
        self.setval(memory, 0, 'int' ,str(int(var1) / int(var2)))
    ############################################################################
    # checks the types of the arguments for comparison instructions
    def _check_compare_args(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, symb)
        self._check_types(2, symb)
    ############################################################################
    def _case_lt_check_args(self):
        self._check_compare_args()

    def _case_lt_run(self, memory: 'Memory'):
        type1,var1 = self.getvar(memory, 1)
        type2,var2 = self.getvar(memory, 2)
        if(type1 != type2):
            exit_error('Argument 1 and 2 are not of same type', 32)
        if(var1 < var2):
            self.setval(memory, 0, 'bool','true')
        else:
            self.setval(memory, 0, 'bool','false')
    ############################################################################

    def _case_gt_check_args(self):
        self._check_compare_args()

    def _case_gt_run(self, memory: 'Memory'):
        type1, var1 = self.getvar(memory, 1)
        type2, var2 = self.getvar(memory, 2)
        if(type1 != type2):
            exit_error('Argument 1 and 2 are not of same type', 32)
        if(var1 > var2):
            self.setval(memory, 0, 'bool', 'true')
        else:
            self.setval(memory, 0, 'bool', 'false')
    ############################################################################

    def _case_eq_check_args(self):
        self._check_compare_args()

    def _case_eq_run(self, memory: 'Memory'):
        type1, var1 = self.getvar(memory, 1)
        type2, var2 = self.getvar(memory, 2)
        if(type1 != type2):
            exit_error('Argument 1 and 2 are not of same type', 32)
        if(var1 == var2):
            self.setval(memory, 0, 'bool', 'true')
        else:
            self.setval(memory, 0, 'bool', 'false')
    ############################################################################
    # checks the types of the arguments for boolean instructions
    def _check_bool_args(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, symb)
        self._check_types(2, symb)
    ############################################################################
    def _case_and_check_args(self):
        self._check_bool_args()

    ############################################################################
    def _case_read_check_args(self):
        self._check_number_args(2)
        if(self.args[0].type != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)
        if(self.args[1].type != 'type'):
            exit_error(f'"{self.opcode}" argument 2 is not type of type', 32)

    def _case_read_run(self, memory: 'Memory'):
        line = memory.getline()
        type = self.args[1].content
        if(type == 'int'):
            val = str(int(line))
        elif(type == 'string'):
            val = line
        elif(type == 'bool'):
            val = str(bool(line)).lower()
        elif(type == 'nil'):
            val = 'nil'
        else:
            exit_error(f'"type" defined in argument 2 is not valid type', 32)

        # @todo line format check for string
        self.setval(memory, 0, type ,val)
    ############################################################################
    def _case_write_check_args(self):
        self._check_number_args(1)
        if(self.args[0].type not in symb):
            exit_error(f'"{self.opcode}" argument 1 is not type of {symb}', 32)

    def _case_write_run(self, memory: 'Memory'):
        if(self.args[0].type == 'nil'):
            print('nil@nil')
        else:
            _,var = self.getvar(memory, 0)
            print(var, end='')
    ############################################################################