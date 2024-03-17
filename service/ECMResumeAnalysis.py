from datetime import datetime, timedelta
import json
import jsonpickle
from flask import make_response, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from config.ServiceConfig import serverconfig

from model.MetaData import MetaData
from model.MatchResponse import MatchResponse
from model.Result import Result

print("-----ECMResumeAnalysis-------")

class ECMResumeAnalysis():
    def __init__(self):
        try:
            credential = AzureKeyCredential(serverconfig['STORAGE_ACCOUNT_KEY'])
            self.search_service = SearchClient(endpoint=serverconfig['SEARCH_ENDPOINT'], index_name=serverconfig['INDEX_NAME'], credential=credential)
        except Exception as e:
            print(e)
    
    def searchText(self):
        print("-----search-----",serverconfig['INDEX_NAME'])

        results = self.search_service.search(search_text="test")
        print('---------data----',str(results))
        for result in results:
            print("======>" + str(result))

        
    def processData(self):
        print('-----process----')
        md = MetaData('cscore')
        rs = Result('1','4','-----')
        mr = MatchResponse('success','1', md, rs)
        return  json.dumps(mr,default=lambda o: o.__dict__)



def classFromArgs(className, argDict):
    fieldSet = {f.name for f in fields(className) if f.init}
    filteredArgDict = {k : v for k, v in argDict.items() if k in fieldSet}
    return className(**filteredArgDict)