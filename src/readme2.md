Implementační dokumentace k 2. úloze do IPP 2021/2022
Jméno a příjmení: Martin Kocich
Login: xkocic02

---
## IPP Project part 2 (interpret.py)
### Basic info
- `iterpret.py` is main script that does interpretation of XML form of IPPcode22.
- `common.py` contains definitions of simple methods and groups of variable types.
- `virtual_mc.py` contains stand alone virtual machine memory definition
- `instruction.py` contains implementation of instructions that operates on VM

### Classes
- `Instruction`
    - implementation of virtual instruction
        |method                 |description|
        |-|-|
        |`run`                  |executes instruction|
        |`_set_args`            |inicializes instruction arguments|
        |`_getvar`              |returns value from memory or constant depending on type of arg|
        |`_setval`              |same as `getvar`, but sets value (error if used on constant)|
        |`_isdefined`           |returns if variable is defined|
        |`_isconst`             |returns if var is constant|
        |`_check_args`          |runs static check for given instruction|
        |`_check_number_args`   |check number of arguments|
        |`_check_type`          |static check arg is type of (type)|
        |`_check_types`         |static check arg is type of (list of types)|

        |opecode specific method                |description|
        |-|-|
        |`_xc_check_args_[opcode]`              |static check of instruction args|
        |`_xc_run_[opcode]`                     |runtime check + instruction execution|
        - `[opcode]` is instruction opcode in lower case
        - opecode specific methods are used by `run`,`_check_args`
    - `Argument`
        - class that contains data of instruction argument
        - on inicialization does static syntax check of input data
            |method         |returns                |description|
            |-|-|-|
            |`gettype`      |type of argument       ||
            |`getvar`       |tuple[`frame`,`name`]  |can be used only when `type=='var'`|
            |`getconstant`  |value of constant      |can't be used with `type=='var'`|
    ---
- `Stack`
    - implementation of stack for generic types
        |method     |purpose|
        |-|-|
        |`push`     |pushes value to stack|
        |`pop`      |pops value from stack|
        |`top`      |returns top value from stack|
        |`isempty`  |returns if stack is empty|
    ---
- `Memory`
    - class that contains memory of VM
        |variables      |description|
        |-|-|
        |`_gs`          |global frame|
        |`_ts`          |temporary frame|
        |`_lf`          |local frames (stack of frames)|
        |`pc`           |program counter|
        |`_labels`      |labels|
        |`_data_stack`  |data stack|
        |`_return_stack`|return stack|
        |`_input`       |input|
        |`_eof`         |bool that indicates end of file|

        |methods        |description|
        |-|-|
        |`inccounter`   |increments program counter|
        |`getinput`     |returns one line from input without trailing whitespaces|


    - `Variable`
        - class that contains data of variable
            |method     |description|
            |-|-|
            |`setvalue` |sets type and value to variable|
            |`getname`  |returns name of current var|
            |`getvalue` |returns value|
            |`gettype`  |returns type|
            |`isdefined`|returns true if type is set|

    - `Frame`
        - class that contains data of frame
            |method     |description|
            |-|-|
            |`createvar`|creates new variable in current frame|
            |`getvar`   |returns variable by name|
            |`isdefined`|returns true if variable is defined|

    - `Label`
        - class that contains data of label
        - has only one method `getpos` that returns position of label in code


---
## IPP Project part 2 (test.php)
### Basic info
- `test.php` is php script for testing `interpret.py`
- `functions.php` contains definitions of basic functions
- `html_builder.php` contains defintion of class `Builder`