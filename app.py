from flask import Flask, request, jsonify
from AddressApi import *


app = Flask(__name__)

@app.route('/', methods=['GET'])
def btc_addr():
    return 'is life'

@app.route('/btc/', methods=['POST'])
def get_btc_addr():
    data = request.get_json()
    if data.get('param') == 'p':
        cls = BitcoinAddress(seed_phrase=data.get('phrase'))
        return jsonify({ 'private key': cls.private_key.hex(), 'public_key': cls.public_key.hex(),'native address': cls.bech32_address, 'segwit': cls.nested_address})
    elif data.get('param') == 'w':
        cls = BitcoinAddress(wif=data.get('phrase'))
        return jsonify({ 'private key': cls.private_key.hex(), 'public key': cls.public_key.hex(),'native address': cls.bech32_address, 'segwit': cls.nested_address})
    else:
        return jsonify({'error': 'Invalid parameter'}), 400

    


#####################################################
# 
# same addreses are usable for usdt,bnb (smart chain), polygon
# 
# ###################################################    
@app.route('/eth/', methods=['POST'])
def get_eth_addr():
    data = request.get_json()
    if data.get('param') == 'p':
        cls = Eth_addr(phrase=data.get('phrase'))
        return jsonify({ 'private key': cls.private_key, 'public_key': str(cls.public_key),'address': cls.address})
    elif data.get('param') == 'w':
        cls = Eth_addr(wif=data.get('phrase'))
        return jsonify({ 'private key': cls.private_key, 'public_key': str(cls.public_key),'address': cls.address})
    else:
        return jsonify({'error': 'Invalid parameter'}), 400

@app.route('/sol/', methods=['POST'])
def get_sol_addr():
    data = request.get_json()
    if data.get('param') == 'p':
        cls = Sol_addr(phrase=data.get('phrase'))
        return jsonify({ 'private key': str(cls.private_key),'address': str(cls.addr)})
    elif data.get('param') == 'w':
        cls = Sol_addr(private_key=data.get('phrase'))
        return jsonify({ 'private key': str(cls.private_key),'address': str(cls.addr)})
    else:
        return jsonify({'error': 'Invalid parameter'}), 400
    


