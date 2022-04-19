Implementační dokumentace k 2. úloze do IPP 2021/2022
Jméno a příjmení: Martin Kocich
Login: xkocic02

---
## IPP Project part 2 (interpret.py)
### Basic info
- `iterpret.py` is main script that does interpretation of XML form of IPPcode22.
- `common.py` contains definitions of simple functions and groups of variable types.
- `virtual_mc.py` contains stand alone virtual machine memory definition
- `instruction.py` contains implementation of instructions that operates on VM

### Classes
- `Instruction`
    - .
        |function       |usage|
        |-|-|
        |`run`          |executes instruction|
        |`_set_args`    |inicializes instruction arguments|
        |`_getvar`      |returns value from memory or constant depending on type of arg|
        |`_setval`      |same as `getvar`, but sets value (error if used on constant)|
        |`_isdefined`   |returns if variable is defined|
        |`_isconst`     |returns if var is constant|
        |`_check_args`  |runs static check for given instruction|

        |opecode specific fuctions           |purpose|
        |-|-|
        |`_xc_check_args_[opcode]`  |static check of instruction args|
        |`_xc_run_[opcode]`         |runtime check + instruction execution|
        |`[opcode]` is instruction opcode in lower case

    - `Argument`
        - is class that contains data of instruction argument
        - on inicialization does static syntax check of input data
            |function       |returns                |usage|
            |-|-|-|
            |`gettype`      |type of argument       |returns type of argument|
            |`getvar`       |tuple[`frame`,`name`]  |can be used only when `type=='var'`|
            |`getconstant`  |value of constant      |can't be used with `type=='var'`|

### Basic functions

### Functions
---
## IPP Project part 2 (test.php)
### Basic info
- `test.php` is php script for testing `interpret.py`
- `functions.php` contains definitions of basic functions
- `html_builder.php` contains defintion of class `Builder`