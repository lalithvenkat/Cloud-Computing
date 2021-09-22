import uuid
from datetime import datetime, timedelta
from os import environ

from flask import Flask, render_template, request, redirect, json, Response
from google.auth.transport import requests
from google.cloud import datastore, storage
import google.oauth2.id_token

import local_constants

firebase_request_adapter = requests.Request()

environ["GOOGLE_APPLICATION_CREDENTIALS"] = "creds.json"

datastore_client = datastore.Client()

app = Flask(__name__)


class myDict(dict):
    def __getattr__(self, val):
        return self[val]


@app.template_filter()
def parent_path(path):
    path = path.rstrip("/")
    path = path.rpartition("/")
    return path[0] + path[1]


def getShared():
    entity_key = datastore_client.key("Shared", "SHARED")
    if not datastore_client.get(entity_key):
        entity = datastore.Entity(key=entity_key)
        entity.update({
            "shared": []
        })
        datastore_client.put(entity)

    entity = datastore_client.get(entity_key)
    return entity


def addShared(claims, path, file_name):
    entity = getShared()
    shared = entity["shared"]
    blob_name = "{}{}{}".format(claims.get("email"), path, file_name)
    if not blob_name in shared:
        shared.append(blob_name)
    entity.update({
        "shared": shared
    })
    datastore_client.put(entity)


def removeShared(claims, path, file_name):
    entity = getShared()
    shared = entity["shared"]
    blob_name = "{}{}{}".format(claims.get("email"), path, file_name)
    if blob_name in shared:
        shared.remove(blob_name)
    entity.update({
        "shared": shared
    })
    datastore_client.put(entity)


def retrieveBlob(claims, path, file, folder_only=False):
    blob_name = "{}{}{}".format(claims.get("email"), path, file.filename)
    storage_client = storage.Client()
    return storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET,
                                     prefix=blob_name, delimiter="/" if folder_only else None)


def addBlob(claims, path, file):
    storage_client = storage.Client()
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob_name = "{}{}{}".format(claims.get("email"), path, file.filename)

    blob = bucket.blob(blob_name)
    blob.upload_from_file(file)

    entity_parent = retrieveDirectory(claims, path)
    files = entity_parent["files"]
    if not files:
        files = []
    if file.filename not in files:
        files.append(file.filename)
    entity_parent.update({
        "files": files
    })
    datastore_client.put(entity_parent)

    return blob


