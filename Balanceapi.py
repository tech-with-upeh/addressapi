import requests
import json

class BalanceApi:
    def __init__(self, addr, coin, test=False):
        self.addr = addr
        self.coin = coin
        self.test = test
    
    def btc(self):
        url = 'https://blockstream.info/api/address/'
        if self.test:
            url = 'https://blockstream.info/testnet/api/address/'
        res = requests.get(url+self.addr)
        jsfy = res.json()
        return (jsfy["chain_stats"]["funded_txo_sum"]- jsfy["chain_stats"]["spent_txo_sum"])/ 100000000

    def eth(self):
        # Get Ethereum balance using etherscan API
        url = 'https://api.etherscan.io/api?module=account&action=balance&address='+self.addr+'&tag=latest&apikey=5AWQUFIMAZ9FBRRKBWEPVS264CQP3UVZZD'
        if self.test:
            url = 'https://api-sepolia.etherscan.io/api?module=account&action=balance&address='+ self.addr+'&tag=latest&apikey=5AWQUFIMAZ9FBRRKBWEPVS264CQP3UVZZD'
        res = requests.get(url)
        jsfy = res.json()
        return (int(jsfy['result'])/10**18)

    def sol(self):
        url = "https://api.mainnet-beta.solana.com"
        if self.test:
            url = "https://api.devnet.solana.com"
        # JSON-RPC request payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [self.addr]
        }
        headers = {
    "Content-Type": "application/json"
}
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Parse the response
        result = response.json()
        print(result)
        if "result" in result:
            lamports = result["result"]["value"]
            sol = lamports / 1e9  # Convert lamports to SOL
            return sol
        else:
            return result.get("error")['message']
    
    def __repr__(self):
        if self.coin == 0:
            return str(self.btc())
        elif self.coin ==  1:
            return str(self.eth())
        elif self.coin == 2:
            return str(self.sol())

# Example usage:
# cls = BalanceApi('0x911f8cF502070E74Bcd0cdC44E33252cBd7c0c55', 1, test=False)
# print(cls)



