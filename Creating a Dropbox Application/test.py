import uuid
from datetime import datetime, timedelta
from os import environ

from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token

firebase_request_adapter = requests.Request()

environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"

datastore_client = datastore.Client()


def clearAll():
    for k in ["User", "Directory"]:
        query = datastore_client.query(kind=k)
        for q in query.fetch():
            datastore_client.delete(q.key)


clearAll()
