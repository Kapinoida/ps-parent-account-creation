"""
Module for creating a service for interacting with Google Sheets API.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def create_service(service, version):
    """
    A function that creates a service for interacting with Google Sheets API.

    This function initializes credentials based on the token.json file.
    If the credentials are not valid, it allows the user to log in and refreshes the
    credentials if expired. The function returns a service for the Google Sheets API with
    the provided credentials.

    Returns:
        service: A service object for interacting with the Google Sheets API.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build(service, version, credentials=creds)
