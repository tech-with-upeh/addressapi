from flask import Flask, request, jsonify
from .AddressApi import BitcoinAddress, Eth_addr, Sol_addr
from .Testnet import TestnetAddress, testEth_addr, testSol_addr
from .Balanceapi import BalanceApi

app = Flask(__name__)

@app.route('/', methods=['GET'])
def btc_addr():
    return 'is life'

@app.route('/btc/', methods=['POST'], defaults={'test': None})
@app.route('/btc/<test>', methods=['POST'])
def get_btc_addr(test):
    data=request.get_json()
    if test:
        if data.get('param')=='p': cls=TestnetAddress(seed_phrase=data.get('phrase'))
        elif data.get('param')=='w': cls=TestnetAddress(wif=data.get('phrase'))
        else: return jsonify({'error':'Invalid parameter'}),400
        bal=BalanceApi(cls.bech32_address,0,test=True).__repr__()
        return jsonify({'private key':cls.private_key.hex(),'public_key':cls.public_key.hex(),'address':cls.bech32_address,'segwit':cls.nested_address,'balance':bal})
    if data.get('param')=='p': cls=BitcoinAddress(seed_phrase=data.get('phrase'))
    elif data.get('param')=='w': cls=BitcoinAddress(wif=data.get('phrase'))
    else: return jsonify({'error':'Invalid parameter'}),400
    bal=BalanceApi(cls.bech32_address,0,test=False).__repr__()
    return jsonify({'private key':cls.private_key.hex(),'public_key':cls.public_key.hex(),'address':cls.bech32_address,'segwit':cls.nested_address,'balance':bal})

@app.route('/eth/', methods=['POST'], defaults={'test': None})
@app.route('/eth/<test>', methods=['POST'])
def get_eth_addr(test):
    data=request.get_json()
    cls = (testEth_addr(phrase=data.get('phrase')) if data.get('param')=='p' else testEth_addr(wif=data.get('phrase')) if data.get('param')=='w' else None) if test else (Eth_addr(phrase=data.get('phrase')) if data.get('param')=='p' else Eth_addr(wif=data.get('phrase')) if data.get('param')=='w' else None)
    if cls is None: return jsonify({'error':'Invalid parameter'}),400
    bal=BalanceApi(cls.address,1,test=bool(test)).__repr__()
    return jsonify({'private key':cls.private_key,'public_key':str(cls.public_key),'address':cls.address,'balance':bal})

@app.route('/sol/', methods=['POST'], defaults={'test': None})
@app.route('/sol/<test>', methods=['POST'])
def get_sol_addr(test):
    data=request.get_json()
    cls = (testSol_addr(phrase=data.get('phrase')) if data.get('param')=='p' else testSol_addr(private_key=data.get('phrase')) if data.get('param')=='w' else None) if test else (Sol_addr(phrase=data.get('phrase')) if data.get('param')=='p' else Sol_addr(private_key=data.get('phrase')) if data.get('param')=='w' else None)
    if cls is None: return jsonify({'error':'Invalid parameter'}),400
    bal=BalanceApi(str(cls.addr),2,test=bool(test)).__repr__()
    return jsonify({'private key':str(cls.private_key),'address':str(cls.addr),'balance':bal})
