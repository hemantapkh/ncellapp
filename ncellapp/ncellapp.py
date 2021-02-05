import requests
from base64 import (b64encode, b64decode)
from ast import literal_eval
from datetime import datetime

from ncellapp.aescipher import AESCipher
from ncellapp.models import NcellResponse

class NcellApp():
    def __init__(self):
        self.baseUrl = 'http://ssa.ncell.com.np:8080/mc/selfcare/v2/proxy' 
        self.aes = AESCipher()
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
        
class register(NcellApp): 
    #: Register class contains the methods for registering the account.
    #: Every methods returns ncellapp.models.NcellResponse object.
    def __init__(self, msisdn):
        NcellApp.__init__(self)
        self.msisdn = str(msisdn)
        self.deviceClientId = None
    
    def sendOtp(self):
        #: Request Ncell to send OTP to the number for registration
        url = self.baseUrl + '/register'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><serviceInstance>{self.msisdn}</serviceInstance></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        try:
            self.deviceClientId = self.aes.encrypt(r.content['deviceClientId'])
        except KeyError:
            pass
        
        return r
    
    def getToken(self, otp):
        #: Send the OTP to the Ncell server for verification and get token as response if correct
        headers2 = self.headers
        headers2.update({
            'X-MobileCare-DeviceClientID':  self.deviceClientId,
            'X-MobileCare-MSISDN': self.msisdn,          
        })
        
        url = self.baseUrl + '/register'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><otp>{otp}</otp></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=headers2, data=data)
        
        r = NcellResponse(response)
        
        if r.opStatus == '0':
            token = b64encode(str({'msisdn':self.msisdn, 'deviceClientId':self.deviceClientId}).encode()).decode()
            r.content.update({'token':token})
          
        return r
         
