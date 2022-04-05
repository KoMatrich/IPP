Implementační dokumentace k 1. úloze do IPP 2021/2022
Jméno a příjmení: Martin Kocich
Login: xkocic02

## IPP Project part 1
### Basic info
`parse.php` does lexical and syntax analysis at same time. When part of input code is correct, then translated part of output code will be generated. When unknown or wrong input code si found program will stop and return `error code`.
On success program will return 0 and output will be in `stdout` XML format.

### Classes
- only class used in this project is `Type` class
- `Type` class serves as replacment for enum
- this project was developed in older version of php that didn't supported enums
    ```
    abstract class Type
    {
        const Label = 0;
        const Symb = 1;
        const Var = 2;
        const Type = 3;
    }
    ```

### Basic functions

`error(int $code, string $target)`
- prints error msg and target where error ocured
- end program with return code
    |return code|error msg|
    |-|-|
    |10|"Wrong starting argument/s"|
    |21|"Missing header"|
    |22|"Wrong op-code"|
    |23|"Wrong syntax or lex"|
    |else|empty string|

`element(int $tab, string $type, string $arg, string $content)`
- creates xml element
- arguments
  - `tab` sets number of tabs infront of element
  - `type` defines type of xml element
  - `arg` defines arguments of given element
  - `content` defines content of given element

### Functions
`argument(int $index, string $type, string $content)`
- encodes `type` and `content` to correct format for xml
- then it creates new xml element "arg`index`" with formated data

`args(array $args, array $types)`
- performs `args` type checking by regex
- calls `argument(.. )` function
  - with `index`=(1-n) that coresponds to order of `args`
  - there for `args[0]` is ignored (contains opcode of instruction)
- arguments
  - `args` is command with args splited by whitespaces
  - `types` is array of `Type`s

`instruction(int $order, array $words, array $types)`
- creates new xml element instuction with atributes
- this element will contain all xml arguments generated by `args` if they are correct
- arguments
  - `order` = instruction order number
  - `opcode` = `words[0]`
  - `types` = `Type`s that are alowed for this instruction