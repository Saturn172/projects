#!/usr/bin/php5.6
<?php

$help = "
Loads input code in IPPcode18 from stadard input, checks lexical and syntax correctness and prints XML representation of the code on standard output.

Usage: ./parse.php [--help] [--stats=file] [--loc] [--comments]

--help        shows this help (cannot combine with any other parameter)
--stats=path  creates file specified by 'path' for purpose of following parameters:

--loc         prints number of instructions in the input code
--comments    prints number of comments in the input code
";

$opt = getopt("", array("help", "stats:", "loc", "comments"));

if(count($opt) != ($argc - 1)){
  fwrite(STDERR, "10: Invalid parameters! Try --help.\n");
  exit(10);
}

if(isset($opt["help"])){
  if($argc > 2){
    fwrite(STDERR, "10: Invalid parameters! Try --help.\n");
    exit(10);
  } else {
  fwrite(STDOUT, $help."\n");
  exit(0);
  }
}

if((isset($opt["comments"]) || isset($opt["loc"])) && !isset($opt["stats"])){
  fwrite(STDERR, "10: Missing parameter --stats! Try --help.\n");
  exit(10);
}

// returns type of argument and its proper value
function getArg($arg){
  $type = "";
  $output = "";
  $sign = strpos($arg, "@");
  $mark = substr($arg, 0, $sign);
  $value = substr($arg, $sign + 1);
  // type
  if($sign === false){
    if(in_array($arg, array("int", "bool", "string"))){
      $type = "type";
      $output = $arg;
  // label
    } else {
      for($i = 0; $i < strlen($arg); $i++){
        if(ctype_alnum($arg[$i]) || in_array($arg[$i], array('_', '-', '$', '&', '%', '*'))){
          if($i == 0 && is_numeric($arg[$i])){
            fwrite(STDERR, "21: Label '$arg' begins with a number!\n");
            exit(21);
          } else {
            $type = "label";
            $output = $arg;
          }
        } else {
          fwrite(STDERR, "21: Invalid label '$arg'!\n");
          exit(21);
        }
      }
    }
  // var
  } else if(in_array($mark, array("GF", "LF", "TF"))){
    for($i = 0; $i < strlen($value); $i++){
      if(ctype_alnum($value[$i]) || in_array($value[$i], array('_', '-', '$', '&', '%', '*'))){
        if($i == 0 && is_numeric($value[$i])){
          fwrite(STDERR, "21: Variable identifier '$value' begins with a number!\n");
          exit(21);
        } else {
          $type = "var";
          $output = $arg;
        }
      } else {
        fwrite(STDERR, "21: Invalid variable identifier '$value'!\n");
        exit(21);
      }
    }
  // bool
  } else if($mark == "bool"){
    if(in_array($value, array("true", "false"))){
      $type = "bool";
      $output = $value;
    } else {
      fwrite(STDERR, "21: Invalid bool value '$value'!\n");
      exit(21);
    }
  // int
  } else if($mark == "int"){
    if(is_numeric($value)){
      $type = "int";
      $output = $value;
    } else {
      fwrite(STDERR, "21: Integer value '$value' is not a number!\n");
      exit(21);
    }
  // string
  } else if($mark == "string"){
    $type = "string";
    $output = $value;
  } else {
    fwrite(STDERR, "21: Invalid operand '$arg'!\n");
    exit(21);
  }
  return array($type, $output);
}

// check for header
if(strtolower(trim(fgets(STDIN))) != ".ippcode18"){
  fwrite(STDERR, "21: .IPPcode18 header missing!\n");
  exit(21);
}

// xml init
$xml = xmlwriter_open_memory();
xmlwriter_set_indent($xml, 1);

xmlwriter_start_document($xml, '1.0', 'UTF-8');
xmlwriter_start_element($xml, 'program');

xmlwriter_start_attribute($xml, 'language');
xmlwriter_text($xml, 'IPPcode18');
xmlwriter_end_attribute($xml);

// init statics
$order = 0;
$comments = 0;

