<?php
function error(int $code, string $target)
{
    $msg = "";
    switch ($code) {
        case 10:
            $msg = "Starting argument/s";
            break;
        case 21:
            $msg = "Mising header";
            break;
        case 22:
            $msg = "Op-code";
            break;
        case 23:
            $msg = "Syntax or lexical";
            break;
    }
    fprintf(STDERR, "[$code]Error: $msg $target\n");
    exit($code);
}

function element(int $tab, string $type, string $arg, string $content)
{
    for (; $tab > 0; $tab--) {
        echo "\t";
    }

    if ($arg == "")
        echo ("<$type>$content</$type>\n");
    else
        echo ("<$type $arg>$content</$type>\n");
}


abstract class Type
{
    const Label = 0;
    const Symb = 1;
    const Var = 2;
    const Type = 3;
}

function argument(int $index, string $type, string $content)
{
    $type = htmlspecialchars($type, ENT_XML1 | ENT_QUOTES);
    $content = htmlspecialchars($content, ENT_XML1 | ENT_QUOTES);
    element(2, "arg$index", "type=\"$type\"", $content);
}

function args(array $args, array $types)
{
    $reg_frame = '/^(GF|LF|TF)$/';
    $reg_name = '/^[\_\-\$\&\%\*\!\?a-zA-Z][\_\-\$\&\%\*\!\?\da-zA-Z]*$/';
    $reg_int = '/^(\+|\-)?(\d+(_\d+)*|0+[xX][\da-fA-F]+(_[\da-fA-F]+)*|0+[oO]?[0-7]+(_[0-7]+)*)$/';
    $reg_string = '/^([^\x00-\x20\x23\x5C]|\x5C\d\d\d)*$/';
    $reg_types = '/^(int|bool|string)$/';

    for ($i = 1; $i < sizeof($args); $i++) {
        //args contains cmd name soo we start from 1
        //but types are indexed from 0-n
        $type = $types[$i - 1];

        //used to check var and symb
        $splited = explode('@', $args[$i], 2);

        //Check if type is symb
        if ($type == Type::Symb){
            //if symb has format as [frame-foramt]@[rest] then it is 
            if (preg_match($reg_frame, $splited[0]))
                $type = Type::Var;
        }
                

        switch ($type) {
            case Type::Label:
                //whole argument is formated as reg_name
                if (!preg_match($reg_name, $args[$i]))
                    error(23, "\"$args[$i]\"");
                argument($i, "label", $args[$i]);
                break;

            case Type::Symb:
                //symbol has to be splited to 2 parts
                if (sizeof($splited) != 2)
                    error(23, "\"$args[$i]\"");
                
                //first part defines type of symb
                switch ($splited[0]) {
                    case "int":
                        //second part defines value of symb
                        if (!preg_match($reg_int, $splited[1]))
                            error(23, "\"$splited[1]\"");
                        break;
                    case "bool":
                        if (!preg_match('/^(true|false)$/', $splited[1]))
                            error(23, "\"$splited[1]\"");
                        break;
                    case "string":
                        if (!preg_match($reg_string, $splited[1]))
                            error(23, "\"$splited[1]\"");
                        break;
                    case "nil":
                        if (!preg_match('/^(nil)$/', $splited[1]))
                            error(23, "\"$splited[1]\"");
                        break;
                    default:
                        error(23, "\"$splited[0]\"");
                }
                argument($i, "$splited[0]", $splited[1]);
                break;

            case Type::Var:
                //var has to be splited to 2 parts
                if (sizeof($splited) != 2)
                    error(23,"\"$args[$i]\"");

                if (!preg_match($reg_frame, $splited[0]))
                    error(23,"\"$splited[0]\"");

                if (!preg_match($reg_name, $splited[1]))
                    error(23,"\"$splited[1]\"");

                argument($i, "var", ($args[$i]));
                break;

            case Type::Type:
                if (!preg_match($reg_types, $args[$i]))
                    error(23,"\"$args[$i]\"");
                argument($i, "type", ($args[$i]));
                break;
        }
    }
}