def deleteBlob(claims, path, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob_name = "{}{}{}".format(claims.get("email"), path, file_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    removeShared(claims, path, file_name)

    entity_parent = retrieveDirectory(claims, path)
    files = entity_parent["files"]
    if not files:
        files = []
    files.remove(file_name)
    entity_parent.update({
        "files": files
    })
    datastore_client.put(entity_parent)

    return blob


def downloadBlob(claims, path, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob_name = "{}{}{}".format(claims.get("email"), path, file_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


def downloadShared(blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


def createDirectory(claims, path, name):
    entity_key = datastore_client.key("User", claims.get("email"), "Directory", "{}{}/".format(path, name))
    if (datastore_client.get(entity_key)):
        return False

    entity = datastore.Entity(key=entity_key)
    entity.update({
        "directories": [],
        "files": []
    })
    datastore_client.put(entity)

    entity_parent = retrieveDirectory(claims, path)
    directories = entity_parent["directories"]
    if not directories:
        directories = []
    directories.append(entity.key)
    entity_parent.update({
        "directories": directories
    })
    datastore_client.put(entity_parent)

    return True


def retrieveDirectory(claims, path):
    entity_key = datastore_client.key("User", claims.get("email"), "Directory", path)
    return datastore_client.get(entity_key)


def deleteDirectory(claims, path):
    if path == "/":
        return False
    entity = retrieveDirectory(claims, path)
    if entity["directories"] or entity["files"]:
        return False

    datastore_client.delete(entity.key)

    path = parent_path(path)



    entity_parent = retrieveDirectory(claims, path)
    directories = entity_parent["directories"]

    if not directories:
        directories = []

    directories.remove(entity.key)
    entity_parent.update({
        "directories": directories
    })
    datastore_client.put(entity_parent)
    return True


def createHome(claims):
    entity_key = datastore_client.key("User", claims.get("email"), "Directory", "/")
    entity = datastore.Entity(key=entity_key)
    entity.update({
        "directories": [],
        "files": []
    })
    datastore_client.put(entity)
    return entity_key


def createUser(claims):
    entity_key = datastore_client.key("User", claims.get("email"))
    if (datastore_client.get(entity_key)):
        return False

    entity = datastore.Entity(key=entity_key)
    entity.update({
        "home": createHome(claims)
    })
    datastore_client.put(entity)
    return True


def retrieveUser(claims):
    entity_key = datastore_client.key("User", claims.get("email"))
    return datastore_client.get(entity_key)


@app.route("/")
def root():
    id_token = request.cookies.get("token")

    return redirect("/home")


@app.route('/home', defaults={'path': ''}, methods=["GET", "POST"])
@app.route('/home/', defaults={'path': ''}, methods=["GET", "POST"])
@app.route('/home/<path:path>', methods=["GET", "POST"])
def home(path):
    path = "/{}".format(path)

    id_token = request.cookies.get("token")

    error_message = None
    error_forward = None
    claims = None
    directory = None
    duplicates = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            createUser(claims)

        except ValueError as exc:
            error_message = str(exc)
            return render_template("refresh.html", path="/home{}".format(path), error_message=error_message)


        if request.method == "POST":
            if "directory_new" in request.form:
                if createDirectory(claims, path, request.form["directory_new"]):
                    error_message = "Directory with name {} created successfully".format(request.form["directory_new"])
                else:
                    error_message = "Directory with name {} exists".format(request.form["directory_new"])

            if "directory_del" in request.form:
                if deleteDirectory(claims, request.form["directory_del"]):
                    error_message = "Directory with name {} deleted successfully".format(request.form["directory_del"])
                else:
                    error_message = "Directory with name {} can't be deleted/not empty".format(
                        request.form["directory_del"])

            if "file_del" in request.form:
                deleteBlob(claims, path, request.form["file_del"])
                error_message = "File with name {} deleted successfully".format(request.form["file_del"])

            if "file_share" in request.form:
                addShared(claims, path, request.form["file_share"])
                error_message = "File with name {} shared successfully".format(request.form["file_share"])

            if "file_unshare" in request.form:
                removeShared(claims, path, request.form["file_unshare"])
                error_message = "File with name {} unshared successfully".format(request.form["file_unshare"])

            if "upload_file" in request.form:
                file = request.files['file_select']
                addBlob(claims, path, file)

            if "download_file" in request.form:
                file_name = request.form['download_file']
                response = Response(downloadBlob(claims, path, file_name), mimetype='application/octet-stream',
                                    headers={
                                        'Content-Disposition': f'attachment; filename={file_name}'
                                    })
                return response

        if claims:
            directory = retrieveDirectory(claims, path)
            hashvals = {}
            for b in retrieveBlob(claims, path, myDict({"filename": ""}), folder_only=True):
                if b.md5_hash not in hashvals.keys():
                    hashvals[b.md5_hash] = []
                hashvals[b.md5_hash].append(b.name.replace(claims.get("email"), "").replace(path, ""))
            duplicates = []
            for k in hashvals.keys():
                if len(hashvals[k]) > 1:
                    duplicates.append(hashvals[k])



    if "error_forward" in request.args:
        error_forward = request.args["error_forward"]

    return render_template("index.html",
                           user_data=claims,
                           directory=directory,
                           error_message=error_message,
                           error_forward=error_forward,
                           duplicates=duplicates,
                           shared=getShared()["shared"],
                           path=path)


@app.route("/exists", methods=["POST"])
def exists():
    data = json.loads(request.data)
    claims = {"email": data["claims"]}
    path = data["path"]
    file = {"filename": data["file"]}

    file = myDict(file)
    blob = [x for x in retrieveBlob(claims, path, file)]

    return json.dumps(len(blob) > 0)


@app.route("/duplicates")
def duplicates():
    claims = None
    duplicates = None
    id_token = request.cookies.get("token")
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            createUser(claims)

        except ValueError as exc:
            error_message = str(exc)
            return render_template("refresh.html", path="/", error_message=error_message)

        hashvals = {}
        for b in retrieveBlob(claims, "/", myDict({"filename": ""})):
            if b.md5_hash not in hashvals.keys():
                hashvals[b.md5_hash] = []
            hashvals[b.md5_hash].append(b.name.replace(claims.get("email"), ""))
        duplicates = []
        for k in hashvals.keys():
            if len(hashvals[k]) > 1:
                duplicates.append(hashvals[k])



    return render_template("duplicates.html",
                           user_data=claims,
                           duplicates=duplicates)


@app.route("/shared", methods=["GET", "POST"])
def shared():
    claims = None
    shared = None
    id_token = request.cookies.get("token")
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            createUser(claims)

        except ValueError as exc:
            error_message = str(exc)
            return render_template("refresh.html", path="/", error_message=error_message)

        shared = getShared()["shared"]

        if request.method == "POST":
            if "download_file" in request.form:
                file_name = request.form['download_file']
                response = Response(downloadShared(file_name), mimetype='application/octet-stream',
                                    headers={
                                        'Content-Disposition': f'attachment; filename={file_name.rpartition("/")[2]}'
                                    })
                return response

    return render_template("shared.html",
                           user_data=claims,
                           shared=shared)


if __name__ == "__main__":
    app.run(host="localhost", port=8081, debug=True)
