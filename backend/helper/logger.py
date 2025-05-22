import os
import datetime


class Logger:
    def __init__(self,path=None):
        self.funcs = []
        self.path = path

    def Log(self,Category,message):
        if self.path == None:
            self.path = os.path.join(os.getcwd(),"logs")
        file_name = str(datetime.date.today()) + "_" + Category + ".txt"
        final_path = os.path.join(self.path,file_name)
        dir_path = os.path.dirname(final_path)
        print(dir_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        print(final_path)
        with open(final_path,'a+') as fp:
            fp.write("\n\n----------------------\n" + message + "\n------------------------\n\n")


        # extra events to be added to logger
        for func in self.funcs:
            func()

    def setPostLog(self,func):
        self.funcs = self.funcs.append(func)