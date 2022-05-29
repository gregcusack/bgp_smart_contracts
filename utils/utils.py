from web3 import Web3
from eth_account.messages import encode_defunct

class utils(object):
    @staticmethod
    def is_null_address(inAddr):
        if str(inAddr) == "0x0000000000000000000000000000000000000000":
            return True
        return False
    
    @staticmethod
    def to_32byte_hex(val):
        return Web3.toHex(Web3.toBytes(val).rjust(32, b'\0'))

    @staticmethod
    def encode_defunct_wrapper(msgToBeSigned):
        return encode_defunct(text=msgToBeSigned.hex())

    @staticmethod
    def sign_message_wrapper(w3, msgToBeSigned, acct2_priv_key):
        return w3.eth.account.sign_message(msgToBeSigned, private_key=acct2_priv_key)

    @staticmethod
    def generate_sig_v_r_s(msgSigned):
        msgSignedHash   = Web3.toHex(msgSigned.messageHash)
        sigV            = msgSigned.v
        sigR            = utils.to_32byte_hex(msgSigned.r)
        sigS            = utils.to_32byte_hex(msgSigned.s)

        return msgSignedHash, sigV, sigR, sigS