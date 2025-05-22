from db.neograph import engine
from db.neograph.engine.query import Query 
import os
from db.neograph.core import Connect

@engine.query.Type("Node")
class User(engine.query.Objects):
    def __init__(self,fullName = None,userName= None,hashpassword= None,salt= None,refreshToken=None):
        super().__init__()
        self.fullName = fullName
        self.userName = userName
        self.hash = hashpassword
        self.salt = salt
        self.refreshToken = refreshToken

def GetUser(id):
    usr = User()
    usr.id = id
    driver = Connect.Connect(os.getenv('NEO4J_URL'),os.getenv('NEO4J_USER'),os.getenv('NEO4J_PASSWORD'))
    query = Query(driver,os.getenv("NEO4J_DB"))
    result = query.GetNode(usr)
    return result[0][0].data()['n']

