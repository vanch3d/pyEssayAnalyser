import logging
import os
from logging.handlers import RotatingFileHandler

import flask
from flask import Flask, request, jsonify, render_template, make_response
from flask_debugtoolbar import DebugToolbarExtension
from flask_swagger_ui import get_swaggerui_blueprint

from EssayAnalyser.errors import EssayError
from EssayAnalyser.essay import Essay

'''
Setup the Flask environment
'''

# create a flask application
template_dir = os.path.abspath('./templates')
app = Flask(__name__, template_folder=template_dir)

# set a hashed private token for security (secret passed with API request, see below)
# to generate one:
# >>> from argon2 import PasswordHasher
# >>> ph = PasswordHasher()
# >>> hash = ph.hash("token sent with request")
app.ARGON2_TOKEN = '$argon2i$v=19$m=512,t=2,p=2$Zxk+Zi2QSU2KjRmsv8auSg$6Uc8aAjuVCC91f1c9WgM8Q'

# Create the debug toolbar
app.debug = True
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'nvl'  # enable the Flask session cookies
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
app.config['DEBUG_TB_PANELS'] = (
    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask_debugtoolbar.panels.logger.LoggingPanel',
    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
)
toolbar = DebugToolbarExtension(app)


# define middleware
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    # @todo
    # app.logger.info("test")
    return response


'''
Define the routes
'''


# Various testing pages
@app.route('/submit')
def show_submit():
    return render_template('essay.html')


'''
The Essay Analyser API
'''


# Swagger specification
@app.route('/openapi.yml')
def get_openapi():
    with open(os.path.abspath("./specs/openapi.yml"), "r") as f:
        response = make_response(f.read())
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        return response


# Swagger specification
@app.route('/schema/<file>.<ext>')
def get_schema_files(file, ext):
    formats = {
        "json": "application/json",
        "xml" : "text/xml",
        "yml" : "text/vnd.yaml",
        "yaml": "text/vnd.yaml"
    }
    if ext not in formats:
        flask.abort(403)
    try:
        path = f"./specs/schema/{file}.{ext}"
        with open(os.path.abspath(path), "r") as f:
            response = make_response(f.read())
            response.headers['Content-Type'] = f'{formats.get(ext)}; charset=utf-8'
            return response
    except FileNotFoundError:
        flask.abort(404)

# Text Analyser
@app.route('/api/analyse', methods=['POST'])
def essay_post_analysis():
    try:
        text = None
        ctype = request.headers.get('Content-Type')
        if ctype == "text/plain":
            text = request.data.decode("utf-8")
            pass
        elif ctype == "application/json":
            text = request.data.decode("utf-8")
            pass
        elif ctype == "application/x-www-form-urlencoded":
            text = request.form['text']
            pass
        else:
            raise Exception("The format is not recognised by pyEA v3")
            pass

        assert text is not None, "text is null, it cannot be processed by pyEA v3"


        if app.ARGON2_TOKEN is not None:
            # @todo[vanch3d] check for token and argon2 validity
            pass
        essay = Essay(text).process()
        json = {
            'data': essay.data,
            'metadata': essay.metadata
        }
        return jsonify(json), 200

    except EssayError as e:
        # Any unsupported exceptions coming from pyEA
        return e.json(), e.status
    #except HTTPException as e:
    #    error = EssayError(e.code,e.description)
    #    error.explanation = e.args
    #    return error.json(), e.code
    except Exception as e:
        # Any unsupported exceptions coming from code
        error = EssayError(500, e.__class__.__name__)
        error.explanation = e.args
        return error.json(), 500


'''
Swagger UI
'''
SWAGGER_URL = ''  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/openapi.yml'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={
        # Swagger UI config overrides
        'app_name': "Swagger | pyEA v3"
    }
)
# Register blueprint at URL (URL must match the one given to factory function above)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


'''
Running the server manually
'''
if __name__ == '__main__':
    # @todo define a better logger
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.info('openapi is running')
    app.run()
