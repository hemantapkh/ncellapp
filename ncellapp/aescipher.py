from base64 import (b64encode, b64decode)

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