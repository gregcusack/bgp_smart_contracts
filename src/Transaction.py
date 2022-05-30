from dotenv import load_dotenv
import sys
from utils.utils import *
from Web3Obj import Web3Obj


# in an ideal world, i think we should have: contract, transaction, tx_sender, msg_signer objects
class Transaction():
    def __init__(self, contract_name, contract_address_env):
        load_dotenv()
        self.w3 = Web3Obj.w3
        self.chain_id = utils.load_chain_id()
        self.abi = utils.get_contract_abi(contract_name) # ex: IANA
        self.contract_address = utils.load_contract_address(contract_address_env) # ex: CONTRACT_ADDRESS
        self.iana = self.w3.eth.contract(address=self.contract_address, abi=self.abi)

        self.tx_sender_pub_key = None
        self.tx_sender_priv_key = None

        #signature validation data
        self.sigV = None
        self.sigR = None
        self.sigS = None

    def set_tx_sender_pub_key(self, pub_key):
        self.tx_sender_pub_key = pub_key

    def set_tx_sender_priv_key(self, priv_key):
        self.tx_sender_priv_key = priv_key

    def sign_transaction(self, transaction):
        return utils.sign_transaction(self.w3, transaction, self.tx_sender_priv_key)

    def execute_transaction(self, signed_transaction):
        return utils.send_transaction(self.w3, signed_transaction)

    def sign_and_execute_transaction(self, transaction):
        tx_signed, err = self.sign_transaction(transaction)
        if err:
            return None, None, TxErrorType.FailedToSignTx
        tx_hash, tx_receipt, err = self.execute_transaction(tx_signed)
        if err:
            return None, None, TxErrorType.FailedToExecuteTx

        return tx_hash, tx_receipt, TxErrorType.OK

    def set_signature_validation_data(self, _sigV, _sigR, _sigS):
        self.sigV = _sigV
        self.sigR = _sigR
        self.sigS = _sigS
    
    def sc_addASN(self, tx_sender_nonce, inASN, inAddress):
        transaction = self.iana.functions.IANA_addASN(inASN, inAddress, self.sigV, self.sigR, self.sigS).buildTransaction({
            "gasPrice": self.w3.eth.gas_price,
            "chainId": self.chain_id,
            "from": self.tx_sender_pub_key,
            "nonce": tx_sender_nonce
        })
        return transaction


