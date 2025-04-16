import sys
from flask import Response
from ..helper import auth

class gmailController:
    def __init__(self):
        pass
    @auth.Authuenticate
    def connect(self,req):
        print(self.payload)
        return "gmail connectened"
        