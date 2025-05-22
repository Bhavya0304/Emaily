from db.neograph import engine
from db.neograph.engine.query import Query 
import os
from db.neograph.core import Connect

@engine.query.Type("Node")
class Account(engine.query.Objects):
    def __init__(self,name = None,token= None,refreshtoken= None,refreshtokenexpiry=None,tokenexpiry=None, createdon=None,tokenupdatedon=None,historyid = None,emailid = None):
        super().__init__()
        self.name = name
        self.refreshtoken = refreshtoken
        self.refreshtokenexpiry = refreshtokenexpiry
        self.token = token
        self.createdon = createdon
        self.tokenupdatedon = tokenupdatedon
        self.tokenexpiry = tokenexpiry
        self.historyid = historyid
        self.emailid = emailid

@engine.query.Type("Relationship")
class MailAccount(engine.query.Objects):
    def __init__(self,mailtype=None):
        super().__init__()
        self.mailtype = mailtype

