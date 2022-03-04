<?php
ini_set('display_errors', 'stdrr');

if($argc > 1)
{
    if($argv[2] == "--help")
    {
        echo("Usage: lorem ipsum");
        exit(0);
    }
}

$header = false;
echo ("<?xml TODO");

while($line = fgets(STDIN))
{
    if(!$header){
        if($line == ".IPPcode22"){
            echo("<program TODO");
            $header = true;
        }
        continue;
        }


    $words = explode(' ', trim($line, '\n'));

    switch(strtoupper($words[0]))
    {
        case "DEFVAR":
            echo("\t<instruction TODO".strtoupper().">");
            if(preg_match("[0-9]",$words[1]))
                echo("\t\t<arg1 type=\"var\">$words[1]</arg1>");
            break;
        default:
            echo "invalid";
            break;
    }
}
?>