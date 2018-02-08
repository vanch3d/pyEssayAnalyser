import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, render_template
from flask_swagger_ui import get_swaggerui_blueprint
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import HTTPException, BadRequestKeyError

from EssayAnalyser.errors import EssayError
from EssayAnalyser.essay import Essay

'''
Setup the Flask environment
'''

# create a flask application
template_dir = os.path.abspath('./templates')
app = Flask(__name__,template_folder=template_dir)

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
    # app.logger.info("sdfdgdfgdfgdfgdfgdfgdf")
    return response


'''
Define the routes
'''

# Main page (?)
@app.route('/')
def hello_world():
    return "Hello World!"


# Various testing pages
@app.route('/test/submit')
def show_submit ():
    return render_template('essay.html')


'''
The Essay Analyser API
'''

# Swagger specification
@app.route('/api/openapi.json')
def get_openapi():
    with open(os.path.abspath("./specs/openapi.json"), "r") as f:
        return f.read()


# Text Analyser
@app.route('/api/analyse', methods=['POST'])
def essay_post_analysis():
    try:
        text = request.form['tcext']
        essay = Essay(text).process()
        json = {
            'data': essay.data,
            'metadata': essay.meta

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
        error = EssayError(500, repr(e))
        error.explanation = e.args
        return error.json(), 500


'''
Swagger UI
'''
SWAGGER_URL = '/api'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/api/openapi.json'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={
        # Swagger UI config overrides
        'app_name': "Test application"
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
