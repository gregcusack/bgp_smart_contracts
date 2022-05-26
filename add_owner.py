from compile import *
from dotenv import load_dotenv
import sys
from ipaddress import IPv4Address

if len(sys.argv) < 4:
    print("please enter an ASN, IP, and subnet")
    sys.exit(-1)

inASN = int(sys.argv[1])
inIP = IPv4Address(sys.argv[2])
inSubnet = int(sys.argv[3])

print(inIP)
print(int(inIP))

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("GANACHE_RPC_URL")))
chain_id = 1337

my_address = os.getenv("ACCOUNT_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

# ABI (Application Binary Interface), An interface for interacting with methods in a smart contract 
abi = json.loads(
    compiled_sol["contracts"]["IANA.sol"]["IANA"]["metadata"]
    )["output"]["abi"]

#  call deploy.py Will get contract_address
contract_address = os.getenv("CONTRACT_ADDRESS")

nonce = w3.eth.get_transaction_count(my_address)

#  Instantiate the contract object 
iana = w3.eth.contract(address=contract_address, abi=abi)

#  call addPrefix Method 
transaction = iana.functions.prefix_addPrefix(int(inIP), inSubnet, inASN).buildTransaction({
    "gasPrice": w3.eth.gas_price,
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce
})
#  Signature 
signed_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
#  Sending transaction 
tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
print('add new ASN<=>IP/mask binding to contract...')
#  Waiting for the deal to complete 
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("ASN<=>IP/mask added")