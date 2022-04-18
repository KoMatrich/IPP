from typing import Generic, TextIO, TypeVar
from common import *


class Variable:
    def __init__(self, name: str):
        self._name = name
        self._value = None
        self._type = None

    def __str__(self):
        if(self._value is None):
            return f'"{self._name}" is not defined'
        return f'{self._type} "{self._name}"="{self._value}"'

    def setvalue(self, type: 'str', value: 'str'):
        self._value = value
        self._type = type

    def getname(self) -> 'str':
        return self._name

    def getvalue(self) -> 'str':
        if(self._value is None):
            exit_error('Using variable that is not defined', 54)
        return self._value

    def gettype(self) -> 'str':
        if(self._type is None):
            exit_error('Using variable that is not defined', 54)
        return self._type

    def defined(self) -> 'bool':
        if(self._type is None):
            return False
        return True


class Frame:
    def __init__(self):
        self._variables: 'list[Variable]' = []

    def __str__(self) -> str:
        return '\n'.join([str(var) for var in self._variables])

    def createvar(self, name: str):
        if(name in self._variables):
            exit_error(f'Variable "{name}" already exists (F)', 52)
        else:
            self._variables.append(Variable(name))
            return self._variables[-1]

    def getvar(self, name: str) -> 'Variable':
        for var in self._variables:
            if(name == var.getname()):
                return var

        exit_error(f'Variable "{name}" is not defined (F)', 54)

    def isdefined(self, name: str) -> 'bool':
        for var in self._variables:
            if(name == var.getname()):
                return var.defined()
        return False


T = TypeVar('T')


class Stack(Generic[T]):
    def __init__(self):
        self._stack: 'list[T]' = []

    def push(self, value: T):
        self._stack.append(value)

    def pop(self) -> T:
        if not self.isempty():
            return self._stack.pop()
        else:
            exit_error('Stack is empty', 55)

    def top(self) -> T:
        if(self.isempty()):
            exit_error('Stack is empty', 55)
        return self._stack[-1]

    def isempty(self) -> bool:
        return len(self._stack) == 0

    def __str__(self) -> str:
        if not self.isempty():
            return str(self.top())
        return 'Empty'


class clabel:
    def __init__(self, name: str, pos: int):
        self._name = name
        self._pos = pos

    def __eq__(self, __o: object) -> bool:
        if(self._name == __o):
            return True
        return False

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return f'{self._name}:{self._pos}'

    def getpos(self) -> int:
        return self._pos


class Memory:
    def __init__(self, input: 'TextIO'):
        # Memory frames
        self._gf: 'Frame' = Frame()
        self._tf: 'Frame|None' = None

        # Stacks
        self._lf: 'Stack[Frame]' = Stack()
        self._data_stack: 'Stack[tuple[str,str]]' = Stack()
        self._return_stack: 'Stack[int]' = Stack()

        # Labels
        self._labels: 'list[clabel]' = []

        # Index of the next instruction
        self.index: 'int' = 0

        # Input file/stream
        self._input: 'TextIO' = input

    def __str__(self) -> str:
        lines = f'index:{self.index}\n'
        lines += f'GF:\n{self._gf}\n'
        if(self._tf is None):
            lines += f'TF:none\n'
        else:
            lines += f'TF:\n{self._tf}\n'
        lines += f'LF:\n{self._lf}\n'
        lines += f'Stack:\n{self._data_stack}\n'
        lines += f'Labels:\n{self._labels}\n'
        return lines

    # basic operations
    def inccounter(self):
        self.index += 1

    def getinput(self) -> 'str':
        line = self._input.readline()
        line = line.rstrip()
        return line

    # data stack operations
    def data_push(self, type: 'str', value: 'str'):
        self._data_stack.push((type, value))

    def data_pop(self) -> 'tuple[str,str]':
        return self._data_stack.pop()

    # return stack operations
    def return_push(self, value: 'int'):
        self._return_stack.push(value)

    def return_pop(self) -> 'int':
        return self._return_stack.pop()

    # frame data operations
    def defvar(self, frame: 'str', name: 'str'):
        if(frame == 'GF'):
            self._gf.createvar(name)
        elif(frame == 'TF'):
            if(self._tf is None):
                exit_error(f'Frame "TF" is not defined', 55)
            self._tf.createvar(name)
        elif(frame == 'LF'):
            self._lf.top().createvar(name)
        else:
            exit_error(f'Invalid frame "{frame}"', 55)

    def isdefined(self, frame: 'str', name: 'str') -> 'bool':
        if(frame == 'GF'):
            return self._gf.isdefined(name)
        elif(frame == 'TF'):
            if(self._tf is None):
                exit_error(f'Frame "TF" is not defined', 55)
            return self._tf.isdefined(name)
        elif(frame == 'LF'):
            return self._lf.top().isdefined(name)
        else:
            exit_error(f'Invalid frame "{frame}"', 55)

    def getvar(self, frame: 'str', name: 'str') -> 'tuple[str,str]':
        if(frame == 'GF'):
            var = self._gf.getvar(name)
        elif(frame == 'TF'):
            if (self._tf is None):
                exit_error(f'Frame "TF" is not defined', 55)
            var = self._tf.getvar(name)
        elif(frame == 'LF'):
            var = self._lf.top().getvar(name)
        else:
            exit_error(f'Invalid frame "{frame}"', 55)
        return var.gettype(), var.getvalue()

    def setvalue(self, frame: 'str', name: 'str', type: 'str', value: 'str'):
        if(frame == 'GF'):
            var = self._gf.getvar(name)
        elif(frame == 'TF'):
            if (self._tf is None):
                exit_error(f'Frame "TF" is not defined', 55)
            var = self._tf.getvar(name)
        elif(frame == 'LF'):
            var = self._lf.top().getvar(name)
        else:
            exit_error(f'Invalid frame "{frame}"', 55)
        var.setvalue(value, type)

    # frame operations
    def createframe(self):
        self._tf = Frame()

    def pushframe(self):
        if(self._tf is None):
            exit_error(f'Frame "TF" is not defined', 55)
        self._lf.push(self._tf)
        self._tf = None

    def popframe(self):
        self._tf = self._lf.pop()

    # label operations
    def setlabel(self, name: str, pos: int):
        if(name in self._labels):
            exit_error(f'Label "{name}" was already defined', 52)
        self._labels.append(clabel(name, pos))

    def _getlabel(self, name: str) -> 'clabel':
        for label in self._labels:
            if(label == name):
                return label
        else:
            exit_error(f'Label "{name}" was not defined', 52)

    def jump(self, label: 'str'):
        self.index = self._getlabel(label).getpos()


if __name__ == "__main__":
    exit_error('This file is not meant to be run directly', 99)
