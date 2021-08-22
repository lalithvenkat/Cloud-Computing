from datetime import datetime
from os import environ

from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token

firebase_request_adapter = requests.Request()

environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'creds.json'

datastore_client = datastore.Client()

app = Flask(__name__)


# geometryShader,  tesselationShader,  shaderInt16,  sparseBinding,  textureCom-pressionETC2, and vertexPipelineStoresAndAtomics.

def createGPU(name, manufacturer, issuedOn, geometryShader, tesselationShader, shaderInt16, sparseBinding,
              textureComressionETC2, vertexPipelineStoresAndAtomics):
    entity_key = datastore_client.key('GPU', name)
    if (datastore_client.get(entity_key)):
        return False

    entity = datastore.Entity(key=entity_key)
    entity.update({
        "manufacturer": manufacturer,
        "issuedOn": datetime.strptime(issuedOn, "%Y-%m-%d"),
        "geometryShader": geometryShader,
        "tesselationShader": tesselationShader,
        "shaderInt16": shaderInt16,
        "sparseBinding": sparseBinding,
        "textureComressionETC2": textureComressionETC2,
        "vertexPipelineStoresAndAtomics": vertexPipelineStoresAndAtomics
    })
    datastore_client.put(entity)
    return True


def updateGPU(name, manufacturer, issuedOn, geometryShader, tesselationShader, shaderInt16, sparseBinding,
              textureComressionETC2, vertexPipelineStoresAndAtomics):
    entity_key = datastore_client.key('GPU', name)
    entity = datastore_client.get(entity_key)
    if (not entity):
        return False

    entity.update({
        "manufacturer": manufacturer,
        "issuedOn": datetime.strptime(issuedOn, "%Y-%m-%d"),
        "geometryShader": geometryShader,
        "tesselationShader": tesselationShader,
        "shaderInt16": shaderInt16,
        "sparseBinding": sparseBinding,
        "textureComressionETC2": textureComressionETC2,
        "vertexPipelineStoresAndAtomics": vertexPipelineStoresAndAtomics
    })
    datastore_client.put(entity)
    return True


def retrieveGPUs():
    query = datastore_client.query(kind='GPU')
    return [x for x in query.fetch()]


def retrieveGPU(name):
    entity_key = datastore_client.key('GPU', name)
    return datastore_client.get(entity_key)


def queryGPU(geometryShader, tesselationShader, shaderInt16, sparseBinding, textureComressionETC2,
             vertexPipelineStoresAndAtomics):
    query = datastore_client.query(kind='GPU')
    if geometryShader:
        query.add_filter('geometryShader', '=', True)
    if tesselationShader:
        query.add_filter('tesselationShader', '=', True)
    if shaderInt16:
        query.add_filter('shaderInt16', '=', True)
    if sparseBinding:
        query.add_filter('sparseBinding', '=', True)
    if textureComressionETC2:
        query.add_filter('textureComressionETC2', '=', True)
    if vertexPipelineStoresAndAtomics:
        query.add_filter('vertexPipelineStoresAndAtomics', '=', True)

    return [x for x in query.fetch()]


@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    return render_template('index.html', user_data=claims, error_message=error_message, gpus=retrieveGPUs(), query={})


@app.route('/add', methods=['GET', 'POST'])
def add():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if request.method == 'POST':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                if createGPU(name=request.form['name'],
                             manufacturer=request.form['manufacturer'],
                             issuedOn=request.form['issuedOn'],
                             geometryShader='geometryShader' in request.form,
                             tesselationShader='tesselationShader' in request.form,
                             shaderInt16='shaderInt16' in request.form,
                             sparseBinding='sparseBinding' in request.form,
                             textureComressionETC2='textureComressionETC2' in request.form,
                             vertexPipelineStoresAndAtomics='vertexPipelineStoresAndAtomics' in request.form):
                    error_message = "GPU with name {} added".format(request.form['name'])
                else:
                    error_message = "GPU with name {} exists".format(request.form['name'])
            except ValueError as exc:
                error_message = str(exc)

        # return redirect('/add')

    return render_template('index.html', user_data=claims, error_message=error_message, gpus=retrieveGPUs(), query={})


@app.route('/show/<name>', methods=['GET'])
def show(name):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

            except ValueError as exc:
                error_message = str(exc)

        return render_template('show.html', user_data=claims, error_message=error_message, gpu=retrieveGPU(name))

    return redirect('/')


@app.route('/modify/<name>', methods=['GET', 'POST'])
def modify(name):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            except ValueError as exc:
                error_message = str(exc)

        return render_template('modify.html', user_data=claims, error_message=error_message, gpu=retrieveGPU(name))

    if request.method == 'POST':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                if updateGPU(name=request.form['name'],
                             manufacturer=request.form['manufacturer'],
                             issuedOn=request.form['issuedOn'],
                             geometryShader='geometryShader' in request.form,
                             tesselationShader='tesselationShader' in request.form,
                             shaderInt16='shaderInt16' in request.form,
                             sparseBinding='sparseBinding' in request.form,
                             textureComressionETC2='textureComressionETC2' in request.form,
                             vertexPipelineStoresAndAtomics='vertexPipelineStoresAndAtomics' in request.form):
                    error_message = "GPU with name {} updated".format(request.form['name'])
                else:
                    error_message = "GPU with name {} does not exists".format(request.form['name'])
            except ValueError as exc:
                error_message = str(exc)

        return render_template('show.html', user_data=claims, error_message=error_message, gpu=retrieveGPU(name))

    return redirect('/')


@app.route('/query', methods=['GET', 'POST'])
def query():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if request.method == 'POST':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            except ValueError as exc:
                error_message = str(exc)

        gpus = queryGPU(geometryShader='geometryShader' in request.form,
                        tesselationShader='tesselationShader' in request.form,
                        shaderInt16='shaderInt16' in request.form,
                        sparseBinding='sparseBinding' in request.form,
                        textureComressionETC2='textureComressionETC2' in request.form,
                        vertexPipelineStoresAndAtomics='vertexPipelineStoresAndAtomics' in request.form)

        return render_template('index.html', user_data=claims, error_message=error_message, gpus=gpus,
                               query={'geometryShader': 'geometryShader' in request.form,
                                      'tesselationShader': 'tesselationShader' in request.form,
                                      'shaderInt16': 'shaderInt16' in request.form,
                                      'sparseBinding': 'sparseBinding' in request.form,
                                      'textureComressionETC2': 'textureComressionETC2' in request.form,
                                      'vertexPipelineStoresAndAtomics': 'vertexPipelineStoresAndAtomics' in request.form})
    return redirect('/')


@app.route('/compare/<name1>/<name2>', methods=['GET'])
def compare(name1, name2):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None

    if request.method == 'GET':
        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

            except ValueError as exc:
                error_message = str(exc)

        return render_template('compare.html', user_data=claims, error_message=error_message, gpu1=retrieveGPU(name1),
                               gpu2=retrieveGPU(name2))

    return redirect('/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
