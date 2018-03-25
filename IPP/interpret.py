#!/usr/bin/python3.6

import xml.etree.ElementTree as ET
import argparse
import sys
#from xml.sax.saxutils import unescape

parser = argparse.ArgumentParser(description='Doing some shit.')
parser.add_argument('--source', required=True, help="input file with XML representation of IPPcode18 program")
args = parser.parse_args()

xml = ET.parse(vars(args)['source'])
program = xml.getroot()
program[:] = sorted(program, key=lambda child: int(child.get('order')))


if program.tag != "program":
  print("31: Root element is invalid!", file=sys.stderr)
  exit(31)

if not ('language' in program.attrib and program.attrib['language'] == "IPPcode18"):
  print("31: Attribute 'language' of root element is missing or invalid!", file=sys.stderr)
  exit(31)

exe = 0

GF = {}
LF = {}
TF = {}
label = {}

value = None
vtype = None

for instruction in program:
  if instruction.attrib['opcode'] == "LABEL":
    label[instruction[0].text] = instruction

def isInt(var):
  try:
    int(var)
  except:
    return(False)
  return(True)

def GFvar(arg, init):
  src = arg.text.split('@')
  # source from global frame
  if src[0] == "GF":
    # search in global frame for variable
    if src[1] in GF:
      if init == False:
        return(src[1])
      # check for value
      if GF[src[1]] != None:
        return([GF[src[1]][0], GF[src[1]][1]])
      else:
        print("56: Variable '" + src[1] + "' in frame '" + src[0] + "' used uninitialized!", file=sys.stderr)
        exit(56)
    else:
      print("54: Non-existent variable '" + src[1] + "' in frame '" + src[0] + "'!", file=sys.stderr)
      exit(54)
  else:
    print("55: Invalid frame '" + src[0] + "'!", file=sys.stderr)
    exit(55)

# parse a symbol
def symb(arg):
  # source is a variable
  if arg.attrib['type'] == "var":
    return GFvar(arg, True)
  # source is a constant
  else:
    value = arg.text
    vtype = arg.attrib['type']
  if value == None:
    value = ""
  return([vtype, value])

