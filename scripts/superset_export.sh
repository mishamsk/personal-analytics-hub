#!/usr/bin/env python
import os
from pathlib import Path
import requests

# Superset API endpoint
BASE_URL = "http://localhost:8088/api/v1/"
login_data = {"password": "admin", "provider": "db", "refresh": True, "username": "admin"}
LOGIN_URL = BASE_URL + "security/login"
EXPORT_URL = BASE_URL + "assets/export"
EXPORT_PATH = Path(os.getcwd()) / "superset/backups/export_assets.zip"

with requests.Session() as session:
    access_token = session.post(LOGIN_URL, json=login_data).json().get("access_token")

    headers = {"Authorization": "Bearer " + access_token, "Accept": "application/zip"}
    export = session.get(EXPORT_URL, headers=headers)
    if export.status_code == 200:
        with open(EXPORT_PATH, "wb") as f:
            f.write(export.content)
        print("Exported Superset assets to {}".format(EXPORT_PATH))
    else:
        print("Export failed with status code {}".format(export.status_code))
        print(export.text)
