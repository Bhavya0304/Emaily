from db.neograph import engine


@engine.query.Type("Node")
class User(engine.query.Objects):
    def __init__(self,fullName = None,userName= None,password= None,salt= None):
        super().__init__()
        self.fullName = fullName
        self.userName = userName
        self.password = password
        self.salt = salt

@engine.query.Type("Node")
class Account(engine.query.Objects):
    def __init__(self,uid= None,accountType= None,accessToken= None,refreshToken = None,expiry= None,historyId= None,isConnected= None):
        super().__init__()
        self.name = accountType
        self.uid = uid
        self.accessToken = accessToken
        self.refreshToken = refreshToken
        self.expiry = expiry
        self.historyId = historyId
        self.isConnected = isConnected

@engine.query.Type("Relationship")
class EmailAccount(engine.query.Objects):
    def __init__(self):
        super().__init__()




