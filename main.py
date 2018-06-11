"""
Shows basic usage of the Sheets API. Prints values from a Google Spreadsheet.
"""
import json
import os

from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# TODO: creds command which does OAuth and spits out credentials
# TODO: update command which reads from azure and writes to sheet


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CLIENT_SECRETS = 'client_secret.json'
SPREADSHEET_ID= '1rBtFtvJELDrPtkLyOPnYEaWuOzbB0BJDrpEcLTnPeQk'

if 'CREDS' in os.environ:
    cred_data = json.loads(os.environ['CREDS'])
    creds = Credentials(
        cred_data["token"],
        refresh_token=cred_data["_refresh_token"],
        token_uri=cred_data["_token_uri"],
        client_id=cred_data["_client_id"],
        client_secret=cred_data["_client_secret"]
    )
else:
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS, scopes=SCOPES
    )
    creds = flow.run_console()
    print("Pass this json back as an env var called CREDS")
    print(json.dumps({k: v for k, v in vars(creds).items() if k != "expiry"}))

service = build('sheets', 'v4', credentials=creds)

values = [
    ["A","B"],
]

RANGE_NAME = 'AutoProd!A1:P'
result = service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=RANGE_NAME,
    valueInputOption="USER_ENTERED",
    body={"values": values}
).execute()

updatedCells = result.get('updatedCells', 0)

print("Updated %d cells" % updatedCells)
