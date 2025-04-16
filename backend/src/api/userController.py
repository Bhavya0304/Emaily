import sys
from flask import Request
import hashlib
import base64
import uuid
from db.neograph.engine.query import Query
from db.neograph.core import Connect
from src.models.user import User
from dotenv import load_dotenv
import os


load_dotenv()

class userController:
    def __init__(self):
        self.driver = Connect.Connect(os.getenv('NEO4J_URL'),os.getenv('NEO4J_USER'),os.getenv('NEO4J_PASSWORD'))
        self.query = Query(self.driver,"emailydb")

    def login(self, req):
        try:
            data = req.json
            if "username" not in data or "password" not in data:
                return "Username and password are required"

            # Step 1: Fetch the user node by username
            userQuery = User(userName=data["username"])
            userQuery.id = None
            result = self.query.GetNode(userQuery)

            if not result:
                return "❌ User not found"

            user_node = result[0]  # Assuming GetNode returns a list of nodes
            if user_node and len(user_node) == 0:
                return "❌ User not found"

            userData = user_node[0].data()['n']
            print(userData)
            stored_hash = userData.get("hash")
            salt = userData.get("salt")
            if not stored_hash or not salt:
                return "❌ Incomplete user data (salt or hash missing)"

            # Step 2: Hash the entered password with the stored salt
            t_sha = hashlib.sha512()
            t_sha.update(data["password"].encode('utf-8') + salt.encode('utf-8'))
            hashed_password = base64.urlsafe_b64encode(t_sha.digest()).decode('utf-8')

            # Step 3: Compare with stored hash
            if hashed_password == stored_hash:
                return "✅ Login successful"
            else:
                return "❌ Invalid credentials"
        except Exception as e:
            print("⚠️ Login Error:", e)
            return "An error occurred during login"


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
            return "registration successfully"
        except Exception as e:
            print(e)
            return "An Error Occuered"
    