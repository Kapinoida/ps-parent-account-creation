"""
Module for interacting with Gmail APIs using service account credentials.
"""

import base64
from email.mime.text import MIMEText

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = "service_account.json"

# Define the scopes required for the Google APIs
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

FROM = "donotreply@min201.org"


def create_gmail_service():
    """
    A function that creates a service for interacting with Google APIs.

    This function initializes credentials based on the service_account.json file or token.json file.
    If the credentials are not valid, it allows the user to log in and refreshes the
    credentials if expired. The function returns a service for the specified Google API with
    the provided credentials.

    Returns:
        service: A service object for interacting with the specified Google API.
    """

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # Delegating domain-wide authority to the service account to a user
    delegated_credentials = credentials.with_subject(FROM)

    return build("gmail", "v1", credentials=delegated_credentials)


def create_message(techs, to, subject, message_text):
    """
    Creates an email message with the given sender, recipient, subject, and message text.

    Args:
        sender (str): The email address of the sender.
        to (str): The email address of the recipient.
        subject (str): The subject of the email.
        message_text (str): The text content of the email.

    Returns:
        dict: A dictionary containing the raw representation of the email message.
    """
    message = MIMEText(message_text, "html")
    message["to"] = to
    message["from"] = FROM
    message["subject"] = subject
    message["cc"] = ", ".join(techs)
    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    return {"raw": raw_message.decode()}


def send_email(tech, to, subject, message_text):
    """
    Sends an email using the Gmail API.

    Args:
        sender (str): The email address of the sender.
        to (str): The email address of the recipient.
        subject (str): The subject of the email.
        message_text (str): The body of the email.

    Returns:
        dict or None: If the email is sent successfully, returns a dictionary containing the
        ID of the sent message.
                      If an error occurs, returns None.

    Raises:
        HttpError: If an HTTP error occurs during the API request.

    This function creates a Gmail service using the provided sender's email address and the
    `create_gmail_service` function.
    It then creates an email message using the `create_message` function with the provided
    sender, recipient, subject, and message text.
    The function sends the email using the Gmail API by calling the `users().messages().send()`
    method with the user ID set to 'me' and the message body.
    If the email is sent successfully, it prints the ID of the sent message and returns the
    sent message dictionary.
    If an error occurs, it prints the error message and returns None.
    """
    service = create_gmail_service()
    message = create_message(tech, to, subject, message_text)
    try:
        sent_message = (
            service.users().messages().send(userId="me", body=message).execute()
        )
        print(f'Message Id: {sent_message["id"]}')
        return sent_message
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
