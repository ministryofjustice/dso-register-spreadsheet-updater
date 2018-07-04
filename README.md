# DSO Register Spreadsheet Updater

## Requirements

* Python 3.6+
* pipenv

## Setup

```
pipenv install
```

Download `client_secret.json` from Google apps...

## Running

```
pipenv shell
python main.py --help
```

Generate credentials file
```
python main.py creds
```

Populate spreadsheet
```
python main.py --subscription-id XXX --sheet-id XXX --sheet-name XXXX
```

# References

https://stackoverflow.com/questions/47309584/how-do-i-update-my-python-google-sheet-api-credentials-code-to-avoid-package-dep

http://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html
