# bgp_smart_contracts

`IANA_addASNSigned()` seems to be working. but i should check with in correct addresses what happens.
```
function IANA_addASNSigned(uint32 ASN, address ASNOwner, bytes32 msgSignedHashed, uint8 sigV, bytes32 sigR, bytes32 sigS) public onlyOwners {
    // It must be signed by the new ASNOwner. We don't have to check for the IANA owner because
    // the onlyOwners routine does that for us.
    // require(ecrecover(IANA_getSignatureMessage(ASN, ASNOwner), sigV, sigR, sigS) == ASNOwner, "ecrecover failed!");
    require(ecrecover(msgSignedHashed, sigV, sigR, sigS) == ASNOwner, "ecrecover failed!");
    require(ASN != 0);
    require(ASNMap[ASN] == address(0), "ASN<=>ASNOwner mapping already added");
    
    // At this point, we have two party agreement on ASN ownership. Add it to the ANSList.
    ASNMap[ASN] = ASNOwner;


}
```

`prefix_addPrefixSigned()` works mostly. If I am in the ASN map: 13<=>my_address, I can add any prefix to ASN 13. Need to do a check here i think. 

For addprefix(), we're just making an ASN<=>IP/mask binding. But that binding needs to be approved by me, the ASN, AND (IANA or whoever is transfering the IP/mask to me). right? I shouldn't just be able to add arbitrary ip/prefixes to myself. 
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

Need to think more....

```
function prefix_addPrefixSigned(uint32 ip, uint8 mask, uint32 newOwnerAS, bytes32 msgSignedHashed, uint8 sigV, bytes32 sigR, bytes32 sigS) public returns (address) {
    // Only valid subnet masks
    require (mask <= 32);
    // Get the ASN's owner
    address newOwnerAddress = ASNMap[newOwnerAS];
    // The owning ASN must exist
    require (newOwnerAddress != address(0), "ASN not added to ASNMap");
    // The owning ASN must have signed the message.
    // require(ecrecover(IANA_getPrefixSignatureMessage(ip, mask, newOwnerAS, newOwnerAddress), sigV, sigR, sigS) == newOwnerAddress);
    require(ecrecover(msgSignedHashed, sigV, sigR, sigS) == newOwnerAddress);

    PrefixASNMap[ip][mask] = newOwnerAS;
}
```