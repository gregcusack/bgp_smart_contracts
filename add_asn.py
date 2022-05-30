from dotenv import load_dotenv
import sys
from utils.utils import *

if len(sys.argv) < 3:
    print("please enter an ASN and its address to add to ASNMap")
    sys.exit(-1)

inASN = int(sys.argv[1])
inAddress = Web3.toChecksumAddress(sys.argv[2])

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv("GANACHE_RPC_URL")))
chain_id = utils.load_chain_id()

acct0_address, acct0_private_key = utils.load_account_from_env(0)
acct1_address, acct1_private_key = utils.load_account_from_env(1)

contract_address = utils.load_contract_address("CONTRACT_ADDRESS")

# ABI (Application Binary Interface), An interface for interacting with methods in a smart contract 
abi = utils.get_contract_abi("IANA")
nonce = w3.eth.get_transaction_count(acct0_address)

#  Instantiate the contract object 
iana = w3.eth.contract(address=contract_address, abi=abi)

# GENERATED BY ACCT1 (trying to get the ASN<=>Acct1_addr binding)
base_message, signed_message, err = utils.hash_and_sign_message(
    w3,
    ['uint32', 'address'], 
    [inASN, inAddress],
    acct1_private_key
)
if err:
    print("ERROR: failed to hash and sign message")
    sys.exit(-1)


# GENERATED BY ACCT0 (IANA/CONTRACT OWNER)
sigV, sigR, sigS = utils.generate_message_validation_data(signed_message)

#  call addPrefix Method 
transaction = iana.functions.IANA_addASN(inASN, inAddress, sigV, sigR, sigS).buildTransaction({
    "gasPrice": w3.eth.gas_price,
    "chainId": chain_id,
    "from": acct0_address,
    "nonce": nonce
})

signed_transaction, err = utils.sign_transaction(w3, transaction, acct0_private_key)
if err:
    sys.exit(-1)

tx_hash, tx_receipt, err = utils.send_transaction(w3, signed_transaction)
if err:
    sys.exit(-1)

print("SUCCESS: ASN<=>Address added")