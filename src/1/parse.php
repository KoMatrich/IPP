<?php
ini_set('display_errors', 'stderr');
error_reporting(E_ALL);

function error($msg)
{
    echo ("Error: $msg\n");
    exit(1);
}

function tabs($tab)
{
    for (; $tab > 0; $tab--) {
        echo "\t";
    }
}

function element_open($tab, $type, $arg)
{
    tabs($tab);
    echo ("<$type $arg>\n");
}

function element_close($tab, $type)
{
    tabs($tab);
    echo ("</$type>\n");
}

if ($argc > 1) {
    if ($argv[1] == "--help") {
        echo ("Usage: lorem ipsum\n");
        exit(0);
    } else {
        error("unknown argument \"$argv[1]\"");
    }
}

if ($argc > 2)
    error("supports only one argument");

$header = false;
$header_name = ".IPPcode22";
while ($line = fgets(STDIN))
    if (!$header)
        if ($line ==  $header_name) {
            $header = true;
            break;
        }

if (!$header) {
    error("mising header");
}

echo ("<?xml version=\"1.0\" encoding=\"UTF-8\"\n");
echo ("<program>\n");
echo ($header_name);
$order = 1;
while ($line = fgets(STDIN)) {
    $code_line = explode('#', $line);                //removes comments
    $words = explode(' ', trim($code_line[0]));     //removes whitespaces and splits to words

    switch (strtoupper($words[0])) {
        case "CREATEFRAME": //
            break;
        case "PUSHFRAME": //
            break;
        case "POPFRAME": //
            break;
        case "BREAK": //
            break;
        case "RETURN": //
            break;

        case "CALL": // lable
            break;
        case "LABLE": // lable
            break;
        case "JUMP": // lable
            break;
        case "DEFVAR": // var
            element_open(1, "instruction" . strtoupper($words[1]), "order=\"$order\",opcode=\"UPERCASE\"");
            if (preg_match("[0-9]", $words[1]))
                echo ("\t\t<arg1 type=\"var\">$words[1]</arg1>");
            element_close(1, "instruction" . strtoupper($words[1]));
            break;
        case "POPS": // var
            break;
        case "PUSHS": // symb
            break;
        case "EXIT": // symb
            break;
        case "DPRINT": // symb
            break;
        case "WRITE": // symb
            break;

        case "MOVE": // var symb
            break;
        case "INT2CHAR": // var symb
            break;
        case "STRLEN": // var symb
            break;
        case "TYPE": // var symb
            break;
        case "READ": // var type
            break;

        case "ADD": // var symb symb
            break;
        case "SUB": // var symb symb
            break;
        case "MUL": // var symb symb
            break;
        case "IDIV": // var symb symb
            break;
        case "LT": // var symb symb
            break;
        case "GT": // var symb symb
            break;
        case "EQ": // var symb symb
            break;
        case "AND": // var symb symb
            break;
        case "OR": // var symb symb
            break;
        case "NOT": // var symb symb
            break;
        case "STRI2INT": // var symb symb
            break;
        case "CONCAT": // var symb symb
            break;
        case "GETCHAR": // var symb symb
            break;
        case "JUMPIFNEQ": // lable symb symb
            break;
        default:
            error("Unknown instruction \"$words[1]\"");
            break;
    }
    $order++;
}

echo ("<\program>\n");
echo ("?>\n");
exit(0);
