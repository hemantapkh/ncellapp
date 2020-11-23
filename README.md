## 📞Unofficial Python API Wrapper of Ncell

This is the unofficial python API wrapper of Ncell App. With this wrapper, you can call almost all functions of the application.

**Note:** This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by Ncell or any of its affiliates or subsidiaries. This is an independent and unofficial API. Use at your own risk.

## Table of Contents
- [Installation](#installation)
- [Start Guide](#start-guide)
   - [Quick Examples](#quick-examples)    
     - [Getting a Token](#1.-Getting-a-Token)
     - [Viewing the balance](#2.-viewing-the-balance)
     - [Sending a free SMS](#3.-sending-a-free-sms)
- [Detailed Documentation](#detailed-documentation)
   - [register](#register)      
   - [ncell](#ncell)
   - [NcellResponse](#ncellapp.NcellResponse-object)
- [Contributing](#contributing)
- [Contributors](#contributors)
- [License](#license)

## Installation
- Install via [pip](https://www.pypi.org/project/ncellapp).
    ```bash
    pip install ncellapp
    ```

- Install from the source.
    ```bash
    git clone https://github.com/hemantapkh/ncellapp.git && cd ncellapp && python setup.py install
    ```

## Start guide

### Quick Examples

#### 1. Getting a Token

```python
>>> from ncellapp import register

>>> reg = register('98140*****')
>>> reg.sendOtp() # Send login OTP to the number
<OperationStatus [12]>
>>> tk = reg.getToken(otp='5698')
>>> # Store the token in a variable if operation is successful, else print the error message
>>> if tk.opStatus == '0': 
...    token = tk.content['token']
... else:
...    tk.errorMessage
>>> token
'eydtc2lzZG4nOiAnOTgxNDAqKioqKicsICdkZXZpY2VDbGllbnRJZCc6ICc0K1g2aXBMa2M3aFJjc1RNTmxIZ29weXFaWkJmUHBYcHBRbEg4cnNPSWFqRjBOcFhKMlZldUE3cmpIWXVEOHJ5J30='
```

#### 2. Viewing the balance
```python
>>> from ncellapp import ncell

>>> account = ncell(token='TOKEN')
>>> account.login() # Login the account
<OperationStatus [0]> 
>>> balance = account.viewBalance()
>>> balance.content
{'prePaid': {'balance': '1.38', 'bucketDes': 'Prepaid Main Balance', 'balanceChange': '2000', 'validity': '2037-01-01', 'unit': 'Rs.', 'unitPosition': 'PREFIX'}, 'notification': {'name': 'Balance Notification', 'descrption': 'Your account balance is less than Rs. 16  ', 'imageUrl': '/mc/images/1.jpg', 'actionUrl': '/mc/images/1.jpg', 'isActionable': 'Y'}}
```

#### 3. Sending a free SMS
```python
>>> sms = account.sendFreeSms(980799****, 'Hey there!, I am sending you an SMS with Python!')
>>> sms.errorMessage # Viewing the error message
'SUCCESS'
>>> sms.content # Viewing the response content
{'srRefNumber': 'Your message has been sent successfully.', 'identifier': 'SENDSMS'}
```

## Detailed documentation


### register
This class contains the methods for registering an account.
```python
from ncellapp import register

reg = register(msisdn='PHONE NUMBER TO REGISTER')
```
Available methods for register class:
 Method   | Description | Arguments 
----------|-------------|-----------
sendOtp()  | Send OTP messages to the phone number for registration | self 
getToken(otp)     | Send the OTP to the Ncell server to get the token | self,<br>otp : `OTP sent in phone number for registration` 
**Return value:** A [ncellapp.NcellResponse](#ncellapp.NcellResponse-object) object

### ncell
This class contains the methods for using the features of ncell app.
```python
from ncellapp import ncell

account = ncell(token='TOKEN')
```
Available methods for ncell class:
 Method   | Description  | Arguments
----------|------------|-------------
login()   | Login to the account with the token | self | account.login()
viewProfile() | View the profile of the account | self 
sendSms(destination, message, schedule) | Send SMS to any Ncell numbers using the current data plan | self, <br>destination : `MSISDN of the destination`<br> message : `Message to send`<br> schedule (optional): `Schedule a date to send a SMS in YYYYMMDDHHMMSS format`
sendFreeSms(destination, message, schedule) | Send free SMS to any Ncell numbers (Limited to 10/Day) |  self, <br>destination : `MSISDN of the destination`<br> message : `Message to send`<br> schedule (optional): `Schedule a date to send a SMS in YYYYMMDDHHMMSS format`
viewBalance() | View the current balance of the account | self
selfRecharge(rpin) | Recharge the current account | self,<br>rpin : `16 digit PIN of the recharge card`
recharge(destination, rpin) | Send an instant balance to any Ncell numbers | self, <br>destination : `MSISDN of the destination`<br>rpin : `16 digit PIN of the recharge card`
rechargeHistory() | View the balance transfer history | self
balanceTransfer(destination, amount) | Transfer an instant balance to any Ncell numbers | self, <br>destination : `MSIDN of the destination`<br>amount : `Amount of balance to transfer` | 
confirmBalanceTransfer(otp) | Confirm the balance transfer | self, <br>otp : `OTP sent in phone number for confirming the balance transfer`
viewTransaction(transactionsFrom, transactionsTo) | View the call history | self,<br>transactionsFrom : `Date from a certain time period in YYYYMMDDHHMMSS format`<br>transactionsTo : `Date to a certain time period in YYYYMMDDHHMMSS format`
confirmViewTransaction(otp) | Confirm the viewing of the call history | self, <br>otp : `OTP sent in phone number for viewing the call history`
viewService(serviceCategory) | View the list of available services to activate | self,<br>serviceCategory (optional): `Category of the service` 
activateService(serviceId) | Activate the certain service | self,<br>serviceId : `Service ID`
viewOffer() | View the available offer for the account | self
activateOffer(offerId) | Activate the certain offer | self,<br>offerId : `offer ID`
view3gPlans() | view available plans for 3G | self

**Return value:** A [ncellapp.NcellResponse](#ncellapp.NcellResponse-object) object

### ncellapp.NcellResponse Object
The ncellapp.NcellResponse() Object contains the server's response to the HTTP request.

Property   | Description
----------|-------------
opStatus   | Returns the operation status of the request
errorMessage | Returns the errorMessage of the request
content | Returns the content of the response from Ncell
cacheDataInMins | Returns the cache data in minutes
currentDate | Returns the date when the request was sent
cookies | Returns a CookieJar object with the cookies sent back from the server
elapsed | Returns a timedelta object with the time elapsed from sending the request to the arrival of the response
headers | Returns a dictionary of response headers
ok | Returns True if status_code is less than 400, otherwise False
reason | Returns a text corresponding to the status code
request | Returns the request object that requested this response
statusCode | Returns a number that indicates the status (200 is OK, 404 is Not Found)
url | Returns the URL of the response

----

## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

*You can also contribute to this project by creating an issue of bugs and feature requests.*

## Contributors
Thanks to every [contributors](https://github.com/hemantapkh/ncellapp/blob/main/contributors.md) who have contributed in this project.

## License

Distributed under the MIT License. See [LICENSE](https://github.com/hemantapkh/ncellapp/blob/main/LICENSE) for more information.

-----
Author/Maintainer: [Hemanta Pokharel](https://github.com/hemantapkh/) | Youtube: [@H9TechYoutube](https://youtube.com/h9techyoutube)
