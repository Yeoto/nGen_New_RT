import openpyxl
import os
import re
import PyUtils
import nGen_New_MecRT

class Checker:
    def __init__(self):
        self.strID = ''
        self.list = []
        self.KeyIndex = -1
        self.bTemp = False

    def HasKey(self):
        return self.KeyIndex != -1

    def IsSame(self, CheckerColl, DataD):
        if self.strID != DataD.strID:
            return False

        if self.strID not in CheckerColl.CheckerList:
            return False

        list_cnt = len(self.list)
        if list_cnt != len(DataD.list):
            return False
        
        CheckerD = CheckerColl.CheckerList[self.strID]

        if CheckerD.bTemp == False:
            if list_cnt != len(CheckerD.list):
                return False

        for i in range(list_cnt):
            src_data = self.list[i]
            dst_data = DataD.list[i]

            if CheckerD.bTemp == False:
                if type(CheckerD.list[i]) == type(''):
                    RecursiveData_List = CheckerColl.DataList[CheckerD.list[i]]
                    if type(RecursiveData_List) != type({}):
                        return False
                    
                    if type(src_data) != type(int) or type(dst_data) != type(int):
                        return False

                    src_recursive_Data = RecursiveData_List[src_data]
                    dst_recursive_Data = RecursiveData_List[dst_data]

                    if src_recursive_Data.IsSame(CheckerColl, dst_recursive_Data) == False:
                        return False
                        
                elif type(CheckerD.list[i]) != type(bool):
                    return False

                if CheckerD.list[i] == False:
                    continue

            if type(src_data) != type(dst_data):
                return False
            if src_data != dst_data:
                return False

        return True
class CheckerCollection:
    def __init__(self):
        self.CheckerList = {}
        self.DataList = {}
        self.__PrevID = ''

    def CopyFrom(self, CheckColl):
        self.CheckerList = CheckColl.CheckerList

    def MakeChekcerListFromExcel(self):
        strChkDataPath = os.path.abspath('CheckerData.xlsx')
        wb = openpyxl.load_workbook(strChkDataPath)
        sheet = wb.active

        nRow = 2
        while True:
            CheckerD = Checker()
            nCol = 2

            # 설마 1만개 이상 나오겠음..? 무한루프 방지
            strID = sheet.cell(row=nRow, column=1).value
            if strID == 'END' or nRow >= 10000:
                break

            if strID == None or strID == '':
                strID = self.__PrevID
                CheckerD = self.CheckerList[strID]
                CheckerD.list.append(False)
            else:
                self.__PrevID = strID

            CheckerD.strID = strID

            while True:
                value = sheet.cell(row=nRow, column=nCol).value

                # 설마 1천개 이상 있겠음..? 무한루프 방지
                if value == 'END' or nCol >= 1000:
                    break

                if value == 'KEY':
                    CheckerD.KeyIndex = nCol-2
                    value = False

                CheckerD.list.append(value)
                nCol += 1

            self.CheckerList[strID] = CheckerD
            nRow += 1

    def ExistChecker(self, strID):
        return strID in self.CheckerList

    def GetCheckDataCount(self, strID):
        return len(self.CheckerList[strID].list)

    def MakeToChecker(self, data_list) -> Checker():
        strID = data_list[0]

        if type(strID) != type(''):
            return False

        CheckerD = Checker()
        CheckerD.strID = strID

        for strData in data_list[1:]:
            if type(strData) == type(''):
                if PyUtils.IsSimmilarByPattern(strData, '\d+\.\d*') == True:
                    CheckerD.list.append(float(strData))
                elif PyUtils.IsSimmilarByPattern(strData, '\d+') == True:
                    CheckerD.list.append(int(strData))
                else:
                    CheckerD.list.append(strData)
            else:
                CheckerD.list.append(strData)

        return CheckerD

    def AddData(self, data_list):
        DataD = self.MakeToChecker(data_list)
        strID = DataD.strID

        KeyIndex = self.CheckerList[strID].KeyIndex
        
        if KeyIndex == -1:
            if strID not in self.DataList:
                self.DataList[strID] = []
            self.DataList[strID].append(DataD)
        else:
            if strID not in self.DataList:
                self.DataList[strID] = {}
            self.DataList[strID][DataD.list[KeyIndex]] = DataD

        return True

    def DelData(self, data_list):
        DataD = self.MakeToChecker(data_list)

        if DataD.strID not in self.DataList:
            return False

        DataList = self.DataList[DataD.strID]
        
        if type(DataList) == type([]):
            for index in range(len(DataList)):
                DstDataD = DataList[index]
                if DataD.IsSame(self, DstDataD):
                    del self.DataList[index]
                    return True
        elif type(DataList) == type({}):
            for Key in DataList:
                DstDataD = DataList[Key]
                if DataD.IsSame(self, DstDataD):
                    del self.DataList[DataD.strID][Key]           
                    return True

        return False

    def AddTempChecker(self, strID):
        # 일단 문자+숫자로 이루어진 문자열만 strID로 쓰도록 함. 설마 이렇게 생긴거 말고 있겠어..?
        if PyUtils.IsSimmilarByPattern(strID, '[\w\d]+') == False:
            return False

        if strID in self.CheckerList:
            return False

        data_list = []
        data_list.append(strID)
        data_list.append(False) #Key
        CheckerD = self.MakeToChecker(data_list)
        CheckerD.KeyIndex = 0
        CheckerD.bTemp = True

        self.CheckerList[strID] = CheckerD
        return True

    def IsValidData(self, parsed_list) -> bool:
        if not self.ExistChecker(parsed_list[0]):
            return False

        CheckerD = self.CheckerList[parsed_list[0]]
        if CheckerD.bTemp == False:
            return len(parsed_list[1:]) == len(CheckerD.list)
        else:
            return True

    def MakeDataListFromMecFile(self, mec_path):
        mecfile = open(mec_path, "r")
        mecfile_lines = mecfile.readlines()

        i = 0
        while i < len(mecfile_lines):
            (parsed_list, i) = PyUtils.GetParsedBlock(mecfile_lines, i)

            if len(parsed_list) < 2:
                continue
            
            if self.IsValidData(parsed_list):
                self.AddData(parsed_list)
            else:
                if self.AddTempChecker(parsed_list[0]):
                    self.AddData(parsed_list)
    
    def DeleteDataListFromMecFile(self, mec_path):
        mecfile = open(mec_path, "r")
        mecfile_lines = mecfile.readlines()

        i = 0
        while i < len(mecfile_lines):
            prev_line = i
            (parsed_list, i) = PyUtils.GetParsedBlock(mecfile_lines, prev_line)

            if len(parsed_list) < 2:
                continue
            
            if not self.IsValidData(parsed_list):
                continue

            if not self.DelData(parsed_list):
                nGen_New_MecRT.log("Can't Find Data On Line:{}".format(prev_line))