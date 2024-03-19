# import imp
# import flask
from flask import request, send_file, json
from app import app
from flask.logging import create_logger
# from werkzeug.exceptions import HTTPException
import logging
from service.ECMResumeAnalysis import ECMResumeAnalysis

from model.MatchResponse import MatchResponse

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
        data = json.loads(request.data)
        if data['category'] != 'resume':
            LOG.debug('Category is not matching')
            mr = MatchResponse('Bad Request : category is not matching. it should be resume',0, None, None)
            return defaultResp(mr)
        LOG.debug('------content type json----')       
        return azObj.searchTfidVet(data['context'], data['threshold'], data['noOfMatches'])
    else:
        LOG.debug('------content type not json----')
        return azObj.processData('test')
@app.get('/ping')
def pingService():
    mr = MatchResponse('healthy',0, None, None)
    return defaultResp(mr)

def defaultResp(obj):
    return json.dumps(obj,default=lambda o: o.__dict__)
print("-----Cntroller end-----",app)

