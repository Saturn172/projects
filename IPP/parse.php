#!/usr/bin/php5.6
<?php

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
      $type = "label";
      $output = $arg;
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

if($argc == 2){
  if($argv[1] == "--help"){
    fwrite(STDOUT, "This is some help.\n");
    exit(0);
  } else {
    fwrite(STDERR, "10: Unrecognized argument! Try --help.\n");
    exit(10);
  }
} else if($argc > 2){
  fwrite(STDERR, "10: Wrong number of arguments!\n");
  exit(10);
}

if(strtolower(trim(fgets(STDIN))) != ".ippcode18"){
  fwrite(STDERR, "21: .IPPcode18 header missing!\n");
  exit(21);
}

$xml = xmlwriter_open_memory();
xmlwriter_set_indent($xml, 1);

xmlwriter_start_document($xml, '1.0', 'UTF-8');
xmlwriter_start_element($xml, 'program');

xmlwriter_start_attribute($xml, 'language');
xmlwriter_text($xml, 'IPPcode18');
xmlwriter_end_attribute($xml);

$order = 0;

while(!feof(STDIN)){
  $line = trim(preg_replace('/\s+/', ' ', fgets(STDIN)));
  $comment = strpos($line, "#");
  if($comment !== false) $line = rtrim(substr($line, 0, $comment));
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

/*
  xmlwriter_start_attribute($xml, '');
  xmlwriter_text($xml, '');
  xmlwriter_end_attribute($xml);
*/

  //echo "\"".$line."\"\n";
  //for($i=0; $i<$count; $i++) echo $word[$i]."\n";

  if($count > 4){
    fwrite(STDERR, "21: Too many operands of instruction '$word[0]'!\n");
    exit(21);
  }

  // no operands
  if($count == 1 && !in_array($word[0], array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK"))){
    fwrite(STDERR, "21: Unknown instruction '$word[0]'!\n");
    exit(21);
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
    // <var> <symb>
    if(!in_array($word[0], array("MOVE", "INT2CHAR", "STRLEN", "TYPE"))){
      fwrite(STDERR, "21: Unknown instruction '$word[0]'!\n");
      exit(21);
    }
  }

  // 3 operands
  else if($count == 4){

    // 6.4.3
    if($word[0] == "ADD");
    else if($word[0] == "SUB");
    else if($word[0] == "MUL");
    else if($word[0] == "IDIV");

    else if($word[0] == "LT");
    else if($word[0] == "GT");
    else if($word[0] == "EQ");

    else if($word[0] == "AND");
    else if($word[0] == "OR");
    else if($word[0] == "NOT");

    else if($word[0] == "STRI2INT");

    // 6.4.5
    else if($word[0] == "CONCAT");
    else if($word[0] == "GETCHAR");
    else if($word[0] == "SETCHAR");

    // 6.4.7
    else if($word[0] == "JUMPIFEQ");
    else if($word[0] == "JUMPIFNEQ");

    else {
      fwrite(STDERR, "21: Unknown instruction '$word[0]'!\n");
      exit(21);
    }

  }

  else if($count == 3);

  xmlwriter_end_element($xml);
}

xmlwriter_end_element($xml);
xmlwriter_end_document($xml);

echo xmlwriter_output_memory($xml);
exit(0);

?>
