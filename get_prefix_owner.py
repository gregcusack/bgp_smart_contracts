from compile import *
from dotenv import load_dotenv
import sys
from utils.utils import *
from ipaddress import IPv4Address

if len(sys.argv) < 3:
    print("please enter an ASN to check if it exists")
    sys.exit(-1)

inIP = IPv4Address(sys.argv[1])
inSubnet = int(sys.argv[2])

load_dotenv(override=True)

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


# print("get ASN " + str(inASN) + " from ASN map")
asn = iana.functions.getPrefixOwner(int(inIP), inSubnet).call()

if str(asn) == "none" or asn == "0":
    print("IANA owns the prefix: " + str(inIP) + "/" + str(inSubnet))
else:
    print("ASN " + str(asn) + " owns the prefix: " + str(inIP) + "/" + str(inSubnet))

