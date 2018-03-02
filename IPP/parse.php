#!/usr/bin/php
<?php

if($argc == 2){
  if($argv[1] == "--help"){
    fwrite(STDOUT, "This is some help.\n");
    exit(0);
  } else {
    fwrite(STDERR, "Unrecognized argument! Try --help.\n");
    exit(10);
  }
} else if($argc > 2){
  fwrite(STDERR, "Wrong number of arguments!\n");
  exit(10);
}

echo "<?xml version='1.0' encoding='UTF-8'?>\n";

while(!feof(STDIN)){
  $line = trim(preg_replace('/\s+/', ' ', fgets(STDIN)));
  $comment = strpos($line, "#");
  if($comment !== false) $line = rtrim(substr($line, 0, $comment));
  $word = explode(' ', $line);
  $count = count($word);

  echo "\"".$line."\"\n";
  //for($i=0; $i<$count; $i++) echo $word[$i]."\n";

  if($count > 4) exit(21);

  // 3 operands
  if($count == 4){

    // 6.4.3
    if(strtoupper($word[0]) == "ADD");
    else if(strtoupper($word[0]) == "SUB");
    else if(strtoupper($word[0]) == "MUL");
    else if(strtoupper($word[0]) == "IDIV");

    else if(strtoupper($word[0]) == "LT");
    else if(strtoupper($word[0]) == "GT");
    else if(strtoupper($word[0]) == "EQ");

    else if(strtoupper($word[0]) == "AND");
    else if(strtoupper($word[0]) == "OR");
    else if(strtoupper($word[0]) == "NOT");

    else if(strtoupper($word[0]) == "STRI2INT");

    // 6.4.5
    else if(strtoupper($word[0]) == "CONCAT");
    else if(strtoupper($word[0]) == "GETCHAR");
    else if(strtoupper($word[0]) == "SETCHAR");

    // 6.4.7
    else if(strtoupper($word[0]) == "JUMPIFEQ");
    else if(strtoupper($word[0]) == "JUMPIFNEQ");

  }

  else if($count == 3);
}

exit(0);

?>
