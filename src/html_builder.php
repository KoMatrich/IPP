<?php
    require_once('functions.php');

    class Builder
    {
        private function get_template(){
            $this->template = fopen('template.html', 'r') or error(99, "can't open file \"template.html\"");
        }

        function __construct()
        {
            $this->get_template();
            $this->index = 2;
            $this->body = "";
        }

        function __destruct()
        {
            fclose($this->template);
        }

        function build($steam,$mode,$count,$done_ok)
        {
            while (($line = stream_get_line($this->template, 1024, "\n")) !== false) {
                $tmp = strtr($line, array(
                '%TITLE%' => 'Test results',
                '%MODE%' => $mode,
                '%COUNT%' => $count,
                '%DONE_OK%' => $done_ok,
                '%DONE_PER%' => $this->precent($done_ok, $count),
                '%BODY%' => $this->body
                ));

                fwrite($steam, $tmp);
            }
        }

        private function precent($done, $count)
        {
            if($count == 0)
                return 100;
            return round($done / $count * 100, 2);
        }

        private function write($str)
        {
            $start = preg_match('/<[^\/>]+[^>]*>/', $str);
            $end = preg_match('/<\/[^>]+>/', $str);

            if(!$start && $end)
                $this->index--;

            if($this->index < 0)
                error(99, "XML elem < 0");
            //fwrite($this->output, html_element($str));
            $this->body = $this->body.str_repeat("\t", $this->index).$str."\n";

            if($start && !$end)
                $this->index++;
        }

        private function addRow($str, $class)
        {
            $this->write('<tr class="'.$class.'">');
            $this->write($str);
            $this->write('</tr>');
        }

        function start_section($name){
            $this->write("<h2>$name</h2>");
            $this->write("<table class=\"results\">");
        }

        function add_header(){
            $this->addRow("<td>Test Path</td><td>Status</td><td>More info</td>", "header");
        }
        function add_success($test){
            $this->addRow("<td>$test</td><td class=\"success\">&#10004;</td><td></td>", "success");
        }
        function add_error($test,$massage){
            $this->addRow("<td>$test</td><td class=\"failure\">&#10008;</td><td>$massage</td>","failure");
        }

        function end_section(){
            $this->write("</table>");
        }
    }