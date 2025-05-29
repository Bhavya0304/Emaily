import json
from flask import Request, Response
from helper.logger import SingletonLogger,LogTypes
import os


class loggerController:
    def __init__(self):
        self.logger = SingletonLogger().get_logger()

    def list(self, req:Request):
        names = [e.name for e in LogTypes]
        return Response(  json.dumps({"types": names}),200,mimetype="application/json")


    def logs(self,req:Request):
        date = req.args["date"]
        logType = req.args["type"]
        if("date" not in req.args.keys() or "type" not in req.args.keys()):
            return Response("Bad Request",400,mimetype="application/json")
        logpath = self.logger.GetLogPath()
        filename = date + "_" + logType + ".txt"
        finalPath = os.path.join(logpath,filename)
        if(os.path.exists(finalPath)):
            responseLog = ""
            with open(finalPath,"r") as f:
                responseLog = f.read()
            return Response(  responseLog,200,mimetype="application/json")
        else:
            return Response("Log Does Not Exists",400,mimetype="application/json")