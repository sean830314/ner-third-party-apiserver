"""Flask Application"""

# load libaries
from flask import Flask, jsonify
import sys
from src.api_spec import spec
# load modules
from src.endpoints.blueprint_test import blueprint_test
from src.endpoints.blueprint_nlp import blueprint_nlp
from flask_swagger_ui import get_swaggerui_blueprint
# init Flask app
app = Flask(__name__)

# register blueprints. ensure that all paths are versioned!
app.register_blueprint(blueprint_test, url_prefix="/api/v1/test")
app.register_blueprint(blueprint_nlp, url_prefix="/api/v1/ner")
with app.test_request_context():
    # register all swagger documented functions here
    for fn_name in app.view_functions:
        if fn_name == 'static':
            continue
        print(f"Loading swagger docs for function: {fn_name}")
        view_fn = app.view_functions[fn_name]
        spec.path(view=view_fn)

@app.route("/api/swagger.json")
def create_swagger_spec():
    return jsonify(spec.to_dict())

if __name__ == "__main__":
    ####################
    # FOR DEVELOPMENT
    ####################
    """Definition of the Swagger UI Blueprint."""
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
    app.run(host='0.0.0.0', port=3001, debug=True)


