import os
import json
from web3 import Web3

#  compile  solidity
# https://github.com/iamdefinitelyahuman/py-solc-x
from solcx import compile_standard, install_solc

with open('./contracts/Recover.sol', 'r', encoding='utf-8') as f:
    recover_file = f.read()

#  download 0.8.0 Version of Solidity compiler 
install_solc('0.8.0')

#  compile Solidity
compiled_recover_sol = compile_standard(
    {
        "language": "Solidity",
        # Solidity file 
        "sources": {"Recover.sol": {"content": recover_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    #  Content generated after compilation 
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    #  edition , When writing smart contracts Solidity The version used corresponds to 
    solc_version="0.8.0",
)

#  The compiled results are written to the file 
with open('compiled_recover_code.json', 'w') as f:
    json.dump(compiled_recover_sol, f)