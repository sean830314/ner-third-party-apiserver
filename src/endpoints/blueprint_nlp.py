from flask import Blueprint, abort, request

from ner import NerTagger

# define the blueprint
blueprint_nlp = Blueprint(name="blueprint_nlp", import_name=__name__)
tagger = NerTagger()


@blueprint_nlp.route("/api/v1/predict/model_predict", methods=["POST"])
def model_predict():
    """
    ---
    post:
      description: select model type to recognition entities
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                paragraph:          # <!--- form field name
                  type: string
                type:    # <!--- form field name
                  type: string
                  enum: ['Azure', 'NLTK', 'Spacy', 'Stanford_CoreNLP', 'All']
              required:
                - paragraph
                - type
      responses:
        '200':
          description: Success to get entities
        '401':
          description: Unauthorized error
      tags:
          - Third-party NER API
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


@blueprint_nlp.route("/api/v1/entities/models_predict", methods=["POST"])
def models_predict():
    """
    ---
    post:
      description: select paragraph id to recognition entities
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                pid:          # <!--- form field name
                  type: integer
                  enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ,11 ,12, 13, 14, 15]
              required:
                - pid
      responses:
        '200':
          description: Success to get entities
        '401':
          description: Unauthorized error
      tags:
          - Third-party NER API
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
