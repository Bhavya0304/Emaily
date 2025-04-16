import sys

class gmailController:
    def __init__(self):
        pass

    def connect(self,req):
        print(req,file=sys.stdout)
        return "gmail connectened"
        