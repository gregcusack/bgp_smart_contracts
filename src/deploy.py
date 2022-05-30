from compile import *
from dotenv import load_dotenv
from utils.utils import *
import sys

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("GANACHE_RPC_URL")))
chain_id = utils.load_chain_id()

acct0_address, acct0_private_key = utils.load_account_from_env(0)

#  Compiled bytecode of smart contract （ Data on the chain ）
bytecode = compiled_sol["contracts"]["IANA.sol"]["IANA"]["evm"]["bytecode"]["object"]

# ABI (Application Binary Interface), An interface for interacting with methods in a smart contract 
abi = utils.get_contract_abi("IANA")

#  Build smart contract objects 
iana = w3.eth.contract(abi=abi, bytecode=bytecode)
#  Of the last transaction in the current blockchain nonce
nonce = w3.eth.get_transaction_count(acct0_address)

#  Deploy smart contracts  -  Create transaction 
transaction = iana.constructor().buildTransaction({
    "gasPrice": w3.eth.gas_price,
    "chainId": chain_id, 
    "from": acct0_address, 
    "nonce": nonce
    }
)

#  Sign the current transaction  -  Prove that you initiated the transaction 
signed_transaction, err = utils.sign_transaction(w3, transaction, acct0_private_key)
if err:
    sys.exit(-1)

tx_hash, tx_receipt, err = utils.send_transaction(w3, signed_transaction)
if err:
    sys.exit(-1)
print('Deployed Done!')
print("contract address: " + tx_receipt.contractAddress)