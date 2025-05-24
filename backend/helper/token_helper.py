import requests
import time
import os
from src.models.mailaccount import Account
from db.neograph.engine.query import Query



def get_valid_token(token_info,query:Query):
    if is_expired(token_info["tokenexpiry"]):
        print(f"Refreshing token for {token_info['name']}")
        new_token = refresh_token(token_info["name"], token_info["refreshtoken"])
        if new_token:
            token_info["token"] = new_token["access_token"]
            token_info["tokenexpiry"] = new_token["expires_at"]
            act = Account()
            act.id = token_info["id"]
            act["token"] = token_info["token"]
            act["tokenexpiry"] = token_info["tokenexpiry"]
            query.UpsertNode(act)
    return token_info["token"]

def is_expired(expires_at):
    try:
        return time.time() > float(expires_at) - 200
    except Exception as e:
        print(f"[is_expired error] expires_at: {expires_at}, error: {e}")
        return True

def refresh_token(provider, refresh_token):
    if provider == "Google":
        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_SECRET"),
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
    else:
        raise ValueError("Unsupported provider")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return {
            "access_token": data["access_token"],
            "expires_at": time.time() + data.get("expires_in", 3600)
        }
    else:
        print(f"Token refresh failed: {response.text}")
        return None
