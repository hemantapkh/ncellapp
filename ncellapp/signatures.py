import time
from os import urandom
from datetime import datetime

# Random MAC address generator
def macGen():
    randBytes = [ i for i in urandom(6) ]
    return ''.join([ f'{i:02X}' for i in randBytes ])

# Time stamp generator
def tsGen():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+'Z'

# Request ID generator
def reqIdGen():
	return str(time.time() * 1000).replace('.','NCELL')

# Transaction ID generator
def tranIdGen():
	# First 14 digit of timestamp
	ts = str(time.time())[:14].replace('.','')
	
	# Concatenate '1' infront of ts
	# Maybe concatenate '2' instead of '1' after January 19, 2038 ;)
	ts = '1' +ts

	return ts