from web3 import Web3, HTTPProvider


class Colors:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Note that you should create only one RPCProvider per
# process, as it recycles underlying TCP/IP network connections between
# your process and Ethereum node
web3 = Web3(HTTPProvider('http://localhost:8545'))

synced_block_str = str(web3.eth.blockNumber)
latest_block_obj = web3.eth.getBlock('latest')
latest_block_str = str(latest_block_obj.number)

print("\n ===== EWF - Client Test =====")
print(Colors.OK_BLUE + "Synced block:" + synced_block_str)
print(Colors.BOLD + "Latest block:" + latest_block_str)

if synced_block_str == latest_block_str:
    print(Colors.WARNING + "They match, your client is synced!" + Colors.END)
else:
    print(Colors.FAIL + "They mismatch, your client is NOT synced. Wait sync before using." + Colors.END)

print("\n")
