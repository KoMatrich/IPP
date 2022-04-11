from typing import TextIO
from common import exit_error, isInt

var_type = ['int', 'bool', 'string', 'nil']


class variables:
    def __init__(self, name: str):
        self._name = name

    def set(self, type: 'str', value: 'str'):
        self._type = type
        self._value = value

    def __str__(self):
        return f'{self._type} {self._name}={self._value}'

    def __eq__(self, __o: object) -> bool:
        return __o.__getattribute__('type') == self._type and __o.__getattribute__('name') == self._name and __o.__getattribute__('value') == self.value

    def define(self, type: 'str', value: 'str'):
        if(self.type is not None):
            exit_error(f'Variable "{self._name}" is already defined', 52)
        if(type not in var_type):
            exit_error(
                f'Variable "{self._name}" has invalid type "{type}"', 53)
        self.type = type
        self.value = value

    def setvalue(self, value: 'str'):
        if(self.type is None):
            exit_error(f'Variable "{self._name}" is not defined', 52)
        if(self.type == 'int' and not isInt(value)):
            exit_error(
                f'Variable "{self._name}" is of type "{self.type}" and cannot be set to "{value}"', 53)
        if(self.type == 'bool' and value not in ['true', 'false']):
            exit_error(
                f'Variable "{self._name}" is of type "{self.type}" and cannot be set to "{value}"', 53)
        if(self.type == 'nil' and value != 'nil'):
            exit_error(
                f'Variable "{self._name}" is of type "{self.type}" and cannot be set to "{value}"', 53)
        self.value = value

    def getname(self):
        return self._name

    def getvalue(self):
        if(self.type is None):
            exit_error(
                f'Using variable that "{self._name}" is not defined', 52)
        return self._value

    def gettype(self):
        if(self._type is None):
            exit_error(
                f'Using variable that "{self._name}" is not defined', 52)
        return self._type


class Frame:
    def __init__(self):
        self.variables: 'list[variables]' = []
        self.lables: 'list[str]' = []


class Stack:
    def __init__(self):
        self._stack: 'list[Frame]' = []

    def push(self, value: Frame):
        self._stack.append(value)

    def pop(self):
        if(len(self._stack) > 0):
            return self._stack.pop()
        else:
            exit_error('Stack is empty', 55)

    def top(self):
        if(len(self._stack) == 0):
            exit_error('Stack is empty', 55)
        return self._stack[-1]

    def create_frame(self):
        frame = Frame()
        self.push(frame)


class Memory:
    def __init__(self, input: 'TextIO'):
        self.index: 'int' = 0

        self.GF: 'Frame' = Frame()
        self.TF: 'Frame|None' = None
        self.LF: 'Stack' = Stack()

        self._input: 'TextIO' = input

    def get_line(self):
        self._input.readline()
