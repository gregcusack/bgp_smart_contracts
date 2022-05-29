from compile import *
from dotenv import load_dotenv
import sys
from utils.utils import *

if len(sys.argv) < 2:
    print("please enter an ASN to check if it exists")
    sys.exit(-1)

inASN = int(sys.argv[1])

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

#  Instantiate the contract object 
iana = w3.eth.contract(address=contract_address, abi=abi)

print("get ASN " + str(inASN) + " from ASN map")
asn = iana.functions.IANA_getASNOwner(inASN).call()

if str(asn) == "none" or utils.is_null_address(asn):
    print("ASN " + str(inASN) + " does not exist")
else:
    print("valid ASN in map! (" + str(inASN) + ", " + str(asn) + ")")

