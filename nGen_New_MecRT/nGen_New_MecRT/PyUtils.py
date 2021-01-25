import os
import re

def search_files(dirname):
    files = []
    filenames = os.listdir(dirname)
    for filename in filenames:
        files.append(filename)
    return files

def IsSimmilarByPattern(string, parttern) -> bool:
    matchlist = re.compile(parttern).findall(string)
    if len(matchlist) != 1 or matchlist[0] != string:
        return False
    return True

def GetParsedBlock(lines, index):
    parsed_list = []
    while index < len(lines):
        line = lines[index]

        if line[0] == '?' or line[0] == '$':
            index += 1
            break

        args = line.split(",")
        if len(args) < 2:
            index += 1
            break

        for j in range(len(args)):
            args[j] = args[j].strip()

        if len(parsed_list) == 0:
            parsed_list += args
        else:
            if args[0] == None or args[0] == '':
                parsed_list += args
            else:
                break;

        index += 1

    return (parsed_list, index)