from Classes.Account import Account
from Utils.Utils import *
from ipaddress import IPv4Address
import sys

"""
Example:
1 -> 2 -> 3 -> 4 -> ...

A1: 10.0.20.0/24 : 1
    - writes to 1's own advertisement contract {10.0.20.0/24, nextHop = 2}
    - sends A1 to 2
A2: 10.0.20.0/24 : 2, 1
    - checks there is a 10.0.20.0/24 with next hop 2 in 1's advertisement contract
    - writes to 2's own advertisement contract {10.0.20.0/2, nextHop = 3}
    - sends A2 to 3
A3: 10.0.20.0/24 : 3, 2, 1
    - checks there is a 10.0.20.0/24 with next hop 3 in 2's advertisement contract
    - checks there is a 10.0.20.0/24 with next hop 2 in 1's advertisement contract
    - writes to 3's own advertisement contract {10.0.20.0/2, nextHop = 4}
    - sends A3 to 4...

"""

"""
Example
1 -> 2 -> 3 -> 4 -> ...
python add_advertisement.py ACCOUNT0 10.0.20.0 24 2
python add_advertisement.py ACCOUNT1 10.0.20.0 24 3
python add_advertisement.py ACCOUNT2 10.0.20.0 24 4

Now validate

python validate_advertisement.py ACCOUNT0 10.0.20.0 24 <myASN> <Received advertisement's AS_PATH>
ex: 
python validate_advertisement.py ACCOUNT0 10.0.20.0 24 2 1

## check down path that path 2->3 exists and 1->2 exists
python validate_advertisement.py ACCOUNT1 10.0.20.0 24 3 2 1

## check down path that paths 3->4, 2->3, and 1->2 exist
python validate_advertisement.py ACCOUNT1 10.0.20.0 24 4 3 2 1

Caviate here: we assume ASN1 = contract0, ASN2 = contract1, etc
"""

def main():
    len_args = len(sys.argv)
    if len_args < 6:
        print("please enter an tx_sender, ip, subnet, your own ASN, and the incoming advertisement's AS_PATH (e.g. 3 2 1) to validate path")
        sys.exit(-1)

    tx_sender_name = str(sys.argv[1])
    inIP = IPv4Address(sys.argv[2])
    inSubnet = int(sys.argv[3])
    myASN = int(sys.argv[4])

    AS_PATH = []
    contract_addresses = []
    for i in range(5, len_args):
        asn = sys.argv[i]
        AS_PATH.append(int(asn))
        contract_addresses.append("ACCOUNT" + str(int(asn)-1) + "_PATH_VALIDATION_CONTRACT")

    asn_contract_zip = zip(AS_PATH, contract_addresses)

    # create accounts
    tx_sender = Account(AccountType.TransactionSender, tx_sender_name)
    tx_sender.load_account_keys()

    print(AS_PATH)
    print(contract_addresses)

    # need to load a map here that maps ASN to the ASN's path_validation contract address
    # hack for now. ASN1 = contract0, ASN2 = contract1, etc
    nextHop = myASN
    for ASN, contract_address in asn_contract_zip:
        # we actually need to pass in the contract address here. or we can do something with a config file
        tx_sender.generate_transaction_object("PATH_VALIDATION", contract_address)
        tx = tx_sender.tx.sc_validateAdvertisement(int(inIP), inSubnet, nextHop)
        nextHop = ASN
        print(tx)

if __name__ == "__main__":
    main()