// load a line from input
while(!feof(STDIN)){
  $line = trim(preg_replace('/\s+/', ' ', fgets(STDIN)));
  $comment = strpos($line, "#");
  if($comment !== false){
    $line = rtrim(substr($line, 0, $comment));
    $comments++;
  }
  if($line == "") continue;
  $order++;
  $word = explode(' ', $line);
  $count = count($word);

  $word[0] = strtoupper($word[0]);

  xmlwriter_start_element($xml, 'instruction');

  xmlwriter_start_attribute($xml, 'order');
  xmlwriter_text($xml, $order);
  xmlwriter_end_attribute($xml);

  xmlwriter_start_attribute($xml, 'opcode');
  xmlwriter_text($xml, $word[0]);
  xmlwriter_end_attribute($xml);

  // no operands
  if($count == 1){
    if(!in_array($word[0], array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK"))){
      fwrite(STDERR, "21: Unknown instruction '$word[0]'!\n");
      exit(21);
    }
  }

  // single operand
  else if($count == 2){
    $arg1 = getArg($word[1]);
    // <var>
    if((!in_array($word[0], array("DEFVAR", "POPS")) || $arg1[0] != "var") &&
    // <symb>
    (!in_array($word[0], array("PUSHS", "WRITE", "DPRINT")) || !in_array($arg1[0], array("var", "int", "bool", "string"))) &&
    // <label>
    (!in_array($word[0], array("CALL", "LABEL", "JUMP")) || $arg1[0] != "label")
    ){
      fwrite(STDERR, "21: Invalid instruction '$word[0]'!\n");
      exit(21);
    // generate element for instruction operand
    } else {
      xmlwriter_start_element($xml, 'arg1');
      xmlwriter_start_attribute($xml, 'type');
      xmlwriter_text($xml, $arg1[0]);
      xmlwriter_end_attribute($xml);
      xmlwriter_text($xml, $arg1[1]);
      xmlwriter_end_element($xml);
    }
  }

  // 2 operands
  else if($count == 3){
    $arg1 = getArg($word[1]);
    $arg2 = getArg($word[2]);
    // <var> <symb>
    if((!in_array($word[0], array("MOVE", "INT2CHAR", "STRLEN", "TYPE", "NOT")) || $arg1[0] != "var" || !in_array($arg2[0], array("var", "int", "bool", "string"))) &&
    // <var> <type>
    ($word[0] != "READ" || $arg1[0] != "var" || $arg2[0] != "type")
    ){
      fwrite(STDERR, "21: Unknown instruction '$word[0]'!\n");
      exit(21);
    } else {
      xmlwriter_start_element($xml, 'arg1');
      xmlwriter_start_attribute($xml, 'type');
      xmlwriter_text($xml, $arg1[0]);
      xmlwriter_end_attribute($xml);
      xmlwriter_text($xml, $arg1[1]);
      xmlwriter_end_element($xml);

      xmlwriter_start_element($xml, 'arg2');
      xmlwriter_start_attribute($xml, 'type');
      xmlwriter_text($xml, $arg2[0]);
      xmlwriter_end_attribute($xml);
      xmlwriter_text($xml, $arg2[1]);
      xmlwriter_end_element($xml);
    }
  }

  // 3 operands
  else if($count == 4){
    $arg1 = getArg($word[1]);
    $arg2 = getArg($word[2]);
    $arg3 = getArg($word[3]);
    if(!in_array($arg2[0], array("var", "int", "bool", "string")) || !in_array($arg3[0], array("var", "int", "bool", "string"))){
      fwrite(STDERR, "21: Invalid instruction '$word[0]'!\n");
      exit(21);
    }
    // <var> <symb> <symb>
    if((!in_array($word[0], array("ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR")) || $arg1[0] != "var") &&
    // <label> <symb> <symb>
    (!in_array($word[0], array("JUMPIFEQ", "JUMPIFNEQ")) || $arg1[0] != "label")
    ){
      fwrite(STDERR, "21: Invalid instruction '$word[0]'!\n");
      exit(21);
    } else {
      xmlwriter_start_element($xml, 'arg1');
      xmlwriter_start_attribute($xml, 'type');
      xmlwriter_text($xml, $arg1[0]);
      xmlwriter_end_attribute($xml);
      xmlwriter_text($xml, $arg1[1]);
      xmlwriter_end_element($xml);

      xmlwriter_start_element($xml, 'arg2');
      xmlwriter_start_attribute($xml, 'type');
      xmlwriter_text($xml, $arg2[0]);
      xmlwriter_end_attribute($xml);
      xmlwriter_text($xml, $arg2[1]);
      xmlwriter_end_element($xml);

      xmlwriter_start_element($xml, 'arg3');
      xmlwriter_start_attribute($xml, 'type');
      xmlwriter_text($xml, $arg3[0]);
      xmlwriter_end_attribute($xml);
      xmlwriter_text($xml, $arg3[1]);
      xmlwriter_end_element($xml);
    }

  } else {
    fwrite(STDERR, "21: Too many operands of instruction '$word[0]'!\n");
    exit(21);
  }

  xmlwriter_end_element($xml);
}

xmlwriter_end_element($xml);
xmlwriter_end_document($xml);

// xml output
echo xmlwriter_output_memory($xml);

// stats output
if(isset($opt["stats"])){
  if(!($file = fopen($opt["stats"], "w"))){
    fwrite(STDERR, "12: Failed to open a file!\n");
    exit(12);
  }
  // loc only
  if(isset($opt["loc"]) && !isset($opt["comments"])) fwrite($file, $order."\n");
  // comments only
  else if(isset($opt["comments"]) && !isset($opt["loc"])) fwrite($file, $comments."\n");
  // both loc and comments
  else if(isset($opt["loc"]) && isset($opt["comments"])){
    if(array_search("--loc", $argv) < array_search("--comments", $argv)) $stats = array($order, $comments);
    else $stats = array($comments, $order);
    fwrite($file, $stats[0]."\n");
    fwrite($file, $stats[1]."\n");
  }
  fclose($file);
}

exit(0);

?>
