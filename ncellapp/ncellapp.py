import requests
from ast import literal_eval
from base64 import b64encode, b64decode

from emoji import demojize

from ncellapp.models import NcellResponse
from ncellapp.signatures import macGen, tsGen, reqIdGen, tranIdGen

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
        self.deviceId = macGen()
        self.token = None
        
class register(NcellApp): 
    #: Register class contains the methods for registering an account
    def __init__(self, msisdn):
        """
        Args:
            msisdn (string): MSISDN to register
        """

        NcellApp.__init__(self)
        self.msisdn = str(msisdn)
    
    def generateOtp(self):
        """Request Ncell to send OTP to the given number for registration

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/user/otp/generate'
        data = f'{{"generateOTPRequest":{{"msisdn":"{self.msisdn}","deviceId":"{self.deviceId}","action":"LOGIN"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"LOGIN","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        
        response = requests.post(url, headers=self.headers, data=data)
        
        return NcellResponse(response)
    
    def validateOtp(self, otp):
        """Send the OTP to the Ncell server for validation and get the token if correct

        Args:
            otp (string): OTP code

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/user/otp/validate'
        data = f'{{"validateOTPRequest":{{"msisdn":"{self.msisdn}","deviceId":"{self.deviceId}","otpDetail":{{"action":"LOGIN","otp":"{otp}"}}}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"LOGIN","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        
        response = requests.post(url, headers=self.headers, data=data)

        #! If ok, create a b64 encoded token in the format {"msisdn": msisdn, "accessToken": accessToken, "refreshToken": refreshToken}
        if response.json()['responseHeader']['responseCode'] == '200':
            accessToken = response.json()['validateOTPResponse']['accessToken']
            refreshToken = response.json()['validateOTPResponse']['refreshToken']
            self.token = b64encode(f'{{"msisdn":"{self.msisdn}","accessToken":"{accessToken}","refreshToken":"{refreshToken}"}}'.encode()).decode()
          
        return NcellResponse(response)

