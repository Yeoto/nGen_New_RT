import os
import re
import logging
import CheckerCollection

class Logger:
    _instance = None

    @classmethod
    def _getInstance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls._instance = cls(*args, **kargs)
        cls.instance = cls._getInstance
        return cls._instance

    def __init__(self):
        self.logger = None

    def DefineLogger(self, root_path):
        self.logger = logging.getLogger('nGen_MecRT')
        self.logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(root_path + "\\log.log", "w", encoding='utf-8')
        handler.setLevel(logging.DEBUG)
        handlerSt = logging.StreamHandler()
        handlerSt.setLevel(logging.DEBUG)

        formatter = logging.Formatter(fmt='%(message)s')

        handler.setFormatter(formatter)
        handlerSt.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.addHandler(handlerSt)

    def log(self, message, lvl = logging.INFO):
        if message[-1] == '\n':
            message = message[0:-1]

        if self.logger:
            self.logger.log(lvl, message)
        else:
            logging.log(lvl, message)

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
            Data_Tgt = True
            return True

    return False

def CheckDataToBase_List(DataColl_Base, DataList_Base, DataColl_Tgt, Data_Tgt):
    for index in range(len(DataList_Base)):
        BaseDataD = DataList_Base[index]
        if BaseDataD.bCheckedData == True:
            continue

        if BaseDataD.IsSame(DataColl_Base, DataColl_Tgt, Data_Tgt):
            BaseDataD.bCheckedData = True
            Data_Tgt = True
            return True

    return False

def IsSameDataList(strID, DataColl_Base : CheckerCollection, DataColl_Tgt : CheckerCollection):
    MLogger = Logger.instance()

    DataList_Base = DataColl_Base.DataList[strID]
    DataList_Tgt = DataColl_Tgt.DataList[strID]

    if type(DataList_Base) != type(DataList_Tgt):
        MLogger.log("Mec Command doesn't match : Using Key : {}".format(strID))
    
    bSuccess = True
    if type(DataList_Tgt) == type({}):
        for Key in DataList_Tgt:
            TgtDataD = DataList_Tgt[Key]
            if not CheckDataToBase_Dict(DataColl_Base, DataList_Base, DataColl_Tgt, TgtDataD):
                MLogger.log("Can't Find Data At Base Mec File. {}:{}".format(DataColl_Tgt.FileFrom, TgtDataD.nLine))
                bSuccess = False
                continue
    elif type(DataList_Tgt) == type([]):
        for Key in DataList_Tgt:
            TgtDataD = DataList_Tgt[Key]
            if not CheckDataToBase_List(DataColl_Base, DataList_Base, DataColl_Tgt, TgtDataD):
                MLogger.log("Can't Find Data At Base Mec File. {}:{}".format(DataColl_Tgt.FileFrom, TgtDataD.nLine))
                bSuccess = False
                continue
    else:
        return False

    return bSuccess

def ExistNoneCheckedData(DataList, FileFrom):
    MLogger = Logger.instance()
    bDataAllClear = True
    if type(DataList) == type({}):
        for Key in DataList:
            BaseDataD = DataList[Key]
            if BaseDataD.bCheckedData == False:
                bDataAllClear &= False
                MLogger.log("Can't Find Data At Target Mec File. {}:{}".format(FileFrom, BaseDataD.nLine))
    elif type(DataList) == type([]):
        for Key in DataList:
            BaseDataD = DataList[Key]
            if BaseDataD.bCheckedData == False:
                bDataAllClear &= False
                MLogger.log("Can't Find Data At Target Mec File. {}:{}".format(FileFrom, BaseDataD.nLine))
    else:
        return False

    return bDataAllClear

def IsSameDataColl(DataColl_Base : CheckerCollection, DataColl_Tgt : CheckerCollection) -> bool:
    MLogger = Logger.instance()

    bSuccess = True
    for strID in DataColl_Tgt.DataList:
        if strID not in DataColl_Base.DataList:
            MLogger.log("Can't Find Data Command From Base File : {}".format(strID))
            continue
        
        bSuccess &= IsSameDataList(strID, DataColl_Base, DataColl_Tgt)
        bSuccess &= ExistNoneCheckedData(DataColl_Base.DataList[strID], DataColl_Base.FileFrom)

    return bSuccess