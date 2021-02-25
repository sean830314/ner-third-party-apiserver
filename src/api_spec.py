"""OpenAPI v3 Specification"""

# apispec via OpenAPI
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

# Create an APISpec
spec = APISpec(
    title="NER API",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description="API for NER",
        version="1.0.0-oas3",
        contact=dict(email="sean830314@gmail.com"),
        license=dict(
            name="Apache 2.0", url="http://www.apache.org/licenses/LICENSE-2.0.html"
        ),
    ),
    servers=[dict(description="NER server", url="http://localhost:3001")],
    tags=[
        dict(
            name="Third-party NER API",
            description="Endpoints related to third-party NER services",
        ),
        dict(name="General API", description="Endpoints related to General API"),
    ],
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)
