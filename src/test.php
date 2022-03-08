<?php
function error(int $code, string $target)
{
    $msg = "";
    switch ($code) {
        case 99:
            $msg = "Internal";
            break;
        case 10:
            $msg = "Starting arguments";
            break;
    }
    fprintf(STDERR, "[$code]Error: $msg $target\n");
    exit($code);
}

$shortopts  = "h";
$shortopts .= "d:";
$shortopts .= "r";
$shortopts .= "ps:";
$shortopts .= "is:";
$shortopts .= "po";
$shortopts .= "io";
$shortopts .= "jp:";
$shortopts .= "nc";

$opts  = array(
    "help",
    "directory:",
    "recursive",
    "parse-script:",
    "int-script:",
    "parser-only",
    "int-only",
    "jexampath:",
    "no-clean",
);

function help()
{
    $table  = array(
        "NAME                                       ",
        "   test.php                                ",
        "DESCRIPTION                                ",
        "   -h  --help                              ",
        "       shows this help                     ",
        "                                           ",
        "   -d  --directory                 [folder]",
        "       sets directory to search for tests  ",
        "       else current working folder is used ",
        "                                           ",
        "   -r  --recursive                         ",
        "       recursion search in subfolders      ",
        "                                           ",
        "   -ps --parse-script          [parser.php]",
        "       sets parser script                  ",
        "       default \".\\parser.php\"           ",
        "                                           ",
        "   -is --int-script          [interpret.py]",
        "       sets interpet script                ",
        "       default \".\\interplert.py\"        ",
        "                                           ",
        "   -po --parser-only                       ",
        "       runs parser tests only              ",
        "       not compatible with \"-io,-is\"     ",
        "                                           ",
        "   -io --int-only                          ",
        "       runs interpret tests only           ",
        "       not compatible with \"-po,-ps\"     ",
        "                                           ",
        "   -jp --jexampath:                        ",
        "       sets path to jexamxml.jar file      ",
        "       default \"/pub/courses/ipp/jexamxml/\"",
        "                                           ",
        "   -nc --no-clean                          ",
        "       test.php temp file will be saved    ",
        "                                           ",
    );


    for ($i = 0; $i < sizeof($table); $i++) {
        echo("$table\n");
    }
}

$options = getopt($shortopts, $longopts);
var_dump($options);

for ($i = 0; $i < sizeof($options); $i++) {
    switch ($options[$i]) {
        case "h":
        case "help":
            help();
            exit(0);
        case "d":
        case "directory":
            break;
        case "r":
        case "recursive":
            break;
        case "ps":
        case "parse-script":
            break;
        case "is":
        case "int-script":
            break;
        case "po":
        case "parser-only":
            break;
        case "io":
        case "int-only":
            break;
        case "jp":
        case "jexampath":
            break;
        case "nc":
        case "no-clean":
            break;
        default:
            error(10, "unknow \"$options[$i]\"");
    }
}
