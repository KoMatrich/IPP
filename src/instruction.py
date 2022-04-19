from common import *
import re
import xml.etree.ElementTree as ET
from virtual_mc import *

# This file contains the code for the interpretation of the instructions

class Instruction(object):
    class Argument:
        def __init__(self, arg: 'ET.Element'):
            self._type = arg.get('type') or ''
            if(self._type is ''):
                exit_error(f'Argument "{arg.tag}" has no type', 32)

            self._type = self._type.lower()

            if(arg.text is None):
                if(self._type == 'string'):
                    arg.text = ''
                else:
                    exit_error(f'Argument "{arg.tag}" has no value', 32)

            if(self._type == 'var'):
                self._frame = arg.text[:2]
                if(self._frame not in ['GF', 'LF', 'TF']):
                    exit_error(
                        f'Argument "{arg.tag}" has invalid frame "{self._frame}"', 32)

                self._name = arg.text[3:]

                if(self._name == ''):
                    exit_error(f'Argument "{arg.tag}" has no name', 32)
            else:
                self._content = arg.text

                if(self._type == 'int'):
                    if isInt(self._content):
                        self._content = self._content
                    else:
                        exit_error(
                            f'Argument "{arg.tag}" of type "{self._type}" has invalid value "{self._content}"', 32)

                elif(self._type == 'bool'):
                    if(self._content in ['true', 'false']):
                        self._content = self._content
                    else:
                        exit_error(
                            f'Argument "{arg.tag}" of type "{self._type}" has invalid value "{self._content}"', 32)

                elif(self._type == 'string'):
                    self._content = self._content

                elif(self._type == 'type'):
                    self._content = self._content.lower()
                    if(self._content not in VAR_T):
                        exit_error(
                            f'Argument "{arg.tag}" type has invalid value "{self._content}"', 32)

                elif(self._type == 'label'):
                    if(self._content == ''):
                        exit_error(f'Label "{arg.tag}" has no name', 32)
                elif(self._type == 'nil'):
                    if(self._content != 'nil'):
                        exit_error(
                            f'Argument "{arg.tag}" type nil can have only value of nil', 32)
                else:
                    exit_error(
                        f'Argument "{arg.tag}" has invalid type "{self._type}"', 32)

        # returns type of
        def gettype(self) -> str:
            return self._type

        # returns tuple[frame,name] of var
        def getvar(self):
            return self._frame, self._name

        # returns content of constant
        def getcontent(self):
            if(self._content is None):
                exit_error('Use of variable as constant value', 99)
            return self._content


    def __init__(self, instruction: ET.Element):
        self.opcode = instruction.get('opcode')
        if(self.opcode is None):
            exit_error('opcode is missing', 32)
        self.opcode = self.opcode.lower()
        self.args: 'list[Instruction.Argument]' = []
        self._set_args(instruction)
        self._check_args()

    # executes the instruction
    # internally calls the correct method for the opcode
    def run(self, memory: 'Memory'):
        method_name = f'_xc_run_{self.opcode}'
        method = getattr(self, method_name)
        if(method is None):
            exit_error(f'{self.opcode} is not valid instruction', 32)
        method(memory)

    # sets the arguments of the instruction and sorts them
    def _set_args(self, instruction: ET.Element):
        args = sorted(instruction, key=lambda x: x.tag[3:])

        index_list: 'list[str]' = []
        max = len(args)
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
                    f'"{self.opcode}" argument "{arg.tag}" tag index "{number}" is not in <1:{max}> or some arguments are missing', 32)

            # check for duplicates
            if(arg.tag in index_list):
                exit_error('argument has duplicate tag index', 32)
            else:
                index_list.append(arg.tag)

        self.args = [Instruction.Argument(arg) for arg in args]

    # inteligently gets value from arg or memory
    def _getvar(self, memory: 'Memory', arg_index: 'int') -> 'tuple[str, str]':
        type = self.args[arg_index].gettype()
        if(type == 'var'):
            # memory variable
            frame, name = self.args[arg_index].getvar()
            # gets values from memory
            type, var = memory.getvar(frame, name)
        else:
            # constant value
            var = self.args[arg_index].getcontent()
            if(type is None):
                exit_error('Invalid argument type', 32)
            if(type == 'string'):
                # convert all escape sequences in string to chars
                while(1):
                    escapes = re.search(r'\\\d\d\d', var)
                    if(escapes):
                        # found escape sequence
                        x = escapes.start()+1
                        y = escapes.end()
                        # int(var[x:y]) extracts the character number from the escape sequence
                        # then converts it to the corresponding character
                        try:
                            var = re.sub(r'\\\d\d\d', chr(
                                int(var[x:y])), var, 1)
                        except ValueError:
                            exit_error('Invalid escape sequence', 32)
                    else:
                        # no escape sequence
                        break
        return type, var

    # sets the value of an argument in memory
    # protection against setting a value to constant
    def _setval(self, memory: 'Memory', arg_index: 'int', type: 'str', value: 'str'):
        if(self.args[arg_index].gettype() == 'var'):
            frame, name = self.args[arg_index].getvar()
            memory.setvar(frame, name, value, type)
        else:
            exit_error('cannot set value to non-variable argument', 32)

    def _isdefined(self, memory: 'Memory', arg_index: 'int') -> 'bool':
        if(self.args[arg_index].gettype() == 'var'):
            frame, name = self.args[arg_index].getvar()
            return memory.isdefined(frame, name)
        else:
            return False

    def _isconst(self, arg_index: 'int') -> 'bool':
        if(self.args[arg_index].gettype() != 'var'):
            return True
        else:
            return False

    # calls the correct argument check method for the opcode
    # static check
    def _check_args(self):
        method_name = f'_xc_check_args_{self.opcode}'
        check_args = getattr((self), method_name,
                             lambda: exit_error(f'{self.opcode} is not valid instruction (while arg checking)', 32))
        check_args()

    # checks the number of arguments of the instruction
    def _check_number_args(self, arg_count: 'int'):
        if(len(self.args) != arg_count):
            exit_error(
                f'{self.opcode} has {len(self.args)} arguments, but {arg_count} are required', 32)

    def _check_type(self, arg_index: 'int', type: 'str'):
        if self.args[arg_index].gettype() != type:
            exit_error(
                f'Instruction {self.opcode} arg{arg_index} is not of type "{type}"', 53)

    def _check_types(self, arg_index: 'int', types: 'list[str]'):
        if not (self.args[arg_index].gettype() in types):
            exit_error(
                f'Instruction {self.opcode} arg{arg_index} is not of type of {SYMB}', 53)

    ############################################################################
    # Instructions implementations
    ############################################################################
    def _xc_check_args_move(self):
        self._check_number_args(2)
        self._check_type(0, 'var')
        self._check_types(1, SYMB)

    def _xc_run_move(self, memory: 'Memory'):
        type, var = self._getvar(memory, 1)
        self._setval(memory, 0, type, var)
    ############################################################################

    def _xc_check_args_createframe(self):
        self._check_number_args(0)

    def _xc_run_createframe(self, memory: 'Memory'):
        memory.createframe()
    ############################################################################

    def _xc_check_args_pushframe(self):
        self._check_number_args(0)

    def _xc_run_pushframe(self, memory: 'Memory'):
        memory.pushframe()
    ############################################################################

    def _xc_check_args_popframe(self):
        self._check_number_args(0)

    def _xc_run_popframe(self, memory: 'Memory'):
        memory.popframe()
    ############################################################################

    def _xc_check_args_defvar(self):
        self._check_number_args(1)
        self._check_type(0, 'var')

    def _xc_run_defvar(self, memory: 'Memory'):
        frame, name = self.args[0].getvar()
        memory.defvar(frame, name)
    ############################################################################

    def _xc_check_args_call(self):
        self._check_number_args(1)
        self._check_type(0, 'label')

    def _xc_run_call(self, memory: 'Memory'):
        memory.return_push(memory.pc)
        memory.jump(self.args[0].getcontent())
    ############################################################################

    def _xc_check_args_return(self):
        self._check_number_args(0)

    def _xc_run_return(self, memory: 'Memory'):
        index = memory.return_pop()
        memory.pc = index
    ############################################################################

    def _xc_check_args_pushs(self):
        self._check_number_args(1)
        self._check_types(0, SYMB)

    def _xc_run_pushs(self, memory: 'Memory'):
        type, var = self._getvar(memory, 0)
        memory.data_push(type, var)
    ############################################################################

    def _xc_check_args_pops(self):
        self._check_number_args(1)
        self._check_type(0, 'var')

    def _xc_run_pops(self, memory: 'Memory'):
        type, val = memory.data_pop()
        self._setval(memory, 0, type, val)
    ############################################################################

    ############################################################################
    # checks the types of the arguments for aritmetic instructions
    def _check_arithmetic_args(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, SYMB_INT)
        self._check_types(2, SYMB_INT)
    ############################################################################

    def _xc_check_args_add(self):
        self._check_arithmetic_args()

    def _xc_run_add(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 53)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 3 is not type of int', 53)
        self._setval(memory, 0, 'int', str(int(var1) + int(var2)))
    ############################################################################

    def _xc_check_args_sub(self):
        self._check_arithmetic_args()

    def _xc_run_sub(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 53)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 3 is not type of int', 53)
        self._setval(memory, 0, 'int', str(int(var1) - int(var2)))
    ############################################################################

    def _xc_check_args_mul(self):
        self._check_arithmetic_args()

    def _xc_run_mul(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 53)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 3 is not type of int', 53)
        self._setval(memory, 0, 'int', str(int(var1) * int(var2)))
    ############################################################################

    def _xc_check_args_idiv(self):
        self._check_arithmetic_args()

    def _xc_run_idiv(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 53)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 3 is not type of int', 53)
        if(int(var2) == 0):
            exit_error('Division by zero', 57)
        self._setval(memory, 0, 'int', str(int(int(var1) / int(var2))))
    ############################################################################

    ############################################################################
    # checks the types of the arguments for comparison instructions
    def _check_compare_args(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, SYMB)
        self._check_types(2, SYMB)
    ############################################################################

    def _xc_check_args_lt(self):
        self._check_compare_args()

    def _xc_run_lt(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != type2):
            exit_error('Argument 1 and 2 are not of same type', 32)
        if(type1 == 'int'):
            self._setval(memory, 0, 'bool', str(int(var1) < int(var2)).lower())
        else:
            self._setval(memory, 0, 'bool', str(var1 < var2).lower())
    ############################################################################

    def _xc_check_args_gt(self):
        self._check_compare_args()

    def _xc_run_gt(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != type2):
            exit_error('Argument 1 and 2 are not of same type', 32)
        if(type1 == 'int'):
            self._setval(memory, 0, 'bool', str(int(var1) > int(var2)).lower())
        else:
            self._setval(memory, 0, 'bool', str(var1 > var2).lower())
    ############################################################################

    def _xc_check_args_eq(self):
        self._check_compare_args()

    def _xc_run_eq(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != type2):
            if(type1 == 'nil' or type2 == 'nil'):
                self._setval(memory, 0, 'bool', 'false')
            else:
                exit_error('Argument 1 and 2 are not of same type', 32)
        if(var1 == var2):
            self._setval(memory, 0, 'bool', 'true')
        else:
            self._setval(memory, 0, 'bool', 'false')
    ############################################################################

    ############################################################################
    # checks the types of the arguments for boolean instructions
    def _check_bool_args(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, SYMB_BOOL)
        self._check_types(2, SYMB_BOOL)
    ############################################################################

    def _xc_check_args_and(self):
        self._check_bool_args()

    def _xc_run_and(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != 'bool'):
            exit_error(f'"{self.opcode}" argument 1 is not type of bool', 32)
        if(type2 != 'bool'):
            exit_error(f'"{self.opcode}" argument 2 is not type of bool', 32)
        if(var1 == 'true' and var2 == 'true'):
            self._setval(memory, 0, 'bool', 'true')
        else:
            self._setval(memory, 0, 'bool', 'false')
    ############################################################################

    def _xc_check_args_or(self):
        self._check_bool_args()

    def _xc_run_or(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != 'bool'):
            exit_error(f'"{self.opcode}" argument 1 is not type of bool', 32)
        if(type2 != 'bool'):
            exit_error(f'"{self.opcode}" argument 2 is not type of bool', 32)
        if(var1 == 'true' or var2 == 'true'):
            self._setval(memory, 0, 'bool', 'true')
        else:
            self._setval(memory, 0, 'bool', 'false')
    ############################################################################

    def _xc_check_args_not(self):
        self._check_number_args(2)
        self._check_type(0, 'var')
        self._check_types(1, SYMB_BOOL)

    def _xc_run_not(self, memory: 'Memory'):
        type, var = self._getvar(memory, 1)
        if(type != 'bool'):
            exit_error(f'"{self.opcode}" argument 1 is not type of bool', 32)
        if(var == 'true'):
            self._setval(memory, 0, 'bool', 'false')
        else:
            self._setval(memory, 0, 'bool', 'true')
    ############################################################################

    ############################################################################
    def _xc_check_args_int2char(self):
        self._check_number_args(2)
        self._check_type(0, 'var')
        self._check_types(1, SYMB)

    def _xc_run_int2char(self, memory: 'Memory'):
        type, var = self._getvar(memory, 1)
        if(type != 'int'):
            exit_error(f'"{self.opcode}" argument 1 is not type of int', 32)
        try:
            out = chr(int(var))
        except(ValueError):
            exit_error(
                f'"{self.opcode}" argument 1 cant be converted to char', 58)
        self._setval(memory, 0, 'string', out)

    def _xc_check_args_stri2int(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, SYMB)
        self._check_types(2, SYMB)

    def _xc_run_stri2int(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type1 != 'string'):
            exit_error(f'"{self.opcode}" argument 1 is not type of str', 32)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 32)

        try:
            out = str(ord(var1[int(var2)]))
        except(IndexError):
            exit_error('"str2int" argument 2 is out of range', 58)

        self._setval(memory, 0, 'int', out)
    ############################################################################

    ############################################################################
    def _xc_check_args_read(self):
        self._check_number_args(2)
        if(self.args[0].gettype() != 'var'):
            exit_error(f'"{self.opcode}" argument 1 is not type of var', 32)
        if(self.args[1].gettype() != 'type'):
            exit_error(f'"{self.opcode}" argument 2 is not type of type', 32)

    def _xc_run_read(self, memory: 'Memory'):
        line = memory.getinput()
        input_type = self.args[1].getcontent()

        try:
            if(memory.endoffile()):
                raise ValueError

            if(input_type == 'int'):
                val = str(int(line))
            elif(input_type == 'string'):
                val = line
            elif(input_type == 'bool'):
                val = str(line.lower() == 'true').lower()
            else:
                exit_error(
                    f'"type" defined in argument 2 is not valid type', 32)

            self._setval(memory, 0, input_type, val)
        except(ValueError):
            self._setval(memory, 0, 'nil', 'nil')
    ############################################################################

    def _xc_check_args_write(self):
        self._check_number_args(1)
        if(self.args[0].gettype() not in SYMB):
            exit_error(f'"{self.opcode}" argument 1 is not type of {SYMB}', 32)

    def _xc_run_write(self, memory: 'Memory'):
        type, var = self._getvar(memory, 0)
        if(type == 'nil'):
            print('', end='')
        else:
            print(var, end='')

    ############################################################################

    ############################################################################
    def _xc_check_args_concat(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, SYMB_STRING)
        self._check_types(2, SYMB_STRING)

    def _xc_run_concat(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)

        if(type1 != 'string'):
            exit_error(f'"{self.opcode}" argument 1 is not type of str', 32)
        if(type2 != 'string'):
            exit_error(f'"{self.opcode}" argument 2 is not type of str', 32)

        self._setval(memory, 0, 'string', var1 + var2)
    ############################################################################

    def _xc_check_args_strlen(self):
        self._check_number_args(2)
        self._check_type(0, 'var')
        self._check_types(1, SYMB_STRING)

    def _xc_run_strlen(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)

        if(type1 != 'string'):
            exit_error(f'"{self.opcode}" argument 1 is not type of str', 32)

        self._setval(memory, 0, 'int', str(len(var1)))
    ############################################################################

    def _xc_check_args_getchar(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, SYMB_STRING)
        self._check_types(2, SYMB_INT)

    def _xc_run_getchar(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)

        if(type1 != 'string'):
            exit_error(f'"{self.opcode}" argument 1 is not type of str', 32)
        if(type2 != 'int'):
            exit_error(f'"{self.opcode}" argument 2 is not type of int', 32)

        try:
            self._setval(memory, 0, 'string', var1[int(var2)])
        except IndexError:
            exit_error('"getchar" argument 2 is out of range', 58)
    ############################################################################

    def _xc_check_args_setchar(self):
        self._check_number_args(3)
        self._check_type(0, 'var')
        self._check_types(1, SYMB_INT)
        self._check_types(2, SYMB_STRING)

    def _xc_run_setchar(self, memory: 'Memory'):
        type, var = self._getvar(memory, 0)
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)
        if(type != 'string'):
            exit_error(f'"{self.opcode}" argument 0 is not type of str', 32)
        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 1 is not type of int', 32)
        if(type2 != 'string'):
            exit_error(f'"{self.opcode}" argument 2 is not type of str', 32)

        # i is index of char in string to change
        i = -1
        try:
            i = int(var1)
        except ValueError:
            exit_error(f'"{self.opcode}" argument 1 is not type of int', 32)

        char = var2[0]

        # try to change char in string
        try:
            var = var[:i]+char+var[i+1:]
        except IndexError:
            exit_error(f'"{self.opcode}" argument 1 is out of range', 58)

        self._setval(memory, 0, 'string', var)
    ############################################################################

    def _xc_check_args_type(self):
        self._check_number_args(2)
        self._check_type(0, 'var')
        self._check_types(1, SYMB)

    def _xc_run_type(self, memory: 'Memory'):
        if(self.args[1].gettype() == 'var'):
            frame, name = self.args[1].getvar()
            if(memory.isdefined(frame, name)):
                type, _ = self._getvar(memory, 1)
                self._setval(memory, 0, 'string', type)
            else:
                self._setval(memory, 0, 'string', '')
        else:
            type, _ = self._getvar(memory, 1)
            self._setval(memory, 0, 'string', type)
    ############################################################################

    ############################################################################
    def _xc_check_args_label(self):
        self._check_number_args(1)
        self._check_type(0, 'label')

    def _xc_run_label(self, memory: 'Memory'):
        memory.setlabel(self.args[0].getcontent(), memory.pc)
    ############################################################################

    def _xc_check_args_jump(self):
        self._check_number_args(1)
        self._check_type(0, 'label')

    def _xc_run_jump(self, memory: 'Memory'):
        memory.jump(self.args[0].getcontent())
    ############################################################################

    def _xc_check_args_jumpifeq(self):
        self._check_number_args(3)
        self._check_type(0, 'label')
        self._check_types(1, SYMB)
        self._check_types(2, SYMB)

    def _xc_run_jumpifeq(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)

        if(type1 != type2):
            if(type1 != 'nil') and (type2 != 'nil'):
                exit_error(
                    f'"{self.opcode}" argument 1 and 2 are not same types "{type1}" != "{type2}"', 32)
        else:
            if(var1 == var2):
                _, var = self._getvar(memory, 0)
                memory.jump(var)
    ############################################################################

    def _xc_check_args_jumpifneq(self):
        self._check_number_args(3)
        self._check_type(0, 'label')
        self._check_types(1, SYMB)
        self._check_types(2, SYMB)

    def _xc_run_jumpifneq(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 1)
        type2, var2 = self._getvar(memory, 2)

        if(type1 != type2):
            if(type1 != 'nil') and (type2 != 'nil'):
                exit_error(
                    f'"{self.opcode}" argument 1 and 2 are not same types "{type1}" != "{type2}"', 32)
        else:
            if(var1 == var2):
                return

        _, var = self._getvar(memory, 0)
        memory.jump(var)
    ############################################################################

    def _xc_check_args_exit(self):
        self._check_number_args(1)
        self._check_types(0, SYMB_INT)

    def _xc_run_exit(self, memory: 'Memory'):
        type1, var1 = self._getvar(memory, 0)

        if(type1 != 'int'):
            exit_error(f'"{self.opcode}" argument 1 is not type of int', 32)

        rc = int(var1)
        if((0 <= rc) and (rc <= 49)):
            exit(rc)
    ###############################################################################

    ###############################################################################
    def _xc_check_args_dprint(self):
        self._check_number_args(1)
        self._check_types(0, SYMB)

    def _xc_run_dprint(self, memory: 'Memory'):
        _, val = self._getvar(memory, 0)
        eprint(val)
    ###############################################################################

    def _xc_check_args_break(self):
        self._check_number_args(0)

    def _xc_run_break(self, memory: 'Memory'):
        eprint(memory)
    ###############################################################################


if __name__ == "__main__":
    exit_error('This file is not meant to be run directly', 99)
