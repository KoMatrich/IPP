<?php
function error(int $code, string $target)
{
    $msg = "";
    switch ($code) {
        case 10:
            if($target == "") {
                $msg = "Missing option, use -h for help";
            } else {
                $msg = "\"$target\" Wrong option/s, use -h for help";
            }
            break;
        case 11:
            $msg = "failed to open file \"$target\"";
            break;
        case 12:
            $msg = "failed to write to file \"$target\"";
            break;
        case 41:
            $msg = "\"$target\" File or directory not found";
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
        error(10, $value);
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
            error(10, $value);
        }
    }else{
        error(10, $value);
    }
}

if($parser_only && $int_only)
    error(10, "--parser-only,--int-only");

function open($dir, $recursive)
{
    $content = scandir($dir, 1);
    if (!$content)
        error(11, $dir);

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

if (!$int_only)
    if (file_exists($parser) == false)
        error(11, $parser);

if (!$parser_only)
    if (file_exists($interpreter) == false)
        error(11, $interpreter);

$files = open($dir, $recursive);
$count = count($files);

function print_progress($name, $index, $count, $done_ok)
{
    if ($done_ok != null) {
        $correct_percent = $done_ok * 100 / $index;
        printf("[%s]: %8d/%8d ,correct %.1f\n", $name, $index, $count, $correct_percent);
    } else {
        printf("[%s]: %8d/%8d\n", $name, $index, $count);
    }
}

//get content of test files to variables
function get_paths($test, &$in, &$out, &$rc, &$src)
{
    if (file_exists($test . ".in") == false) {
        $in = fopen($test . ".in", "w") or error(12, $test . ".in");
        fclose($in);
    }
    $in = file_get_contents($test . ".in");
    if ($in === false)
        error(11, $test . ".in");

    if (file_exists($test . ".out") == false) {
        $out = fopen($test . ".out", "w") or error(12, $test . ".out");
        fclose($out);
    }
    $out = file($test . ".out", FILE_IGNORE_NEW_LINES);
    if ($out === false)
        error(11, $test . ".out");

    if (file_exists($test . ".rc") == false) {
        $rc = fopen($test . ".rc", "w") or error(12, $test . ".rc");
        fwrite($rc, "0");
        fclose($rc);
    }
    $rc = file_get_contents($test . ".rc");
    if ($rc === false)
        error(11, $test . ".rc");

    if (file_exists($test . ".src") == false) {
        error(11, $test . ".src");
    }

    $src = file_get_contents($test . ".src");
    if ($src === false) {
        error(11, $test . ".src");
    }
}

$p_rc = ".p_run_rc";
$p_out = ".p_run_out";
$i_rc = ".i_run_rc";
$i_out = ".i_run_out";

$correct = $files;

if (!$int_only) {//run paser
    $index = 0;
    $done_ok = 0;
    foreach ($files as $test) {
        $index++;

        get_paths($test, $in, $out, $rc, $src);

        exec("cat \"$test.src\" | php $parser $in 2>&1", $run_out, $run_rc);
        $rc_file = fopen($test . $p_rc, "w") or error(12, $test . $p_rc);
        fwrite($rc_file, $run_rc);
        fclose($rc_file);

        $out_file = fopen($test . $p_out, "w") or error(12, $test . $p_out);
        fwrite($out_file, implode("\n", $run_out));
        fclose($out_file);

        if ($parser_only) {
            if ($rc != $run_rc) {
                Printf("[Parser tests]: %-45s %s %d != %d\n", $test, "Test retuned wrong return code", $run_rc, $rc);
                continue;
            }

            exec("diff -w -B -q $test$p_out $test$p_out", $_, $return_code);
            if ($return_code != 0) {
                Printf("[Parser tests]: %-45s output file differ from presset\n", $test);
                continue;
            }
        } else {
            if ($rc != 0) {
                Printf("[Interpreter tests]: %-45s %s %d != %d\n", $test, "Test retuned wrong return code", $run_rc, $rc);
                unset($correct[$index - 1]);
                continue;
            }
        }

        $done_ok++;
        if ($index % 20 == 0 || $index == $count) {
            print_progress("Parser tests", $index, $count, $done_ok);
        }
    }
}
if (!$parser_only) {//run interpreter
    $index = 0;
    $done_ok = 0;
    foreach ($correct as $test) {
        $index++;

        get_paths($test, $in, $out, $rc, $src);

        if ($int_only)
            exec("cat \"$test.src\" | php $interpreter $in 2>&1", $run_out, $run_rc);
        else
            exec("cat \"$test.$p_out\" | php $interpreter $in 2>&1", $run_out, $run_rc);

        $rc_file = fopen($test . $i_rc, "w") or error(12, $test . $i_rc);
        fwrite($rc_file, $run_rc);
        fclose($rc_file);

        $out_file = fopen($test . $i_out, "w") or error(12, $test . $i_out);
        fwrite($out_file, implode("\n", $run_out));
        fclose($out_file);

        if ($rc != $run_rc) {
            Printf("[Interpeter tests]: %-45s %s %d != %d\n", $test, "Test retuned wrong return code", $run_rc, $rc);
            continue;
        }

        exec("diff -w -B -q $test$i_out $test$i_out", $_, $return_code);
        if (
            $return_code != 0
        ) {
            Printf("[Interpeter tests]: %-45s output file differ from presset\n", $test);
            continue;
        }

        $done_ok++;
        if (
            $index % 20 == 0 || $index == $count
        )
            print_progress("Interpeter tests", $index, $count, $done_ok);
    }
}

if (!$no_clean) {//run clean-up
    $index = 0;
    foreach ($files as $test) {
        $index++;
        $tmp_files = array($test . $p_out, $test . $p_rc, $test . $i_out, $test . $i_rc);
        foreach ($tmp_files as $file)
            if (file_exists($file))
                unlink($file);
        if (
            $index % 20 == 0 || $index == $count
        )
            print_progress("Clean-up", $index, $count, null);
    }
}


exit (0);