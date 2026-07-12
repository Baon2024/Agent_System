from pathlib import Path

from fastmcp import FastMCP
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

BASE_DIR = Path(__file__).resolve().parent

CLIENT_SECRET_FILE = (
    BASE_DIR
    / "client_secret_648740632845-52e6g769krpabkj1as56c7o5ik2koblt.apps.googleusercontent.com.json"
)

TOKEN_FILE = BASE_DIR / "token.json"



def get_user_credentials():
    print("BASE_DIR:", BASE_DIR)
    print("CLIENT_SECRET_FILE:", CLIENT_SECRET_FILE, CLIENT_SECRET_FILE.exists())
    print("TOKEN_FILE:", TOKEN_FILE)

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        print("Refreshed token saved")

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRET_FILE),
            SCOPES,
        )

        creds = flow.run_local_server(
            port=0,
            access_type="offline",
            prompt="consent",
        )

        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        print("New token saved to:", TOKEN_FILE)

    return creds


creds = get_user_credentials()
print("Creds valid:", creds.valid)
print("Token exists:", TOKEN_FILE.exists())