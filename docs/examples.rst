Quick Examples
==============

Getting a Token
----------------

.. code:: python

    >>> from ncellapp import register

    >>> reg = register('98140*****')
    >>> reg.generateOtp()
    <Response [OTP1000]>
    >>> reg.validateOtp('569845')
    <Response [OTP1000]>
    >>> reg.token
    'eyJt...'

Viewing the balance
--------------------

.. code:: python

        >>> from ncellapp import ncell

        >>> account = ncell(token='eyJt...')
        >>> balance = account.balance()
        >>> balance.content
        {'queryBalanceResponse': {'smsBalanceList': [], 'dataBalanceList': [], 'creditBalanceDetail': {'expiryDate': 'Sep 12 2021 23:59:59', 'freeSmsCount': 10, 'tariffPlanRateOffNet': 0.0, 'balance': 4.89793, 'unBilledAmount': 0.0, 'tariffPlanName': 'Sajilo', 'lastLoanTakenDate': 'Mar 23 2021 08:22:54', 'lastRechargeDate': 'Apr 27 2021 00:36:58', 'loanAmount': 0.0, 'creditUom': 'Rs.', 'tariffPlanRateOnNet': 0.0}, 'msisdn': '98140*****', 'voiceBalanceList': [], 'paidMode': 'Prepaid'}}
        
    
Sending a free SMS
-------------------

.. code:: python

        >>> sms = account.sendFreeSms(980799****, 'Hey there!, I am sending you an SMS with Python!')
        >>> sms.content
        {'sendFreeSMSResponse': {'description': 'Operation succeeded', 'status': 'success', 'statusCode': '0'}}
        >>> sms.responseHeader
        {'responseDesc': 'Success', 'requestId': '1626770987071NCELL968', 'responseDescDisplay': 'SMS1000', 'responseCode': '200', 'timestamp': '2021-07-20T14:34:47.12712'}

Manually refreshing the token and storing the refreshed token (Not recommended)
-------------------------------------------------------------------------------

.. code:: python

        # This function will be executed after refreshing the token
        >>>def storeToken(token):
        ...     with open('token','w') as f_in:
        ...     f_in.write(token)

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

Refreshing the token automatically and storing the refreshed Token (Recommended)
--------------------------------------------------------------------------------

.. code:: python

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