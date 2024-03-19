# import imp
# import flask
from flask import request, send_file, json
from app import app
from flask.logging import create_logger
# from werkzeug.exceptions import HTTPException
import logging
from service.ECMResumeAnalysis import ECMResumeAnalysis

#Logging and tracing
LOG = create_logger(app)
LOG.setLevel(logging.INFO)

azObj = ECMResumeAnalysis()

print("-----Cntroller loaded-----")

@app.route("/store")
def get_stores():
    LOG.info("-----------------")
    azObj.searchText()
    return {"stores": "data loaded"}

@app.post("/search")
def searchBestMatch():
    LOG.debug('------search method----')
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        LOG.debug('------content type json----')
        data = json.loads(request.data)
        return azObj.searchTfidVet(data['context'], data['threshold'], data['noOfMatches'])
    else:
        LOG.debug('------content type not json----')
        return azObj.processData('test')
@app.get('/ping')
def pingService():
    return azObj.processData('test')
print("-----Cntroller end-----",app)

