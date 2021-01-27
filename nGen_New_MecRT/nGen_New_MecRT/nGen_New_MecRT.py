#-*- coding: utf-8 -*-
import sys
import difflib
import os
import subprocess
import datetime
import re

import CheckerCollection
import emaillib
import PyUtils
from PyUtils import Logger

def main():
    if len(sys.argv) < 4:
        print('Parameter Error. Use Parameter "nGen.exe Path" "Base Mec Files Folder" "Target mpb Files Folder" [mail to]')
        return

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
    
    MLogger = Logger.instance()
    MLogger.DefineLogger(CopytoPath)

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

        DataColl_Base = CheckerCollection.CheckerCollection()
        DataColl_Base.CopyFrom(CheckerColl)

        DataColl_Tgt = CheckerCollection.CheckerCollection()
        DataColl_Tgt.CopyFrom(CheckerColl)

        DataColl_Base.AddDataListFromMecFile(full_path_base)
        DataColl_Tgt.AddDataListFromMecFile(full_path_tgt)

        file_modified |= not PyUtils.IsSameDataColl(DataColl_Base, DataColl_Tgt)
        MLogger.log('\n\n\n\n')

    if file_modified == True and len(toEmail) > 0:
        eMailInst = emaillib.emaillib()
        eMailInst.sendMail(toEmail, [], [''])

if __name__ == "__main__":
    main()