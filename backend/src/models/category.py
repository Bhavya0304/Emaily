from db.neograph import engine
from db.neograph.engine.query import Query 
import os
from db.neograph.core import Connect

@engine.query.Type("Node")
class Category(engine.query.Objects):
    def __init__(self,name = None,description= None,precision= None):
        super().__init__()
        self.name = name
        self.description = description
        self.precision = precision

@engine.query.Type("Relationship")
class UserCategories(engine.query.Objects):
    def __init__(self):
        super().__init__()


        