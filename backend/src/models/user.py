from db.neograph import engine


@engine.query.Type("Node")
class User(engine.query.Objects):
    def __init__(self,fullName = None,userName= None,hashpassword= None,salt= None):
        super().__init__()
        self.fullName = fullName
        self.userName = userName
        self.hash = hashpassword
        self.salt = salt