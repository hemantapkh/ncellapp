import requests
from base64 import b64encode

from ncellapp.NcellApp import NcellApp
from ncellapp.models import NcellResponse
from ncellapp.signatures import tsGen, reqIdGen, macGen

class register(NcellApp):
    """This class contains the methods for registering an account.

    Args:
        msisdn (string): MSISDN of the user
    
    Attributes:
        baseUrl (string): The base URL of the Ncell API
        headers (string): The headers of the Ncell API
        connectionType (string): Type of the connection. Defaults to 'WIFI'
        languageCode (string): Language code of the API. Defaults to 'en'
        deviceType (string): Type of the device. Defaults to 'ANDROID'
        deviceModel(string): Device model of the device. Defaults to 'Samsung Galaxy S7'
        token (string): Token of the account

    Example:
        >>> from ncellapp import register

        >>> reg = register(msisdn='PHONE NUMBER TO REGISTER')
    """
    def __init__(self, msisdn):
        NcellApp.__init__(self)
        self.msisdn = str(msisdn)
        self.__deviceId = macGen()
    
    def generateOtp(self):
        """Request Ncell to send OTP to the given number for registration

        Returns:
            ncellapp.models.NcellResponse: Response from the Ncell server
        
        Example:
        
            >>> reg.generateOtp()
            <Response [OTP1000]>
        """

        url = self.baseUrl + '/user/otp/generate'
        data = f'{{"generateOTPRequest":{{"msisdn":"{self.msisdn}","deviceId":"{self.__deviceId}","action":"LOGIN"}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.__deviceId}","clientip":"N/A","action":"LOGIN","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        
        response = requests.post(url, headers=self.headers, data=data)
        
        return NcellResponse(response)
    
    def validateOtp(self, otp):
        """Send the OTP to the Ncell server for validation and get the token if correct

        Args:
            otp (string): OTP code

        Returns:
            ncellapp.models.NcellResponse: Response from the Ncell server

        Example:

            >>> reg.validateOtp('123456')
            <Response [OTP1000]>
            >>> reg.token
            'eyJt...'
        """

        url = self.baseUrl + '/user/otp/validate'
        data = f'{{"validateOTPRequest":{{"msisdn":"{self.msisdn}","deviceId":"{self.__deviceId}","otpDetail":{{"action":"LOGIN","otp":"{otp}"}}}},"requestHeader":{{"requestId":"{reqIdGen()}","timestamp":"{tsGen()}","channel":"sca","deviceType":"{self.deviceType}","deviceId":"{self.__deviceId}","clientip":"N/A","action":"LOGIN","connectionType":"{self.connectionType}","msisdn":"{self.msisdn}","deviceModel":"{self.deviceModel}","location":"N/A","primaryMsisdn":"{self.msisdn}","languageCode":"{self.languageCode}"}}}}'
        
        response = requests.post(url, headers=self.headers, data=data)

        #! If ok, create a b64 encoded token in the format {"msisdn": msisdn, "accessToken": accessToken, "refreshToken": refreshToken}
        if response.json()['responseHeader']['responseCode'] == '200':
            accessToken = response.json()['validateOTPResponse']['accessToken']
            refreshToken = response.json()['validateOTPResponse']['refreshToken']
            self.token = b64encode(f'{{"msisdn":"{self.msisdn}","deviceId":"{self.__deviceId}","accessToken":"{accessToken}","refreshToken":"{refreshToken}"}}'.encode()).decode()
          
        return NcellResponse(response)