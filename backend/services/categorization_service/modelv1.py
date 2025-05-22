from groq import Groq
import os
import json
import sys
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from db.neograph.engine.query import Query
from db.neograph.core import Connect
from src.models.mailaccount import Account
from helper.token_helper import get_valid_token

def get_gmail_service(access_token: str):
    creds = Credentials(token=access_token)
    return build('gmail', 'v1', credentials=creds)

load_dotenv()


class GroqAPI():
    def __init__(self) -> None:
        super().__init__()
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def Get(self,query):
        chat_completion = self.client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": query,
        }
    ],
    model="llama3-8b-8192",
)
        return chat_completion.choices[0].message.content


def Categorize(email_data: dict, categories: list, min_threshold: int = 30,message_id = None,account_id = None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, 'prompts', 'categorization_prompt.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        base_prompt = f.read()

    filled_prompt = base_prompt.replace("{{min_threshold}}", str(min_threshold))
    filled_prompt += f"\n\nCategories:\n{json.dumps(categories, indent=2)}"
    filled_prompt += f"\n\nEmail:\n{json.dumps(email_data, indent=2)}"

    agent = GroqAPI()
    response = agent.Get(filled_prompt)

    try:
        result = json.loads(response)
        print(result,file=sys.stdout)
        category = result['category']
        if(category.lower() != "na"):
            account = get_access_token(account_id)
            token = get_valid_token(account,get_query())
            categorize_and_move_email(token, message_id, category)
        return result
    except json.JSONDecodeError:
        return {"category": "NA", "match_percentage": 0}
    
def get_access_token(account_id):
    act = Account()
    act.id = account_id
    result = get_query().GetNode(act)
    return result[0][0].data()['n']
    


def get_query():
    driver = Connect.Connect(
        os.getenv("NEO4J_URL"),
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD")
    )
    return Query(driver, os.getenv("NEO4J_DB"))   

def get_or_create_label(service, user_id: str, category: str) -> str:
    # Get list of labels
    results = service.users().labels().list(userId=user_id).execute()
    labels = results.get('labels', [])

    for label in labels:
        if label['name'].lower() == category.lower():
            return label['id']

    # If not found, create label
    label_body = {
        'name': category,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }
    new_label = service.users().labels().create(userId=user_id, body=label_body).execute()
    return new_label['id']

def move_email_to_label(service, user_id: str, message_id: str, label_id: str):
    # First, get current labels on the message
    msg = service.users().messages().get(userId=user_id, id=message_id).execute()
    current_labels = msg.get('labelIds', [])

    # Add new label and remove INBOX to "move"
    new_labels = list(set(current_labels + [label_id]))
    if 'INBOX' in new_labels:
        new_labels.remove('INBOX')

    # Modify the message
    service.users().messages().modify(
        userId=user_id,
        id=message_id,
        body={
            'addLabelIds': [label_id],
            'removeLabelIds': ['INBOX']
        }
    ).execute()

def categorize_and_move_email(access_token: str, message_id: str, category: str):
    service = get_gmail_service(access_token)
    user_id = 'me'  # 'me' works for the authenticated user

    label_id = get_or_create_label(service, user_id, category)
    move_email_to_label(service, user_id, message_id, label_id)