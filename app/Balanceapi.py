import requests
import json

class BalanceApi:
    def __init__(self,addr,coin,test=False): self.addr=addr; self.coin=coin; self.test=test
    def btc(self):
        url='https://blockstream.info/testnet/api/address/' if self.test else 'https://blockstream.info/api/address/'
        jsfy=requests.get(url+self.addr).json()
        return (jsfy['chain_stats']['funded_txo_sum']-jsfy['chain_stats']['spent_txo_sum'])/100000000
    def eth(self):
        base='https://api-sepolia.etherscan.io' if self.test else 'https://api.etherscan.io'
        url=base+'/api?module=account&action=balance&address='+self.addr+'&tag=latest&apikey=5AWQUFIMAZ9FBRRKBWEPVS264CQP3UVZZD'
        return int(requests.get(url).json()['result'])/10**18
    def sol(self):
        url='https://api.devnet.solana.com' if self.test else 'https://api.mainnet-beta.solana.com'
        payload={'jsonrpc':'2.0','id':1,'method':'getBalance','params':[self.addr]}
        result=requests.post(url,headers={'Content-Type':'application/json'},data=json.dumps(payload)).json()
        if 'result' in result: return result['result']['value']/1e9
        return result.get('error')['message']
    def __repr__(self):
        if self.coin==0: return str(self.btc())
        if self.coin==1: return str(self.eth())
        if self.coin==2: return str(self.sol())
