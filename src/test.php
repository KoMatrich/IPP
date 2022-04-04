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
        case 44:
            $msg = "Creation of file \"$target\" failed";
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
$recursive = false;
$parser = "parse.php";
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
                $dir = getarg(++$index, $argc, $argv, $value);
            break;
        case "-r":
        case "--recursive":
            $recursive = true;
            break;
        case "-ps":
        case "--parse-script":
                $parser = getarg(++$index, $argc, $argv, $value);
            break;
        case "-is":
        case "--int-script":
                $int_script = getarg(++$index, $argc, $argv, $value);
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
                $jexampath = getarg(++$index, $argc, $argv, $value);
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

function open($dir, $recursive)
{
    $content = scandir($dir, 1);
    if (!$content)
        error(41, $dir);

    $files = array();
    $file_name = "";
    foreach ($content as $file) {
        if ($file == "." || $file == "..")
            continue;

        if (is_dir($dir . "/" . $file)) {
            if ($recursive)
                $files = array_merge($files, open($dir . "/" . $file, $recursive));
        } else {
            $suffix = substr($file, strrpos($file, ".") + 1);
            switch ($suffix) {
                case "in":
                case "out";
                case "rc":
                case "src";
                    if ($file_name != pathinfo($file, PATHINFO_FILENAME)) {
                        $file_name = pathinfo($file, PATHINFO_FILENAME);
                        $files[] = $dir . "/" . $file_name;
                    }
                    break;
                default:
                    break;
            }
        }
    }
    return $files;
}

$files = open($dir, $recursive);
$index = 0;
$done_ok = 0;
$count = count($files);

foreach ($files as $test) {
    $index++;

    if (file_exists($test . ".in") == false) {
        $in = fopen($test . ".in", "w") or error(44, $test . ".in");
        fclose($in);
    }
    $in = file_get_contents($test . ".in");
    if ($in === false)
        error(44, $test . ".in");

    if (file_exists($test . ".out") == false) {
        $out = fopen($test . ".out", "w") or error(44, $test . ".out");
        fclose($out);
    }
    $out = file($test . ".out", FILE_IGNORE_NEW_LINES);
    if ($out === false)
        error(44, $test . ".out");

    if (file_exists($test . ".rc") == false) {
        $rc = fopen($test . ".rc", "w") or error(44, $test . ".rc");
        fwrite($rc, "0");
        fclose($rc);
    }
    $rc = file_get_contents($test . ".rc");
    if ($rc === false)
        error(44, $test . ".rc");

    if (file_exists($test . ".src") == false) {
        continue;
    }
    $src = file_get_contents($test . ".src");
    if ($src === false) {
        continue;
    }

    $p_rc=".p_run_rc";
    $p_out=".p_run_out";

    $i_rc=".i_run_rc";
    $i_out=".i_run_out";

    if (!$int_only) { //parser tests
        exec("cat \"$test.src\" | php $parser $in 2>&1", $run_out, $run_rc);
        $rc_file = fopen($test.$p_rc, "w") or error(44, $test.$p_rc);
        fwrite($rc_file, $run_rc);
        fclose($rc_file);

        $out_file = fopen($test.$p_out, "w") or error(44, $test.$p_out);
        fwrite($out_file, implode("\n", $run_out));
        fclose($out_file);
        
        if($rc != $run_rc){
            Printf("Parser tests: %-45s %s %d != %d\n",$test,"Test retuned wrong return code",$run_rc,$rc);
            continue;
        }

        exec("diff -w -B -q $test$p_out $test$p_out", $_ ,$return_code);
        if($return_code != 0){
            Printf("Parser tests: %-45s output file differ from presset\n",$test);
            continue;
        }

        $done_ok++;
        if ($index % 20 == 0)
            printf("Parser tests: %d/%d done, with %.1f%% correct\n", $index, $count, $done_ok / $index * 100);
    }

    if (!$parser_only) { //interpreter tests
        exec("cat \"$test$p_out\" | python $interpreter 2>$1", $run_out, $run_rc);
        $rc_file = fopen($test.$i_rc, "w") or error(44, $test.$i_rc);
        fwrite($rc_file, $run_rc);
        fclose($rc_file);

        $out_file = fopen($test.$i_out, "w") or error(44, $test.$i_out);
        fwrite($out_file, implode("\n", $run_out));
        fclose($out_file);
        
        if($rc != $run_rc){
            Printf("Interpeter tests: %-45s %s %d != %d\n",$test,"Test retuned wrong return code",$run_rc,$rc);
            continue;
        }

        exec("diff -w -B -q $test$i_out $test$i_out", $_ ,$return_code);
        if($return_code != 0){
            Printf("Interpeter tests: %-45s output file differ from presset\n",$test);
            continue;
        }

        $done_ok++;
        if ($index % 20 == 0)
            printf("Interpeter tests: %d/%d done, with %.1f%% correct\n", $index, $count, $done_ok / $index * 100);
    }
}

exit (0);