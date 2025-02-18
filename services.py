import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
 
# Define the required scopes for the Gmail API
SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.modify"]
 
def gmail_authenticate():
    """
    Authenticate the user and return the Gmail API service.
    """
    creds = None
    # Check if the token.pickle file exists (stores access and refresh tokens)
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
 
    # If no valid credentials, initiate the authorization flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
 
    # Return the Gmail API service
    return build('gmail', 'v1', credentials=creds)
