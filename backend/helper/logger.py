import os
import datetime
from enum import Enum


class LogTypes(Enum):
    API=1
    LLM=2
    Agent=3
    Gmail=4
    Global=5

class SingletonLogger:
    _instance = None
    _isLoggerActive = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self,path=None):
        if not self.__class__._isLoggerActive:
            self._setup_logger(path)
            self.__class__._isLoggerActive = True

    def _setup_logger(self,path=None):
        self.logger = Logger(path)

    def get_logger(self):
        return self.logger

class Logger:
    def __init__(self,path=None):
        self.funcs = []
        self.path = path
        if self.path == None:
            self.path = os.path.join(os.getcwd(),"logs")

    def Log(self,Category:LogTypes,message):
        
        file_name = str(datetime.date.today()) + "_" + Category.name + ".txt"
        final_path = os.path.join(self.path,file_name)
        dir_path = os.path.dirname(final_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(final_path,'a+') as fp:
            fp.write("\n\n----------------------\n" + message + "\n------------------------\n\n")


        # extra events to be added to logger
        for func in self.funcs:
            func()

    def GetLogPath(self):
        return self.path

    def setPostLog(self,func):
        self.funcs = self.funcs.append(func)