#!/usr/bin/php5.6
<?php

$help = "
Loads tests to check proper function of parse.php and interpret.py.

Usage: ./test.php [--help] [--directory=dir] [--recursive] [--parse-script=script] [--int-script=script]

--help                  shows this help (cannot combine with any other parameter)
--directory=path        specifies directory where script will search for tests
--recursive             script will search also in subdirectories
--parse-script=path     specifies path to parse script (default: ./parse.php)
--int-script=path       specifies path to interpret script (default: ./interpret.py)
";

$opt = getopt("", array("help", "directory:", "recursive", "parse-script:", "int-script:"));

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

if(isset($opt["directory"])){
  $path = $opt["directory"];
} else {
  $path = ".";
}

if(isset($opt["recursive"])){
  $rec = "";
} else {
  $rec = "-maxdepth 1";
}

if(isset($opt["parse-script"])){
  $parse = $opt["parse-script"];
} else {
  $parse = "./parse.php";
}

if(isset($opt["int-script"])){
  $int = $opt["int-script"];
} else {
  $int = "./interpret.py";
}

$test = explode("\n", shell_exec("find $path/ -name '*.src' $rec 2>/dev/null"));
$N = count($test) - 1;

$errors = 0;
$failed = [];

for($i = 0; $i < $N; $i++){
  // file for parse.php output
  $temp1 = tmpfile();
  $MD = stream_get_meta_data($temp1);
  $source = $MD['uri'];

  // file for interpret.py output
  $temp2 = tmpfile();
  $MD = stream_get_meta_data($temp2);
  $stdout = $MD['uri'];

  // interpret.py input
  if(($in = @fopen(substr($test[$i], 0, -3)."in", "r")) === false || filesize(substr($test[$i], 0, -3)."in") == 0) $stdin = "";
  else {
    $stdin = fread($in, filesize(substr($test[$i], 0, -3)."in"));
    fclose($in);
  }

  // interpret.py sample output
  if(file_exists(substr($test[$i], 0, -3)."out") === false){
    $temp3 = tmpfile();
    $MD = stream_get_meta_data($temp3);
    $sample = $MD['uri'];
  } else {
    $sample = substr($test[$i], 0, -3)."out";
  }

  // proper return value
  if(($rc = @fopen(substr($test[$i], 0, -3)."rc", "r")) === false) $retval = 0;
  else {
    $retval = fgets($rc);
    fclose($rc);
  }

  // execute parse.php, store XML
  exec("cat '$test[$i]' | php5.6 '$parse' 2>/dev/null", $shell, $retcode);
  fwrite($temp1, implode("\n", $shell)."\n");

  // clear shell output
  $shell = [];

  // check retcode after parse.php
  if($retcode == 0){

    // execute interpret.py, store output
    exec("echo '$stdin' | python3.6 '$int' --source='$source' 1>$stdout 2>/dev/null", $shell, $retcode);
    //if(!count($shell)) $write = NULL;
    //else $write = implode("\n", $shell)."\n";
    //echo "'".$write."'<br>";
    //fwrite($temp2, implode("\n", $shell)."\n");
    //if(count($shell)) fwrite($temp2, implode("\n", $shell)."\n");
    //fwrite($temp2, $write);

    // diff
    if($retcode != $retval || shell_exec("diff '$stdout' '$sample'") != ""){
      $errors++;
      $failed[count($failed)] = substr($test[$i], 0, -4);
    }

  // parse.php havent returned anything
  } else {
    if($retcode != $retval){
      $errors++;
      $failed[count($failed)] = substr($test[$i], 0, -4);
    }
  }
}

echo "<html>";

  echo "<head>";
    echo "<meta http-equiv='content-type' content='text/html; charset=utf-8'>";
    echo "<title>IPP project - Results</title>";
  echo "</head>";

  echo "<body style='color: white; background-color: black; font-family: arial; text-align: center'>";
    echo "<h1 style='font-family: impact'>IPP PROJECT</h1>";
    echo "<h2 style='font-family: impact'>test.php</h2>";

    if($N == 0) echo "<span style='color: red'><b>No tests found!</b></span>";
    else {
      echo "<h3 style='text-decoration: underline'>RESULTS</h3>";
      echo "<table align='center'>";
      echo "<tr><td width='150'>Tests executed:</td><td>$N</td></tr>";
      echo "<tr><td>Tests failed:</td><td style='color: ";
      if($errors == 0) echo "green"; else echo "red";
      echo "'><b>$errors</b></td></tr>";
      echo "</table>";
      if($errors == 0) echo "<h4>All tests succeeded!</h4>";
      else {
        echo "<h3 style='text-decoration: underline'>LIST OF FAILED TESTS</h3>";
        for($i = 0; $i < count($failed); $i++){
          echo $failed[$i]."<br>";
        }
      }
    }

  echo "</body>";
echo "</html>\n";

?>
