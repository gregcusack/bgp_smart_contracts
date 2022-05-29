pragma solidity ^0.8.0;

contract IANA {
    struct Prefix {
        uint32 ip;
        uint8 mask;
        uint32 owningAS;
        uint[] subPrefixes; // Pointer to prefix index in the larger prefixes array.
    }
    
    // All the people who can change the function pointers
    mapping (address => bool) public ownerMap;
    // The associative mapping that maps ASNs to their owner's public key.
    mapping (uint32 => address) public ASNMap;

    // ip => masks => ASN
    mapping (uint32 => mapping(uint8 => uint32)) public PrefixASNMap;

    // List of prefixes.
    Prefix[] public prefixes;
    // Holds the table of links keyed by sha256(encodePacked(ASN1,ASN2))
    // A link is valid if both ASN1->ASN2 and ASN2->ASN1 exist.
    // This particular structure has the potential to be astoundingly large.
    mapping (bytes32 => bool) links;


    /// Simple modifier to ensure that only owners can make changes
    modifier onlyOwners {
        require(ownerMap[msg.sender] == true);
        _;
    }

    address importantAddress;
    constructor(address _importantAddress) public {
        // Automatically add the contract creator as an owner
        ownerMap[msg.sender] = true;

        // Mark that the root is owned by a dummy address.
        ASNMap[0] = address(0);
        // Build up the prefix for the root prefix
        PrefixASNMap[0][0] = 0;
        importantAddress = _importantAddress;

    }


    /// Adds the specified prefix to the prefix table. Must be done by the owner of the prefixes containing
    /// AS and must include the signature of the message returned by IANA_getPrefixSignatureMessage for the new AS.
    /// @param ip The IP address of the prefix to add
    /// @param mask The number of bits in the netmask of the prefix to add
    /// @param newOwnerAS The AS number to associate with the new prefix to.
    function prefix_addPrefix(uint32 ip, uint8 mask, uint32 newOwnerAS) public {//, bytes32 msgSignedHashed, uint8 sigV, bytes32 sigR, bytes32 sigS) public {
        // Only valid subnet masks
        require (mask <= 32);
        // Get the ASN's owner
        address newOwnerAddress = ASNMap[newOwnerAS];
        // The owning ASN must exist
        require (newOwnerAddress != address(0), "ASN not added to ASNMap");
        // The owning ASN must have signed the message.
        // require(ecrecover(IANA_getPrefixSignatureMessage(ip, mask, newOwnerAS, newOwnerAddress), sigV, sigR, sigS) == newOwnerAddress);
        // require(ecrecover(msgSignedHashed, sigV, sigR, sigS) == newOwnerAddress);

        PrefixASNMap[ip][mask] = newOwnerAS;
    }

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

    function prefix_validatePrefix(uint32 ip, uint8 mask, uint32 ASN) public {
        require (mask <= 32);

        //check that there is an IP/mask mapping to an ASN. 
        uint32 ownerAS = PrefixASNMap[ip][mask];

        //ensure IP/mask mapping to ASN exists. will be 0 if IP/mask has not been assigned
        require(ownerAS != 0, "IP/mask in advertisement not registered to assigned to an AS");
        
        // Ensure the ASN from advertisement and stored in PrefixMap are the same
        require(ASN == ownerAS, "ASN in advertisement != ASN in PrefixASNMap");
        
        // If an ASN has been assigned a prefix, it has to be in this map. This should never trigger.
        address asnAddress = ASNMap[ownerAS];
        require (asnAddress != address(0), "ASN not added to ASNMap. BAD THINGS IF WE SEE THIS");


    }

    /// Generates the message text to be signed for add authentication.
    /// @param ASN The ASN to be added
    /// @param ASNOwner The public key of the new owner.
    /// @return bytes32 The sha256 hash of abi.encodePacked(ASN,ASNOwner).
    function IANA_getPrefixSignatureMessage(uint32 ip, uint8 mask, uint32 ASN, address ASNOwner) pure public returns(bytes32) {
        return sha256(abi.encodePacked(ip, mask, ASN, ASNOwner));
    }
    


    /// Returns the owner's address for the given ASN, or 0 if no one owns the ASN.
    /// @param ASN The ASN whose owner is to be returned
    /// @return address The address of the owner.
    function IANA_getASNOwner(uint32 ASN) public view returns (address) {
        return ASNMap[ASN];
    }
    
    /// Generates the message text to be signed for add authentication.
    /// @param ASN The ASN to be added
    /// @param ASNOwner The public key of the new owner.
    /// @return bytes32 The sha256 hash of abi.encodePacked(ASN,ASNOwner).
    // function IANA_getSignatureMessage(uint32 ASN, address ASNOwner) pure public returns(bytes32) {
    //     return sha256(abi.encodePacked(ASN,ASNOwner));
    // }
    
    function IANA_getSignatureMessage(uint32 ASN, address ASNOwner) pure public returns(bytes32) {
        return keccak256(abi.encodePacked(ASN,ASNOwner));
    }

    /// Adds an additional ASN to the ASN list. The operation has to include a signature
    /// from the ASN owner signing sha256(abi.encodePacked(ASN,ASNOwner)) which can be
    /// generated by calling IANA_getSignatureMessage()
    /// @param ASN The ASN to be added
    /// @param ASNOwner The public key of the new owner.
    function IANA_addASN(uint32 ASN, address ASNOwner) public onlyOwners { //, uint8 sigV, bytes32 sigR, bytes32 sigS) public onlyOwners {
        // It must be signed by the new ASNOwner. We don't have to check for the IANA owner because
        // the onlyOwners routine does that for us.
        // require(ecrecover(IANA_getSignatureMessage(ASN, ASNOwner), sigV, sigR, sigS) == ASNOwner);
        require(ASN != 0);
        
        // At this point, we have two party agreement on ASN ownership. Add it to the ANSList.
        ASNMap[ASN] = ASNOwner;
    }

    // function IANA_addASNSigned(uint32 ASN, address ASNOwner, uint8 sigV, bytes32 sigR, bytes32 sigS) public onlyOwners {
    //     // It must be signed by the new ASNOwner. We don't have to check for the IANA owner because
    //     // the onlyOwners routine does that for us.
    //     require(ecrecover(IANA_getSignatureMessage(ASN, ASNOwner), sigV, sigR, sigS) == ASNOwner, "ecrecover failed!");
    //     require(ASN != 0);
        
    //     // At this point, we have two party agreement on ASN ownership. Add it to the ANSList.
    //     ASNMap[ASN] = ASNOwner;
    // }

    // function IANA_addASNSigned(uint32 ASN, address ASNOwner, bytes32 msgSignedHashed, uint8 sigV, bytes32 sigR, bytes32 sigS) public onlyOwners {
    function IANA_addASNSigned(uint32 ASN, address ASNOwner, uint8 sigV, bytes32 sigR, bytes32 sigS) public view onlyOwners returns (address) {

        // It must be signed by the new ASNOwner. We don't have to check for the IANA owner because
        // the onlyOwners routine does that for us.
        // require(ecrecover(IANA_getSignatureMessage(ASN, ASNOwner), sigV, sigR, sigS) == ASNOwner, "ecrecover failed!");
        // require(ecrecover(msgSignedHashed, sigV, sigR, sigS) == ASNOwner, "ecrecover failed!");
        // bytes memory prefix = "\x19Ethereum Signed Message:\n32";
        bytes32 hashASN = IANA_getSignatureMessage(ASN, ASNOwner);
        // bytes32 prefixedHash = keccak256(abi.encodePacked(prefix, hashASN));

        // address addr = ecrecover(prefixedHash, sigV, sigR, sigS);
        address addr = ecrecover(hashASN, sigV, sigR, sigS);

        // require( == ASNOwner);
        
        // require(ASN != 0);
        // require(ASNMap[ASN] == address(0), "ASN<=>ASNOwner mapping already added");
        
        // At this point, we have two party agreement on ASN ownership. Add it to the ANSList.
        // ASNMap[ASN] = ASNOwner;
        return addr;
    }

    /// Removes an ASN to the ASN list. The operation has to include a signature
    /// from the ASN owner signing sha256(abi.encodePacked(ASN,ASNOwner)) which can be
    /// generated by calling IANA_getSignatureMessage()
    /// @param ASN The ASN to be added
    /// @param ASNOwner The public key of the new owner.
    /// @param sigV The V parameter of the signature.
    /// @param sigR The R parameter of the signature.
    /// @param sigS The S parameter of the signature.
    function IANA_removeASN(uint32 ASN, address ASNOwner, uint8 sigV, bytes32 sigR, bytes32 sigS) public onlyOwners {
        // Get hash of the packed message that was signed.
        bytes32 msghash = sha256(abi.encodePacked(ASN,ASNOwner));
        // It must be signed by the new ASNOwner. We don't have to check for the IANA owner because
        // the onlyOwners routine does that for us.
        require(ecrecover(msghash, sigV, sigR, sigS) == ASNOwner);
        require(ASN != 0);
        
        // At this point, we have two party agreement on ASN ownership. Mark the ASN as unowned
        ASNMap[ASN] = address(0);
    }

    /// Adds an additional user to the owners table, allowing them to modify the discovery tables.
    /// @param owner The public key of the new owner.
    function IANA_addOwner(address owner) public onlyOwners {
        ownerMap[owner] = true;
    }

    /// Removes a user from the owners table, who will no longer be allowed to edit the discovery table.
    /// @param owner The public key of the owner to be removed.
    function IANA_removeOwner(address owner) public onlyOwners {
        delete(ownerMap[owner]);
    }


  function splitSignature(bytes memory sig)
       public
       pure
       returns (uint8, bytes32, bytes32)
   {
       require(sig.length == 65);
       
       bytes32 r;
       bytes32 s;
       uint8 v;
       assembly {
           // first 32 bytes, after the length prefix
           r := mload(add(sig, 32))
           // second 32 bytes
           s := mload(add(sig, 64))
           // final byte (first byte of the next 32 bytes)
           v := byte(0, mload(add(sig, 96)))
       }
       return (v, r, s);
   }

   function recoverSigner(bytes32 message, bytes memory sig)
       public
       pure
       returns (address)
    {
       uint8 v;
       bytes32 r;
       bytes32 s;
       (v, r, s) = splitSignature(sig);
       return ecrecover(message, v, r, s);
  }

  
   function isValidData(uint256 _number, string memory _word, bytes memory sig) public view returns(bool){
       bytes32 message = keccak256(abi.encodePacked(_number, _word));
       return (recoverSigner(message, sig) == importantAddress);
   }

    
}
