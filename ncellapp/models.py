class NcellResponse(object):
    def __init__(self, response):
        self.__response = response
        self.__responseDict = self.__response.json()
        self.__responseDict2 = self.__responseDict.copy()
                       
    def __repr__(self):
        return f"<Response [{self.responseHeader['responseDescDisplay']}]>"
    
    @property
    def responseHeader(self):
        return self.__responseDict['responseHeader']

    @property
    def content(self):
        self.__responseDict2.pop('responseHeader', None)
        return self.__responseDict2
    
    @property
    def cookies(self):
        return self.__response.cookies
    
    @property
    def elapsed(self):
        return self.__response.elapsed
    
    @property
    def headers(self):
        return self.__response.headers
    
    @property
    def ok(self):
        return self.__response.ok
    
    @property
    def reason(self):
        return self.__response.reason
    
    @property
    def request(self):
        return self.__response.request
    
    @property
    def statusCode(self):
        return self.__response.status_code
    
    @property
    def url(self):
        return self.__response.url