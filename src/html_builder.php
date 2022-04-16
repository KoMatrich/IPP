<?php
    require_once('functions.php');

    class Builder
    {
        private function get_template(){
            $this->template = fopen('template.html', 'r') or error(99, "can't open file \"template.html\"");
        }

        function __construct($output)
        {
            $this->get_template();
            $this->index = 2;
            $this->output = $output;
            $this->body = "";
        }

        function __destruct()
        {
            fclose($this->template);
        }

        function build($mode,$count,$done_ok)
        {

            while (($line = stream_get_line($this->template, 1024, "\n")) !== false) {
                $tmp = strtr($line, array(
                '%TITLE%' => 'Test results',
                '%MODE%' => $mode,
                '%COUNT%' => $count,
                '%DONE_OK%' => $done_ok,
                '%DONE_PER%' => round($done_ok / $count * 100, 2),
                '%BODY%' => $this->body
                ));

                fwrite($this->output, $tmp);
            }
        }

        private function write($str)
        {
            //fwrite($this->output, html_element($str));
            $this->body = $this->body.str_repeat("\t", $this->index).$str."\n";
            //sets correct indentation
            if(preg_match('/<[^>]*>/', $str))
                $this->index++;
            if(preg_match('/<\/[^>]*>/', $str))
                $this->index--;
        }

        function start_section($name){
            $this->write("<h2>$name</h2>");
            $this->write("<table>");
        }

        function add_header(){
            $this->write("<tr><td>Test Path</td><td>Status</td><td>More info</td></tr>");
        }

        function add_success($test){
            $this->write("<tr><td>$test</td><td>Passed</td><td></td></tr>");
        }

        function add_error($test,$massage){
            $this->write("<tr><td>$test</td><td>Failed</td><td>$massage</td></tr>");
        }

        function end_section(){
            $this->write("</table>");
        }
    }