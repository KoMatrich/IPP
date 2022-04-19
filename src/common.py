import sys

# print to stderr
def eprint(*args: 'object', **kwargs: 'dict[str, object]'):
    print(*args, file=sys.stderr, **kwargs)

# prints error message and exits with code
def exit_error(error_message: 'str', rc: 'int'):
    eprint(f'interpret.py: {error_message}')
    exit(rc)

# help menu of the program
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

# definition of variable types
NUMERIC_T = ['int']
VAR_T = NUMERIC_T + ['bool', 'string', 'nil']

SYMB_STRING = ['var', 'string']
SYMB_BOOL = ['var', 'bool']
SYMB_INT = ['var'] + NUMERIC_T
SYMB = ['var'] + VAR_T

if __name__ == "__main__":
    exit_error('This file is not meant to be run directly', 99)
