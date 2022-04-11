from typing import Generic, TextIO, TypeVar
from common import *


class variables:
    def __init__(self, name: str):
        self._name = name
        sd

    def set(self, type: 'str', value: 'str'):
        self._type = type
        self._value = value

    def __str__(self):
        return f'{self._type} {self._name}={self._value}'

    def define(self, type: 'str', value: 'str'):
        if(self.type is not None):
            exit_error(f'Variable "{self._name}" is already defined', 52)
        if(type not in var_types):
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
        if(self._value is None):
            exit_error('Using variable that is not defined', 52)
        return self._value

    def gettype(self):
        if(self._type is None):
            exit_error(
                f'Using variable that "{self._name}" is not defined', 52)
        return self._type


class Frame:
    def __init__(self):
        self.variables: 'list[variables]' = []

    def __str__(self) -> str:
        return '\n'.join([str(var) for var in self.variables])

    def createvar(self, name: str):
        if(name in self.variables):
            exit_error(f'Variable "{name}" is already exists', 52)
        else:
            self.variables.append(variables(name))
            return self.variables[-1]

    def getvar(self, name: str):
        if(name in self.variables):
            return self.variables[name]
        else:
            exit_error(f'Variable "{name}" is not defined', 52)


T = TypeVar('T')


class Stack(Generic[T]):
    def __init__(self):
        self._stack: 'list[T]' = []

    def push(self, value: T):
        self._stack.append(value)

    def pop(self) -> T:
        if(len(self._stack) > 0):
            return self._stack.pop()
        else:
            exit_error('Stack is empty', 55)

    def top(self) -> T:
        if(len(self._stack) == 0):
            exit_error('Stack is empty', 55)
        return self._stack[-1]

    def __str__(self) -> str:
        if(len(self._stack) != 0):
            return str(self.top())
        return ''


class clabel:
    def __init__(self, name: str, pos: int):
        self._name = name
        self._pos = pos

    def __eq__(self, __o: object):
        return __o.__getattribute__('name') == self._name

    def __str__(self):
        return f'{self._name}:{self._pos}'

    def getpos(self):
        return self._pos


class Memory:
    def __init__(self, input: 'TextIO'):
        self.index: 'int' = 0

        self.gf: 'Frame' = Frame()
        self.tf: 'Frame|None' = None
        self.lf: 'Stack[Frame]' = Stack()
        self.stack: 'Stack[str]' = Stack()

        self.labels: 'list[clabel]' = []

        self._input: 'TextIO' = input

    def __str__(self) -> str:
        lines = f'index:{self.index}\n'
        lines += f'gf:\n{self.gf}'
        lines += f'tf:\n{self.tf}'
        lines += f'lf:\n{self.lf}'
        lines += f'stack:\n{self.stack}'
        lines += f'labels:\n{self.labels}'
        return lines

    def getline(self):
        return self._input.readline()

    def defvar(self, frame: 'str', name: 'str'):
        if(frame == 'GF'):
            self.gf.createvar(name)
        elif(frame == 'TF'):
            if(self.tf is None):
                exit_error(f'Frame "TF" is not defined', 55)
            self.tf.createvar(name)
        elif(frame == 'LF'):
            self.lf.top().createvar(name)
        else:
            exit_error(f'Invalid frame "{frame}"', 99)
        pass

    def getvalue(self, frame: 'str', name: 'str'):
        if(frame == 'GF'):
            var = self.gf.getvar(name)
        elif(frame == 'TF'):
            if (self.tf is None):
                exit_error(f'Frame "TF" is not defined', 52)
            var = self.tf.getvar(name)
        elif(frame == 'LF'):
            var = self.lf.top().getvar(name)
        else:
            exit_error(f'Invalid frame "{frame}"', 52)

        if(var.type != ""):
            exit_error('Variable is not defined', 52)
        return var.getvalue()

    def setvalue(self, frame: 'str', name: 'str', value: 'str'):
        if(frame == 'GF'):
            var = self.gf.getvar(name)
        elif(frame == 'TF'):
            if (self.tf is None):
                exit_error(f'Frame "TF" is not defined', 52)
            var = self.tf.getvar(name)
        elif(frame == 'LF'):
            var = self.lf.top().getvar(name)
        else:
            exit_error(f'Invalid frame "{frame}"', 52)

        if(var.type != ""):
            exit_error('Variable is not defined', 52)
        var.setvalue(value)

    def createframe(self):
        self.tf = Frame()

    def pushframe(self):
        if(self.tf is None):
            exit_error(f'Frame "TF" is not defined', 55)
        self.lf.push(self.tf)

    def popframe(self):
        self.tf = self.lf.pop()

    def inccounter(self):
        self.index += 1

    def _setlabel(self, name: str, pos: int):
        if(name in self.labels):
            exit_error(f'Label "{name}" was already defined', 52)
        self.labels.append(clabel(name, pos))

    def _getlabel(self, name: str):
        if(name in self.labels):
            return self.labels[name]
        else:
            exit_error(f'Label "{name}" was not defined', 52)

    def jump(self, label: 'str'):
        self.index = self._getlabel(label).getpos()


if __name__ == "__main__":
    exit_error('This file is not meant to be run directly', 1)