class ncell(NcellApp):
    #: Ncell class contains the methods for using the features of ncell app.
    #: Every methods returns ncellapp.models.NcellResponse object.  
    def __init__(self, token):
        NcellApp.__init__(self)
        self.token = token
        self.name = self.msisdn = self.status = self.partyID = self.accountId = self.serviceFlag = self.currentPlan = self.secureToken = self.hubID = None
        
    def login(self):
        #: Extract the msisdn and client ID from the token and view the profile to check the token validity and to extract other important information
        try:
            self.msisdn = literal_eval(b64decode(self.token).decode())['msisdn']
            self.deviceClientId = literal_eval(b64decode(self.token).decode())['deviceClientId']
        except Exception:
            r = NcellResponse(None, customOp='invalid', customError='The token you provided is invalid.')
            return r
        
        self.headers.update({
            'X-MobileCare-DeviceClientID': self.deviceClientId,
            'X-MobileCare-MSISDN': self.msisdn,          
        })
        
        profile = self.viewProfile().content
        
        try:
            self.name = profile['myProfile']['name']
            self.msisdn = profile['myProfile']['MSISDN']
            self.status = profile['myProfile']['status']
            self.partyID = profile['myProfile']['partyID']
            self.accountId = profile['myProfile']['accountID']
            self.serviceFlag = profile['myProfile']['serviceFlag']
            self.currentPlan = profile['myProfile']['currentPlan']
            self.secureToken = profile['myProfile']['secureToken']
            self.hubID = profile['myProfile']['hubID']
            
            r = NcellResponse(None, customOp='0', customError='SUCCESS')
            return r
            
        except KeyError:      
            r = NcellResponse(None, customOp='expired', customError='The token you provided has expired.')
            return r
            
    def viewProfile(self):
        #: View the profile of the account
        url = self.baseUrl + '/viewMyProfile'

        data = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData /></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def sendSms(self, destination, message, schedule=None, serviceFlag=None, accountId=None):
        #: Send SMS with the currentPlan
        url = self.baseUrl + '/updateServiceRequest'
        schedule = schedule or datetime.now().strftime("%Y%m%d%H%M%S")

        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><userId>{schedule}</userId><problemDesc>{message}</problemDesc><serviceId>SENDSMS</serviceId><accountId>{accountId or self.accountId}</accountId><code>{destination}</code><offerId>yes</offerId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def sendFreeSms(self, destination, message, schedule=None, serviceFlag=None, accountId=None):
        #: Send SMS with free 10 SMS plan
        url = self.baseUrl + '/updateServiceRequest'
        schedule = schedule or datetime.now().strftime("%Y%m%d%H%M%S")

        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><userId>{schedule}</userId><problemDesc>{message}</problemDesc><serviceId>SENDSMS</serviceId><accountId>{accountID or self.accountId}</accountId><code>{destination}</code><offerId>no</offerId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
        
    def viewBalance(self, serviceFlag=None, accountId=None, hubID=None):
        #: View the current balance of the account
        url = self.baseUrl + '/myBalance'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><contractId></contractId><customerId></customerId><code>{accountID or self.accountId}</code><accountId>{accountID or self.accountId}</accountId><offerId>{hubID or self.hubID}</offerId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def selfRecharge(self, rpin, serviceFlag=None):
        #: Recharging the current account
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><alternateContactNumber></alternateContactNumber><contractId></contractId><customerId></customerId><serviceId>RECHARGENOW</serviceId><code>{rpin}</code></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def recharge(self, destination, rpin, serviceFlag=None):
        #: Recharging other's account
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><alternateContactNumber>{destination}</alternateContactNumber><contractId></contractId><customerId></customerId><serviceId>RECHARGENOW</serviceId><code>{rpin}</code></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def rechargeHistory(self, serviceFlag=None, accountId=None):
        #: View the recharge history of the account
        url = self.baseUrl + '/rechargeHistory'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><contractId></contractId><customerId></customerId><userId>TransferHistory</userId><accountId>{accountId or self.accountId}</accountId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def balanceTransfer(self, destination, amount, serviceFlag=None):
        #: Initiate the balance transformation to the destination number
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><alternateContactNumber>{destination}</alternateContactNumber><contractId></contractId><customerId></customerId><action>NEW</action><serviceId>BALANCETRANSFER</serviceId><code>{amount}</code></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def confirmBalanceTransfer(self, otp, serviceFlag=None):
        #: Confirm the balance transfer
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><password>{otp}</password><contractId></contractId><customerId></customerId><action>NEW</action><serviceId>BALANCETRANSFER</serviceId><offerId>validate</offerId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def viewTransaction(self, transactionsFrom, transactionsTo, accountId=None):
        #: Initiate to view call history
        url = self.baseUrl + '/viewTransactions'
        
        self.transactionsFrom = transactionsFrom
        self.transactionsTo = transactionsTo
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>prepaid</lob><userId>{self.transactionsFrom}</userId><code>GET</code><accountId>{accountID or self.accountId}</accountId><offerId>{self.transactionsTo}</offerId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def confirmViewTransaction(self, otp, accountID=None):
        #: Confirm to view call history
        url = self.baseUrl + '/viewTransactions'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>prepaid</lob><action>{otp}</action><userId>{self.transactionsFrom}</userId><code>VALIDATE</code><accountId>{accountID or self.accountId}</accountId><offerId>{self.transactionsTo}</offerId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def viewService(self, serviceCategory='', serviceFlag=None, accountID=None, hubID=None):
        #: View the list of available services to activate. Default service category is All.
        url = self.baseUrl + '/viewMyService'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><contractId></contractId><customerId></customerId><code>R3027</code><serviceCategory>{serviceCategory}</serviceCategory><accountId>{accountID or self.accountId}</accountId><offerId>{hubID or self.hubID}</offerId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def activateService(self, serviceId, serviceFlag=None):
        #: Activate the certain service. Note: ServiceID is in isMandatory key instead of serviceId of viewService.
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><contractId></contractId><customerId></customerId><serviceId>SUBSCRIBEAPRODUCT</serviceId><code>{serviceId}</code></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def viewOffer(self, serviceFlag=None, accountID=None):
        #: View the available offer for the account
        url = self.baseUrl + '/viewOffers'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><customerId></customerId><lob>{serviceFlag or self.serviceFlag}</lob><accountId>{accountID or self.accountId}</accountId><contractId></contractId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def activateOffer(self, offerId, serviceFlag=None):
        #: Activate the certain offer
        url = self.baseUrl + '/updateServiceRequest'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{serviceFlag or self.serviceFlag}</lob><contractId></contractId><customerId></customerId><serviceId>SUBSCRIBEAPRODUCT</serviceId><code>{offerId}</code></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r
    
    def view3gPlans(self, serviceFlag=None, accountID=None, hubID=None):
        #: View available plans for 3G
        url = self.baseUrl + '/view3gPlans'
        
        data = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><mAppData><userOperationData><lob>{self.serviceFlag}</lob><contractId></contractId><customerId></customerId><code>{self.accountId}</code><accountId>{self.accountId}</accountId><offerId>{self.hubID}</offerId></userOperationData></mAppData>"
        data = self.aes.encrypt(data)
        
        response = requests.post(url, headers=self.headers, data=data)
        
        r = NcellResponse(response)
        
        return r