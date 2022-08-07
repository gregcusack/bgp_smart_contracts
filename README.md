# bgp_smart_contracts


## TODO (written: 5/29/22) (updated: 8/7/22):
1) Make the below programs easier to run
    [x] pass in "owner" and "modifier" accounts in command line
    [x] I should be able to toggle between any of the three accounts across all python scripts instead of having to go in and change the account we're reading from in the env file. it's confusing lol
2) Implement The following
    - [x] Remove ASN 
    - [x] Remove Prefix
    - [x] Validate Prefix
    - [x] Add Advertisement
    - [x] Valdiate Advertisement 
3) BGP Code integration
    - [x] Add Origin Validation into BGP code
    - [ ] Add Path Validation to BGP code
    - [ ] Ensure Origin/Path validation working together



## How to Run (so far)
#### General Methods
- compile contract
- deploy contract

#### Origin Validation Methods
- add/remove ASN
- add/remove prefix
- validate prefix
- get ASN owner
- get prefix owner
- get prefixes owned by ASN

#### Path Validation Methods
- add advertisement
- validate advertisement

**Implementation done with cryptographic signings**

## Install Python Dependancies
```
python -m pip install -r requirements.txt
```

### A couple notes
The following accounts/addresses must be stored in .env
- ACCOUNT0_ADDRESS, ACCOUNT0_PRIVATE_KEY
    - The IANA account. Owner of the smart contract
- ACCOUNT1_ADDRESS, ACCOUNT1_PRIVATE_KEY
    - An AS Account (1)
- ACCOUNT2_ADDRESS, ACCOUNT2_PRIVATE_KEY
    - Another AS Account (2)

For path validation, each AS must have the contract address of all other AS's Path Validation Contracts
- Need asn_address_mapping.yaml

### Comile and deploy the smart contract
```
python compile.py <contract-name> 
# e.g. 
python compile.py IANA 
# or
python compile.py PATH_VALIDATION

python deploy.py <accountN> <contract-name>
# e.g. 
python deploy.py ACCOUNT0 PATH_VALIDATION
```

Next: 
For IANA contract deploy, 
- Copy address printed out from deploy.py into .env file

For PATH_VALIDATION contract deploy,
- Copy address printed out into the asn_address_mapping.yaml file under the apprpriate ASN

If use ACCOUNT0
- Note: these two commands will deploy from ACCOUNT0_ADDRESS in .env
- ACCOUNT0_ADDRESS becomes the owner of the contract. 
- ACCOUNT0_ADDRESS is the owner/IANA


### Add ASN to ASN<=>Address 
- this gives an ASN the ability to get assigned IP prefixes
- But an AS first needs to get added to the AS map by IANA

