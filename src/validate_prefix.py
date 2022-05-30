from compile import *
from dotenv import load_dotenv
import sys
from utils.utils import *
from ipaddress import IPv4Address

if len(sys.argv) < 4:
    print("please enter an ip, subnet, and ASN to check if advertised prefix is valid")
    sys.exit(-1)

# All we're checking is an ip/subnet<=>ASN binding! Nothing else!
inIP = IPv4Address(sys.argv[1])
inSubnet = int(sys.argv[2])
inASN = int(sys.argv[3])

load_dotenv(override=True)

w3 = Web3(Web3.HTTPProvider(os.getenv("GANACHE_RPC_URL")))

# ABI (Application Binary Interface), An interface for interacting with methods in a smart contract 
abi = utils.get_contract_abi("IANA")

#  call deploy.py Will get contract_address
contract_address = utils.load_contract_address("CONTRACT_ADDRESS")

#  Instantiate the contract object 
iana = w3.eth.contract(address=contract_address, abi=abi)

# Validate the prefix<=>ASN mapping. Returns an enum.
validationResult = validatePrefixResult(iana.functions.prefix_validatePrefix(int(inIP), inSubnet, inASN).call())
print(validationResult)
