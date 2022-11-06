#!/usr/bin/env python
import os
from pathlib import Path
import requests

# Superset API endpoint
BASE_URL = "http://localhost:8088/api/v1/"
login_data = {"password": "admin", "provider": "db", "refresh": True, "username": "admin"}
LOGIN_URL = BASE_URL + "security/login"
IMPORT_URL = BASE_URL + "assets/export"
IMPORT_PATH = Path(os.getcwd()) / "superset/backups/export_assets.zip"

with requests.Session() as session:
    access_token = session.post(LOGIN_URL, json=login_data).json().get("access_token")

    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "multipart/form-data",
    }
    data = {"databases/PostgreSQL.yaml": os.getenv("PAH_POSTGRES_PASSWORD", "password")}
    files = {"bundle": IMPORT_PATH.open("rb")}
    imp = session.post(IMPORT_URL, headers=headers, files=files, data=data)
    if imp.status_code == 200:
        print("Import successful")
    else:
        print("Import failed with status code {}".format(imp.status_code))
        print(imp.text)
