from flask import Flask, request, jsonify
from AddressApi import *
from Testnet import *
from Balanceapi import BalanceApi


app = Flask(__name__)

@app.route('/', methods=['GET'])
def btc_addr():
    return 'is life'

@app.route('/btc/',  methods=['POST'], defaults={'test': None})
@app.route('/btc/<test>', methods=['POST'])
def get_btc_addr(test):
    if test:
        data = request.get_json()
        if data.get('param') == 'p':
            cls = TestnetAddress(seed_phrase=data.get('phrase'))
            bal = BalanceApi(cls.bech32_address, 0, test=True).__repr__()
            return jsonify({ 'private key': cls.private_key.hex(), 'public_key': cls.public_key.hex(),'address': cls.bech32_address, 'segwit': cls.nested_address, 'balance': bal})
        elif data.get('param') == 'w':
            cls = TestnetAddress(wif=data.get('phrase'))
            bal = BalanceApi(cls.bech32_address, 0, test=True).__repr__()
            return jsonify({ 'private key': cls.private_key.hex(), 'public key': cls.public_key.hex(),'address': cls.bech32_address, 'segwit': cls.nested_address,  'balance': bal})
        else:
            return jsonify({'error': 'Invalid parameter'}), 400
    data = request.get_json()
    if data.get('param') == 'p':
        cls = BitcoinAddress(seed_phrase=data.get('phrase'))
        bal = BalanceApi(cls.bech32_address, 0, test=False).__repr__()
        return jsonify({ 'private key': cls.private_key.hex(), 'public_key': cls.public_key.hex(),'address': cls.bech32_address, 'segwit': cls.nested_address,  'balance': bal})
    elif data.get('param') == 'w':
        cls = BitcoinAddress(wif=data.get('phrase'))
        bal = BalanceApi(cls.bech32_address, 0, test=False).__repr__()
        return jsonify({ 'private key': cls.private_key.hex(), 'public key': cls.public_key.hex(),'address': cls.bech32_address, 'segwit': cls.nested_address,  'balance': bal})
    else:
        return jsonify({'error': 'Invalid parameter'}), 400

    


#####################################################
# 
# same addreses are usable for usdt,bnb (smart chain), polygon
# 
# ###################################################    
@app.route('/eth/', methods=['POST'], defaults={'test': None})
@app.route('/eth/<test>', methods=['POST'])
def get_eth_addr(test):
    if test:
        data = request.get_json()
        if data.get('param') == 'p':
            cls = testEth_addr(phrase=data.get('phrase'))
            bal = BalanceApi(cls.address, 1, test=True).__repr__()
            return jsonify({ 'private key': cls.private_key, 'public_key': str(cls.public_key),'address': cls.address, 'balance': bal})
        elif data.get('param') == 'w':
            cls = testEth_addr(wif=data.get('phrase'))
            bal = BalanceApi(cls.address, 1, test=True).__repr__()
            return jsonify({ 'private key': cls.private_key, 'public_key': str(cls.public_key),'address': cls.address, 'balance': bal})
        else:
            return jsonify({'error': 'Invalid parameter'}), 400
    data = request.get_json()
    if data.get('param') == 'p':
        cls = Eth_addr(phrase=data.get('phrase'))
        bal = BalanceApi(cls.address, 1, test=False).__repr__()
        return jsonify({ 'private key': cls.private_key, 'public_key': str(cls.public_key),'address': cls.address, 'balance': bal}) 
    elif data.get('param') == 'w':
        cls = Eth_addr(wif=data.get('phrase'))
        bal = BalanceApi(cls.address, 1, test=False).__repr__()
        return jsonify({ 'private key': cls.private_key, 'public_key': str(cls.public_key),'address': cls.address, 'balance': bal})
    else:
        return jsonify({'error': 'Invalid parameter'}), 400

@app.route('/sol/', methods=['POST'], defaults={'test': None})
@app.route('/sol/<test>', methods=['POST'])
def get_sol_addr(test):
    if test:
        data = request.get_json()
        if data.get('param') == 'p':
            cls = testSol_addr(phrase=data.get('phrase'))
            bal = BalanceApi(str(cls.addr), 2, test=False).__repr__()
            return jsonify({ 'private key': str(cls.private_key),'address': str(cls.addr), 'balance': bal})
        elif data.get('param') == 'w':
            cls = testSol_addr(private_key=data.get('phrase'))
            bal = BalanceApi(str(cls.addr), 2, test=False).__repr__()
            return jsonify({ 'private key': str(cls.private_key),'address': str(cls.addr), 'balance': bal})
        else:
            return jsonify({'error': 'Invalid parameter'}), 400
    data = request.get_json()
    if data.get('param') == 'p':
        cls = Sol_addr(phrase=data.get('phrase'))
        bal = BalanceApi(str(cls.addr), 2, test=False).__repr__()
        return jsonify({ 'private key': str(cls.private_key),'address': str(cls.addr), 'balance': bal})
    elif data.get('param') == 'w':
        cls = Sol_addr(private_key=data.get('phrase'))
        bal = BalanceApi(str(cls.addr), 2, test=False).__repr__()
        return jsonify({ 'private key': str(cls.private_key),'address': str(cls.addr), 'balance': bal})
    else:
        return jsonify({'error': 'Invalid parameter'}), 400
    


