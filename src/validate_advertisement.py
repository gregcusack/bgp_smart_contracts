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

def main():
    if len(sys.argv) < 5:
        print("please enter an tx_sender, ip, subnet, your own ASN, and the advertisement's AS_PATH (e.g. 3 2 1) to validate path")
        sys.exit(-1)

    tx_sender_name = str(sys.argv[1])
    inIP = IPv4Address(sys.argv[2])
    inSubnet = int(sys.argv[3])
    inPrevHop = int(sys.argv[4])
    myASN = int(sys.argv[4])

    # create accounts
    tx_sender = Account(AccountType.TransactionSender, tx_sender_name)
    tx_sender.load_account_keys()

    # we actually need to pass in the contract address here. or we can do something with a config file
    tx_sender.generate_transaction_object("PATH_VALIDATION", "MY_PATH_VALIDATION_CONTRACT_ADDRESS")

    # data to hash and sign
    data_types = ['uint32', 'uint8', 'uint32']
    data = [int(inIP), inSubnet, inPrevHop]

    tx = tx_sender.tx.sc_validateAdvertisement(int(inIP), inSubnet, inPrevHop)
    print(tx)
    
    # # sign and hash data
    # signed_message, err = msg_sender.hash_and_sign_message(data_types, data)
    # if err:
    #     print("ERROR: failed to hash and sign message")
    #     sys.exit(-1)

    # # generate signed message validation data
    # tx_sender.generate_signature_validation_data_from_signed_message(signed_message)

    # # generate contract transaction
    # tx = tx_sender.tx.sc_addASN(tx_sender.get_nonce(), inASN, inAddress)

    # sign and execute transaction
    # tx_hash, tx_receipt, err = tx_sender.tx.sign_and_execute_transaction(tx)
    # if TxErrorType(err) != TxErrorType.OK:
    #     print("ERROR: " + str(TxErrorType(err)) + ". Transaction NOT executed")
        
    # print("SUCCESS: ASN<=>Address added")


if __name__ == "__main__":
    main()