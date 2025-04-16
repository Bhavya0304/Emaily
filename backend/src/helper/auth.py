import jwt
from jwt.exceptions import ExpiredSignatureError
import sys
from flask import Request,Response,json
import os
from ..models.user import GetUser
import time, datetime
from datetime import timezone

def GenerateJWT(payload,key):
    payload["exp"] = datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(minutes=30)
    token = jwt.encode(
    payload=payload,
    key=key,
    algorithm="HS256",
    
    )
    return token

def VerifyJWT(token,key):
    try:
        return jwt.decode(token,key=key,algorithms=["HS256"])
    except ExpiredSignatureError as e:
        return "Expired"
    except Exception as e:
        return None
    
def DecodeJWT(token):
    try:
        return jwt.decode(token,options={"verify_signature":False})
    except Exception as e:
        return None


def Authuenticate(action):
    def wrapper(*args,**kwargs):
        obj = args[0]
        request : Request = args[1]
        if("Authorization" in list(request.headers.keys())):
            token = request.headers.get("Authorization")
            print(token)
            payload = VerifyJWT(token.replace("Bearer ",""),os.getenv("SECRET_KEY"))
            if payload == None:
                return Response("Unauthorized",401)
            elif payload == "Expired":
                pass
                payload = DecodeJWT(token=token.replace("Bearer ",""))
                print(payload)
                user =  GetUser(payload["id"])
                print(user)
                if(user["refreshToken"] == payload["refreshToken"]):
                    newToken = GenerateJWT({"id":user["id"],"refreshToken":user["refreshToken"]},os.getenv("SECRET_KEY"))
                    return Response(json.dumps({"Token":newToken,"Message":"Try With New Token! Old Token Expired"}),401,mimetype="application/json")
                else:
                    return Response("Unauthorized",401)
                # refreshToken = 
            else:
                obj.payload = payload
                return action(*args,**kwargs)
        else:
            return Response("Unauthorized",401)
        return action(*args,**kwargs)
    return wrapper

