from dotenv import load_dotenv
import sys
from utils.utils import *
from Web3Obj import Web3Obj

class Account(Web3Obj):
    def __init__(self, account_type, account_name):
        self.w3 = Web3Obj.w3
        self.account_type = account_type
        self.account_name = account_name
        self.public_key = None
        self.private_key = None

    def load_account_keys(self):
        self.public_key, self.private_key = utils.load_account_from_env_v2(self.account_name)

    def get_public_key(self):
        return self.public_key

    # this is obviously very bad. we wouldn't want someone to be able to get our private key
    # but fine for now i guess
    def get_private_key(self):
        return self.private_key

    def get_nonce(self):
        if self.public_key == None:
            print("ERROR: public key not set. can't get nonce")
            sys.exit(-1)
        return self.w3.eth.get_transaction_count(self.public_key)

    def hash_and_sign_message(self, data_types, data):
        _, signed_message, err = utils.hash_and_sign_message(
            self.w3,
            data_types, 
            data,
            self.private_key
        )
        if err:
            print("ERROR: failed to hash and sign message")
        
        return signed_message, err

    def generate_message_validation_data(self, signed_message):
        return utils.generate_message_validation_data(signed_message)

