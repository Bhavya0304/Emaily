import os
import datetime
from helper.token_helper import get_valid_token 
import requests
from db.neograph.core import Connect
from db.neograph.engine.query import Query
from src.models.category import Category,UserCategories
from src.models.user import User
from src.models.mailaccount import Account
from helper.logger import LogTypes, SingletonLogger
from helper import load_env

load_env.Load()

logger = SingletonLogger().get_logger()

class GmailWebhookManager:
    def __init__(self, query):
        self.query = query

    def register_webhook_for_gmail(self, access_token, email):
        try:
            webhook_url = "https://www.googleapis.com/gmail/v1/users/me/watch"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            data = {
                "topicName": "projects/gen-lang-client-0936859336/topics/emaily-webhook",
                "labelIds": ["INBOX"]
            }

            res = requests.post(webhook_url, headers=headers, json=data)
            if res.status_code == 200:
                history_data = res.json()
                account = Account(emailid=email)
                account.id = None
                account.historyid = history_data.get('historyId')
                self.query.UpsertNode(account, merge_keys=["emailid"])
                logger.Log(LogTypes.CRON,f"{email} - History ID updated:" + history_data.get('historyId'))
            else:
                logger.Log(LogTypes.CRON,f"Failed to register watch for {email}: {res.status_code} - {res.text}")
        except Exception as e:
            logger.Log(LogTypes.CRON,str(e))


def GetDB():
    driver = Connect.Connect(
            os.getenv("NEO4J_URL"),
            os.getenv("NEO4J_USER"),
            os.getenv("NEO4J_PASSWORD")
        )
    return Query(driver, os.getenv("NEO4J_DB"))

def main():
    try:
        query = GetDB()
        manager = GmailWebhookManager(query)
        accounts = query.GetNodesByLabel("Account")
        for account in accounts[0]:
            email = account['n'].get('emailid')
            token = account['n'].get('token')
            if email !=None and token != None:
                access_token = get_valid_token(account.data()['n'],query) 
                if access_token:
                    manager.register_webhook_for_gmail(access_token, email)
                else:
                    logger.Log(LogTypes.CRON,f"Skipped {email} due to missing or invalid token.")
            else:
                logger.Log(LogTypes.CRON,f"Token not found for Email {email}")
    except Exception as e:
        logger.Log(LogTypes.CRON,str(e))

if __name__ == "__main__":
    logger.Log(LogTypes.CRON,"Running Gmail watch re-subscription")
    main()