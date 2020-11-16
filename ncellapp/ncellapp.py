import requests
from base64 import (b64encode, b64decode)
from ast import literal_eval
from datetime import datetime

from Crypto.Cipher import AES

class AESCipher(object):
    
    def __init__(self):
        self.key = b'zSXdd0rx59ThQlul'
        self.bs = AES.block_size

    def encrypt(self, raw):
        raw = self._pad(raw)
        # zero based byte[16]
        iv = b'\0'*16
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(cipher.encrypt(raw.encode())).decode('UTF-8')

    def decrypt(self, enc):
        enc = b64decode(enc)
        # zero based byte[16]
        iv = b'\0'*16
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc)).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
  
class register(AESCipher): 
      
    def __init__(self, msidn):
        AESCipher.__init__(self)
        self.msidn = msidn
        self.baseUrl = 'http://ssa.ncell.com.np:8080/mc/selfcare/v2/proxy'
        self.headers = {
            'X-MobileCare-AppClientVersion': 'SHn7MOIW3T/R/OL8LsAvxw==',
            'Cache-Control': 'no-cache',
            'X-MobileCare-PreferredLocale': 'cAsAM2g0t7oB6OSJKH1ptQ==',
            'Content-Type': 'application/xml',
            'X-MobileCare-APIKey': 'ABC_KEY',
            'X-MobileCare-AppResolution': 'iRRhXh87ipDTZpyEWGWteg==',
            'X-MobileCare-AppPlatformVersion': 'QJ2ZR3DKpuBfBr7GuTQh7w==',
            'ACCEPT': 'application/json',
            'X-MobileCare-AppPlatformName': 'yEHXRN3mrQMvwG4bfE2ApQ==',
            'Host': 'ssa.ncell.com.np:8080',
            'Connection': 'Keep-Alive',
        }
    
    def sendOtp(self):
        '''[Send OTP to the number for registration]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/register'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><serviceInstance>{self.msidn}</serviceInstance></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)
        
        response = literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
        
        try:
            self.deviceClientId = AESCipher.encrypt(self, response['deviceClientId'])
        except KeyError:
            self.deviceClientId = None
        
        return response
    
    def getToken(self, otp):
        '''[Send the OTP to the Ncell server and return the token if successful]

        Args:
            otp ([string]): [OTP sent in the phone number]

        Returns:
            [dict]: [response from the Ncell server with token]
        '''
        self.headers.update({
            'X-MobileCare-DeviceClientID':  self.deviceClientId,
            'X-MobileCare-MSISDN': self.msidn,          
        })
        
        url = self.baseUrl + '/register'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><otp>{otp}</otp></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)
        
        response = literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
        
        if response['opStatus'] == '0':
            token = b64encode(str({'msidn':self.msidn, 'deviceClientId':self.deviceClientId}).encode()).decode()
            response.update({'token':token})
            
        return response
         
class ncell(AESCipher):
    
    def __init__(self, token):
        AESCipher.__init__(self)
        self.token = token
        self.baseUrl = 'http://ssa.ncell.com.np:8080/mc/selfcare/v2/proxy'
        
    def login(self):
        '''[Extract the msidn and client ID from the token and login]

        Returns:
            [dict]: [returns opStatus=0 if successful]
        '''
        try:
            self.msidn = literal_eval(b64decode(self.token).decode())['msidn']
            self.deviceClientId = literal_eval(b64decode(self.token).decode())['deviceClientId']
        except Exception:
            self.msidn = self.deviceClientId = None
            return {'opStatus': 'invalid', 'errorMessage': 'The token you provided is not valid.'}
        
        self.headers = {
            'X-MobileCare-AppClientVersion': 'SHn7MOIW3T/R/OL8LsAvxw==',
            'Cache-Control': 'no-cache',
            'X-MobileCare-PreferredLocale': 'cAsAM2g0t7oB6OSJKH1ptQ==',
            'Content-Type': 'application/xml',
            'X-MobileCare-APIKey': 'ABC_KEY',
            'X-MobileCare-AppResolution': 'iRRhXh87ipDTZpyEWGWteg==',
            'X-MobileCare-DeviceClientID': self.deviceClientId,
            'X-MobileCare-MSISDN': self.msidn,
            'X-MobileCare-AppPlatformVersion': 'QJ2ZR3DKpuBfBr7GuTQh7w==',
            'ACCEPT': 'application/json',
            'X-MobileCare-AppPlatformName': 'yEHXRN3mrQMvwG4bfE2ApQ==',
            'Host': 'ssa.ncell.com.np:8080',
            'Connection': 'Keep-Alive',            
        }
        
        profile = self.viewProfile()
        
        try:
            self.name = profile['myProfile']['name']
            self.status = profile['myProfile']['status']
            self.partyID = profile['myProfile']['partyID']
            self.accountId = profile['myProfile']['accountID']
            self.serviceFlag = profile['myProfile']['serviceFlag']
            self.currentPlan = profile['myProfile']['currentPlan']
            self.secureToken = profile['myProfile']['secureToken']
            self.hubID = profile['myProfile']['hubID']
            return {'opStatus': '0', 'errorMessage': 'SUCCESS'}
            
        except KeyError:
            self.name = self.status = self.partyID = self.accountId = self.serviceFlag = self.currentPlan = self.secureToken = self.hubID = None
            return {'opStatus': 'expired', 'errorMessage': 'The token you provided has expired.'}
            
    def viewProfile(self):
        '''[View the profile of the account]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/viewMyProfile'

        data = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData /></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)
        
        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def sendSms(self, destination, message, schedule=None):
        '''[Send SMS with the currentPlan]

        Args:
            destination ([int]): [MSIDN of the destination]
            message ([String]): [Message to send]
            schedule ([int], optional): [Schedule date in order of YYYYMMDDHHMMSS format, eg.20201105124500]. Defaults to None.

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/updateServiceRequest'
        schedule = schedule or datetime.now().strftime("%Y%m%d%H%M%S")

        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><userId>{schedule}</userId><problemDesc>{message}</problemDesc><serviceId>SENDSMS</serviceId><accountId>{self.accountId}</accountId><code>{destination}</code><offerId>yes</offerId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)
        
        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def sendFreeSms(self, destination, message, schedule=None):
        '''[Send free 10 SMS]

        Args:
            destination ([int]): [MSIDN of the destination]
            message ([String]): [Message to send]
            schedule ([int], optional): [Schedule date in order of YYYYMMDDHHMMSS format, eg.20201105124500]. Defaults to None.

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/updateServiceRequest'
        schedule = schedule or datetime.now().strftime("%Y%m%d%H%M%S")

        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><userId>{schedule}</userId><problemDesc>{message}</problemDesc><serviceId>SENDSMS</serviceId><accountId>{self.accountId}</accountId><code>{destination}</code><offerId>no</offerId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)
        
        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
        
    def viewBalance(self):
        '''[View the current balance]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/myBalance'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><contractId></contractId><customerId></customerId><code>{self.accountId}</code><accountId>{self.accountId}</accountId><offerId>{self.hubID}</offerId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def selfRecharge(self, rpin):
        '''[Recharging the current account]

        Args:
            rpin ([int]): [16 digit PIN of the recharge card]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><alternateContactNumber></alternateContactNumber><contractId></contractId><customerId></customerId><serviceId>RECHARGENOW</serviceId><code>{rpin}</code></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def recharge(self, destination, rpin):
        '''[Recharging other's account]

        Args:
            destination ([int]): [MSIDN of the destination]
            rpin ([int]): [16 digit PIN of the recharge card]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><alternateContactNumber>{destination}</alternateContactNumber><contractId></contractId><customerId></customerId><serviceId>RECHARGENOW</serviceId><code>{rpin}</code></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def rechargeHistory(self):
        '''[latest balance transfer history]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/rechargeHistory'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><contractId></contractId><customerId></customerId><userId>TransferHistory</userId><accountId>{self.accountId}</accountId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def balanceTransfer(self, destination, amount):
        '''[Initiate the balance transformation to the destination number]

        Args:
            destination ([int]): [MSIDN of the destination]
            amount ([int]): [Amount of balance to transfer]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><alternateContactNumber>{destination}</alternateContactNumber><contractId></contractId><customerId></customerId><action>NEW</action><serviceId>BALANCETRANSFER</serviceId><code>{amount}</code></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def confirmBalanceTransfer(self, otp):
        '''[Confirm the balance transfer]

        Args:
            otp ([int]): [OTP sent in phone number]

        Returns:
            [type]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><password>{otp}</password><contractId></contractId><customerId></customerId><action>NEW</action><serviceId>BALANCETRANSFER</serviceId><offerId>validate</offerId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def viewTransaction(self, transactionsFrom, transactionsTo):
        '''[Initiate to view call history]

        Args:
            transactionsFrom ([int]): [From date in YYYYMMDDHHMMSS order]
            transactionsTo ([int]): [To date in YYYYMMDDHHMMSS order]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/viewTransactions'
        
        self.transactionsFrom = transactionsFrom
        self.transactionsTo = transactionsTo
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>prepaid</lob><userId>{self.transactionsFrom}</userId><code>GET</code><accountId>{self.accountId}</accountId><offerId>{self.transactionsTo}</offerId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def confirmViewTransaction(self, otp):
        '''[Confirm to view call history]

        Args:
            otp ([int]): [OTP sent in phone number]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/viewTransactions'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>prepaid</lob><action>{otp}</action><userId>{self.transactionsFrom}</userId><code>VALIDATE</code><accountId>{self.accountId}</accountId><offerId>{self.transactionsTo}</offerId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def viewService(self, serviceCategory=''):
        '''[View the list of available services to activate]

        Args:
            serviceCategory ([str], optional): [Category of the service]. Defaults to None.

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/viewMyService'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><contractId></contractId><customerId></customerId><code>R3027</code><serviceCategory>{serviceCategory}</serviceCategory><accountId>{self.accountId}</accountId><offerId>{self.hubID}</offerId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def activateService(self, serviceId):
        '''[Activate the certain service]

        Args:
            serviceId ([int]): [Service ID found in isMandatory field of viewService()]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><contractId></contractId><customerId></customerId><serviceId>SUBSCRIBEAPRODUCT</serviceId><code>{serviceId}</code></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def viewOffer(self):
        '''[View the available offer for the account]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/viewOffers'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><customerId></customerId><lob>{self.serviceFlag}</lob><accountId>{self.accountId}</accountId><contractId></contractId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def activateOffer(self, offerId):
        '''[Activate the certain offer]

        Args:
            offerId ([int]): [offer ID found in offerID field of viewOffer()]

        Returns:
            [type]: [description]
        '''
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><contractId></contractId><customerId></customerId><serviceId>SUBSCRIBEAPRODUCT</serviceId><code>{offerId}</code></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']
    
    def view3gPlans(self):
        '''[View available plans for 3G]

        Returns:
            [dict]: [response from the Ncell server]
        '''
        url = self.baseUrl + '/view3gPlans'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><contractId></contractId><customerId></customerId><code>{self.accountId}</code><accountId>{self.accountId}</accountId><offerId>{self.hubID}</offerId></userOperationData></mAppData>"
        data = AESCipher.encrypt(self, data)
        
        self.request = requests.post(url, headers=self.headers, data=data)

        return literal_eval(AESCipher.decrypt(self, self.request.text))['businessOutput']