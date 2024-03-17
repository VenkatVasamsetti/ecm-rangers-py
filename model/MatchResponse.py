from model import MetaData,Result
class MatchResponse(object):
    def __init__(self, status, count, metaData, results):
        self.status=status
        self.count=count
        self.metaData=metaData
        self.results=results