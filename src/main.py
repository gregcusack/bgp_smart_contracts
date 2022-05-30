from Transaction import Transaction
from Account import Account
from utils.utils import *
from Web3Obj import Web3Obj
import sys

def main():
    if len(sys.argv) < 3:
        print("please enter an ASN and its address to add to ASNMap")
        sys.exit(-1)

    inASN = int(sys.argv[1])
    inAddress = Web3.toChecksumAddress(sys.argv[2])

    # create accounts
    tx_sender = Account(AccountType.TransactionSender, "ACCOUNT0")
    tx_sender.load_account_keys()

    msg_sender = Account(AccountType.MessageSender, "ACCOUNT1")
    msg_sender.load_account_keys()


    # create a transaction object
    tx_object = Transaction("IANA", "CONTRACT_ADDRESS")

    # data to hash and sign
    data_types = ['uint32', 'address']
    data = [inASN, inAddress]
    
    # sign and hash data
    signed_message, err = msg_sender.hash_and_sign_message(data_types, data)
    if err:
        print("ERROR: failed to hash and sign message")
        sys.exit(-1)

    # generate signed message validation data
    sigV, sigR, sigS = tx_sender.generate_message_validation_data(signed_message)

    # generate contract transaction
    tx = tx_object.sc_addASN(tx_sender, inASN, inAddress, sigV, sigR, sigS)

    signed_tx, err = tx_object.sign_transaction(tx, tx_sender)
    if err:
        print("ERROR: failed to sign transaction")
        sys.exit(-1)

    tx_hash, tx_receipt, err = tx_object.execute_transaction(signed_tx)
    if err:
        print("ERROR: failed to execute transaction")
        sys.exit(-1)

    print("SUCCESS: ASN<=>Address added")






if __name__ == "__main__":
    main()