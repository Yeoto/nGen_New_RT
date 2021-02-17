import os
import re
import CheckerCollection
from sys import float_info
from MLogger import Logger
import copy
from tqdm import tqdm
import concurrent.futures

def search_files(dirname):
    files = []
    filenames = os.listdir(dirname)
    for filename in filenames:
        if os.path.splitext(filename)[1] != '.mec':
            continue
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
                break

        index += 1

    return (parsed_list, index)

def CheckDataToBase_Dict(DataColl_Base, DataList_Base, DataColl_Tgt, Data_Tgt):
    for Key in DataList_Base:
        BaseDataD = DataList_Base[Key]
        if BaseDataD.bCheckedData == True:
            continue

        if BaseDataD.IsSame(DataColl_Base, DataColl_Tgt, Data_Tgt):
            BaseDataD.bCheckedData = True
            return True

    return False

def CheckDataToBase_List(DataColl_Base, DataList_Base, DataColl_Tgt, Data_Tgt):
    for index in range(len(DataList_Base)):
        BaseDataD = DataList_Base[index]
        if BaseDataD.bCheckedData == True:
            continue

        if BaseDataD.IsSame(DataColl_Base, DataColl_Tgt, Data_Tgt):
            BaseDataD.bCheckedData = True
            return True

    return False

def IsSameData(DataColl_Base, DataList_Base, DataColl_Tgt, TgtDataD, bDict):
    MyLogger = Logger.instance()
    
    bFind = False
    if bDict == True:
        bFind = CheckDataToBase_Dict(DataColl_Base, DataList_Base, DataColl_Tgt, TgtDataD)
    else:
        bFind = CheckDataToBase_List(DataColl_Base, DataList_Base, DataColl_Tgt, TgtDataD)

    if bFind == False:
        MyLogger.stackLog("Can't Find Data At Base Mec File. {}:{}".format(DataColl_Tgt.FileFrom, TgtDataD.nLine))
        return False

    return True

def IsSameDataList(strID, DataColl_Base : CheckerCollection, DataColl_Tgt : CheckerCollection):
    MyLogger = Logger.instance()

    DataList_Base = DataColl_Base.DataList[strID]
    DataList_Tgt = DataColl_Tgt.DataList[strID]

    if type(DataList_Base) != type(DataList_Tgt):
        MyLogger.stackLog("Mec Command doesn't match : Using Key : {}".format(strID))
    
    strFileaName = os.path.basename(DataColl_Base.FileFrom)
    descrip = '{}:({})'.format(strFileaName, strID)

    bSuccess = True
    itr_list = []
    bDict = False
    if type(DataList_Tgt) == type({}):
        itr_list = DataList_Tgt.keys()
        bDict = True
    elif type(DataList_Tgt) == type([]):
        itr_list = list(range(len(DataList_Tgt)))
        bDict = False

    with tqdm(total=len(itr_list), desc=descrip) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            futures = {executor.submit(IsSameData, DataColl_Base, DataList_Base, DataColl_Tgt, DataList_Tgt[Key], bDict): Key for Key in itr_list}
            bSuccess = True
            for future in concurrent.futures.as_completed(futures):
                bSuccess &= future.result()
                pbar.update(1)
        pbar.close()

    #elif type(DataList_Tgt) == type([]):
    #    for Key in tqdm(range(0,len(DataList_Tgt)), desc=descrip):
    #        TgtDataD = DataList_Tgt[Key]
    #        bFind = CheckDataToBase_List(DataColl_Base, DataList_Base, DataColl_Tgt, TgtDataD)
#
    #        if bFind == False:
    #            MyLogger.stackLog("Can't Find Data At Base Mec File. {}:{}".format(DataColl_Tgt.FileFrom, TgtDataD.nLine))
    #            bSuccess = False

    return bSuccess

def ExistNoneCheckedData(DataList, FileFrom):
    MyLogger = Logger.instance()
    bDataAllClear = True
    if type(DataList) == type({}):
        for Key in DataList:
            BaseDataD = DataList[Key]
            if BaseDataD.bCheckedData == False:
                bDataAllClear &= False
                MyLogger.stackLog("Can't Find Data At Target Mec File. {}:{}".format(FileFrom, BaseDataD.nLine))
    elif type(DataList) == type([]):
        for Key in range(0,len(DataList)):
            BaseDataD = DataList[Key]
            if BaseDataD.bCheckedData == False:
                bDataAllClear &= False
                MyLogger.stackLog("Can't Find Data At Target Mec File. {}:{}".format(FileFrom, BaseDataD.nLine))
    else:
        return False

    return bDataAllClear

def IsSameDataColl(DataColl_Base : CheckerCollection, DataColl_Tgt : CheckerCollection) -> bool:
    MyLogger = Logger.instance()

    bSuccess = True
    BaseDataKeyList = copy.deepcopy(DataColl_Base.DataKeyList)
    TgtDataKeyList = copy.deepcopy(DataColl_Tgt.DataKeyList)

    for strID in TgtDataKeyList:
        if strID not in DataColl_Base.DataList:
            MyLogger.stackLog("Can't Find Data Command From Base File : {}".format(strID))
            bSuccess &= False
            continue
        
        bSuccess &= IsSameDataList(strID, DataColl_Base, DataColl_Tgt)
        bSuccess &= ExistNoneCheckedData(DataColl_Base.DataList[strID], DataColl_Base.FileFrom)

    MyLogger.PopAllLog()
    return bSuccess

def IsSameValue(val1, val2) -> bool:
    if type(val1) != type(val2):
        return False

    if type(val1) == type(0.0):
        if abs(val1 - val2) > float_info.epsilon:
            return False
    else:
        if val1 != val2:
            return False

    return True