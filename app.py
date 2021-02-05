from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, abort, request
from flask_cors import CORS

from ner import NerTagger

load_dotenv()
tagger = NerTagger()
app = Flask(__name__)
template = {
    "swagger": "2.0",
    "info": {
        "title": "NLP API",
        "description": "API for NLP",
        "contact": {
            "responsibleOrganization": "kroos.chen",
            "responsibleDeveloper": "kroos.chen",
            "email": "sean830314@gmail.com",
            "url": "https://github.com/sean830314",
        },
        "version": "0.0.1",
    },
    "host": "localhost:3001",  # overrides localhost:3001
    "basePath": "/api/v1",  # base bash for blueprint registration
    "schemes": ["http", "https"],
    "operationId": "get nlp result",
}
CORS(app)
Swagger(app, template=template)


@app.route("/api/v1/ping", methods=["GET"])
def ping():
    """
    Get Ping Server
    Ping server
    ---
    tags:
      - General APIs
    produces: application/json,
    responses:
      401:
        description: Unauthorized error
      200:
        description: Server is healthy
    """
    ret = {"data": "healthy"}
    return ret


@app.route("/api/v1/predict/model_predict", methods=["POST"])
def model_predict():
    """
    POST All Enties
    Get All Enties
    ---
    tags:
      - NLP APIs
    produces: application/json,
    parameters:
    - name: paragraph
      in: formData
      type: string
      required: true
    - name: type
      in: formData
      type: string
      enum: ['Azure', 'NLTK', 'Spacy', 'Stanford_CoreNLP', 'All']
      required: true
    responses:
      401:
        description: Unauthorized error
      200:
        description: Success to get entities
    """
    if request.method == "POST":
        try:
            print("Received: ", request.form["paragraph"], request.form["type"])
            response = tagger.predict(request.form["type"], request.form["paragraph"])
            print("Response")
            print(response)
            return response
        except Exception as err:
            print(err)
            abort(500)
    abort(400)


@app.route("/api/v1/entities/models_predict", methods=["POST"])
def models_predict():
    """
    POST Predict All Entities
    Get Predict All Entities
    ---
    tags:
      - NLP APIs
    produces: application/json,
    parameters:
    - name: pid
      in: formData
      type: integer
      enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ,11 ,12, 13, 14, 15]
      required: true
    responses:
      401:
        description: Unauthorized error
      200:
        description: Success to get entities
    """
    if request.method == "POST":
        try:
            print("Received: ", request.form["pid"])
            pid = str(request.form["pid"])
            response = tagger.predict_by_models(pid)
            print("Response")
            print(response)
            return response
        except Exception as err:
            print(err)
            abort(500)
    abort(400)


def main():
    app.run(host="0.0.0.0", port=3001)


if __name__ == "__main__":
    main()
