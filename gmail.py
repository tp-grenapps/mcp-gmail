import os.path
import base64
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv
 
load_dotenv()
 
cred_file=os.getenv("CRED_FILE")
token_file = os.getenv("TOKEN_FILE")

# If modifying these scopes, delete the file token.json.
# SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

SCOPES = [
'https://www.googleapis.com/auth/gmail.readonly', # Read-only access
'https://www.googleapis.com/auth/gmail.send', # Send emails
'https://www.googleapis.com/auth/gmail.modify', # Read and modify
'https://www.googleapis.com/auth/gmail.labels', # Manage labels
'https://www.googleapis.com/auth/gmail.compose',  # Create and send
'https://www.googleapis.com/auth/gmail.insert', # Insert messages
'https://www.googleapis.com/auth/gmail.readonly',
'https://mail.google.com/'  # Full access
]


class GoogleMailAPI:
  def __init__(self, credentials_file: str = cred_file, token_file: str = token_file):
    """
    Initialize Google Mail API client
    
    Args:
        credentials_file: Path to your OAuth2 credentials JSON file
        token_file: Path to store the access token
    """
    self.Scopes = SCOPES
    self.credentials_file = credentials_file
    self.token_file = token_file
    self.service = None
    self._authenticate()

  def _authenticate(self):
    """Handle OAuth2 authentication"""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(self.token_file):
      creds = Credentials.from_authorized_user_file(self.token_file, self.Scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            cred_file, SCOPES
        )
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open(self.token_file, "w") as token:
        token.write(creds.to_json())
        
    # Build the service
    self.service = build("gmail", "v1", credentials=creds)    
    print("Successfully authenticated with Google GMail API!")  
      
  # # setup webhook
    # request = {
    #   'labelIds': ['INBOX'],
    #   'topicName': 'projects/mcp-gdrive-api/topics/GoAction'
    # }
    # response = self.service.users().watch(userId='me', body=request).execute()
    # print(response)

  def _setup_webhook(self):
    """Set up a webhook for receiving notifications"""
    request = {
      'labelIds': ['INBOX'],
      'topicName': 'projects/mcp-gdrive-api/topics/GoAction'
    }
    response = self.service.users().watch(userId='me', body=request).execute()
    print("Webhook setup response:", response)
    return response
  
  def list_messages(self):
      # messages
    results = self.service.users().messages().list(userId="me").execute()
    messages = results.get("messages", [])
    # 
    # props = print(dir(service.users().messages()))
    # print(props)
    # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__enter__', '__eq__', 
    # '__exit__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', 
    # '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', 
    # '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', 
    # '__weakref__', '_add_basic_methods', '_add_nested_resources', '_add_next_methods', '_baseUrl', 
    # '_credentials_validated', '_developerKey', '_dynamic_attrs', '_http', '_model', '_requestBuilder', 
    # '_resourceDesc', '_rootDesc', '_schema', '_set_dynamic_attr', '_set_service_methods', '_universe_domain', 
    # '_validate_credentials', 'attachments', 'batchDelete', 'batchModify', 'close', 'delete', 'get', 'import_', 
    # 'insert', 'list', 'list_next', 'modify', 'send', 'trash', 'untrash']
    # 
    
    
    # print(messages)
    
    # for message in messages:
    #   print(dir(message))
    #   ['__class__', '__class_getitem__', '__contains__', '__delattr__', '__delitem__', '__dir__', '__doc__', 
    #    '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getstate__', '__gt__', '__hash__', 
    #    '__init__', '__init_subclass__', '__ior__', '__iter__', '__le__', '__len__', '__lt__', '__ne__', '__new__', 
    #    '__or__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__ror__', '__setattr__', '__setitem__', 
    #    '__sizeof__', '__str__', '__subclasshook__', 'clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 
    #    'pop', 'popitem', 'setdefault', 'update', 'values']
    #   break
    
    # get message 
    results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
    messageIds = results.get('messages', [])
    # # print(messages)
    # # [{'id': '19740c639b178d8c', 'threadId': '19740c639b178d8c'}, 
    # # {'id': '196f932cfd12ad4e', 'threadId': '196f932cfd12ad4e'}, 
    # # {'id': '196a96c1b0a28ca8', 'threadId': '196a96c1b0a28ca8'}]
    message_list = []
    for msgId in messageIds:    
      msg = self.service.users().messages().get(userId='me', id=msgId["id"]).execute()
      # print(msg['snippet'])  # Shows a short preview of the message
      message_list.append({
        "id":msgId["id"],
        "snippet": msg["snippet"]
      })
    return message_list
      
  def list_history(self, history_id=None):
    """  
    # # Your base64-encoded string
    # encoded_data = "eyJlbWFpbEFkZHJlc3MiOiJ0ZWNrcGlvQHNreWRyaXZlc29sdXRpb24uY29tIiwiaGlzdG9yeUlkIjoxNjU1Nzd9"
    # # Decode from base64
    # decoded_bytes = base64.urlsafe_b64decode(encoded_data)
    # decoded_str = decoded_bytes.decode('utf-8')
    # # Convert to JSON
    # data = json.loads(decoded_str)
    # # Print the result
    # # print(data)
    # # # {'emailAddress': 'teckpio@skydrivesolution.com', 'historyId': 165559}
    """
    # history_id = "0"  # Default to a specific history ID if not provided
    history_response = self.service.users().history().list(
      userId='me',  
      startHistoryId=history_id,  # Use the historyId from the decoded data
      maxResults=10,  # Optional: limit the number of history records returned
      # Optional: specify the types of history you want to retrieve
      historyTypes=['messageAdded']
    ).execute()
    print('resp', history_response)
    # # {
    #   # 'history': [{
    #     # 'id': '165583', 
    #     # 'messages': [{'id': '197795d56cdb8fff', 'threadId': '197795d56cdb8fff'}], 
    #     # 'messagesAdded': [{
    #           # 'message': {
    #             # 'id': '197795d56cdb8fff', 
    #             # 'threadId': '197795d56cdb8fff', 
    #             # 'labelIds': ['UNREAD', 'CATEGORY_PERSONAL', 'INBOX']
    #           # }
    #       # }]
    #     # }], 
    #   # 'historyId': '165644'
    # # }
    
    message_list = []
    if 'history' in history_response:
      for record in history_response['history']:
        for msg in record.get('messagesAdded', []):
          msg_id = msg['message']['id']
          message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
          print(f"Message ID: {msg_id}")
          print(f"Snippet: {message['snippet']}")
          message_list.append({
            "id": msg_id,
            "snippet": message['snippet'],
          })
    else:
      print("No history found.")
      
    return message_list   
    
    
  def send_message(self, recipient='', subject='', content=''):
    import base64
    from email.mime.text import MIMEText

    def create_message(to, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw}

    message = create_message(recipient, subject, content)
    send_message = self.service.users().messages().send(userId='me', body=message).execute()
    return (send_message)
  
  def delete_message():	
      pass
  
  def list_labels():
      pass
      # labels
        # results = service.users().labels().list(userId="me").execute()
        # labels = results.get("labels", [])
        
        # if not labels:
        #   print("No labels found.")
        #   return
        # print("Labels:")
        # for label in labels:
        #   print(label["name"])
            
# def main():
#   """Shows basic usage of the Gmail API.
#   Lists the user's Gmail labels.
#   """
#   creds = None
#   # The file token.json stores the user's access and refresh tokens, and is
#   # created automatically when the authorization flow completes for the first
#   # time.
#   if os.path.exists(token_file):
#     creds = Credentials.from_authorized_user_file(token_file, SCOPES)
#   # If there are no (valid) credentials available, let the user log in.
#   if not creds or not creds.valid:
#     if creds and creds.expired and creds.refresh_token:
#       creds.refresh(Request())
#     else:
#       flow = InstalledAppFlow.from_client_secrets_file(
#           cred_file, SCOPES
#       )
#       creds = flow.run_local_server(port=0)
#     # Save the credentials for the next run
#     with open(token_file, "w") as token:
#       token.write(creds.to_json())

#   try:
#     # Call the Gmail API
#     service = build("gmail", "v1", credentials=creds)

#   except HttpError as error:
#     # TODO(developer) - Handle errors from gmail API.
#     print(f"An error occurred: {error}")

def main():
    gmail_api = GoogleMailAPI()
    # gmail_api._setup_webhook()
    print(gmail_api.list_history("166588"))
    pass
    
if __name__ == "__main__":
  main()