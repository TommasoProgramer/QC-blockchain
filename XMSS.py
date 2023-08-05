import hashlib
import random

class XMSS:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.generate_key_pair()

    def generate_key_pair(self):
        seed = hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()
        self.private_key = seed
        self.public_key = hashlib.sha256(seed.encode()).hexdigest()

    def get_public_key(self):
        return self.public_key

def xmss_signature(private_key, message):
    signature = hashlib.sha256((private_key + message).encode()).hexdigest()
    return signature

def xmss_verify_signature(public_key, message, signature):
    expected_signature = hashlib.sha256((public_key + message).encode()).hexdigest()
    return signature == expected_signature
