from fastapi import FastAPI, Depends, HTTPException,Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import requests
import os
import jwt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import base64
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mock database for users
users_db = {"bhavyajsh": {"password": "testpass", "id": "123"}}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your_secret_key"
EXPIRATION_TIME = timedelta(hours=24)

# OAuth credentials
MICROSOFT_CLIENT_ID = "your_outlook_client_id"
MICROSOFT_CLIENT_SECRET = "your_outlook_client_secret"
GOOGLE_CLIENT_ID = "1012958788516-skml6q80fkm8uev9nvpbiohe69k5og2l.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

# Fake database for storing OAuth tokens
oauth_tokens = {}

# OAuth Login Model
class UserLogin(BaseModel):
    username: str
    password: str

# Generate JWT Token
def create_token(user_id: str):
    payload = {"sub": user_id, "exp": datetime.utcnow() + EXPIRATION_TIME}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    return {"access_token": create_token(user["id"]), "token_type": "bearer"}

@app.get("/outlook/connect")
def connect_outlook():
    return {"url": f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={MICROSOFT_CLIENT_ID}&response_type=code&scope=Mail.ReadWrite Mail.Send offline_access&redirect_uri=http://localhost:8000/outlook/callback"}

@app.get("/outlook/callback")
def outlook_callback(code: str):
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    data = {
        "client_id": MICROSOFT_CLIENT_ID,
        "client_secret": MICROSOFT_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:8000/outlook/callback"
    }
    
    res = requests.post(token_url, data=data)
    if res.status_code == 200:
        token = res.json()
        oauth_tokens["outlook"] = token["access_token"]
        
        # Register Webhook Automatically
        register_outlook_webhook(token["access_token"])
        
        return {"message": "Outlook Connected!"}
    else:
        raise HTTPException(status_code=400, detail="OAuth failed")

def register_outlook_webhook(access_token):
    webhook_url = "https://graph.microsoft.com/v1.0/subscriptions"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {
        "changeType": "created",
        "notificationUrl": "http://localhost:8000/api/outlook/webhook",
        "resource": "/me/messages",
        "expirationDateTime": (datetime.utcnow() + timedelta(days=2)).isoformat() + "Z",
        "clientState": "your_secret"
    }
    res = requests.post(webhook_url, headers=headers, json=data)
    print("📬 Outlook Webhook Response:", res.json())

@app.get("/gmail/connect")
def connect_gmail():
    return {"url": f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&response_type=code&scope=https://www.googleapis.com/auth/gmail.modify+https://www.googleapis.com/auth/cloud-platform&redirect_uri=http://localhost:8000/gmail/callback"}

@app.get("/gmail/callback")
def gmail_callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:8000/gmail/callback"
    }
    
    res = requests.post(token_url, data=data)
    if res.status_code == 200:
        token = res.json()
        oauth_tokens["gmail"] = token["access_token"]
        print(token)
        # Register Webhook Automatically
        register_gmail_webhook(token["access_token"])
        
        return {"message": "Gmail Connected!"}
    else:
        raise HTTPException(status_code=400, detail="OAuth failed")

def register_gmail_webhook(access_token):
    webhook_url = "https://www.googleapis.com/gmail/v1/users/me/watch"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"topicName": "projects/gen-lang-client-0936859336/topics/emaily-webhook", "labelIds": ["INBOX"]}
    
    res = requests.post(webhook_url, headers=headers, json=data)
    print("📬 Gmail Webhook Response:", res.json())


@app.route('/gmail-webhook', methods=['POST'])
async def gmail_webhook(request: Request):
    try:
        data = await request.json()  # ✅ Use FastAPI's request handling
        print("📩 New Gmail Notification:", json.dumps(data, indent=2))

        if "message" in data and "data" in data["message"]:
            encoded_message_data = data["message"]["data"]  # Extract encoded message
            
            # ✅ Decode Base64 message data
            decoded_message = json.loads(base64.b64decode(encoded_message_data).decode("utf-8"))
            message_id = data["message"]["message_id"]
            
            if not message_id:
                print("⚠️ No message_id found in decoded data!")
                return JSONResponse(content={"data": str("yupp")}, status_code=200)
            
            print("📌 Extracted Message ID:", message_id)

            # Fetch email details using the message ID
            access_token = oauth_tokens["gmail"]
            email_details = get_email_details(access_token, data)

            print("📨 Email Details Fetched:", json.dumps(email_details, indent=2))
            return JSONResponse(content={"data": str("yupp")}, status_code=200)

        return JSONResponse(content={"data": str("yupp")}, status_code=200)

    except Exception as e:
        print("❌ Error processing webhook:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

def get_email_details(access_token, pubsub_message):
    decoded_data = base64.b64decode(pubsub_message["message"]["data"]).decode("utf-8")
    email_info = json.loads(decoded_data)

    history_id = email_info.get("historyId")
    if not history_id:
        print("🚨 Error: historyId not found!")
        return None

    print(f"📌 Extracted historyId: {history_id}")

    # Get the correct Gmail Message ID
    message_id = get_latest_message_id(access_token, history_id)
    if not message_id:
        print("🚨 Could not find a valid Gmail message ID!")
        return None

    print(f"📩 Correct Gmail Message ID: {message_id}")

    # Fetch email from Gmail API
    url = f"https://www.googleapis.com/gmail/v1/users/me/messages/{message_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    res = requests.get(url, headers=headers)
    email_data = res.json()

    print("📧 Email Details:", email_data)
    return email_data

def get_latest_message_id(access_token, history_id):
    url = f"https://www.googleapis.com/gmail/v1/users/me/history?startHistoryId={history_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    res = requests.get(url, headers=headers)
    history_data = res.json()
    print(history_data)
    if "history" not in history_data:
        print("🚨 No history records found!")
        return None

    # Find the latest added message
    for event in history_data["history"]:
        if "messagesAdded" in event:
            for message in event["messagesAdded"]:
                return message["message"]["id"]  # This is the correct Gmail message ID

    print("🚨 No new messages found in history!")
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