function instruction(int $order,array $words,array $types)
{
    if (sizeof($words) - 1 != sizeof($types))
        error(23, "wrong argument count");

    if (sizeof($types) == 0) {
        echo ("\t<instruction order=\"$order\" opcode=\"" . strtoupper($words[0]) . "\" />\n");
    } else {
        echo ("\t<instruction order=\"$order\" opcode=\"" . strtoupper($words[0]) . "\">\n");
        args($words, $types);
        echo ("\t</instruction>\n");
    }
}

//begining of main program

ini_set('display_errors', 'stderr');
error_reporting(E_ALL);

$stdin = fopen("php://stdin", 'r');
//for testing
//$stdin = fopen("input.txt", 'r');

if ($argc > 1) {
    if ($argv[1] == "--help") {
        echo ("Used as parser\n");
        exit(0);
    } else {
        error(10,"unknown \"$argv[1]\"");
    }
}

if ($argc > 2)
    error(10,"supports only one");

$header = false;
$header_name = ".IPPcode22";
while ($line = fgets($stdin)) {
    $code_line = explode('#', trim($line), 2);               //removes comments
    $words = preg_split('/\s+/', trim($code_line[0]));    //splits by words

    if ($words[0] == "" && sizeof($words) == 1) {
        //empty line or line with only comment
        continue;
    }

    if (sizeof($words) != 1)
        error(21,"");

    if (strtoupper($words[0]) ==  strtoupper($header_name)) {
        $header = true;
        break;
    }

    error(21,"");
}

if (!$header) {
    error(21,"");
}

//removes dot infront of header_name
$header_name = ltrim($header_name, '.');

echo ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
echo ("<program language=\"$header_name\">\n");
$order = 1;

while ($line = fgets($stdin)) {
    $code_line = explode('#', trim($line), 2);
    $words = preg_split('/\s+/', trim($code_line[0]));

    if ($words[0] == "" && sizeof($words) == 1) {
        //empty line or line with only comment
        continue;
    }

    switch (strtoupper($words[0])) {
        case "CREATEFRAME": //
        case "PUSHFRAME": //
        case "POPFRAME": //
        case "BREAK": //
        case "RETURN": //
            instruction($order, $words, array());
            break;

        case "CALL": // lable
        case "LABEL": // lable
        case "JUMP": // lable
            instruction($order, $words, array(Type::Label));
            break;
        case "DEFVAR": // var
        case "POPS": // var
            instruction($order, $words, array(Type::Var));
            break;
        case "PUSHS": // symb
        case "EXIT": // symb
        case "DPRINT": // symb
        case "WRITE": // symb
            instruction($order, $words, array(Type::Symb));
            break;

        case "MOVE": // var symb
        case "INT2CHAR": // var symb
        case "STRLEN": // var symb
        case "TYPE": // var symb
        case "NOT": // var symb
            instruction($order, $words, array(Type::Var, Type::Symb));
            break;

        case "READ": // var type
            instruction($order, $words, array(Type::Var, Type::Type));
            break;

        case "ADD": // var symb symb
        case "SUB": // var symb symb
        case "MUL": // var symb symb
        case "IDIV": // var symb symb
        case "LT": // var symb symb
        case "GT": // var symb symb
        case "EQ": // var symb symb
        case "AND": // var symb symb
        case "OR": // var symb symb
        case "STRI2INT": // var symb symb
        case "CONCAT": // var symb symb
        case "GETCHAR": // var symb symb
        case "SETCHAR": // var symb symb
            instruction($order, $words, array(Type::Var, Type::Symb, Type::Symb));
            break;
        case "JUMPIFEQ": // lable symb symb
        case "JUMPIFNEQ": // lable symb symb
            instruction($order, $words, array(Type::Label, Type::Symb, Type::Symb));
            break;
        default:
            error(22,"Unknown instruction \"$words[0]\"");
            break;
    }
    $order++;
}

echo ("</program>\n");
exit(0);
