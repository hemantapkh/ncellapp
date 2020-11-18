## 📞Unofficial Python API Wrapper for Ncell

This is the unofficial python API wrapper for Ncell application. With this wrapper, you can call almost all functions of the application.

**Note:** Ncell doesn't provide any public API. So, use this unofficial wrapper wisely.

## Table of Contents
- [Installation](#installation)
- [Quick Start Guide](#quick-start-guide)
- [Detailed Documentation](#detailed-documentation)
   - [register](#register)
     - [sendOtp](#sendotp)
     - [getToken](#gettoken)       
   - [ncell](#ncell)
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
- Install via [pip](https://www.pypi.org/project/ncellapp).
    ```bash
    pip install ncellapp
    ```

- Install from the source.
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
>>> account.login() # Login to the account
{'opStatus': '0', 'errorMessage': 'SUCCESS'}
>>> account.sendFreeSms(980799****, 'Hey there!, I am sending you an SMS with Python!')
{'cacheDataInMins': '0', 'srRefNumber': 'Your message has been sent successfully.', 'currentDate': '17-Nov-2020 05:19 PM', 'opStatus': '0', 'errorMessage': 'SUCCESS', 'identifier': 'SENDSMS'}
```

## Detailed documentation
**Note:** For every methods calls, it returns the response from the Ncell server in dictionary type.

### register

```python
from ncellapp import register

reg = register('your number')
```

  ### ``sendOtp``
  To send OTP messages to the phone number for registration.
  ```python
  reg.sendOtp()
  ```

  ### ``getToken``
  To get the login token.
  
   ```python
  reg.getToken(otp)
  ```
  *Args:*<br>
  otp (int): OTP sent in phone number for registration

----

### ncell

```python
from ncellapp import ncell

account = ncell('token')
```

### ``login``
To login to the account with the token. 
```python
account.login()
```


After the successful login:<br>
`account.name`: return the account name<br>
`account.accountId`: return the accountID<br>
`account.status`: return the account status<br>
`account.msidn`: return the account phone number<br>
`account.serviceFlag`: return the account service flag (prepaid/postpaid)<br>
`account.currentPlan`: return the account current plan<br>
`account.secureToken`: return the account secure token<br>
`account.hubID`: return the account hubID<br>
`account.partyID`: return the account partyID<br><br>

**Note:** You must login to the account to use the methods below.<br>

### ``viewProfile``
To view the profile of the account.
```python
account.viewProfile()
```

### ``sendSms``
To send SMS to any Ncell numbers using the current data plan.

```python
account.sendSms(destination, message, schedule)
```

*Args:*<br>
destination (int): MSIDN of the destination<br>
message (String): Message to send<br>
schedule (int, optional): Schedule a date to send a SMS (Format: YYYYMMDDHHMMSS), eg.20201105124500. Defaults to None.

### ``sendFreeSms``
To send free SMS to any Ncell numbers.

```python
account.sendFreeSms(destination, message, schedule)
```

*Args:*<br>
destination (int): MSIDN of the destination<br>
message (String): Message to send<br>
schedule (int, optional): Schedule a date to send a SMS (Format: YYYYMMDDHHMMSS), eg.20201105124500. Defaults to None.

### ``viewBalance``
To view the current balance of the account.
```python
account.viewBalance()
```

### ``selfRecharge``
To recharge the current account.

```python
account.selfRecharge(rpin)
```
*Args:*<br>rpin (int): 16 digit PIN of the recharge card.

### ``recharge``
To send an instant balance to any Ncell numbers.

```python
account.recharge(destination, rpin)
```
*Args:*<br>
rpin (int): 16 digit PIN of the recharge card.

### ``rechargeHistory``
To view the balance transfer history.
```python
account.rechargeHistory()
```

### ``balanceTransfer``
To transfer an instant  balance to any Ncell numbers.

```python
account.balanceTransfer(destination, amount)
```

*Args:*<br>
destination (int): MSIDN of the destination<br>
amount (int): Amount of balance to transfer


### ``confirmBalanceTransfer``
To confirm the balance transfer.

```python
account.confirmBalanceTransfer(otp)
```

*Args:*<br>
otp (int): OTP sent in phone number for confirming the balance transfer

### ``viewTransaction``
To view the call history.

```python
account.viewTransaction(transactionsFrom, transactionsTo)
```

*Args:*<br>
transactionsFrom (int): Date from a certain time period (Format: YYYYMMDDHHMMSS)<br>
transactionsTo (int): Date to a certain time period (Format: YYYYMMDDHHMMSS)<br>

### ``confirmViewTransaction``
To confirm the viewing of the call history.

```python
account.confirmViewTransaction(otp)
```
*Args:*<br>
otp (int): OTP sent in phone number for viewing the call history

### ``viewService``
To view the list of available services to activate.

```python
account.viewService(serviceCategory)
```
*Args:*<br>
serviceCategory (str, optional): Category of the service. Defaults to None.

### ``activateService``
To activate the certain service.

```python
account.activateService(serviceId)
```

*Args:*<br>
serviceId (int): Service ID

### ``viewOffer``
To view the available offer for the account.
```python
account.viewOffer()
```

### ``activateOffer``
To activate the certain offer.

```python
account.activateOffer(offerId)
```
*Args:*<br>
offerId (int): offer ID

### ``view3gPlans``
To view available plans for 3G.
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
Thanks to every [contributors](contributors.md) who have contributed in this project.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

-----
Author/Maintainer: [Hemanta Pokharel](https://github.com/hemantapkh/) [[✉️](mailto:hemantapkh@yahoo.com) [💬](https://t.me/hemantapkh) [📺](https://youtube.com/h9techyoutube)]
