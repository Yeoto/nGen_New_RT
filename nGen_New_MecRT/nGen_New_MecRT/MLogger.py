import os
import logging
from junit_xml import TestSuite, TestCase
import shutil

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
        self.TestCases = []
        self.LoggerPath = ''
        self.JunitPath = ''
        self.StakcedLog = []

    def DefineLogger(self, root_path, junit_path):
        self.logger = logging.getLogger('nGen_MecRT')
        self.logger.setLevel(logging.DEBUG)
        self.LoggerPath = root_path
        self.JunitPath = junit_path

        handler = logging.FileHandler(root_path + "\\log.log", "w", encoding='utf-8')
        handler.setLevel(logging.DEBUG)
        handlerSt = logging.StreamHandler()
        handlerSt.setLevel(logging.DEBUG)

        formatter = logging.Formatter(fmt='%(message)s')

        handler.setFormatter(formatter)
        handlerSt.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.addHandler(handlerSt)

    def AppendCase(self, Name, Message, lvl = logging.INFO):
        test_case = TestCase(Name)
        if lvl == logging.WARN:
            test_case.add_skipped_info(Message)
        elif lvl == logging.ERROR:
            test_case.add_failure_info(Message)

        self.TestCases.append(test_case)
        self.log(Message, lvl)

    def log(self, message, lvl = logging.INFO):
        if len(message) > 0 and message[-1] == '\n':
            message = message[0:-1]

        if self.logger:
            self.logger.log(lvl, message)
        else:
            logging.log(lvl, message)

    def stackLog(self, message, lvl = logging.INFO):
        LogData = (message, lvl)
        self.StakcedLog.append(LogData)

    def PopAllLog(self):
        for LogData in self.StakcedLog:
            message, lvl = LogData
            if self.logger:
                self.logger.log(lvl, message)
            else:
                logging.log(lvl, message)
        self.StakcedLog.clear()

    def ExportXml(self):
        ts = TestSuite("nGen Mec Regression Test", self.TestCases)
        JunitTempPath = self.LoggerPath + "\\junit.xml"
        with open(JunitTempPath, 'w') as f:
            TestSuite.to_file(f, [ts], prettyprint=False)
        f.close()

        shutil.copy(JunitTempPath, self.JunitPath)
