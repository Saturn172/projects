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
  if($count == 4);

  //if(strtoupper($word[0]) == )
}

exit(0);

?>