class ncell(NcellApp):
    #: Ncell class contains the methods for using the features of ncell app  
    def __init__(self, token, autoRefresh=False, afterRefresh=[], args=[]):
        """
        Args:
            token (string): Account token
            autoRefresh (bool, optional): True to automatically refresh the token after it expires. Defaults to False.
            afterRefresh (list, optional): A function to call after refreshing the token in this format: [module, function]. Defaults to None.
            args (string, optional): Arguments to pass in afterRefresh function. Defaults to None.
        """

        NcellApp.__init__(self)
        self.token = token
        self.autoRefresh = autoRefresh
        self.afterRefresh = afterRefresh
        self.args = args

        self.msisdn = literal_eval(b64decode(self.token.encode()).decode())['msisdn']
        self.__accessToken = literal_eval(b64decode(self.token.encode()).decode())['accessToken']
        self.__rToken = literal_eval(b64decode(self.token.encode()).decode())['refreshToken']

        self.headers.update({
            'authorization': f'Bearer {self.__accessToken}',
        })
    
    def refreshToken(self):
        """Refresh the token

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/user/refresh/token'
        data = f'{{"refreshTokenRequest":{{"refreshToken":"{self.__rToken}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"LOGOUT_ACTION","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        #! If token refreshed successfully, change the token variable and update the header
        if response.json()['responseHeader']['responseCode'] == '200':
            self.__accessToken = response.json()['userAuthResponse']['accessToken']
            self.__rToken = response.json()['userAuthResponse']['refreshToken']
            self.token = b64encode(f'{{"msisdn":"{self.msisdn}","accessToken":"{self.accessToken}","refreshToken":"{self.__rToken}"}}'.encode()).decode()

            self.headers.update({
                'authorization': f'Bearer {response.json()["userAuthResponse"]["accessToken"]}',
            })

            #! Call the afterRefresh function
            if self.afterRefresh:
                module = self.afterRefresh[0]
                function = self.afterRefresh[1]

                module = __import__(module)
                function = getattr(module, function)

                if self.args:
                    self.argsCopy = self.args.copy()
                    for i,j in enumerate(self.argsCopy):
                        if j == '__token__':
                            self.argsCopy[i] = self.token
                    function(*self.argsCopy)
                else:
                    function()

        return NcellResponse(response)

    def __autoRefresh(self, response, url, data):
        """Refresh the token automatically after it expires

        Args:
            response (response object): Response object
            url (string): HTTP URL
            data (string): HTTP data

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        #! If token is expired
        if response.json()['responseHeader']['responseDescDisplay'] == 'LGN2001':
            refreshResponse = self.refreshToken()

            #! If token refreshed successfully, request with new token and return the response
            if refreshResponse.responseCode == 200:
                response = requests.post(url, headers=self.headers, data=data)
                
                return NcellResponse(response)
            
            #! If token refreshed failled, return the refreshToken response 
            else:
                return refreshResponse     
            
        #! If token is not epired, return the response
        else:
            return NcellResponse(response)

    def config(self):
        """Get the basic app configuration

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/utilitymgt/app-basic-config/view'
        data = f'{{"basicAppInfo":{{"langCode":"en","osType":"{self.deviceType.upper()}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"BASIC_CONFIG_ACTION","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def profile(self):
        """Get the user's profile

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/subscriber/profile/query'
        data = f'{{"querySubscriberProfileRequest":{{"msisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"PROFILE","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def balance(self):
        """Get the user's balance

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/balance/query'
        data = f'{{"queryBalanceRequest":{{"deviceId":"{self.deviceId}","msisdn":"{self.msisdn}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"MY_SERVICES","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)
        
        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def notifications(self):
        """Get notifications

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + 'notificationmgt/notification/query'
        data = f'{{"notificationQueryRequest":{{"msisdn":["{self.msisdn}"]}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"NOTIFICATIONS","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def recommendation(self):
        """Get recommendations

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/recommendationmgt/recommendation/details'
        data = f'{{"recommendationDetailRequest":{{"deviceId":"{self.deviceId}","msisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"TRAY_ACTION","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def subscribedProducts(self):
        """Get the subscribed products

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/billingmgt/vas/subscribedproducts/query'
        data = f'{{"queryAllProductsRequest":{{"deviceId":"{self.deviceId}","msisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"MY_SERVICES","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def sendFreeSms(self, destination, text, schedule='null'):
        """Send free SMS

        Args:
            destination (string): MSISDN to send free SMS
            text (string): Text to send
            schedule (str, optional): Schedule the SMS. Defaults to 'null'. (Currently Ncell don't support scheduling)

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/smsmgt/free/sms/send'
        text = demojize(text).replace('\n','')

        data = f'{{"sendSMSFreeRequest":{{"source":"{self.msisdn}","destination":"{destination}","content":"{text}","schedule":{schedule},"isConfirm":0}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"MY_SERVICES","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def sendSms(self, destination, text, schedule='null'):
        """Send SMS using current data plan

        Args:
            destination (string): MSISDN to send SMS
            text (string): Text to send
            schedule (str, optional): Schedule the SMS. Defaults to 'null'. (Currently Ncell don't support scheduling)

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/smsmgt/free/sms/send'
        text = demojize(text).replace('\n','')
        data = f'{{"sendSMSFreeRequest":{{"source":"{self.msisdn}","destination":"{destination}","content":"{text}","schedule":{schedule},"isConfirm":1}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"MY_SERVICES","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def rechargeHistory(self):
        """Get the recharge history

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/history/recharge'
        data = f'{{"queryRechargeLogRequest":{{"msisdn":"{self.msisdn}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"RECHARGE_LOG_ACTION","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def selfRecharge(self, rPin):
        """Self recharge with recharge pin

        Args:
            rPin (string): 16 digit recharge pin

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/manual-recharge'
        data = f'{{"manualRechargeInfo":{{"msisdn":"{self.msisdn}","deviceId":"{self.deviceId}","cardPinNumber":"{rPin}","rechargeMode":"PIN"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"RECHARGE_SELF","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def recharge(self, destination, rPin):
        """Recharge balance with recharge pin

        Args:
            destination (string): Destination MSISDN to recharge balance
            rPin (string): 16 digit recharge pin

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/manual-recharge'
        data = f'{{"manualRechargeInfo":{{"msisdn":"{destination}","deviceId":"{self.deviceId}","cardPinNumber":"{rPin}","rechargeMode":"PIN"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"RECHARGE_OTHER","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def selfOnlineRecharge(self, amount):
        """Self online recharge

        Args:
            amount (string): Amount to recharge

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/paymentmgt/url-pin-request'
        data = f'{{"paymentInfo":{{"transactionId":"{tranIdGen()}","msisdn":"{self.msisdn}","description":"Recharge Action","amount":"{amount}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"ONLINE","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def onlineRecharge(self, amount, destination):
        """Online recharge

        Args:
            amount (string): Amount to recharge
            destination (string): Destination MSISDN to recharge balance

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/paymentmgt/url-pin-request'
        data = f'{{"paymentInfo":{{"transactionId":"{tranIdGen()}","msisdn":"{destination}","description":"Recharge Action","amount":"{amount}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"ONLINE","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def takeLoan(self):
        """Apply for loan

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/apply-loan'
        data = f'{{"creditLoanInfo":{{"msisdn":"{self.msisdn}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"LOAN_ACTION","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}' 
        
        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def balanceTransferHistory(self):
        """Get the balance transfer history

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/history/balance-transfer'
        data = f'{{"balanceTransferHistoryRequest":{{"msisdn":"{self.msisdn}"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"BALANCE_TRANSFER","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def balanceTransfer(self, destination, amount):
        """Transfer balance

        Args:
            destination (string): MSISDN to transfer the balance
            amount (string): Amount to transfer

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/balance-transfer'
        data = f'{{"balanceTransferInfo":{{"sender":"{self.msisdn}","receiver":"{destination}","amount":"{amount}","deviceId":"{self.deviceId}","otpDetails":{{"otpState":"GENERATE","otp":""}}}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"BALANCE_TRANSFER","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def confirmBalanceTransfer(self, destination, amount, otp):
        """Confirm the balance transfer

        Args:
            destination (string): MSISDN to transfer the balance
            amount (string): Amount to transfer
            otp (string): OTP code

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/balance-transfer'
        data = f'{{"balanceTransferInfo":{{"sender":"{self.msisdn}","receiver":"{destination}","amount":"{amount}","deviceId":"{self.deviceId}","otpDetails":{{"otpState":"VALIDATE","otp":"{otp}"}}}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"BALANCE_TRANSFER","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def dataPlans(self, categoryId=None, keyword=''):
        """Get data plans

        Args:
            categoryId (string, optional): Category ID to get the plans of certain category. Defaults to None.
            keyword (string, optional): Keywords to search the plans.

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/product/data-plans'
        
        if categoryId:
            data = f'{{"languageCode":"{self.languageCode}","keyword":"{keyword}","pageableDto":{{"pageNumber":1,"pageSize":50}},"categoryId":{categoryId},"sortby":null,"msisdn":"{self.msisdn}","requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"SHOP","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        else:
            data = f'{{"languageCode":"{self.languageCode}","keyword":"{keyword}","pageableDto":{{"pageNumber":1,"pageSize":50}},"sortby":null,"msisdn":"{self.msisdn}","requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"SHOP","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        
        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def voiceAndSmsPlans(self, categoryId=None, keyword=''):
        """Get voice and SMS plans

        Args:
            categoryId (string, optional): Category ID to get the plans of certain category. Defaults to None.
            keyword (string, optional): Keywords to search the plans.

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/product/voice-plans'
        
        if categoryId:
            data = f'{{"languageCode":"{self.languageCode}","keyword":"{keyword}","pageableDto":{{"pageNumber":1,"pageSize":50}},"categoryId":{categoryId},"sortby":null,"msisdn":"{self.msisdn}","requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"SHOP","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        else:
            data = f'{{"languageCode":"{self.languageCode}","keyword":"{keyword}","pageableDto":{{"pageNumber":1,"pageSize":50}},"sortby":null,"msisdn":"{self.msisdn}","requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"SHOP","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        
        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def vasPlans(self, categoryId=None, keyword=''):
        """Get VAS plans and products

        Args:
            categoryId (string, optional): Category ID to get the plans of certain category. Defaults to None.
            keyword (string, optional): Keywords to search the plans.

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/product/vas-plans'
        
        if categoryId:
            data = f'{{"languageCode":"{self.languageCode}","keyword":"{keyword}","pageableDto":{{"pageNumber":1,"pageSize":50}},"categoryId":{categoryId},"sortby":null,"msisdn":"{self.msisdn}","requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"SHOP","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        else:
            data = f'{{"languageCode":"{self.languageCode}","keyword":"{keyword}","pageableDto":{{"pageNumber":1,"pageSize":50}},"sortby":null,"msisdn":"{self.msisdn}","requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"SHOP","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        
        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def subscribeProduct(self, subscriptionCode):
        """Subscribe a product

        Args:
            subscriptionCode (string): Subscription code of a product

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/billingmgt/product/subscribe'
        data = f'{{"productSubscriptionSummaryRequest":{{"deviceId":"{self.deviceId}","msisdn":"{self.msisdn}","subscriptionCode":"{subscriptionCode}","productName":"Monthly voice pack 720min","productPrice":"306.46","ncellProductName":"Monthly voice pack 720min","medium":"APP","linkId":"00000000000000000"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"SUBSCRIBE","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)
 
    def unsubscribeProduct(self, subscriptionCode):
        """Unsubscribe a product

        Args:
            subscriptionCode (string): Subscription code of a product

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/billingmgt/product/unsubscribe'
        data = f'{{"productSubscriptionSummaryRequest":{{"deviceId":"{self.deviceId}","msisdn":"{self.msisdn}","subscriptionCode":"{subscriptionCode}","productName":"Free Missed Call Notification Service","languageCode":"{self.languageCode}","medium":"APP","linkId":"00000000000000000"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"SUBSCRIBE","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def generateTransactionOtp(self):
        """Generate a transaction OTP

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/otp/generate'
        data = f'{{"generateOTPRequest":{{"msisdn":"{self.msisdn}","deviceId":"{self.deviceId}","subId":"1044209462","action":"TRAN","null":null}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"android","deviceId":"{self.deviceId}","clientip":"N/A","action":"TRANSACTION","connectionType":"wifi","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def validateTransactionOtp(self, otp):
        """Validate the transaction OTP

        Args:
            otp (string): OTP code

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/otp/validate'
        data = f'{{"validateOTPRequest":{{"msisdn":"{self.msisdn}","deviceId":"{self.deviceId}","subId":"1044209462","action":"TRAN","otp":"{otp}","null":null}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"TRANSACTION","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def transactionHistory(self):
        """Get the transaction history

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/transaction/history/detail'
        data = f'{{"transactionDetailRequest":{{"msisdn":"{self.msisdn}","deviceId":"{self.deviceId}","subId":"1044209462","action":"TRAN","dateRange":{{"from":"2021-02-06T00:00:00.000Z","to":"2021-02-12T07:38:09.000Z"}},"pagination":{{"range":100,"start":1,"pageOffSet":1,"totalRecords":0,"originalTotalRecords":0}},"transactionType":"USAGE","timeZone":"America/New_York"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"TRANSACTION","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)

    def transactionSummary(self):
        """Get the transaction summary

        Returns:
            [ncellapp.models.NcellResponse]: Response from the Ncell server
        """

        url = self.baseUrl + '/accountmgt/transaction/history/summary'
        data = f'{{"transactionSummaryRequest":{{"msisdn":"{self.msisdn}","deviceId":"{self.deviceId}","subId":"1044209462","action":"TRAN","dateRange":{{"from":"2021-02-06T00:00:00.000Z","to":"2021-02-12T07:38:09.000Z"}},"transactionType":"USAGE","timeZone":"America/New_York","null":null}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.deviceId}","clientip":"N/A","action":"TRANSACTION","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'

        response = requests.post(url, headers=self.headers, data=data)

        return self.__autoRefresh(response, url, data) if self.autoRefresh else NcellResponse(response)