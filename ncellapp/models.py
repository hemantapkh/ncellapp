class NcellResponse(object):
    def __init__(self, response):
        self.__response = response
        self.__responseDict = self.__response.json()
        self.__responseDict2 = self.__responseDict.copy()
                       
    def __repr__(self):
        return f"<Response [{self.responseHeader['responseDescDisplay']}]>"
    
    @property
    def responseHeader(self):
        """
        Returns a dictionary of response header from ncell
        """
        return self.__responseDict['responseHeader']

    @property
    def content(self):
        """
        Returns the content of the response
        """
        self.__responseDict2.pop('responseHeader', None)
        return self.__responseDict2
    
    @property
    def cookies(self):
        """
        Returns a CookieJar object with the cookies sent back from the server
        """
        return self.__response.cookies
    
    @property
    def elapsed(self):
        """
        Returns a timedelta object with the time elapsed from sending the request to the arrival of the response
        """
        return self.__response.elapsed
    
    @property
    def headers(self):
        """
        Returns a dictionary of response headers
        """
        return self.__response.headers
    
    @property
    def ok(self):
        """
        Returns True if status_code is less than 400, otherwise False
        """
        return self.__response.ok
    
    @property
    def reason(self):
        """
        Returns a text corresponding to the status code of the response
        """
        return self.__response.reason
    
    @property
    def request(self):
        """
        Returns the request object that requested this response
        """
        return self.__response.request
    
    @property
    def statusCode(self):
        """
        Returns a number that indicates the status (200 is OK, 404 is Not Found)
        """
        return self.__response.status_code
    
    @property
    def url(self):
        """
        Returns the URL of the response
        """
        return self.__response.url