#!/usr/bin/python3.6

import xml.etree.ElementTree as ET
import argparse
import sys

parser = argparse.ArgumentParser(description='Loads XML representation of IPPcode18 program and interprets it.')
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

variable = {'GF': {}, 'TF': None, 'LF': None}
LF = []

label = {}
call = []
data = []

for instruction in program:
  if instruction.attrib['opcode'] == "LABEL":
    if instruction[0].text in label:
      print("52: Multiple definitions of label '" + instruction[0].text + "'!", file=sys.stderr)
      exit(52)
    label[instruction[0].text] = int(instruction.attrib['order'])

def GFvar(arg, init):
  global variable
  src = arg.text.split('@')
  # search in global frame for variable
  if src[1] in variable[src[0]]:
    if init == False:
      return(src)
    # check for value
    if variable[src[0]][src[1]] != None:
      return(variable[src[0]][src[1]])
    else:
      print("56: Variable '" + src[1] + "' in frame '" + src[0] + "' used uninitialized!", file=sys.stderr)
      exit(56)
  else:
    print("54: Non-existent variable '" + src[1] + "' in frame '" + src[0] + "'!", file=sys.stderr)
    exit(54)

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

    global exe, LF, variable, label, call, data
    exe += 1

    # 6.4.1
    # MOVE
    if instruction.attrib['opcode'] == "MOVE":
      var = instruction[0].text.split('@')
      # store into variable
      variable[var[0]][var[1]] = symb(instruction[1])

    # CREATEFRAME
    elif instruction.attrib['opcode'] == "CREATEFRAME":
      variable["TF"] = {}

    # PUSHFRAME
    elif instruction.attrib['opcode'] == "PUSHFRAME":
      if variable["TF"] == None:
        print("55: Temporary frame undefined!", file=sys.stderr)
        exit(55)
      LF.append (variable["TF"])
      variable["LF"] = LF[len(LF) - 1]
      variable["TF"] = None

    # POPFRAME
    elif instruction.attrib['opcode'] == "POPFRAME":
      if len(LF) == 0:
        print("55: Frame stack is empty!", file=sys.stderr)
        exit(55)
      variable["TF"] = LF.pop()
      if len(LF) > 0:
        variable["LF"] = LF[len(LF) - 1]
      else:
        variable["LF"] = None

    # DEFVAR
    elif instruction.attrib['opcode'] == "DEFVAR":
      var = instruction[0].text.split('@')
      if var[0] == "GF":
        variable["GF"][var[1]] = None
      elif var[0] == "LF":
        LF[var[1]] = None
      elif var[0] == "TF":
        if variable["TF"] == None:
          print("55: Temporary frame undefined!", file=sys.stderr)
          exit(55)
        variable["TF"][var[1]] = None
      else:
        print("55: Invalid frame '" + var[0] + "'!", file=sys.stderr)
        exit(55)

    # CALL
    elif instruction.attrib['opcode'] == "CALL":
      if not instruction[0].text in label:
        print("52: Inexistent label '" + instruction[0].text + "'!", file=sys.stderr)
        exit(52)
      call.append(int(instruction.attrib['order']))
      execute(program[label[instruction[0].text]:])
      break

    # RETURN
    elif instruction.attrib['opcode'] == "RETURN":
      if len(call) == 0:
        print("56: There is no place to return!", file=sys.stderr)
        exit(56)
      execute(program[call.pop():])
      break

    # 6.4.2
    # PUSHS
    elif instruction.attrib['opcode'] == "PUSHS":
      symb1 = symb(instruction[0])
      data.append(symb1)

    # POPS
    elif instruction.attrib['opcode'] == "POPS":
      if len(data) == 0:
        print("56: Data stack is empty!", file=sys.stderr)
        exit(56)
      var = GFvar(instruction[0], False)
      variable[var[0]][var[1]] = data.pop()

    # 6.4.3
    # ADD
    elif instruction.attrib['opcode'] == "ADD":
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
      variable[var[0]][var[1]] = ["int", int(symb1[1]) + int(symb2[1])]

    # SUB
    elif instruction.attrib['opcode'] == "SUB":
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
      variable[var[0]][var[1]] = ["int", int(symb1[1]) - int(symb2[1])]

    # MUL
    elif instruction.attrib['opcode'] == "MUL":
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
      variable[var[0]][var[1]] = ["int", int(int(symb1[1]) * int(symb2[1]))]

    # IDIV
    elif instruction.attrib['opcode'] == "IDIV":
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
      variable[var[0]][var[1]] = ["int", int(int(symb1[1]) / int(symb2[1]))]

    # LT
    elif instruction.attrib['opcode'] == "LT":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == symb2[0]:
        if symb1[0] == "string":
          if str(symb1[1]) < str(symb2[1]):
            variable[var[0]][var[1]] = ["bool", "true"]
          else:
            variable[var[0]][var[1]] = ["bool", "false"]
        elif symb1[0] == "int":
          if int(symb1[1]) < int(symb2[1]):
            variable[var[0]][var[1]] = ["bool", "true"]
          else:
            variable[var[0]][var[1]] = ["bool", "false"]
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
            variable[var[0]][var[1]] = ["bool", "true"]
          else:
            variable[var[0]][var[1]] = ["bool", "false"]
        else:
          print("53: Unknown type '" + symb1[0] + "'!", file=sys.stderr)
          exit(53)
      else:
        print("53: Types in instruction 'LT' not match!", file=sys.stderr)
        exit(53)

    # GT
    elif instruction.attrib['opcode'] == "GT":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == symb2[0]:
        if symb1[0] == "string":
          if str(symb1[1]) > str(symb2[1]):
            variable[var[0]][var[1]] = ["bool", "true"]
          else:
            variable[var[0]][var[1]] = ["bool", "false"]
        elif symb1[0] == "int":
          if int(symb1[1]) > int(symb2[1]):
            variable[var[0]][var[1]] = ["bool", "true"]
          else:
            variable[var[0]][var[1]] = ["bool", "false"]
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
            variable[var[0]][var[1]] = ["bool", "true"]
          else:
            variable[var[0]][var[1]] = ["bool", "false"]
        else:
          print("53: Unknown type '" + symb1[0] + "'!", file=sys.stderr)
          exit(53)
      else:
        print("53: Types in instruction 'GT' not match!", file=sys.stderr)
        exit(53)

    # EQ
    elif instruction.attrib['opcode'] == "EQ":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == symb2[0]:
        if symb1[0] == "string":
          if str(symb1[1]) == str(symb2[1]):
            variable[var[0]][var[1]] = ["bool", "true"]
          else:
            variable[var[0]][var[1]] = ["bool", "false"]
        elif symb1[0] == "int":
          if int(symb1[1]) == int(symb2[1]):
            variable[var[0]][var[1]] = ["bool", "true"]
          else:
            variable[var[0]][var[1]] = ["bool", "false"]
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
            variable[var[0]][var[1]] = ["bool", "true"]
          else:
            variable[var[0]][var[1]] = ["bool", "false"]
        else:
          print("53: Unknown type '" + str(symb1[0]) + "'!", file=sys.stderr)
          exit(53)
      else:
        print("53: Types in instruction 'EQ' not match!", file=sys.stderr)
        exit(53)

    # AND
    elif instruction.attrib['opcode'] == "AND":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == "bool" and symb2[0] == "bool":
        if symb1[1] == "true" and symb2[1] == "true":
          variable[var[0]][var[1]] = ["bool", "true"]
        else:
          variable[var[0]][var[1]] = ["bool", "false"]
      else:
        print("53: Operands in instruction 'AND' must be bools!", file=sys.stderr)
        exit(53)

    # OR
    elif instruction.attrib['opcode'] == "OR":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == "bool" and symb2[0] == "bool":
        if symb1[1] == "true" or symb2[1] == "true":
          variable[var[0]][var[1]] = ["bool", "true"]
        else:
          variable[var[0]][var[1]] = ["bool", "false"]
      else:
        print("53: Operands in instruction 'OR' must be bools!", file=sys.stderr)
        exit(53)

    # NOT
    elif instruction.attrib['opcode'] == "NOT":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      if symb1[0] == "bool":
        if symb1[1] == "true":
          variable[var[0]][var[1]] = ["bool", "false"]
        else:
          variable[var[0]][var[1]] = ["bool", "true"]
      else:
        print("53: Operand in instruction 'NOT' must be bool!", file=sys.stderr)
        exit(53)

    # INT2CHAR
    elif instruction.attrib['opcode'] == "INT2CHAR":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      if symb1[0] == "int":
        try:
          chr(int(symb1[1]))
        except:
          print("58: Char value '" + str(symb1[1]) + "' is invalid!", file=sys.stderr)
          exit(58)
        variable[var[0]][var[1]] = ["string", chr(int(symb1[1]))]
      else:
        print("53: Operand in instruction 'INT2CHAR' must be int!", file=sys.stderr)
        exit(53)

    # STRI2INT
    elif instruction.attrib['opcode'] == "STRI2INT":
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
        variable[var[0]][var[1]] = ["string", ord(str(symb1[1][int(symb2[1])]))]
      else:
        print("53: Wrong operand types in instruction 'INT2CHAR'!", file=sys.stderr)
        exit(53)

    # 6.4.4
    # READ
    elif instruction.attrib['opcode'] == "READ":
      var = GFvar(instruction[0], False)
      if instruction[1].text == "int":
        val = input()
        try:
          int(val)
        except:
          val = "0"
        variable[var[0]][var[1]] = ["int", int(val)]
      elif instruction[1].text == "string":
        variable[var[0]][var[1]] = ["string", str(input())]
      elif instruction[1].text == "bool":
        val = input()
        if val.lower() == "true":
          variable[var[0]][var[1]] = ["bool", "true"]
        else:
          variable[var[0]][var[1]] = ["bool", "false"]
      else:
        print("53: Unknown type '" + instruction[1].text + "'!", file=sys.stderr)
        exit(53)

    # WRITE
    elif instruction.attrib['opcode'] == "WRITE":
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
    elif instruction.attrib['opcode'] == "CONCAT":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] != "string" or symb2[0] != "string":
        print("53: Operands for instruction 'CONCAT' must be strings!", file=sys.stderr)
        exit(53)
      variable[var[0]][var[1]] = ["string", symb1[1] + symb2[1]]

    # STRLEN
    elif instruction.attrib['opcode'] == "STRLEN":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      if symb1[0] != "string":
        print("53: Operand for instruction 'CONCAT' must be string!", file=sys.stderr)
        exit(53)
      variable[var[0]][var[1]] = ["int", len(str(symb1[1]))]

    # GETCHAR
    elif instruction.attrib['opcode'] == "GETCHAR":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == "string" and symb2[0] == "int":
        if int(symb2[1]) >= len(symb1[1]):
          print("58: Invalid index '" + str(symb2[1]) + "' in string '" + str(symb1[1]) + "'!", file=sys.stderr)
          exit(58)
        variable[var[0]][var[1]] = ["string", str(symb1[1][int(symb2[1])])]
      else:
        print("53: Wrong operand types in instruction 'GETCHAR'!", file=sys.stderr)
        exit(53)

    # SETCHAR
    elif instruction.attrib['opcode'] == "SETCHAR":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if symb1[0] == "int" and symb2[0] == "string" and variable[var[0]][var[1]][0] == "string":
        if int(symb1[1]) >= len(variable[var[0]][var[1]][1]):
          print("58: Invalid index '" + str(symb1[1]) + "' in string '" + str(variable[var[0]][var[1]][1]) + "'!", file=sys.stderr)
          exit(58)
        variable[var[0]][var[1]][1] = variable[var[0]][var[1]][1][:int(symb1[1])] + symb2[1][0] + variable[var[0]][var[1]][1][(int(symb1[1]) + 1):]
      else:
        print("53: Wrong operand types in instruction 'SETCHAR'!", file=sys.stderr)
        exit(53)

    # 6.4.6
    # TYPE
    elif instruction.attrib['opcode'] == "TYPE":
      var = GFvar(instruction[0], False)
      symb1 = symb(instruction[1])
      variable[var[0]][var[1]] = ["string", symb1[0]]

    # 6.4.7
    # LABEL
    elif instruction.attrib['opcode'] == "LABEL":
      continue

    # JUMP
    elif instruction.attrib['opcode'] == "JUMP":
      if not instruction[0].text in label:
        print("52: Inexistent label '" + instruction[0].text + "'!", file=sys.stderr)
        exit(52)
      execute(program[(label[instruction[0].text]):])
      break

    # JUMPIFEQ
    elif instruction.attrib['opcode'] == "JUMPIFEQ":
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if not instruction[0].text in label:
        print("52: Inexistent label '" + instruction[0].text + "'!", file=sys.stderr)
        exit(52)
      if symb1[0] != symb2[0]:
        print("53: Types in instruction 'JUMPIFEQ' not match!", file=sys.stderr)
        exit(53)
      if str(symb1[1]) == str(symb2[1]):
        execute(program[(label[instruction[0].text]):])
        break

    # JUMPIFNEQ
    elif instruction.attrib['opcode'] == "JUMPIFNEQ":
      symb1 = symb(instruction[1])
      symb2 = symb(instruction[2])
      if not instruction[0].text in label:
        print("52: Inexistent label '" + instruction[0].text + "'!", file=sys.stderr)
        exit(52)
      if symb1[0] != symb2[0]:
        print("53: Types in instruction 'JUMPIFEQ' not match!", file=sys.stderr)
        exit(53)
      if str(symb1[1]) != str(symb2[1]):
        execute(program[(label[instruction[0].text]):])
        break

    # 6.4.8
    # DPRINT
    elif instruction.attrib['opcode'] == "DPRINT":
      symb1 = symb(instruction[0])
      print(symb1[1], file=sys.stderr)

    # BREAK
    elif instruction.attrib['opcode'] == "BREAK":
      print("#", file=sys.stderr)
      print("# INTEPRET STATUS:", file=sys.stderr)
      print("#", file=sys.stderr)
      print("# Instruction number: " + instruction.attrib['order'], file=sys.stderr)
      print("# Instructions executed total: " + str(exe), file=sys.stderr)
      print("# GF: " + str(variable["GF"]), file=sys.stderr)
      print("# LF: " + str(variable["LF"]), file=sys.stderr)
      print("# LF stack: " + str(LF), file=sys.stderr)
      print("# TF: " + str(variable["TF"]), file=sys.stderr)
      print("# Data stack: " + str(data), file=sys.stderr)
      print("# Labels: " + str(label), file=sys.stderr)
      print("#", file=sys.stderr)

    else:
      print("32: Unknown instruction '" + instruction.attrib['opcode'] + "'!", file=sys.stderr)
      exit(32)

execute(program)
exit(0)
