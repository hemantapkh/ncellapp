from ncellapp.aescipher import AESCipher
from ast import literal_eval

class NcellResponse(object):
    def __init__(self, response, customOp=None, customError=None):
        self.aes = AESCipher()
        self.response = response
        self.customOp = customOp
        self.customError = customError
        
        try:
            self.responseDict = literal_eval(self.aes.decrypt(self.response.text))['businessOutput']
        except Exception:
            self.responseDict = None
                       
    def __repr__(self):
        return '<OperationStatus [%s]>' % (self.opStatus)
    
    @property
    def cacheDataInMins(self):
        try:
            return self.responseDict['cacheDataInMins']
        except Exception:
            return None
    
    @property
    def currentDate(self):
        try:
            return self.responseDict['currentDate']
        except Exception:
            return None
    
    @property
    def opStatus(self):
        try:
            if self.customOp:
                return self.customOp
            else:
                return self.responseDict['opStatus']
        except Exception:
            return None

    @property
    def errorMessage(self):
        try:
            if self.customError:
                return self.customError
            else:
                return self.responseDict['errorMessage']
        except Exception:
            return None
        
    @property
    def content(self):
        return self.responseDict