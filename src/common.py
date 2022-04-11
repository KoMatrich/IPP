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
