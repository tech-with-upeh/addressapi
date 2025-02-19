from mnemonic import Mnemonic
from bit import Key
from eth_account import Account
from bip32utils import BIP32Key
import hashlib
import base58
import ecdsa
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Bech32 functions (added for address encoding)
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def bech32_polymod(values):
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk

def bech32_hrp_expand(hrp):
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_verify_checksum(hrp, data):
    """Verify a checksum given HRP and converted data characters."""
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1

def bech32_create_checksum(hrp, data):
    """Compute the checksum values given HRP and data."""
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_encode(hrp, data):
    """Compute a Bech32 string given HRP and data values."""
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])

def bech32_decode(bech):
    """Validate a Bech32 string, and determine HRP and data."""
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
    return (hrp, data[:-6])  # Skip the last 6 bytes of checksum

def convertbits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
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
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret

# Function to generate Bitcoin address from WIF or Seed Phrase
class TestnetAddress:
    def __init__(self, seed_phrase=None, wif=None):
        self.seed_phrase = seed_phrase
        self.wif = wif

        # Generate private key if seed phrase is provided
        if seed_phrase:
            self.private_key = self.generate_private_key_from_seed(seed_phrase)
        
        # Decode WIF private key if provided
        if wif:
            self.private_key = self.decode_wif(wif)

        # Generate the public key from the private key
        self.public_key = self.generate_public_key(self.private_key)
        
        # Generate address
        self.keyhash = self.generate_keyhash(self.public_key)
        self.nested_address = self.generate_nested_address(self.keyhash)
        self.bech32_address = self.generate_bech32_address(self.keyhash)

    def generate_private_key_from_seed(self, seed_phrase):
        """Generate private key from seed phrase"""
        # Seed generation logic for seed phrase to private key
        # For simplicity, here we are using a random generated private key
        return hashlib.pbkdf2_hmac('sha256', seed_phrase.encode('utf8'), b'', 1000000, 32)

    def decode_wif(self, wif):
        """Decode Wallet Import Format (WIF) private key"""
        decoded = base58.b58decode(wif)
        version_byte = decoded[0]  # Version byte (0x80 for Bitcoin)
        private_key = decoded[1:-5]
        return private_key

    def generate_public_key(self, private_key):
        """Generate public key from private key using ECDSA and SECP256k1"""
        signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.get_verifying_key()
        x_cor = bytes.fromhex(verifying_key.to_string().hex())[:32]
        y_cor = bytes.fromhex(verifying_key.to_string().hex())[32:]
        if int.from_bytes(y_cor, byteorder="big", signed=True) % 2 == 0:
            public_key = bytes.fromhex(f'02{x_cor.hex()}')
        else:
            public_key = bytes.fromhex(f'03{x_cor.hex()}')
        return public_key

    def generate_keyhash(self, public_key):
        """Generate key hash from public key using SHA256 + RIPEMD160"""
        sha256_1 = hashlib.sha256(public_key)
        ripemd160 = hashlib.new("ripemd160")
        ripemd160.update(sha256_1.digest())
        return ripemd160.digest()

    def generate_nested_address(self, keyhash):
        """Generate P2SH nested address"""
        P2WPKH_VO = bytes.fromhex(f'0014{keyhash.hex()}')
        sha256_P2WPKH_VO = hashlib.sha256(P2WPKH_VO)
        ripemd160_P2WPKH_VO = hashlib.new("ripemd160")
        ripemd160_P2WPKH_VO.update(sha256_P2WPKH_VO.digest())
        hashed_P2WPKH_VO = ripemd160_P2WPKH_VO.digest()
        P2SH_P2WPKH_V0 = bytes.fromhex(f'a9{hashed_P2WPKH_VO.hex()}87')
        checksum_full = hashlib.sha256(hashlib.sha256(bytes.fromhex(f'c4{hashed_P2WPKH_VO.hex()}')).digest()).digest()
        checksum = checksum_full[:4]
        bin_addr = bytes.fromhex(f'c4{hashed_P2WPKH_VO.hex()}{checksum.hex()}')
        return base58.b58encode(bin_addr).decode()

    def generate_bech32_address(self, keyhash):
        """Generate Bech32 address from keyhash"""
        return bech32_encode('tb', [0] + convertbits(keyhash, 8, 5))

# Ethereum Address Generator Class
class testEth_addr:
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

            except Exception as  e:
                self.private_key = e
                self.public_key = e
                self.address = e

# Solana Address Generator Class
class testSol_addr:
    def __init__(self, phrase=None, private_key=None):
        self.phrase = phrase
        self.private_key = private_key
        if self.private_key:
            key_to_bytes = base58.b58decode(self.private_key)
            self.sol_keypair = Keypair.from_bytes(key_to_bytes[:64])
            self.addr = self.sol_keypair.pubkey()
        if self.phrase:
            self.sol_keypair = Keypair().from_seed_phrase_and_passphrase(seed_phrase=self.phrase, passphrase='')
            self.addr = self.sol_keypair.pubkey()
            self.private_key = base58.b58encode(self.sol_keypair.secret()).decode()

# Example Usage
# seed_phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
# bitcoin_wallet = TestnetAddress(wif='KxYN4B5LvvmikjNb6QMkWGwV27BmRJSPqaCaUVdaywn9936wNWof')

# print(f"🔹 Nested SegWit Address (P2SH)  : {bitcoin_wallet.nested_address}")
# print(f"🔹 Bech32 Address (SegWit): {bitcoin_wallet.bech32_address}")
# print(f"🔹 Private key: {bitcoin_wallet.private_key.hex()}")

# eth_wallet = Eth_addr(phrase=seed_phrase)
# print(f"🔹 Ethereum Address: {eth_wallet.address}")
# print(f"🔹 Ethereum Private Key: {eth_wallet.private_key}")

# sol_wallet = Sol_addr(phrase=seed_phrase)
# print(f"🔹 Solana Address: {sol_wallet.addr}")
# print(f"🔹 Solana Private Key: {sol_wallet.private_key}")