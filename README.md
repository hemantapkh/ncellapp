## 📞Ncell unofficial API wrapper for python

Python API wrapper for Ncell app to call almost all functions of the app. 

Note: ```Ncell don't provide any public API. I am not responsible for any things you do using this wrapper.```

## Table of Contents
- [Installation](#installation)
- [Quick Start Guide](#quick-start-guide)
- [Detailed Documentation](#detailed-documentation)
   - [register](#register)
     - [sendOtp](#sendotp)
     - [getToken](#gettoken)       
   - [ncell](#the-tiktokuser-class)
     - [login](#login)
     - [viewProfile](#viewprofile)
     - [sendSms](#sendsms)
     - [sendFreeSms](#sendfreesms)
     - [viewBalance](#viewbalance)
     - [selfRecharge](#selfrecharge)
     - [recharge](#recharge)
     - [rechargeHistory](#rechargehistory)
     - [balanceTransfer](#balancetransfer)
     - [confirmBalanceTransfer](#confirmbalancetransfer)
     - [viewTransaction](#viewtransaction)
     - [confirmViewTransaction](#confirmviewtransaction)
     - [viewService](#viewservice)
     - [activateService](#activateservice)
     - [viewOffer](#viewoffer)
     - [activateOffer](#activateoffer)
     - [view3gPlans](#view3gplans)
- [Contributing](#contributing)
- [Contributors](#contributors)
- [License](#license)

## Installation
- Install via [pip](https://www.pypi.org/projects/ncellapp)
    ```bash
    pip install ncellapp
    ```

- Install from source
    ```bash
    git clone https://github.com/hemantapkh/ncellapp.git && cd ncellapp && python setup.py install
    ```

## Quick start guide

#### Example 1 (Getting a Token)

```python
>>> from ncellapp import register

>>> reg = register('98140*****')
>>> reg.sendOtp() # Send login OTP to the number
{'cacheDataInMins': '0', 'msisdn': '98140*****', 'deviceClientId': '50*3494d-1*9a-42b4-*ffd-217*78866*f6', 'currentDate': '17-Nov-2020 05:11 PM', 'opStatus': '12', 'errorMessage': 'Please use your One Time Password Verification to complete Registration'}
>>> token = reg.getToken()['token'] # Parse the token from the dict
```

#### Example 2 (Sending a free SMS)
```python
>>> from ncellapp import ncell

>>> account = ncell(token)
>>> account.login()
{'opStatus': '0', 'errorMessage': 'SUCCESS'}
>>> account.sendFreeSms(980799****, 'Hey there!, I am sending you an SMS with Python!')
{'cacheDataInMins': '0', 'srRefNumber': 'Your message has been sent successfully.', 'currentDate': '17-Nov-2020 05:19 PM', 'opStatus': '0', 'errorMessage': 'SUCCESS', 'identifier': 'SENDSMS'}
```

## Detailed documentation
For every method calls, it returns the response from the Ncell server in dictionary type.

### register
```python
from ncellapp import register

reg = register('your number')
```

  ### ``sendOtp``
  To send OTP message to the phone number for registration
  ```python
  reg.sendOtp()
  ```

  ### ``getToken``
  To get the token, send the OTP back to the Ncell server

  otp (int): OTP sent in phone number
  ```python
  reg.getToken(otp)
  ```
----
### ncell
```python
from ncellapp import ncell

account = ncell('token')
```

### ``login``
Login using the token before using any methods below
```python
account.login()
```

### ``viewProfile``
View the profile of the account
```python
account.viewProfile()
```

### ``sendSms``
Send SMS to any Ncell numbers using the current data plan

destination (int): MSIDN of the destination<br>
message (String): Message to send<br>
schedule (int, optional): Schedule date in order of YYYYMMDDHHMMSS format, eg.20201105124500. Defaults to None.

```python
account.sendSms(destination, message, schedule)
```

### ``sendFreeSms``
Send free SMS to any Ncell numbers

destination (int): MSIDN of the destination<br>
message (String): Message to send<br>
schedule (int, optional): Schedule date in order of YYYYMMDDHHMMSS format, eg.20201105124500. Defaults to None.

```python
account.sendFreeSms(destination, message, schedule)
```

### ``viewBalance``
View the current balance of the account
```python
account.viewBalance()
```

### ``selfRecharge``
Recharge the current account

rpin (int): 16 digit PIN of the recharge card
```python
account.selfRecharge(rpin)
```

### ``recharge``
Send recharge to any Ncell numbers

rpin (int): 16 digit PIN of the recharge card
```python
account.recharge(destination, rpin)
```

### ``rechargeHistory``
View the balance transfer history
```python
account.rechargeHistory()
```

### ``balanceTransfer``
Transfer balance to any Ncell numbers

destination (int): MSIDN of the destination<br>
amount (int): Amount of balance to transfer

```python
account.balanceTransfer(destination, amount)
```

### ``confirmBalanceTransfer``
Send the OTP to the Ncell and get the login token

otp (int): OTP sent in phone number
```python
account.confirmBalanceTransfer(otp)
```

### ``viewTransaction``
View call history

transactionsFrom (int): From date in YYYYMMDDHHMMSS order<br>
transactionsTo (int): To date in YYYYMMDDHHMMSS order
```python
account.viewTransaction(transactionsFrom, transactionsTo)
```

### ``confirmViewTransaction``
Confirm the view call history

otp (int): OTP sent in phone number
```python
reg.getToken(otp)
```

### ``viewService``
View the list of available services to activate

serviceCategory (str, optional): Category of the service. Defaults to None.
```python
account.viewService(serviceCategory)
```

### ``activateService``
Activate the certain service

serviceId (int): Service ID 
```python
account.activateService(serviceId)
```

### ``viewOffer``
View the available offer for the account
```python
account.viewOffer()
```

### ``activateOffer``
Activate the certain offer

offerId (int): offer ID found in offerID field of viewOffer()
```python
account.activateOffer(offerId)
```

### ``view3gPlans``
View available plans for 3G
```python
account.view3gPlans()
```
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

Special thanks to:

* [Sharnab Bogati](https://www.sharnabbogati.com.np) <a  title="Documentation">📖</a> <a  title="Logo">🎨</a>

See also the list of [contributors](https://github.com/hemantapkh/ncellapp/contributors) who participated in this project.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

-----
Author/Maintainer: [Hemanta Pokharel](https://github.com/hemantapkh/) [[✉️](mailto:hemantapkh@yahoo.com) [💬](https://t.me/hemantapkh) [📺](https://youtube.com/h9techyoutube)]