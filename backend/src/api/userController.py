import sys
from flask import Request,json
from flask import Response
import hashlib
import base64
import uuid
from db.neograph.engine.query import Query
from db.neograph.core import Connect
from src.models.user import User
import os
import jwt
from ..helper import auth
from helper.logger import Logger




class userController:
    def __init__(self):
        self.driver = Connect.Connect(os.getenv('NEO4J_URL'),os.getenv('NEO4J_USER'),os.getenv('NEO4J_PASSWORD'))
        self.query = Query(self.driver,os.getenv("NEO4J_DB"))
        self.loggger = Logger()
    def login(self, req):
        try:
            
            data = req.json
            if "username" not in data or "password" not in data:
                return Response(json.dumps({"Message":"Username and Password are Required!"}),400,mimetype="application/json")

            # Step 1: Fetch the user node by username
            userQuery = User(userName=data["username"])
            userQuery.id = None
            result = self.query.GetNode(userQuery)

            if not result:
                return Response(json.dumps({"Message":"Username not found!"}),400,mimetype="application/json")

            user_node = result[0]  # Assuming GetNode returns a list of nodes
            if user_node and len(user_node) == 0:
                return Response(json.dumps({"Message":"Username not found!"}),400,mimetype="application/json")

            userData = user_node[0].data()['n']
            print(userData)
            stored_hash = userData.get("hash")
            salt = userData.get("salt")
            if not stored_hash or not salt:
                return Response(json.dumps({"Message":"Incomplete Data!"}),400,mimetype="application/json")

            # Step 2: Hash the entered password with the stored salt
            t_sha = hashlib.sha512()
            t_sha.update(data["password"].encode('utf-8') + salt.encode('utf-8'))
            hashed_password = base64.urlsafe_b64encode(t_sha.digest()).decode('utf-8')

            # Step 3: Compare with stored hash
            if hashed_password == stored_hash:
                refreshToken = str(uuid.uuid4())
                token = auth.GenerateJWT({"id":userData.get("id"),"refreshToken":refreshToken},os.getenv("SECRET_KEY"))
                newUser = User(refreshToken=refreshToken)
                newUser.id = userData.get("id")
                self.query.UpsertNode(newUser)
                return Response(json.dumps({"Message":"Login Successfull!","accessToken":token}),200,mimetype="application/json")
            else:
                return Response(json.dumps({"Message":"Invalid Credentails!"}),401,mimetype="application/json")
        except Exception as e:
            self.loggger.Log("API",str(e))
            return Response(json.dumps({"Message":"Something Went Wrong!"}),500,mimetype="application/json")


    def register(self,req : Request):
        try:
            data = req.json
            print(data)
            salt = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')
            t_sha = hashlib.sha512()
            t_sha.update(str(data["password"]).encode('utf-8') + salt.encode('utf-8'))
            hashed_password = base64.urlsafe_b64encode(t_sha.digest())
            userData = User(fullName=data["fullname"],userName=data["username"],hashpassword=hashed_password.decode('utf-8'),salt=salt)
            self.query.UpsertNode(userData)
            return Response(json.dumps({"Message":"Registration Successfull!"}),200,mimetype="application/json")
        except Exception as e:
            self.loggger.Log("API",str(e))
            return Response(json.dumps({"Message":"Something Went Wrong!"}),500,mimetype="application/json")
    

