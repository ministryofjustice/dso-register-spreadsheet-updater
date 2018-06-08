"""
Shows basic usage of the Sheets API. Prints values from a Google Spreadsheet.
"""
from __future__ import print_function
from apiclient.discovery import build

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CLIENT_SECRETS = 'creds.json'

flow = InstalledAppFlow.from_client_secrets_file(
    CLIENT_SECRETS, scopes=SCOPES)

creds = flow.run_console()

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
RANGE_NAME = 'Class Data!A2:E'
result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=RANGE_NAME).execute()
values = result.get('values', [])
if not values:
    print('No data found.')
else:
    print('Name, Major:')
    for row in values:
        # Print columns A and E, which correspond to indices 0 and 4.
        print('%s, %s' % (row[0], row[4]))
