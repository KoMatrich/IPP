<?php
function error(string $msg, int $code)
{
    //fprintf(STDERR, "[$code]Error: $msg\n");
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

function instruction($order, $words, $types)
{
    if (sizeof($words) - 1 != sizeof($types))
        error("Required arguments not matching actual", 23);

    if (sizeof($types) == 0) {
        echo ("\t<instruction order=\"$order\" opcode=\"" . strtoupper($words[0]) . "\" />\n");
    } else {
        echo ("\t<instruction order=\"$order\" opcode=\"" . strtoupper($words[0]) . "\">\n");
        args($words, $types);
        echo ("\t</instruction>\n");
    }
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
    for ($i = 1; $i < sizeof($args); $i++) {
        $processed = explode('@', $args[$i], 2);
        $type = $types[$i - 1];

        //Check if symb is var
        //  change type to var
        if ($type == Type::Symb)
            if (preg_match("/^(GF|LF|TF)$/", $processed[0]))
                $type = Type::Var;

        switch ($type) {
            case Type::Label:
                if (!preg_match('/^([\_\-\$\&\%\*\!\?]|[A-z0-9])+$/', $processed[0])) //TODO
                    error("Wrong syntax \"$processed[0]\"", 23);
                argument($i, "label", $processed[0]);
                break;

            case Type::Symb:
                if (sizeof($processed) != 2)
                    error("Wrong syntax \"$args[$i]\"", 23);
                switch ($processed[0]) {
                    case "int":
                        if (!preg_match('/^(\+|\-)?([0-9]+(_[0-9]+)*|0+[xX][0-9a-fA-F]+(_[0-9a-fA-F]+)*|0+[oO]?[0-7]+(_[0-7]+)*)$/', $processed[1]))
                            error("Wrong syntax \"$processed[1]\"", 23);
                        break;
                    case "bool":
                        if (!preg_match('/^(true|false)$/', $processed[1]))
                            error("Wrong syntax \"$processed[1]\"", 23);
                        break;
                    case "string":
                        if (!preg_match('/^(([^\x00-\x20\x23\x5C]|\\\d\d\d|[A-z0-9])*)$/', $processed[1]))
                            error("Wrong syntax \"$processed[1]\"", 23);
                        break;
                    case "nil":
                        if (!preg_match('/^(nil)$/', $processed[1]))
                            error("Wrong syntax \"$processed[1]\"", 23);
                        break;
                    default:
                        error("Wrong syntax \"$processed[0]\"", 23);
                }
                argument($i, "$processed[0]", $processed[1]);
                break;

            case Type::Var:
                if (sizeof($processed) != 2)
                    error("Wrong syntax \"$args[$i]\"", 23);

                if (!preg_match("/^(GF|LF|TF)$/", $processed[0]))
                    error("Wrong syntax \"$processed[0]\"", 23);

                if (!preg_match("/^[\_\-\$\&\%\*\!\?A-z0-9]*$/", $processed[1]))
                    error("Wrong syntax \"$processed[1]\"", 23);

                argument($i, "var", ($args[$i]));
                break;

            case Type::Type:
                if (!preg_match("/^(int|bool|string)$/", $args[$i]))
                    error("Wrong syntax \"$args[$i]\"", 23);
                argument($i, "type", ($args[$i]));
                break;
        }
    }
}

ini_set('display_errors', 'stderr');
error_reporting(E_ALL);

//$stdin = fopen("php://stdin", 'r');
$stdin = fopen("input.txt", 'r');

if ($argc > 1) {
    if ($argv[1] == "--help") {
        echo ("Usage: lorem ipsum\n");
        exit(0);
    } else {
        error("unknown argument \"$argv[1]\"", 10);
    }
}

if ($argc > 2)
    error("supports only one argument", 10);

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
        error("mising header", 21);

    if (strtoupper($words[0]) ==  strtoupper($header_name)) {
        $header = true;
        break;
    }

    error("mising header", 21);
}

if (!$header) {
    error("mising header", 21);
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
            error("Unknown instruction \"$words[0]\"", 22);
            break;
    }
    $order++;
}

echo ("</program>\n");
exit(0);
