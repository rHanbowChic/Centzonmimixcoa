import base64
from libnotemsx import Notems
from hashlib import pbkdf2_hmac, sha256
from Crypto.Cipher import AES
from Crypto import Random

class Lugh:
    def __init__(self, host="https://note.ms", proxy=""):
        self.n = Notems(host=host, proxy=proxy)
        self.salt_pagename = sha256(b'Lugh').digest()
        self.salt_aes = sha256(b'Sabitsuki').digest()  # Finally, here!
        self.current_page_digest = b''
        self.current_aes_digest = b''
        self.current_key = ""
        self.current_page = ""

    def post_note(self, key: str, page: str, text: str):
        if self.current_page != page or self.current_key != key:
            page_digest = pbkdf2_hmac('sha256', page.encode("utf-8"),
                                      self.salt_pagename + key.encode("utf-8"),
                                      1000000)
            self.current_page_digest = page_digest
        else:
            page_digest = self.current_page_digest
        target_page = page_digest.hex()[:24]

        if self.current_page != page or self.current_key != key:
            aes_digest = pbkdf2_hmac('sha256', page.encode("utf-8"),
                                     self.salt_aes + key.encode("utf-8"),
                                     1000000)
            self.current_aes_digest = aes_digest
            self.current_page = page
            self.current_key = key
        else:
            aes_digest = self.current_aes_digest
        aes_cipher = AESCipher(aes_digest)
        encrypted_text = aes_cipher.encrypt(text.encode("utf=8").hex())
        print(f"post {encrypted_text} to {target_page}")

        self.n.post_note(target_page, encrypted_text.decode("utf-8"))
        return ""

    def get_note(self, key: str, page: str):
        if self.current_page != page or self.current_key != key:
            page_digest = pbkdf2_hmac('sha256', page.encode("utf-8"),
                                      self.salt_pagename + key.encode("utf-8"), 1000000)
            self.current_page_digest = page_digest
        else:
            page_digest = self.current_page_digest
        target_page = page_digest.hex()[:24]

        encrypted_text = self.n.get_note(target_page)
        print(f"get {encrypted_text} from {target_page}")
        if encrypted_text == "":
            text = ""
        else:
            if self.current_page != page or self.current_key != key:
                aes_digest = pbkdf2_hmac('sha256', page.encode("utf-8"),
                                         self.salt_aes + key.encode("utf-8"), 1000000)
                self.current_aes_digest = aes_digest

            else:
                aes_digest = self.current_aes_digest
            aes_cipher = AESCipher(aes_digest)
            try:
                text = aes_cipher.decrypt(encrypted_text.encode("utf-8"))
                text = bytes.fromhex(text).decode("utf-8")
            except ValueError:
                text = ""
        self.current_page = page
        self.current_key = key
        return text


class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = key

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return AESCipher._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]