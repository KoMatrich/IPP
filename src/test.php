<?php
function error(int $code, string $target)
{
    $msg = "";
    switch ($code) {
        case 40:
            $msg = "\"$target\" Wrong option type, use -h for help";
            break;
        case 41:
            $msg = "\"$target\" File or directory not found";
            break;
        case 42:
            $msg = "Mising argument for \"$target\" option";
            break;
        case 43:
            $msg = "Wrong combination of arguments \"$target\"";
            break;
        case 99:
            $msg = "Internal";
            break;
    }
    fprintf(STDERR, "[$code]Error: $msg\n");
    exit($code);
}

function help()
{
    $table  = array(
        "NAME                                         ",
        "   test.php                                  ",
        "DESCRIPTION                                  ",
        "   -h  --help                                ",
        "       shows this help                       ",
        "                                             ",
        "   -d  --directory                   [folder]",
        "       sets directory to search for tests    ",
        "       else current working folder is used   ",
        "                                             ",
        "   -r  --recursive                           ",
        "       recursion search in subfolders        ",
        "                                             ",
        "   -ps --parse-script            [parser.php]",
        "       sets parser script                    ",
        "       default \".\\parser.php\"             ",
        "                                             ",
        "   -is --int-script            [interpret.py]",
        "       sets interpet script                  ",
        "       default \".\\interplert.py\"          ",
        "                                             ",
        "   -po --parser-only                         ",
        "       runs parser tests only                ",
        "       not compatible with \"-io,-is\"       ",
        "                                             ",
        "   -io --int-only                            ",
        "       runs interpret tests only             ",
        "       not compatible with \"-po,-ps\"       ",
        "                                             ",
        "   -jp --jexampath:                          ",
        "       sets path to jexamxml.jar file        ",
        "       default \"/pub/courses/ipp/jexamxml/\"",
        "                                             ",
        "   -nc --no-clean                            ",
        "       test.php temp file will be saved      ",
        "                                             ",
    );
    foreach($table as $row) {
        echo("$row\n");
    }
}

//begining of main program
ini_set('display_errors', 'stderr');
$dir = ".";
$rec = false;
$parser = "parser.php";
$interpreter = "interpret.py";
$parser_only = false;
$int_only = false;
$jexampath = "";
$no_clean = false;

foreach($argv as $arg){
    switch($arg){
        case "-h":
        case "--help":
            help();
            exit(0);
            break;
        }
}

function getarg($index,$argc,$argv,$value){
    if($index >= $argc) {
        error(42, $value);
    }
    return $argv[$index];
}

$index = 1;
for(; $index < $argc; $index++) {
    $value = $argv[$index];
    if($value[0] == '-') {
    switch($value){
        case "-d":
        case "--directory":
            $dir = getarg($index,$argc,$argv,$value);
            break;
        case "-r":
        case "--recursive":
            $recursive = true;
            break;
        case "-ps":
        case "--parse-script":
            $parser = getarg($index,$argc,$argv,$value);
            break;
        case "-is":
        case "--int-script":
            $int_script = getarg($index,$argc,$argv,$value);
            break;
        case "-po":
        case "--parser-only":
            $parser_only = true;
            break;
        case "-io":
        case "--int-only":
            $int_only = true;
            break;
        case "-jp":
        case "--jexampath":
            $jexampath = getarg($index,$argc,$argv,$value);
            break;
        case "-nc":
        case "--no-clean":
            $no_clean = true;
            break;
        default:
            error(40, $value);
        }
    }else{
        error(40, $value);
    }
}

if($parser_only && $int_only)
    error(43, "--parser-only,--int-only");

$file = scandir($dir, 1);
if($file){
    
}else{

}

if(!$int_only){
    shell_exec("php $paser");
}

if(!$parser_only){
    # shell_exec("php $interpreter");
}

exit (0);