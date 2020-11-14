import logging
import os

import connexion
from flask import render_template
from flask_cors import CORS

from linkprediction.openapi_server import encoder


def set_cors_headers_on_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, PATCH, OPTIONS'
    return response


app = connexion.App(__name__, 
                    specification_dir='openapi_server/openapi/',
                    options={'swagger_ui': False})

app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            pythonic_params=True)
app.app.after_request(set_cors_headers_on_response)

CORS(app.app)

def run_webserver():
    """Start the webserver on localhost:8080."""
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(port=8080, debug=False)
