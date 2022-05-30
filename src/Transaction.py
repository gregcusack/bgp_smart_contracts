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

        # self.tx_sender = None
        # self.msg_signer = None


    def setup_accounts(self, **kwargs):
        tx_sender_account = kwargs["transaction_sender"]
        self.tx_sender = utils.load_account_from_env_v2(tx_sender_account)
        
        self.msg_signer = None
        if(len(kwargs) > 1):
            msg_signer_account = kwargs["msg_signer"]
            self.msg_signer = utils.load_account_from_env_v2(msg_signer_account)

    def sc_addASN(self, tx_sender, inASN, inAddress, sigV, sigR, sigS):
        transaction = self.iana.functions.IANA_addASN(inASN, inAddress, sigV, sigR, sigS).buildTransaction({
            "gasPrice": self.w3.eth.gas_price,
            "chainId": self.chain_id,
            "from": tx_sender.get_public_key(),
            "nonce": tx_sender.get_nonce()
        })
        return transaction

    def sign_transaction(self, transaction, tx_sender):
        return utils.sign_transaction(self.w3, transaction, tx_sender.get_private_key())


    def execute_transaction(self, signed_transaction):
        return utils.send_transaction(self.w3, signed_transaction)
    
