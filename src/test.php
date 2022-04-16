<?php
require_once('fuctions.php');

//begining of main program
ini_set('display_errors', 'stderr');
//directory of tests
$dir = ".";
//recursive search
$recursive = false;
//default parser script path
$parser = "parse.php";
//default interpreter script path
$interpreter = "interpret.py";
//selectors
$parser_only = false;
$int_only = false;
//default jexamxml path
$jexampath = "/pub/courses/ipp/jexamxml/";
//no clean tmp files
$no_clean = false;

//extension of files
$p_rc = ".p_run_rc";
$p_out = ".p_run_out";
$i_rc = ".i_run_rc";
$i_out = ".i_run_out";

//check for help argument
foreach($argv as $arg){
    switch($arg){
        case "-h":
        case "--help":
            help();
            exit(0);
            break;
        }
}

//arguments preprocessing (splits arguments with "=" and sets variables)
$varg = array();
for($i = 0; $i < $argc; $i++){
    $splited = explode("=", $argv[$i],2);
    $argv[$i] = $splited[0];
    if(count($splited) == 2){
        $varg[$i] = $splited[1];
    }
}

//argument processing
for($index = 1; $index < $argc; $index++) {
    $value = $argv[$index];
    if($value[0] == '-') {
    switch($value){
        case "-d":
        case "--directory":
                $dir = getarg($index,$varg,$value);
            break;
        case "-r":
        case "--recursive":
            $recursive = true;
            break;
        case "-ps":
        case "--parse-script":
                $parser = getarg($index,$varg,$value);
            break;
        case "-is":
        case "--int-script":
                $interpreter = getarg($index,$varg,$value);
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
                $jexampath = getarg($index,$varg,$value);
            break;
        case "-nc":
        case "--no-clean":
            $no_clean = true;
            break;
        default:
            error(10, "unknown option \"$value\"");
        }
    }else{
        error(10, "unknown command \"$value\"");
    }
}

//check for conflicting options
if($parser_only && $int_only)
    error(10, "parser-only and int-only options are mutually exclusive");

//checks if parser exists
if (!$int_only)
    file_exists($parser) or error(11, "parser script \"$parser\" doesn't exist");

//checks if interpreter exists
if (!$parser_only)
    file_exists($interpreter) or error(11, "interpreter script \"$interpreter\" doesn't exist");

//gets all test files
$output = fopen('index.html', 'w') or error(12, "can't create file \"+index.html+\"");

$correct = $files = open($dir, $recursive);
$count = count($files);

if (!$int_only) {//run paser
    $index = 0;
    $done_ok = 0;
    foreach ($files as $test) {
        $index++;

        get_paths($test, $in, $out, $rc, $src);

        exec("cat $test.src | php $parser $in 2>&1", $run_out, $run_rc);

        write_tmp_file($test.$p_out, implode("\n", $run_out));
        write_tmp_file($test.$p_rc, $run_rc);

        if ($parser_only) {
            if ($rc != $run_rc) {
                Printf("[Parser tests]: %-45s %s %d != %d\n", $test, "Test retuned wrong return code", $run_rc, $rc);
                continue;
            }

            ///@TODO use JExamXML
            exec("diff -w -B -q $test$p_out $test$p_out", $_, $return_code);
            if ($return_code != 0) {
                Printf("[Parser tests]: %-45s output file differ from presset\n", $test);
                continue;
            }
        } else {
            if ($rc != 0) {
                Printf("[Parser tests]: %-45s %s %d != %d\n", $test, "Test retuned wrong return code", $run_rc, $rc);
                unset($correct[$index - 1]);
                continue;
            }

            exec("diff -w -B -q $test$p_out $test$p_out", $_, $return_code);
            if ($return_code != 0) {
                Printf("[Parser tests]: %-45s output file differ from presset\n", $test);
                continue;
            }
        }

        $done_ok++;
        if ($index % 20 == 0 || $index == $count) {
            print_progress("Parser tests", $index, $count, $done_ok);
        }

        if(!$no_clean){
            if (file_exists($test.$p_out))
                unlink($test.$p_out);
            if (file_exists($test.$p_rc))
                unlink($test.$p_rc);
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
            exec("cat $test.src | php $interpreter $in 2>&1", $run_out, $run_rc);
        else
            exec("cat $test.$p_out | php $interpreter $in 2>&1", $run_out, $run_rc);

        write_tmp_file($test.$i_out, implode("\n", $run_out));
        write_tmp_file($test.$i_rc, $run_rc);

        if ($rc != $run_rc) {
            Printf("[Interpeter tests]: %-45s %s %d != %d\n", $test, "Test retuned wrong return code", $run_rc, $rc);
            continue;
        }

        exec("diff -w -B -q $test$i_out $test$i_out", $_, $return_code);
        if ($return_code != 0) {
            Printf("[Interpeter tests]: %-45s output file differ from presset\n", $test);
            continue;
        }

        Printf("[Interpeter tests]: %-45s %s\n", $test, "OK");

        $done_ok++;

        if(!$no_clean){
            if (file_exists($test.$i_out))
                unlink($test.$i_out);
            if (file_exists($test.$i_rc))
                unlink($test.$i_rc);
        }
    }
}

exit (0);