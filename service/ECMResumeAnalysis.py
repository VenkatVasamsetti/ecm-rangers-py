from datetime import datetime, timedelta
import json
from flask import make_response, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
# from config.ServiceConfig import serverconfig

from model.MetaData import MetaData
from model.MatchResponse import MatchResponse
from model.Result import Result
import json  
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from azure.storage.blob import BlobServiceClient
import io
import pdfplumber

print("-----ECMResumeAnalysis-------")

class ECMResumeAnalysis():
    def __init__(self):
        CONN_STR = "DefaultEndpointsProtocol=https;AccountName=teststorageaish;AccountKey=iiUkV33CZRzyLbK3mlId75+fKB4bZT01GoAjmAV6eiSY/MfVlqrf8bfL3eopjfnrSmc+tU6vYm5h+AStfB7PMw==;EndpointSuffix=core.windows.net"
        try:
            credential = AzureKeyCredential('wvjaKDw3qX9W49n3g9GHsqH3YTpomkHKBBlSWBRdsSAzSeBHXwZE')
            self.search_service = SearchClient(endpoint='https://aitestcvsearch.search.windows.net', index_name='azureblob-index', credential=credential)
            blobSer = BlobServiceClient.from_connection_string(CONN_STR)
            self.containSer = blobSer.get_container_client('testresumeblobstorage')
        except Exception as e:
            print(e)
    
    def searchText(self, search):
        # print("-----search-----",'INDEX_NAME')

        results = self.search_service.search(search_text=search)
        print('---------data----',str(results))
        df = pd.json_normalize(results,meta = [
                'metadata_storage_file_extension',
                'metadata_storage_last_modified',
                'metadata_storage_last_modified',
                'metadata_storage_name',
                'content',
                'metadata_storage_path',
                'keyphrases',
                '@search.score',
                '@search.reranker_score',
                '@search.highlights',
                '@search.captions'   
                ])
        df['content'] = df.content.apply(lambda x: cleanResume(x))
        df['keyphrases_str'] = df.keyphrases.apply(lambda x: ', '.join([str(i) for i in x]))
        df['keyphrases_str'] = df.keyphrases_str.apply(lambda x: cleanResume(x))
        df['resumadata'] = df['content'] + df['keyphrases_str']
        cv = CountVectorizer()
        df['match_per'] = df['resumadata'].apply(lambda x: findPersent(x, search))
        df = df.sort_values(by=['match_per'], ascending=False)
 
    def searchTfidVet(self, search, threshold, noOfMatches):
        dft = pd.DataFrame(columns=['resume_name', 'resume_data'])
        listBlob = self.containSer.list_blobs()
        for blob in listBlob:
            if blob.name.endswith('.pdf'):
                blobPDF = self.containSer.get_blob_client(blob)
                fileData = blobPDF.download_blob().readall()
                dft.loc[len(dft)] = [blob.name,fileData]
        dft['resume_data'] = dft.resume_data.apply(lambda x: self.getPdfData(x))
        dft['resume_data'] = dft.resume_data.apply(lambda x: self.cleanResume(x))
        dft['match_score'] = dft['resume_data'].apply(lambda x: self.processResumeData(x, search))
        dft['match_score_rnd'] = dft['match_score'].round(decimals= 2)
        confidence_score = dft['match_score_rnd'].sum()
        dftfl = dft[dft.match_score_rnd >= threshold]
        dftfl.sort_values(by=['match_score_rnd'], ascending=False)
        count = len(dftfl.index) 
        dftfl = dftfl.head(noOfMatches)
        #process data
        md = MetaData(confidence_score.round(decimals= 2))
        list = []
        for index, row in dftfl.iterrows():
            list.append(Result(index,row['match_score_rnd'],row['resume_name']))     
        mr = MatchResponse('success',count, md, list)
        return  json.dumps(mr,default=lambda o: o.__dict__)
    


    def getPdfData(self,blobPDF):
        pdfText = ''
        filePdf = io.BytesIO(blobPDF)
        with pdfplumber.open(filePdf) as pFile:
            for pg in pFile.pages:
                pdfText += pg.extract_text()
        return pdfText
    
    def processResumeData(self,data, matchKey):
        cv = TfidfVectorizer(sublinear_tf=True, stop_words='english')
        text = [matchKey,data]
        cm = cv.fit_transform(text)
        return cosine_similarity(cm)[0][1] 

    def findPersent(self,data, str):
        text = [data,str]
        cm = cv.fit_transform(text)
        mper = cosine_similarity(cm)[0][1]
        return round(mper*100,2)    

    def cleanResume(self,resumeText):
        resumeText = re.sub('http\S+\s*', ' ', resumeText)  # remove URLs
        resumeText = re.sub('RT|cc', ' ', resumeText)  # remove RT and cc
        resumeText = re.sub('#\S+', '', resumeText)  # remove hashtags
        resumeText = re.sub('@\S+', '  ', resumeText)  # remove mentions
        resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', resumeText)  # remove punctuations
        resumeText = re.sub(r'[^\x00-\x7f]',r' ', resumeText) 
        resumeText = re.sub('\s+', ' ', resumeText)  # remove extra whitespace
        return resumeText
        
    def processData(self, search):
        print('-----process----')
        md = MetaData('cscore')
        rs = Result('1','4','-----')
        mr = MatchResponse('success','1', md, rs)
        return  json.dumps(mr,default=lambda o: o.__dict__)



# def classFromArgs(className, argDict):
#     fieldSet = {f.name for f in fields(className) if f.init}
#     filteredArgDict = {k : v for k, v in argDict.items() if k in fieldSet}
#     return className(**filteredArgDict)