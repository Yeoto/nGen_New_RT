import sys
import os
import subprocess
import datetime
import logging
import shutil

import CheckerCollection
import PyUtils
from MLogger import Logger

def main():
    if len(sys.argv) < 4:
        print('Parameter Error. Use Parameter "nGen.exe Path" "Base Mec Files Folder" "Target mpb Files Folder"')
        return

    dt = datetime.datetime.now()

    Program_Path = os.path.abspath(sys.argv[1])
    Base_root_Path = os.path.abspath(sys.argv[2])
    Base_upper_Path = os.path.abspath(Base_root_Path + "\\..")
    RTModelPath = os.path.abspath(sys.argv[3])

    if not os.path.isfile(Program_Path):
        print('Not Fount Program Path : "{}"'.format(Program_Path))
        return

    CopytoPath = Base_upper_Path + '\\Target Mec Files\\' + dt.strftime('%Y-%m-%d_%H_%M')
    fullpath = r'"{}" -RT PATH:"{}" COPYTO:"{}"'.format(Program_Path, RTModelPath, CopytoPath)
    subprocess.Popen(fullpath, shell=True).wait()
    
    MyLogger = Logger.instance()
    MyLogger.DefineLogger(CopytoPath, os.path.abspath(sys.argv[0] + "\\.."))

    base_mec_files = PyUtils.search_files(Base_root_Path)
    tgt_mec_files = PyUtils.search_files(CopytoPath)

    CheckerColl = CheckerCollection.CheckerCollection()
    CheckerColl.MakeChekcerListFromExcel((os.path.abspath(sys.argv[0] + "\\..")) + "\\CheckerData.xlsx")

    file_modified = False
    for tgt_mec_path in tgt_mec_files:
        full_path_tgt = os.path.join(CopytoPath, tgt_mec_path)
        full_path_base = os.path.join(Base_root_Path, tgt_mec_path)
        
        MyLogger.log("Checking Mec File : {} ...".format(tgt_mec_path))
        if not tgt_mec_path in base_mec_files:
            MyLogger.AppendCase(tgt_mec_path, "Can't Find File From Base Path", logging.WARN)
            shutil.copy(full_path_tgt, full_path_base)
            continue

        DataColl_Base = CheckerCollection.CheckerCollection()
        DataColl_Base.CopyFrom(CheckerColl)

        DataColl_Tgt = CheckerCollection.CheckerCollection()
        DataColl_Tgt.CopyFrom(CheckerColl)

        DataColl_Base.AddDataListFromMecFile(full_path_base)
        DataColl_Tgt.AddDataListFromMecFile(full_path_tgt)
        
        bDiffSuccess = PyUtils.IsSameDataColl(DataColl_Base, DataColl_Tgt)
        file_modified |= not bDiffSuccess

        if bDiffSuccess == False:
            MyLogger.AppendCase(tgt_mec_path, "Mec File Not Matching !!!", logging.ERROR)
        else:
            MyLogger.AppendCase(tgt_mec_path, "", logging.INFO)
            shutil.copy(full_path_tgt, full_path_base)

        MyLogger.log('\n\n\n\n')
    
    MyLogger.ExportXml()

if __name__ == "__main__":
    main()