# execute a block of istructions
def execute(code):
  for instruction in code:
    global exe
    exe += 1
    # 6.4.1
    # MOVE
    if instruction.attrib['opcode'] == "MOVE":
      var = instruction[0].text.split('@')
      # global frame
      if var[0] == "GF":
        # store into variable
        GF[var[1]] = symb(instruction[1])

    # DEFVAR
    if instruction.attrib['opcode'] == "DEFVAR":
      var = instruction[0].text.split('@')
      if var[0] == "GF":
        GF[var[1]] = None
      elif var[0] == "LF":
        LF[var[1]] = None
      elif var[0] == "TF":
        TF[var[1]] = None
      else:
        print("55: Invalid frame '" + var[0] + "'!", file=sys.stderr)
        exit(55)

    # 6.4.3
    # ADD
    if instruction.attrib['opcode'] == "ADD":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] != "int" or symb2[0] != "int":
        print("53: Operands for instruction 'ADD' must be ints!", file=sys.stderr)
        exit(53)
      try:
        int(symb1[1])
        int(symb2[1])
      except:
        print("53: Invalid int value entered in instruction 'ADD'!", file=sys.stderr)
        exit(53)
      GF[var] = ["int", int(symb1[1]) + int(symb2[1])]

    # SUB
    if instruction.attrib['opcode'] == "SUB":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] != "int" or symb2[0] != "int":
        print("53: Operands for instruction 'SUB' must be ints!", file=sys.stderr)
        exit(53)
      try:
        int(symb1[1])
        int(symb2[1])
      except:
        print("53: Invalid int value entered in instruction 'SUB'!", file=sys.stderr)
        exit(53)
        GF[var] = ["int", int(symb1[1]) - int(symb2[1])]

    # MUL
    if instruction.attrib['opcode'] == "MUL":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] != "int" or symb2[0] != "int":
        print("53: Operands for instruction 'MUL' must be ints!", file=sys.stderr)
        exit(53)
      try:
        int(symb1[1])
        int(symb2[1])
      except:
        print("53: Invalid int value entered in instruction 'MUL'!", file=sys.stderr)
        exit(53)
      GF[var] = ["int", int(int(symb1[1]) * int(symb2[1]))]

    # IDIV
    if instruction.attrib['opcode'] == "IDIV":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] != "int" or symb2[0] != "int":
        print("53: Operands for instruction 'IDIV' must be ints!", file=sys.stderr)
        exit(53)
      try:
        int(symb1[1])
        int(symb2[1])
      except:
        print("53: Invalid int value entered in instruction 'IDIV'!", file=sys.stderr)
        exit(53)
      if int(symb2[1]) == 0:
        print("57: Division by zero!", file=sys.stderr)
        exit(57)
      GF[var] = ["int", int(int(symb1[1]) / int(symb2[1]))]

    # LT
    if instruction.attrib['opcode'] == "LT":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == symb2[0]:
        if symb1[0] == "string":
          if str(symb1[1]) < str(symb2[1]):
            GF[var] = ["bool", True]
          else:
            GF[var] = ["bool", False]
        elif symb1[0] == "int":
          if int(symb1[1]) < int(symb2[1]):
            GF[var] = ["bool", True]
          else:
            GF[var] = ["bool", False]
        elif symb1[0] == "bool":
          if symb1[1] == "true":
            symb1[1] = 1
          else:
            symb1[1] = 0
          if symb2[1] == "true":
            symb2[1] = 1
          else:
            symb2[1] = 0
          if int(symb1[1]) < int(symb2[1]):
            GF[var] = ["bool", True]
          else:
            GF[var] = ["bool", False]
        else:
          print("53: Unknown type '" + symb1[0] + "' not match!", file=sys.stderr)
          exit(53)
      else:
        print("53: Types in instruction 'LT' not match!", file=sys.stderr)
        exit(53)

    # GT
    if instruction.attrib['opcode'] == "GT":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == symb2[0]:
        if symb1[0] == "string":
          if str(symb1[1]) > str(symb2[1]):
            GF[var] = ["bool", True]
          else:
            GF[var] = ["bool", False]
        elif symb1[0] == "int":
          if int(symb1[1]) > int(symb2[1]):
            GF[var] = ["bool", True]
          else:
            GF[var] = ["bool", False]
        elif symb1[0] == "bool":
          if symb1[1] == "true":
            symb1[1] = 1
          else:
            symb1[1] = 0
          if symb2[1] == "true":
            symb2[1] = 1
          else:
            symb2[1] = 0
          if int(symb1[1]) > int(symb2[1]):
            GF[var] = ["bool", True]
          else:
            GF[var] = ["bool", False]
        else:
          print("53: Unknown type '" + symb1[0] + "' not match!", file=sys.stderr)
          exit(53)
      else:
        print("53: Types in instruction 'GT' not match!", file=sys.stderr)
        exit(53)

    # EQ
    if instruction.attrib['opcode'] == "EQ":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == symb2[0]:
        if symb1[0] == "string":
          if str(symb1[1]) == str(symb2[1]):
            GF[var] = ["bool", True]
          else:
            GF[var] = ["bool", False]
        elif symb1[0] == "int":
          if int(symb1[1]) == int(symb2[1]):
            GF[var] = ["bool", True]
          else:
            GF[var] = ["bool", False]
        elif symb1[0] == "bool":
          if symb1[1] == "true":
            symb1[1] = 1
          else:
            symb1[1] = 0
          if symb2[1] == "true":
            symb2[1] = 1
          else:
            symb2[1] = 0
          if int(symb1[1]) == int(symb2[1]):
            GF[var] = ["bool", True]
          else:
            GF[var] = ["bool", False]
        else:
          print("53: Unknown type '" + str(symb1[0]) + "' not match!", file=sys.stderr)
          exit(53)
      else:
        print("53: Types in instruction 'EQ' not match!", file=sys.stderr)
        exit(53)

    # AND
    if instruction.attrib['opcode'] == "AND":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == "bool" and symb2[0] == "bool":
        if symb1[1] == "true" and symb2[1] == "true":
          GF[var] = ["bool", "true"]
        else:
          GF[var] = ["bool", "false"]
      else:
        print("53: Operands in instruction 'AND' must be bools!", file=sys.stderr)
        exit(53)

    # OR
    if instruction.attrib['opcode'] == "OR":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == "bool" and symb2[0] == "bool":
        if symb1[1] == "true" or symb2[1] == "true":
          GF[var] = ["bool", "true"]
        else:
          GF[var] = ["bool", "false"]
      else:
        print("53: Operands in instruction 'OR' must be bools!", file=sys.stderr)
        exit(53)

    # NOT
    if instruction.attrib['opcode'] == "NOT":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      if symb1[0] == "bool":
        if symb1[1] == "true":
          GF[var] = ["bool", "false"]
        else:
          GF[var] = ["bool", "true"]
      else:
        print("53: Operand in instruction 'NOT' must be bool!", file=sys.stderr)
        exit(53)

    # INT2CHAR
    if instruction.attrib['opcode'] == "INT2CHAR":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      if symb1[0] == "int":
        try:
          chr(int(symb1[1]))
        except:
          print("58: Char value '" + str(symb1[1]) + "' is invalid!", file=sys.stderr)
          exit(58)
        GF[var] = ["string", chr(symb1[1])]
      else:
        print("53: Operand in instruction 'INT2CHAR' must be int!", file=sys.stderr)
        exit(53)

    # STRI2INT
    if instruction.attrib['opcode'] == "STRI2INT":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == "string" and symb2[0] == "int":
        if int(symb2[1]) >= len(symb1[1]):
          print("58: Invalid index '" + str(symb2[1]) + "' in string '" + str(symb1[1]) + "'!", file=sys.stderr)
          exit(58)
        try:
          ord(str(symb1[1][int(symb2[1])]))
        except:
          print("58: ASCII value '" + str(symb1[1]) + "' is invalid!", file=sys.stderr)
          exit(58)
        GF[var] = ["string", ord(str(symb1[1][int(symb2[1])]))]
      else:
        print("53: Wrong operand types in instruction 'INT2CHAR'!", file=sys.stderr)
        exit(53)

    # 6.4.4
    # READ
    if instruction.attrib['opcode'] == "READ":
      var = GFvar(instruction[0], False)
      if instruction[1].text == "int":
        val = input("--> ")
        try:
          int(val)
        except:
          val = "0"
        GF[var] = ["int", int(val)]
      elif instruction[1].text == "string":
        GF[var] = ["string", str(input("--> "))]
      elif instruction[1].text == "bool":
        val = input("--> ")
        if val.lower() == "true":
          GF[var] = ["bool", "true"]
        else:
          GF[var] = ["bool", "false"]
      else:
        print("53: Unknown type '" + instruction[1].text + "'!", file=sys.stderr)
        exit(53)

    # WRITE
    if instruction.attrib['opcode'] == "WRITE":
      # variable
      if instruction[0].attrib['type'] == "var":
        print(GFvar(instruction[0], True)[1])
      # string
      elif instruction[0].attrib['type'] == "string":
        state = 0
        i = 0
        seq = ""
        # escape sequences parsing
        for char in instruction[0].text:
          if state == 0:
            if char == '\\':
              state = 1
              continue
            else:
              print(char, end='')
          if state == 1:
            seq += char
            i += 1;
            if i == 3:
              state = 0
              i = 0
              print(chr(int(seq)), end='')
              seq = ""
        print()
      # integer
      elif instruction[0].attrib['type'] == "int":
        print(int(instruction[0].text))

    # 6.4.5
    # CONCAT
    if instruction.attrib['opcode'] == "CONCAT":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] != "string" or symb2[0] != "string":
        print("53: Operands for instruction 'CONCAT' must be strings!", file=sys.stderr)
        exit(53)
      GF[var] = ["string", symb1[1] + symb2[1]]

    # STRLEN
    if instruction.attrib['opcode'] == "STRLEN":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      if symb1[0] != "string":
        print("53: Operand for instruction 'CONCAT' must be string!", file=sys.stderr)
        exit(53)
      GF[var] = ["int", len(str(symb1[1]))]

    # GETCHAR
    if instruction.attrib['opcode'] == "GETCHAR":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == "string" and symb2[0] == "int":
        if int(symb2[1]) >= len(symb1[1]):
          print("58: Invalid index '" + str(symb2[1]) + "' in string '" + str(symb1[1]) + "'!", file=sys.stderr)
          exit(58)
        GF[var] = ["string", str(symb1[1][int(symb2[1])])]
      else:
        print("53: Wrong operand types in instruction 'GETCHAR'!", file=sys.stderr)
        exit(53)

    # SETCHAR
    if instruction.attrib['opcode'] == "SETCHAR":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == "int" and symb2[0] == "string" and GF[var][0] == "string":
        if int(symb1[1]) >= len(GF[var][1]):
          print("58: Invalid index '" + str(symb1[1]) + "' in string '" + str(GF[var][1]) + "'!", file=sys.stderr)
          exit(58)
        GF[var][1] = GF[var][1][:int(symb1[1])] + symb2[1][0] + GF[var][1][(int(symb1[1]) + 1):]
      else:
        print("53: Wrong operand types in instruction 'SETCHAR'!", file=sys.stderr)
        exit(53)

    # 6.4.6
    # TYPE
    if instruction.attrib['opcode'] == "TYPE":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      GF[var] = ["string", symb1[0]]

    # 6.4.7
    # LABEL
    if instruction.attrib['opcode'] == "LABEL":
      continue

    # JUMP
    if instruction.attrib['opcode'] == "JUMP":
      execute(program[(int(label[instruction[0].text].attrib['order'])):])
      break

    # JUMPIFEQ
    if instruction.attrib['opcode'] == "JUMPIFEQ":
      if symb(instruction[1]) == symb(instruction[2]):
        execute(program[(int(label[instruction[0].text].attrib['order'])):])
        break

    # JUMPIFNEQ
    if instruction.attrib['opcode'] == "JUMPIFNEQ":
      if symb(instruction[1]) != symb(instruction[2]):
        execute(program[(int(label[instruction[0].text].attrib['order'])):])
        break

    # 6.4.8
    # DPRINT
    if instruction.attrib['opcode'] == "DPRINT":
      symb1 = symb(instruction[0])
      print(symb1[1], file=sys.stderr)

    # BREAK
    if instruction.attrib['opcode'] == "BREAK":
      print("#", file=sys.stderr)
      print("# INTEPRET STATUS:", file=sys.stderr)
      print("#", file=sys.stderr)
      print("# Instruction number: " + instruction.attrib['order'], file=sys.stderr)
      print("# Instructions executed: " + str(exe), file=sys.stderr)
      print("#", file=sys.stderr)

    #print(instruction.tag + " " + instruction.attrib['order'] + ": " + instruction.attrib['opcode'])

execute(program)

#print(GF)
#print(label)
