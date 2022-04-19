Implementační dokumentace k 2. úloze do IPP 2021/2022
Jméno a příjmení: Martin Kocich
Login: xkocic02

---
## IPP Project part 2 (interpret.py)
### Basic info
- `iterpret.py` is main script that does interpretation of XML form of IPPcode22.
- `common.py` contains definitions of simple methods and groups of variable types.
- `virtual_mc.py` contains stand alone VM memory definition
- `instruction.py` contains implementation of instructions that operates on VM

- This implementation is based on [IPPcode22](https://wis.fit.vutbr.cz/FIT/st/cfs.php/course/IPP-IT/projects/2021-2022/Zadani/ipp22spec.pdf)
- Implementation stores values as strings, which is not optimal,
    becouse of their size in memory and need of conversions to int.
- In this implementation, all instructions are operating with virtual machine memory,
    Which is defined in `virtual_mc.py`. This allow quick and easy implementation of
    new instructions.
- For usage type `python3 interpret.py --help`

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
        |`getinput`     |returns one line from input without '\n' at end|
        |`endoffile`    |returns if end of file is reached|

        |data stack methods |
        |-|
        |`data_push`        |
        |`data_pop`         |

        |return stack methods|
        |-|
        |`return_push`      |
        |`return_pop`       |

        |frame data methods|
        |-|
        |`defvar`|
        |`getvar`|
        |`setvar`|
        |`isdefined`|

        |frame methods|
        |-|
        |`createframe`|
        |`pushframe`|
        |`popframe`|

        |label methods  |description|
        |-|-|
        |`setlabel`     |adds label to memory|
        |`jump`         |sets `_pc` to label pos|


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
- `template.html` contains template for html page used by `html_builder.php`
- For usage type `php8.1 test.php --help`

### Classes
- `Builder`
    - builds `index.htm` page from template
    - in template variables (%var%) are replaced by values from `test.php`
    |function           |description|
    |-|-|
    |`build`            |builds whole html|
    |`start_section`    |starts new section (table)|
    |`add_header`       |adds header of table|
    |`add_success`      |adds success message|
    |`add_failure`      |adds failure message|
    |`end_section`      |ends section (table)|