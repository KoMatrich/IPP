<?php
require_once('functions.php');
require_once('html_builder.php');

//begining of main program
ini_set('display_errors', 'stderr');
//directory of tests
$dir = ".";
//recursive search
$recursive = false;
//default parser script path
$parser = "parse.php";
$parser_set = false;
//default interpreter script path
$interpreter = "interpret.py";
$interpreter_set = false;
//selectors
$parser_only = false;
$int_only = false;
//default jexamxml path
$jexampath = "/pub/courses/ipp/jexamxml";
$jexampath_set = false;
//no clean tmp files
$no_clean = false;

//extension of files
$p_rc = ".p_run_rc";
$p_out = ".p_run_out";
$p_err = ".p_run_err";
$i_rc = ".i_run_rc";
$i_out = ".i_run_out";
$i_err = ".i_run_err";

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

if(count($argv) !== count(array_unique($argv)))
    error(10, "duplicate arguments");

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
            $parser_set = true;
            break;
        case "-is":
        case "--int-script":
            $interpreter = getarg($index,$varg,$value);
            $interpreter_set = true;
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
            $jexampath_set = true;
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
if($parser_only && ($int_only || $interpreter_set)){
    error(10, "conflicting options \"--parser-only\" and interpreter options");
}

if($int_only && ($parser_only || $parser_set || $jexampath_set)){
    error(10, "conflicting options \"--int-only\" and parser options");
}


//checks if parser exists
if (!$int_only){
    file_exists($parser) or error(11, "parser script \"$parser\" doesn't exist");
    if($parser_only){
        file_exists($jexampath) or error(11, "jexamxml path \"$jexampath\" doesn't exist");
        file_exists("$jexampath/jexamxml.jar") or error(11, "jexamxml.jar file doesn't exist");
    }
}

//checks if interpreter exists
if (!$parser_only){
    file_exists($interpreter) or error(11, "interpreter script \"$interpreter\" doesn't exist");
}

$builder = new Builder();

//gets all test files
$correct = $files = open($dir, $recursive);
$count = count($files);
$done_ok = 0;

if (!$int_only) {//run paser
    $index = 0;
    $builder->start_section("Parser tests");
    $builder->add_header();

    foreach ($files as $test) {
        $index++;

        get_paths($test, $out, $rc);
        $run_out = array();
        $run_rc = -1;

        exec("cat $test.src | php8.1 $parser 2>$test$p_err", $run_out, $run_rc);

        write_tmp_file($test.$p_out, implode("\n", $run_out));
        write_tmp_file($test.$p_rc, $run_rc);

        if ($parser_only) {
            if ($rc != $run_rc) {
                $builder->add_error($test, "return code \"$run_rc\" is not equal to \"$rc\"");
                goto skip_parser;
            }

            // check output with jexamxml
            exec("java -jar $jexampath/jexamxml.jar $test.out $test$p_out $jexampath/options", $run_out, $run_rc);
            if($run_rc != 0){
                if($run_rc == 1)
                    $builder->add_error($test, "jexamxml error: there are some different elements in output");
                elseif($run_rc == 2)
                    $builder->add_error($test, "jexamxml error: there are some deleted elements in output");
                elseif($run_rc == 4)
                    error(11, "jexamxml error: options file doesn't exist or is incorect");
                elseif($run_rc == 6)
                    $builder->add_error($test, "jexamxml error: output file is not correctly formatted");
                else
                    error(99, "jexamxml error: return code is $run_rc");
                goto skip_parser;
            }
        } else {
            if ($run_rc != 0) {
                $builder->add_error($test, "parser failed with return code \"$run_rc\"");
                //failed to parse remove test for interpreter
                unset($correct[$index - 1]);
                goto skip_parser;
            }
            //no output preset file to check with jexamxml or diff
        }

        $done_ok++;
        $builder->add_success($test);

        skip_parser:
    }
    $builder->end_section();
}

if (!$parser_only) {//run interpreter
    $index = 0;
    $builder->start_section("Interpreter tests");
    $builder->add_header();

    foreach ($correct as $test) {
        $index++;

        get_paths($test, $out, $rc);
        $run_out = array();
        $run_rc = -1;

        if ($int_only)
            exec("timeout 5s python3 $interpreter --input=\"$test.in\" --source=\"$test.src\" 2>$test$i_err", $run_out, $run_rc);
        else
            exec("timeout 5s python3 $interpreter --input=\"$test.in\" --source=\"$test$p_out\" 2>$test$i_err", $run_out, $run_rc);

        write_tmp_file($test.$i_out, implode("\n", $run_out));
        write_tmp_file($test.$i_rc, $run_rc);

        if($rc == 124){
            $builder->add_error($test, "interpreter timeout (propably infinite loop or large program)");
            goto skip_interpret;
        }

        if ($rc != $run_rc) {
            $builder->add_error($test, "return code \"$run_rc\" is not equal to \"$rc\"");
            goto skip_interpret;
        }

        exec("diff -w -B -q $test.out $test$i_out", $_, $return_code);
        if ($return_code != 0) {
            $builder->add_error($test, "output is not equal to preset");
            goto skip_interpret;
        }

        $builder->add_success($test);

        $done_ok++;

        skip_interpret:
    }
    $builder->end_section();
}

$mode = $parser_only || $int_only ? ($int_only ? 'Interpret only': 'Parser only') : 'Parser and Interpreter';

if(!$parser_only && !$int_only){
    $done_ok/=2;
}

$builder->build($mode,$count,$done_ok);

if(!$no_clean)
    foreach($files as $test){
            if (file_exists($test.$p_err))
                exec("rm $test$p_err");
            if (file_exists($test.$p_out))
                exec("rm $test$p_out");
            if (file_exists($test.$p_rc))
                exec("rm $test$p_rc");

            if (file_exists($test.$i_err))
                exec("rm $test$i_err");
            if (file_exists($test.$i_out))
                exec("rm $test$i_out");
            if (file_exists($test.$i_rc))
                exec("rm $test$i_rc");
    }

exit (0);