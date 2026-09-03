from mnemonic import Mnemonic
from bit import Key
from eth_account import Account
from bip32utils import BIP32Key
import hashlib
import base58
import ecdsa
from solders.keypair import Keypair
from solders.pubkey import Pubkey

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def bech32_polymod(values):
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk

def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_verify_checksum(hrp, data):
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1

def bech32_create_checksum(hrp, data):
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_encode(hrp, data):
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])

def bech32_decode(bech):
    if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
            (bech.lower() != bech and bech.upper() != bech)):
        return (None, None)
    bech = bech.lower()
    pos = bech.rfind('1')
    if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
        return (None, None)
    if not all(x in CHARSET for x in bech[pos+1:]):
        return (None, None)
    hrp = bech[:pos]
    data = [CHARSET.find(x) for x in bech[pos+1:]]
    if not bech32_verify_checksum(hrp, data):
        return (None, None)
    return (hrp, data[:-6])

def convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad and bits:
        ret.append((acc << (tobits - bits)) & maxv)
    elif not pad and (bits >= frombits or ((acc << (tobits - bits)) & maxv)):
        return None
    return ret

class BitcoinAddress:
    def __init__(self, seed_phrase=None, wif=None):
        self.seed_phrase = seed_phrase
        self.wif = wif
        if seed_phrase:
            self.private_key = self.generate_private_key_from_seed(seed_phrase)
        if wif:
            self.private_key = self.decode_wif(wif)
        self.public_key = self.generate_public_key(self.private_key)
        self.keyhash = self.generate_keyhash(self.public_key)
        self.nested_address = self.generate_nested_address(self.keyhash)
        self.bech32_address = self.generate_bech32_address(self.keyhash)

    def generate_private_key_from_seed(self, seed_phrase):
        return hashlib.pbkdf2_hmac('sha256', seed_phrase.encode('utf8'), b'', 1000000, 32)

    def decode_wif(self, wif):
        decoded = base58.b58decode(wif)
        return decoded[1:-5]

    def generate_public_key(self, private_key):
        signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.get_verifying_key()
        x_cor = verifying_key.to_string()[:32]
        y_cor = verifying_key.to_string()[32:]
        prefix = '02' if int.from_bytes(y_cor, byteorder="big", signed=True) % 2 == 0 else '03'
        return bytes.fromhex(f'{prefix}{x_cor.hex()}')

    def generate_keyhash(self, public_key):
        sha256_1 = hashlib.sha256(public_key)
        ripemd160 = hashlib.new("ripemd160")
        ripemd160.update(sha256_1.digest())
        return ripemd160.digest()

    def generate_nested_address(self, keyhash):
        p2wpkh = bytes.fromhex(f'0014{keyhash.hex()}')
        sha256_p2wpkh = hashlib.sha256(p2wpkh)
        ripemd160_p2wpkh = hashlib.new("ripemd160")
        ripemd160_p2wpkh.update(sha256_p2wpkh.digest())
        hashed = ripemd160_p2wpkh.digest()
        checksum = hashlib.sha256(hashlib.sha256(bytes.fromhex(f'05{hashed.hex()}')).digest()).digest()[:4]
        return base58.b58encode(bytes.fromhex(f'05{hashed.hex()}{checksum.hex()}')).decode()

    def generate_bech32_address(self, keyhash):
        return bech32_encode('bc', [0] + convertbits(keyhash, 8, 5))

class Eth_addr:
    def __init__(self, phrase=None, wif=None):
        self.phrase = phrase
        self.wif = wif
        Account.enable_unaudited_hdwallet_features()
        if self.phrase:
            acct = Account.from_mnemonic(self.phrase)
            self.private_key = '0x' + acct._private_key.hex()
            self.public_key = acct._key_obj.public_key
            self.address = acct.address
        if self.wif:
            try:
                acct = Account.from_key(wif)
                self.private_key = '0x' + acct._private_key.hex()
                self.public_key = acct._key_obj.public_key
                self.address = acct.address
            except Exception as e:
                self.private_key = e
                self.public_key = e
                self.address = e

class Sol_addr:
    def __init__(self, phrase=None, private_key=None):
        self.phrase = phrase
        self.private_key = private_key
        if self.private_key:
            key_to_bytes = base58.b58decode(self.private_key)
            self.sol_keypair = Keypair.from_bytes(key_to_bytes[:64])
            self.addr = self.sol_keypair.pubkey()
        if self.phrase:
            self.sol_keypair = Keypair().from_seed_phrase_and_passphrase(seed_phrase=phrase, passphrase='')
            self.addr = self.sol_keypair.pubkey()
            self.private_key = self.sol_keypair
