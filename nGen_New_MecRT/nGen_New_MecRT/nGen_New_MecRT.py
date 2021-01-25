#-*- coding: utf-8 -*-
import sys
import difflib
import os
import subprocess
import datetime
import logging
import re

import CheckerCollection
import emaillib
import PyUtils

glogger = None
mail_text = []

def log(message, lvl=logging.INFO):
    if message[-1] == '\n':
        message = message[0:-1]

    if glogger:
        glogger.log(lvl, message)
    else:
        logging.log(lvl, message)


def GetLogger(root_path):
    logger = logging.getLogger('nGen_MecRT')
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(root_path + "\\log.log", "w", encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    handlerSt = logging.StreamHandler()
    handlerSt.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt='[%(asctime)s]%(message)s',
        datefmt='%Y/%m/%d %I:%M')

    handler.setFormatter(formatter)
    handlerSt.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(handlerSt)
    return logger

def main():
    if len(sys.argv) < 4:
        print('Parameter Error. Use Parameter "nGen.exe Path" "Base Mec Files Folder" "Target mpb Files Folder" [mail to]')
        return

    global glogger
    global mail_text
    dt = datetime.datetime.now()

    Program_Path = os.path.abspath(sys.argv[1])
    Base_root_Path = os.path.abspath(sys.argv[2])
    Base_upper_Path = os.path.abspath(Base_root_Path + "\..")
    RTModelPath = os.path.abspath(sys.argv[3])
    toEmail = ''
    if len(sys.argv) > 4:
        toEmail = sys.argv[4]

    if not os.path.isfile(Program_Path):
        print('Not Fount Program Path : "{}"'.format(Program_Path))
        return

    CopytoPath = Base_upper_Path + '\\Target Mec Files\\' + dt.strftime('%Y-%m-%d_%H_%M')
    fullpath = r'"{}" -RT PATH:"{}" COPYTO:"{}"'.format(Program_Path, RTModelPath, CopytoPath)
    subprocess.Popen(fullpath, shell=True).wait()

    glogger = GetLogger(CopytoPath)

    base_mec_files = PyUtils.search_files(Base_root_Path)
    tgt_mec_files = PyUtils.search_files(CopytoPath)

    CheckerColl = CheckerCollection.CheckerCollection()
    CheckerColl.MakeChekcerListFromExcel()

    file_modified = False
    for base_mec_path in base_mec_files:
        if not base_mec_path in tgt_mec_files:
            continue

        full_path_base = os.path.join(Base_root_Path, base_mec_path)
        full_path_tgt = os.path.join(CopytoPath, base_mec_path)

        DataColl = CheckerCollection.CheckerCollection()
        DataColl.CopyFrom(CheckerColl)

        DataColl.MakeDataListFromMecFile(full_path_base)
        DataColl.DeleteDataListFromMecFile(full_path_tgt)
        log('\n\n\n\n')

    mail_text.append("nGen Regression Test 문제 발생 !!\n")
    mail_text.append("자세한 비교 내용은 " + CopytoPath + " 참고 !!\n\n")

    if file_modified == True and len(toEmail) > 0:
        eMailInst = emaillib.emaillib()
        eMailInst.sendMail(toEmail, [], mail_text)

if __name__ == "__main__":
    main()