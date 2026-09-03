from eth_account import Account
import hashlib
import base58
import ecdsa
from solders.keypair import Keypair

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def bech32_polymod(values):
    generator=[0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3]
    chk=1
    for value in values:
        top=chk>>25; chk=(chk&0x1ffffff)<<5^value
        for i in range(5): chk ^= generator[i] if ((top>>i)&1) else 0
    return chk

def bech32_hrp_expand(hrp): return [ord(x)>>5 for x in hrp]+[0]+[ord(x)&31 for x in hrp]
def bech32_verify_checksum(hrp,data): return bech32_polymod(bech32_hrp_expand(hrp)+data)==1

def bech32_create_checksum(hrp,data):
    polymod=bech32_polymod(bech32_hrp_expand(hrp)+data+[0,0,0,0,0,0])^1
    return [(polymod>>5*(5-i))&31 for i in range(6)]

def bech32_encode(hrp,data):
    combined=data+bech32_create_checksum(hrp,data)
    return hrp+'1'+''.join(CHARSET[d] for d in combined)

def convertbits(data,frombits,tobits,pad=True):
    acc=bits=0; ret=[]; maxv=(1<<tobits)-1; max_acc=(1<<(frombits+tobits-1))-1
    for value in data:
        if value<0 or value>>frombits: return None
        acc=((acc<<frombits)|value)&max_acc; bits+=frombits
        while bits>=tobits:
            bits-=tobits; ret.append((acc>>bits)&maxv)
    if pad and bits: ret.append((acc<<(tobits-bits))&maxv)
    elif not pad and (bits>=frombits or ((acc<<(tobits-bits))&maxv)): return None
    return ret

class TestnetAddress:
    def __init__(self,seed_phrase=None,wif=None):
        self.seed_phrase=seed_phrase; self.wif=wif
        if seed_phrase: self.private_key=self.generate_private_key_from_seed(seed_phrase)
        if wif: self.private_key=self.decode_wif(wif)
        self.public_key=self.generate_public_key(self.private_key)
        self.keyhash=self.generate_keyhash(self.public_key)
        self.nested_address=self.generate_nested_address(self.keyhash)
        self.bech32_address=self.generate_bech32_address(self.keyhash)
    def generate_private_key_from_seed(self,seed_phrase): return hashlib.pbkdf2_hmac('sha256',seed_phrase.encode('utf8'),b'',1000000,32)
    def decode_wif(self,wif): return base58.b58decode(wif)[1:-5]
    def generate_public_key(self,private_key):
        sk=ecdsa.SigningKey.from_string(private_key,curve=ecdsa.SECP256k1); vk=sk.get_verifying_key(); raw=vk.to_string(); x,y=raw[:32],raw[32:]
        return bytes.fromhex(('02' if int.from_bytes(y,byteorder='big',signed=True)%2==0 else '03')+x.hex())
    def generate_keyhash(self,public_key):
        h=hashlib.sha256(public_key); r=hashlib.new('ripemd160'); r.update(h.digest()); return r.digest()
    def generate_nested_address(self,keyhash):
        p2w=bytes.fromhex('0014'+keyhash.hex()); h=hashlib.sha256(p2w); r=hashlib.new('ripemd160'); r.update(h.digest()); hashed=r.digest(); checksum=hashlib.sha256(hashlib.sha256(bytes.fromhex('c4'+hashed.hex())).digest()).digest()[:4]
        return base58.b58encode(bytes.fromhex('c4'+hashed.hex()+checksum.hex())).decode()
    def generate_bech32_address(self,keyhash): return bech32_encode('tb',[0]+convertbits(keyhash,8,5))

class testEth_addr:
    def __init__(self,phrase=None,wif=None):
        self.phrase=phrase; self.wif=wif; Account.enable_unaudited_hdwallet_features()
        if phrase:
            acct=Account.from_mnemonic(phrase); self.private_key='0x'+acct._private_key.hex(); self.public_key=acct._key_obj.public_key; self.address=acct.address
        if wif:
            try:
                acct=Account.from_key(wif); self.private_key='0x'+acct._private_key.hex(); self.public_key=acct._key_obj.public_key; self.address=acct.address
            except Exception as e: self.private_key=e; self.public_key=e; self.address=e

class testSol_addr:
    def __init__(self,phrase=None,private_key=None):
        self.phrase=phrase; self.private_key=private_key
        if private_key:
            key_to_bytes=base58.b58decode(private_key); self.sol_keypair=Keypair.from_bytes(key_to_bytes[:64]); self.addr=self.sol_keypair.pubkey()
        if phrase:
            self.sol_keypair=Keypair().from_seed_phrase_and_passphrase(seed_phrase=phrase,passphrase=''); self.addr=self.sol_keypair.pubkey(); self.private_key=base58.b58encode(self.sol_keypair.secret()).decode()
