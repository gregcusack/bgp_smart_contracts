# bgp_smart_contracts

## TODO (written: 5/29/22):
1) Make the below programs easier to run
    - pass in "owner" and "modifier" accounts in command line
        - Aka I should be able to toggle between any of the three accounts across all python scripts instead of having to go in and change the account we're reading from in the env file. it's confusing lol
2) Implement The following
    - Remove ASN
    - Remove Prefix
    - Validate Prefix

## How to Run (so far)
- Add ASN, Add Prefix
    - With cryptographic signings

### A couple notes
The following accounts/addresses must be stored in .env
- account0_address 
    - The IANA account. Owner of the smart contract
- account1_address 
    - An AS Account (1)
- account2_address
    - Another AS Account (2)

### Comile and deploy the smart contract
```
python compile.py 
python deploy.py 
```
Next: Copy address printed out from deploy.py into .env file

- Note: these two commands will deploy from account0_address in .env
- account0_address becomes the owner of the contract. 
- account0_address is the owner/IANA


### Add ASN to ASN<=>Address 
- this gives an ASN the ability to get assigned IP prefixes
- But an AS first needs to get added to the AS map by IANA

#### Add ASN1 to ASNMap
```
python add_asn.py <ASN1> <account1_address>
```
- Note ensure account1_address passed in is equivalent to account1 in the .env file. (You can change this but they way it's set up now, you have make sure they are equivalent)

#### Add ASN2 to ASNMap
- Now update add_prefix.py. And read in account2 data instead of account 1. This will allow us to add an ASN for account2
```
python add_asn.py <ASN2> <account2_address>
```

### Add Prefix! IP/Subnet<=> ASN
- Note: currently `add_prefix.py` uses account0_address (IANA) to send all transactions.
    - Since we're going to allocate new prefixes to ASes below, this is what we want. Since IANA currently owns all IP space. And only IANA can allocate that space to someone else

#### Add a prefix for ASN1 (account1_address)
```
python add_prefix.py <ASN1> <ip1> <subnet> <account1_address>
```
Example: 
```python add_prefix 12 10.0.20.0 24 0x79bb7739B28ab9D6a846012156f5eadD0dE67361```
- Note same issue as above, acct1 in .env == <account1_address>

#### Add a prefix for ASN2 (account2_address)
- Now update add_prefix.py. And read in account2 data instead of account 1. This will allow us to add a prefix for account2
```
python add_prefix.py <ASN2> <ip2> <subnet> <account2_address>
```
Example: 
```python add_prefix 13 10.0.20.1 24 0xcF0A72EFd623c7aC7f9886213daFd93a2D628327```
- Note same issue as above, acct2 in .env == <account2_address>


### Tests
- These should all fail
```
python add_prefix.py <ASN2> <ip2> <subnet> <account1_address>
python add_prefix.py <ASN1> <ip2> <subnet> <account1_address>
```

- These should succeed
```
python add_prefix.py <ASN2> <ip3> <subnet3> <account2_address>
python add_prefix.py <ASN2> <ip3> <subnet5> <account2_address>
```

### Transfer Prefix From ASN1 to ASN2
- Now, let's give ASN2 ASN1's IP/mask
    - this may occur if ASN2 is a customer of ASN1 and ASN1 needs to give IP space to ASN2
- we're going to use `add_prefix_asn_to_asn.py` here
- this will transfer ASN1's IP/mask to ASN2. 

```
python add_prefix_asn_to_asn.py <ASN2> <ip1> <subnet1> <account2_address>
```
Example:
```
python add_prefix_asn_to_asn.py 13 10.0.0.0 24 0xcF0A72EFd623c7aC7f9886213daFd93a2D628327
```
- Flow: ASN2 says they want to now own ip1/subnet1, so they hash and sign the data and "send" it to acct1.
    - Not really sent here. It's just passed to acct1 in the python file
- ASN1 takes the signed message from ASN2, generates the sigV, sigR, sigS, and then calls `prefix_addPrefix()` in the smart contract.
- the smart contract will 
    - validate that ASN2 signed the message saying it want ASN1's IP/subnet. 
    - ensure ASN1 is the one calling `prefix_addPrefix()`.
        - This is important because we don't want someone else to be able to call `prefix_addPrefix()` and transfer ASN1's IP/subnet away to someone else.

------------------------------------------

## Notes/Thoughts
Check
- who owns this. 
    - if ASN<=>IP/mask binding returns 0, then IANA owns it. in that case, caller of this function must be IANA? (let's start here)
    - if ASN<=>IP/mask binding returns some address, we need to figure out who that is.
        - we may need to make this a transfer_prefix() function or something. Need both current owner and new owner to sign and approve.
        - in fact, we could just ensure that the caller of this function (msg.sender) is the current owner of the IP/mask.
    - so it would just need to be an if statement. 
        - if current owner is 0,
            - Then this function must be called by someone in the owner's list (aka iana)
        - if current owner is 0xAFD14...A398F, then they must be the ones calling this function. 
    - essentially enforced a top down approach. current owner must delegate to new owner. 
    - but then new owner and current owner must both agree or something when to give up the space. or something. idk