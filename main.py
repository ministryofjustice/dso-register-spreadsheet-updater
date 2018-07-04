import argparse
import json
import os
import subprocess
import sys

from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.compute import ComputeManagementClient

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def main():
    parser = argparse.ArgumentParser(description=
    'Publish VM lists from azure into a google sheet'
    )
    parser.add_argument("--creds",
        help="Path to creds.json",
        type=argparse.FileType('r+'),
        default='creds.json'
    )

    subparsers = parser.add_subparsers(metavar="subcommand", dest="subcommand")
    subparsers.required = True

    creds_parser = subparsers.add_parser("creds",
        help="Don't publish anything, "
        "just do the auth handshake and write to creds.json"
    )
    creds_parser.add_argument("--client-secret",
        help="Path to client_secret.json",
        default='client_secret.json',
        type=argparse.FileType('r')
    )
    creds_parser.set_defaults(func=generate_creds)

    publish_parser = subparsers.add_parser("publish",
        help="Download the VMs list from Azure and write it to google sheets"
    )
    publish_parser.add_argument("--subscription-id",
        help="Azure Subscription ID (will use az cli's auth)",
        required=True
    )
    publish_parser.add_argument("--spreadsheet-id",
        help="Google Sheets ID",
        required=True
    )
    publish_parser.add_argument("--sheet-name",
        help="Name of sheet inside spreadsheet to write to",
        required=True
    )
    publish_parser.set_defaults(func=publish_vms)

    args = parser.parse_args()

    args.func(args)

def generate_creds(args):
    config = json.load(args.client_secret)
    flow = InstalledAppFlow.from_client_config(config, scopes=SCOPES)
    creds = flow.run_console()

    args.creds.truncate(0)
    args.creds.seek(0)
    json.dump(vars(creds), args.creds, default=lambda x: 0)

    print("Saved credentials to %r" % args.creds.name)

def publish_vms(args):
    header = (
        "Name",
        "Private IPs",
        "Description",
        "Resource Group",
        "VM Size",
        "OS Type",
        "OS Version",
        "Power State",
        "Public IPs",
        "Location",
        "License Requirements"
    )
    rows = [(
        vm["name"],
        vm["privateIps"],
        vm["tags"].get("description"),
        vm["resourceGroup"],
        vm["hardwareProfile"]["vmSize"],
        vm["storageProfile"]["osDisk"]["osType"],
        vm["tags"].get("os_version"),
        vm["powerState"],
        vm["publicIps"],
        vm["location"],
        vm["tags"].get("license_requirements")
    ) for vm in get_vms(args.subscription_id)]

    update_sheet(args, header, rows)

def get_vms(subscription_id):
    print("Loading VMs...")

    subprocess.run(
        ["az", "account", "set", "-s", subscription_id],
        check=True
    )
    return json.loads(subprocess.run(
        ["az", "vm", "list", "--show-details"],
        check=True,
        stdout=subprocess.PIPE
    ).stdout.decode())

def update_sheet(args, header, rows):
    print("Preparing google sheets service")
    service = make_sheet_service(args)

    print("Writing VM Sheet header row")
    service.spreadsheets().values().update(
        spreadsheetId=args.spreadsheet_id,
        range=args.sheet_name + "!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [header]}
    ).execute()

    print("Writing VM Sheet data")
    service.spreadsheets().values().update(
        spreadsheetId=args.spreadsheet_id,
        range=args.sheet_name + "!A2",
        valueInputOption="USER_ENTERED",
        body={"values": rows}
    ).execute()

    print("Done")

def make_sheet_service(args):
    cred_data = json.load(args.creds)
    creds = Credentials(
        cred_data["token"],
        refresh_token=cred_data["_refresh_token"],
        token_uri=cred_data["_token_uri"],
        client_id=cred_data["_client_id"],
        client_secret=cred_data["_client_secret"]
    )
    return build('sheets', 'v4', credentials=creds)

main()
