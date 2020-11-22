from ast import literal_eval

from ncellapp.aescipher import AESCipher

class NcellResponse(object):
    def __init__(self, response, customOp=None, customError=None):
        self.aes = AESCipher()
        self.response = response
        self.customOp = customOp
        self.customError = customError
        
        try:
            self.responseDict = literal_eval(self.aes.decrypt(self.response.text))['businessOutput']
        except AttributeError:
            self.responseDict = None
                       
    def __repr__(self):
        return f'<OperationStatus [{self.opStatus}]>'
    
    @property
    def cacheDataInMins(self):
        try:
            return self.responseDict['cacheDataInMins']
        except AttributeError:
            pass
    
    @property
    def currentDate(self):
        try:
            return self.responseDict['currentDate']
        except AttributeError:
            pass
    
    @property
    def opStatus(self):
        try:
            if self.customOp:
                return self.customOp
            else:
                return self.responseDict['opStatus']
        except AttributeError:
            pass

    @property
    def errorMessage(self):
        try:
            if self.customError:
                return self.customError
            else:
                return self.responseDict['errorMessage']
        except AttributeError:
            pass
        
    @property
    def content(self):
        return self.responseDict
    
    @property
    def cookies(self):
        try:
            return self.response.cookies
        except AttributeError:
            pass
    
    @property
    def elapsed(self):
        try:
            return self.response.elapsed
        except AttributeError:
            pass
    
    @property
    def headers(self):
        try:
            return self.response.headers
        except AttributeError:
            pass
    
    @property
    def ok(self):
        try:
            return self.response.ok
        except AttributeError:
            pass
    
    @property
    def reason(self):
        try:
            return self.response.reason
        except AttributeError:
            pass
    
    @property
    def request(self):
        try:
            return self.response.request
        except AttributeError:
            pass
    
    @property
    def statusCode(self):
        try:
            return self.response.status_code
        except AttributeError:
            pass
    
    @property
    def url(self):
        try:
            return self.response.url
        except AttributeError:
            pass