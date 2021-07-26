from ncellapp.signatures import macGen

class NcellApp():
    def __init__(self):
        self.baseUrl = 'https://sca.ncell.axiata.com/adl/et/telco/selfcare/ncell/api/v1.0'
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Connection': 'Keep-Alive',
            'User-Agent': 'okhttp/3.12.6',
        }
        
        self.connectionType = 'wifi'
        self.languageCode = '1'
        self.deviceType = 'android'
        self.deviceModel = 'Samsung Galaxy S7'
        self.token = None