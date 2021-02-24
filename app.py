from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, Blueprint, abort, request, jsonify
from flask_cors import CORS
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from ner import NerTagger
import json
from pprint import pprint
from flask_swagger_ui import get_swaggerui_blueprint
load_dotenv()
tagger = NerTagger()
app = Flask(__name__)
blueprint_x = Blueprint(name="blueprint_x", import_name=__name__)
spec = APISpec(
    title="NLP API",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description="API for NLP",
        version="1.0.0-oas3",
        contact=dict(
            email="sean830314@gmail.com"
            ),
        license=dict(
            name="Apache 2.0",
            url='http://www.apache.org/licenses/LICENSE-2.0.html'
            )
        ),
    servers=[
        dict(
            description="Test server",
            url="10.0.4.58:3001"
            )
        ],
    tags=[
        dict(
            name="Demo",
            description="Endpoints related to Demo"
            )
        ],
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)
app.register_blueprint(blueprint_x, url_prefix="/api/v1/path_for_blueprint_x")
# Since path inspects the view and its route,
# we need to be in a Flask request context
with app.test_request_context():
  # register all swagger documented functions here
  for fn_name in app.view_functions:
      if fn_name == 'static':
          continue
      print(f"Loading swagger docs for function: {fn_name}")
      view_fn = app.view_functions[fn_name]
      spec.path(view=view_fn)
@blueprint_x.route("/api/v1/ping", methods=["GET"])
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


@blueprint_x.route("/api/v1/predict/model_predict", methods=["POST"])
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


@blueprint_x.route("/api/v1/entities/models_predict", methods=["POST"])
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

@app.route("/api/swagger.json")
def create_swagger_spec():
    return jsonify(spec.to_dict())
def main():
    # We're good to go! Save this to a file for now.
    with open('swagger.json', 'w') as f:
        json.dump(spec.to_dict(), f)

    pprint(spec.to_dict())
    print(spec.to_yaml())
    SWAGGER_URL = '/api/docs'
    API_URL = "/api/swagger.json"

    # Call factory function to create our blueprint
    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "My App"
        }
    )
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
    app.run(host="0.0.0.0", port=3001)



if __name__ == "__main__":
    main()