#### Add ASN1 to ASNMap
```
python add_asn.py <account0> <account1> <ASN1> <account1_address>
```
e.g.
```
python add_asn.py ACCOUNT0 ACCOUNT1 100 0x79bb7739B28ab9D6a846012156f5eadD0dE67361
```
- Note ensure account1_address passed in is equivalent to account1 in the .env file. (You can change this but they way it's set up now, you have make sure they are equivalent)

#### Add ASN2 to ASNMap
- Now update add_prefix.py. And read in account2 data instead of account 1. This will allow us to add an ASN for account2
```
python add_asn.py <account0> <account2> <ASN2> <account2_address>
```
e.g.
```
python add_asn.py ACCOUNT0 ACCOUNT2 200 0xcF0A72EFd623c7aC7f9886213daFd93a2D62832
```

### Add Prefix! IP/Subnet<=> ASN
-Note: IANA initially owns all IP space. And only IANA can allocate that space to someone else. unless that space is owned by someone else

#### Add a prefix for ASN1 (account1_address)
```
python add_prefix.py <account0> <account1> <ASN1> <ip1> <subnet1> <account1_address>
```
Example: 
```python add_prefix.py ACCOUNT0 ACCOUNT1 100 100.0.100.0 24 0x79bb7739B28ab9D6a846012156f5eadD0dE67361 ```
- Note same issue as above, acct1 in .env == <account1_address>

#### Add a prefix for ASN2 (account2_address)
- Now update add_prefix.py. And read in account2 data instead of account 1. This will allow us to add a prefix for account2
```
python add_prefix.py <ASN2> <ip2> <subnet> <account2_address>
```
Example: 
```python add_prefix.py ACCOUNT0 ACCOUNT2 200 200.0.200.0 24 0xcF0A72EFd623c7aC7f9886213daFd93a2D628327```
- Note same issue as above, acct2 in .env == <account2_address>


### Tests
- These should all fail
```
python add_prefix.py <account0> <account2> <ASN2> <ip2> <subnet> <account1_address>
python add_prefix.py <account0> <account2> <ASN1> <ip2> <subnet> <account1_address>
```

- These should succeed
```
python add_prefix.py <account0> <account2> <ASN2> <ip3> <subnet3> <account2_address>
python add_prefix.py <account0> <account2> <ASN2> <ip3> <subnet5> <account2_address>
```

### Transfer Prefix From ASN1 to ASN2
- Now, let's give ASN2 ASN1's IP/mask
    - this may occur if ASN2 is a customer of ASN1 and ASN1 needs to give IP space to ASN2
- we're going to use `add_prefix.py` here
- this will transfer ASN1's IP/mask to ASN2. 

```
python add_prefix.py <account1> <account2> <ASN2> <ip1> <subnet1> <account2_address>

```
Example:
```
python add_prefix.py ACCOUNT1 ACCOUNT2 200 100.0.100.0 24 0xcF0A72EFd623c7aC7f9886213daFd93a2D628327
```
- Flow: ASN2 says they want to now own ip1/subnet1, so they hash and sign the data and "send" it to acct1.
    - Not really sent here. It's just passed to acct1 in the python file
- ASN1 takes the signed message from ASN2, generates the sigV, sigR, sigS, and then calls `prefix_addPrefix()` in the smart contract.
- the smart contract will 
    - validate that ASN2 signed the message saying it want ASN1's IP/subnet. 
    - ensure ASN1 is the one calling `prefix_addPrefix()`.
        - This is important because we don't want someone else to be able to call `prefix_addPrefix()` and transfer ASN1's IP/subnet away to someone else.

### Valdiate Prefix
```
python validate_prefix.py <account1> <ip2> <subnet2> <ASN2>
```

Example:
```
python validate_prefix.py ACCOUNT1 100.0.100.0 24 200
```

## Path Validation
- BGPSEC implementation without all the heavyweight signing
- Each AS has its own advertisement contract!
  - Owner of contract can write to it but anybody can read from it
  - Contract contains:
    - Prefix and the ASN of the next Hop

## Example
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

### Add Announcement
Path of advertisements for example:
- 1 -> 2 -> 3 -> 4 -> ...
  
Format:
```
python add_advertisement.py <account> <ip> <subnet> <nextHopASN>
```

Example:
```
python add_advertisement.py ACCOUNT0 10.0.20.0 24 2
python add_advertisement.py ACCOUNT1 10.0.20.0 24 3
python add_advertisement.py ACCOUNT2 10.0.20.0 24 4
```

### Validate Advertisement

```
python validate_advertisement.py <account1> <ip> <subnet> <myASN> <Received advertisement's AS_PATH>
```

Example - Account 1 (ASN2) needs to validate that ASN1 has said for this ip/prefix it is sending it to ASN2
```
python validate_advertisement.py ACCOUNT0 10.0.20.0 24 2 1
```

Example - Account 2 (ASN3) needs to check down path that path 2->3 exists and 1->2 exists
```
python validate_advertisement.py ACCOUNT2 10.0.20.0 24 3 2 1
```

Example - Account 3 (ASN 4) checks down path that paths 3->4, 2->3, and 1->2 exist
```
python validate_advertisement.py ACCOUNT2 10.0.20.0 24 4 3 2 1
```
Example output for the last command:
```
AS_PATH Validation Results for: "10.0.20.0/24 : 3, 2, 1"
ASN 3 -> ASN 4 hop in AS_PATH is: valdiateAdvertisementResult.advertisementVALID
ASN 2 -> ASN 3 hop in AS_PATH is: valdiateAdvertisementResult.advertisementVALID
ASN 1 -> ASN 2 hop in AS_PATH is: valdiateAdvertisementResult.advertisementVALID
```

Example of a bad path:
- Account 4 (ASN 5) gets an advertisement: `10.0.20.0/24 : 3 2 1`
- Note that ASN3 never said they were sending to ASN5! So this should fail. Let's try:

```
python validate_advertisement.py ACCOUNT3 10.0.20.0 24 5 3 2 1
```
Result:
```
AS_PATH Validation Results for: "10.0.20.0/24 : 3, 2, 1"
ASN 3 -> ASN 5 hop in AS_PATH is: valdiateAdvertisementResult.advertisementINVALID
ASN 2 -> ASN 3 hop in AS_PATH is: valdiateAdvertisementResult.advertisementVALID
ASN 1 -> ASN 2 hop in AS_PATH is: valdiateAdvertisementResult.advertisementVALID
```
^ so this path 1 -> 2 -> 3 -> 5 is invalid!

------------------------------------------

## Notes/Thoughts
prefix_validatePrefix(addvertisedIp, advertisedMask, advertisedASN)
- all we're checking here is that an ASN and IP/subnet are matched together in the contract.
- we do not check that the advertisement received was actually sent by the ASN. 
    - this would require signing BGP updates/announcements. and adding signature in the BGP payload or something.
- 


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
