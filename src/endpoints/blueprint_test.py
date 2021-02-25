from flask import Blueprint

# define the blueprint
blueprint_test = Blueprint(name="blueprint_test", import_name=__name__)


@blueprint_test.route("ping", methods=["GET"])
def ping():
    """
    ---
    get:
      description: ping server
      responses:
        '200':
          description: call successful
        '401':
          description: Unauthorized error
      tags:
          - General API
    """
    ret = {"data": "healthy"}
    return ret
