<?php
function error(int $code, string $message){
    fprintf(STDERR, "[$code]Error: $message\n");
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

function open($dir, $recursive)
{
    file_exists($dir) or error(41, "directory \"$dir\" does not exist");
    $content = scandir($dir, 1);
    if (!$content)
        error(11, "can't read directory \"$dir\"");

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

//gets variable from argv array for currnet option
function getarg($index,$varg,$value){
    if(isset($varg[$index])){
        return $varg[$index];
    } else {
        error(10, "option \"$value\" requires an argument");
    }
}

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
//if optional files are missing, generate them
function get_paths($test, &$out, &$rc)
{
    if (!file_exists($test . ".in")) {
        $in = fopen($test . ".in", "w") or error(12,"can't create file \"$test.in\"");
        fclose($in);
    }

    if (file_exists($test . ".out") == false) {
        $out = fopen($test . ".out", "w") or error(12,"can't create file \"$test.out\"");
        fclose($out);
    }
    $out = file($test . ".out", FILE_IGNORE_NEW_LINES);
    if ($out === false)
        error(11, "can't read file \"$test.out\"");

    if (file_exists($test . ".rc") == false) {
        $rc = fopen($test . ".rc", "w") or error(12,"can't create file \"$test.rc\"");
        fwrite($rc, "0");
        fclose($rc);
    }
    $rc = file_get_contents($test . ".rc");
    if ($rc === false)
        error(11, "can't read file \"$test.rc\"");


    if (!file_exists($test . ".src")) {
        error(11, "can't read file \"$test.src\"");
    }
}

//writes content of variables to tmp file
//and doesn't allow overwriting
function write_tmp_file($file_name, $content){
    if(file_exists($file_name)){
        error(12, "file \"$file_name\" already exists");
    }
    $rc_file = fopen($file_name, "w") or error(12, "can't create file \"$file_name\"");
    fwrite($rc_file, $content);
    fclose($rc_file);
    return 0;
}
?>