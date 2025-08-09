import sys
from flask import Response
from ..helper import auth
from flask import Request,json
import os
import requests
from ..models.mailaccount import Account,MailAccount
from ..models.user import User 
import datetime
from db.neograph.engine.query import Query
from db.neograph.core import Connect
import base64
from services.categorization_service.categorizer import categorize_email
from helper.token_helper import get_valid_token
from helper.logger import LogTypes, SingletonLogger

class gmailController:
    def __init__(self):
        self.query = self.get_query()
        self.logger = SingletonLogger().get_logger()

    def get_query(self):
        driver = Connect.Connect(
            os.getenv("NEO4J_URL"),
            os.getenv("NEO4J_USER"),
            os.getenv("NEO4J_PASSWORD")
        )
        return Query(driver, os.getenv("NEO4J_DB"))
    
    @auth.Authuenticate
    def connect(self,req):
        return Response(json.dumps({"url":f"https://accounts.google.com/o/oauth2/auth?client_id={os.getenv('GOOGLE_CLIENT_ID')}&response_type=code&scope=https://www.googleapis.com/auth/gmail.modify+https://www.googleapis.com/auth/cloud-platform+profile+email&redirect_uri={os.getenv('GOOGLE_CALLBACK_URL')}&state={self.payload['id']}&access_type=offline&prompt=consent"}),200,mimetype="application/json")
        
    def callback(self,req:Request):
        try:
            code = req.args["code"]
            user_id = req.args["state"]
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_SECRET"),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": os.getenv('GOOGLE_CALLBACK_URL')
            }
        
            res = requests.post(token_url, data=data)
            if res.status_code == 200:
                token = res.json()
                print(token,file=sys.stdout)
                usergmailinfo = self.get_user_info(token["access_token"])
                print(usergmailinfo,file=sys.stdout)
                # save token in db
                does_account_exists =  self.GetAccount(user_id)
                        
                gmailaccount = Account(
                    name="Google",
                    token=token["access_token"],
                    tokenexpiry=token["expires_in"],
                    createdon= datetime.date.today(),
                    refreshtoken=token["refresh_token"],
                    refreshtokenexpiry=token["refresh_token_expires_in"],
                    emailid=usergmailinfo["email"]
                )

                user = User()
                user.id = user_id

                query = self.get_query()
                if len(does_account_exists) > 0:
                    gmailaccount.id = does_account_exists[0]['id']

                
                query.UpsertNode(gmailaccount)

                rel = MailAccount(mailtype="Gmail")
                
                mailToAsso = Account()
                mailToAsso.id = gmailaccount.id
                if len(does_account_exists) == 0:
                    query.AssociateNode(user, mailToAsso, relationship=rel)

                # Register Webhook Automatically
                self.registerWebhookForGmail(token["access_token"],usergmailinfo["email"])
            
                return Response(json.dumps({"data":"success"}),200,mimetype="application/json")
            else:
                return Response(json.dumps({"data":"failure"}),500,mimetype="application/json")
        except Exception as e:
            self.logger.Log(LogTypes.Gmail,str(e))
            return Response(json.dumps({"data":"failure"}),500,mimetype="application/json")
    
    def get_user_info(self,access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
        if res.ok:
            return res.json()  # contains email, id, etc.
        else:
            raise Exception(res.text)

    def GetAccount(self,userid):
        query = self.get_query()
        user = User()
        user.id = userid
        mailrel = MailAccount()
        mailrel.id = None
        mailrel.mailtype = "Gmail"
        doesexists = query.GetRelatedNodesWithProps(user,"MAILACCOUNT","OUTGOING",1,mailrel)
        rel_data = []
        for record in doesexists[0]:
            cat_node = record.data()["related"]
            rel_data.append(cat_node)
        print(rel_data)
        return rel_data

    def registerWebhookForGmail(self,accessToken,email):
        webhook_url = "https://www.googleapis.com/gmail/v1/users/me/watch"
        headers = {"Authorization": f"Bearer {accessToken}", "Content-Type": "application/json"}
        data = {"topicName": os.getenv("GOOGLE_GMAIL_TOPIC"), "labelIds": ["INBOX"]}
    
        res = requests.post(webhook_url, headers=headers, json=data)
        historydata = res.json()
        account = Account(emailid=email)
        account.id = None
        account.historyid = historydata.get('historyId')
        self.query.UpsertNode(account, merge_keys=["emailid"])
        print("✅ History ID updated")
        print("📬 Gmail Webhook Response:", historydata)

    def gmailhook(self,req : Request):
        try:
            data = req.get_json()
            print(data, file=sys.stdout)

    # Step 1: Decode the base64-encoded Pub/Sub message
            pubsub_message = data.get("message", {}).get("data")
            if not pubsub_message:
                print("❌ Missing 'data' in Pub/Sub message")
                return Response(json.dumps({"data": "Invalid payload"}), 200, mimetype="application/json")

            decoded_bytes = base64.b64decode(pubsub_message)
            decoded_str = decoded_bytes.decode("utf-8")
            decoded_data = json.loads(decoded_str)

            print("✅ Decoded Pub/Sub data:", decoded_data, file=sys.stdout)

            email = decoded_data.get("emailAddress")
            new_history_id = decoded_data.get("historyId")

            if not email or not new_history_id:
                print("❌ Missing email or historyId in decoded data")
                return Response(json.dumps({"data": "Invalid payload"}), 200, mimetype="application/json")

            print(f"📬 Webhook for {email} with historyId {new_history_id}")

    # Step 2: Find Account node using email
            account = Account(emailid=email)
            account.id = None
            existing_accounts = self.query.GetNode(account)

            if not existing_accounts or not existing_accounts[0]:
                print(f"⚠️ No account found for {email}")
                return Response(json.dumps({"data": "No account found"}), 200, mimetype="application/json")

            account_data = existing_accounts[0][0].data()['n']
            print(account_data,file=sys.stdout)
            old_history_id = account_data.get("historyid")
            access_token = account_data.get("token")
            access_token = get_valid_token(account_data,self.query)

            if not access_token:
                print("❌ No access token stored for this account")
                return Response(json.dumps({"data": "Missing token"}), 200, mimetype="application/json")

            messages = []

                # Step 3: Only call Gmail API if old_history_id exists
            if old_history_id:
                history_url = "https://gmail.googleapis.com/gmail/v1/users/me/history"
                headers = {"Authorization": f"Bearer {access_token}"}
                params = {
                    "startHistoryId": old_history_id,
                    "historyTypes": "messageAdded"
                }

                res = requests.get(history_url, headers=headers, params=params)
                history_data = res.json()

                for hist in history_data.get("history", []):
                    for msg in hist.get("messages", []):
                        messages.append(msg.get("id"))

                if messages:
                    for msg_id in messages:
                        self.fetch_and_save_email(msg_id,access_token,email,account_data['id'])
                    print(f"📝 Pushed {len(messages)} message IDs to Queue")
                else:
                    print("📭 No new messages to log")
            else:
                print("⚠️ No old historyId found — skipping Gmail API call")

    # Step 4: Always update the new historyId
            account.historyid = new_history_id
            self.query.UpsertNode(account, merge_keys=["emailid"])
            print("✅ History ID updated")

            return Response(json.dumps({"data": "OK"}), 200, mimetype="application/json")

        except Exception as e:
            self.logger.Log(LogTypes.Gmail,str(e))
            return Response(json.dumps({"data": "Internal Server Error"}), 200, mimetype="application/json")
    
    def fetch_and_save_email(self,message_id, token, user_email,account_id):
        try:
            url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
            headers = {"Authorization": f"Bearer {token}"}
            params = {"format": "full"}

            res = requests.get(url, headers=headers, params=params)
            if res.status_code != 200:
                print(f"❌ Failed to fetch message {message_id}")
                return

            msg_data = res.json()
            payload = msg_data.get("payload", {})
            headers_list = payload.get("headers", [])

            subject = next((h["value"] for h in headers_list if h["name"] == "Subject"), "(No Subject)")
            sender = next((h["value"] for h in headers_list if h["name"] == "From"), "(No Sender)")

            # Attempt to extract body (plaintext, not attachments or HTML for now)
            body = ""
            if "parts" in payload:
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain":
                        body_data = part["body"].get("data")
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
                            break
            else:
                # fallback to single body
                body_data = payload.get("body", {}).get("data")
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
            email_data = {
                "title": subject,
                "sender": sender,
                "body": body
            }
            category = self.GetCategories(user_email)
            task = categorize_email.delay(email_data, category, "70",message_id,account_id)
            print(f"📨 Sent email {message_id} to categorization task (task_id={task.id})")

        except Exception as e:
            self.logger.Log(LogTypes.Gmail,str(e))
            print(f"🔥 Error fetching message {message_id}: {str(e)}")
    
    def getcategoriesmyemail(self,req:Request):
        email = req.args["email"]
        result = self.GetCategories(email)
        return Response(json.dumps({"data":result}),200,mimetype="application/json") 
    
    def GetCategories(self,email):
        account = Account()
        account.id = None
        account.emailid = email

        result = self.query.GetRelatedNodes(account,"MAILACCOUNT","INCOMING",1)
        userid = result[0][0].data()['related']['id']
        user = User()
        user.id = userid

        categories = self.query.GetRelatedNodes(user, "USERCATEGORIES", direction="OUTGOING")

        cat_data = []
        for record in categories[0]:
            cat_node = record.data()["related"]
            cat_data.append(cat_node) 
        return cat_data   
