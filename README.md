
<h2 align='center'>📞Unofficial Python API Wrapper of Ncell</h2>
<p align="center">
<img src="https://raw.githubusercontent.com/hemantapkh/ncellapp/main/images/ncellpy.jpg" align="center" height=200 alt="NcellPy" />
</p>
<p align="center">
<a href="https://pypi.org/ncellapp">
<img src='https://img.shields.io/pypi/v/ncellapp.svg'>
</a>
<a>
<img src="https://img.shields.io/badge/platform-cross-blue">
</a>
<a href="https://pypi.org/ncellapp">
<img src='https://img.shields.io/pypi/pyversions/ncellapp.svg'>
</a>
<a href="https://pypi.org/project/ncellapp/">
<img src='https://pepy.tech/badge/ncellapp'>
</a>
<img src='https://visitor-badge.laobi.icu/badge?page_id=hemantapkh.ncellapp'>
<a href="https://github.com/hemantapkh/ncellapp/stargazers">
<img src="https://img.shields.io/github/stars/hemantapkh/ncellapp" alt="Stars"/>
</a>
<a href="https://github.com/hemantapkh/ncellapp/issues">
<img src="https://img.shields.io/github/issues/hemantapkh/ncellapp" alt="Issues"/>
</a>
<a href="https://github.com/hemantapkh/ncellapp/graphs/contributors">
<img src="https://img.shields.io/github/contributors/hemantapkh/ncellapp.svg" alt="Contributors" />
</a>

<p align="center">
This is the unofficial python API wrapper of Ncell App.
<p align="center">
<b>⚠️ Disclaimer:</b> This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by Ncell or any of its affiliates or subsidiaries. This is an independent and unofficial API. Use at your own risk.

## Installation
- Install via [PyPi](https://www.pypi.org/project/ncellapp)
    ```bash
    pip install ncellapp
    ```

- Install from the source
    ```bash
    git clone https://github.com/hemantapkh/ncellapp && cd ncellapp && python setup.py sdist && pip install dist/*
    ```
**Note:** You may need to change the `pip` to `pip3` or `python` to `python3` on the above command depending on your system.

## Start guide

### Quick Examples

#### 1. Getting a Token

```python
>>> from ncellapp import register

>>> reg = register('98140*****')
>>> reg.generateOtp()
<Response [OTP1000]>
>>> reg.validateOtp('569845')
<Response [OTP1000]>
>>> reg.token
'eyJt...'
```

#### 2. Viewing the balance
```python
>>> from ncellapp import ncell

>>> account = ncell(token='eyJtc...', autoRefresh=True)
>>> balance = account.balance()
>>> balance.content
{'queryBalanceResponse': {'smsBalanceList': [], 'dataBalanceList': [], 'creditBalanceDetail': {'expiryDate': 'Sep 12 2021 23:59:59', 'freeSmsCount': 10, 'tariffPlanRateOffNet': 0.0, 'balance': 4.89793, 'unBilledAmount': 0.0, 'tariffPlanName': 'Sajilo', 'lastLoanTakenDate': 'Mar 23 2021 08:22:54', 'lastRechargeDate': 'Apr 27 2021 00:36:58', 'loanAmount': 0.0, 'creditUom': 'Rs.', 'tariffPlanRateOnNet': 0.0}, 'msisdn': '98140*****', 'voiceBalanceList': [], 'paidMode': 'Prepaid'}}
```

#### 3. Sending a free SMS
```python
>>> sms = account.sendFreeSms(980799****, 'Hey there!, I am sending you an SMS with Python!')
>>> sms.content
{'sendFreeSMSResponse': {'description': 'Operation succeeded', 'status': 'success', 'statusCode': '0'}}
>>> sms.responseHeader
{'responseDesc': 'Success', 'requestId': '1626770987071NCELL968', 'responseDescDisplay': 'SMS1000', 'responseCode': '200', 'timestamp': '2021-07-20T14:34:47.12712'}
```

#### 4. Manually refreshing the token and storing the refreshed token (Not recommended)

```python
# This function will be executed after refreshing the token
>>>def storeToken(token):
...     with open('token','w') as f_in:
...         f_in.write(token)

# Creating an object of ncell which contains 'afterRefresh' and 'args' arguments.
# See the documentation for more information.
>>> ac = ncellapp.ncell(token=token, afterRefresh=[__name__, 'storeToken'], args=['__token__'])

# Token expired
>>> ac.balance()
<Response [LGN2001]>

# Manually refreshing the token
>>> ac.refreshToken()
<Response [OTP1000]>

# Viewing the balance after manually refreshing the token
>>> ac.balance()
<Response [BAL1000]>
```

#### 5. Refreshing the token automatically and storing the refreshed Token (Recommended)

```python
# This function will be executed after refreshing the token.
>>>def storeToken(token):
    with open('token','w') as f_in:
        f_in.write(token)

# Creating an object of ncell and setting autoRefresh=True. 
# See documentation for more information.
>>> ac = ncellapp.ncell(token=token, autoRefresh=True, afterRefresh=[__name__, 'storeToken'], args=['__token__'])

# Token will be refreshed and stored automatically if it expires
>>> ac.balace()
<Response [BAL1000]>
```

## Detailed documentation

The documentation of ncellapp is available [here](https://ncellapp.readthedocs.io/en/latest/).

## Contributing

Any contributions you make are **greatly appreciated**.

For minor fix, you can directly create a pull request and for adding a new feature, let's first discuss about it.

*Thanks to every [contributors](https://github.com/hemantapkh/ncellapp/graphs/contributors) who have contributed in this project.*

## License

Distributed under the MIT License. See [LICENSE](https://github.com/hemantapkh/ncellapp/blob/main/LICENSE) for more information.

-----
Author/Maintainer: Hemanta Pokharel
