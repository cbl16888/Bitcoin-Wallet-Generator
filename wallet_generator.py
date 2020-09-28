import argparse
import hashlib
import os
from binascii import hexlify, unhexlify
from struct import Struct
from utils import g, b58encode, b58decode
import blockcypher
from moneywagon import AddressBalance

PACKER = Struct('>QQQQ')


def count_leading_zeroes(s):
    count = 0
    for c in s:
        if c == '\0':
            count += 1
        else:
            break
    return count


def base58_check_encode(prefix, payload, compressed=False):
    # Add version byte in front of RIPEMD-160 hash (0x00 for Main Network)
    s = prefix + payload
    if compressed:
        s = prefix + payload + b'\x01'

    # Add the 4 checksum bytes at the end of extended RIPEMD-160 hash. This is the 25-byte binary Bitcoin Address.
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
    result = s + checksum
    return '1' * count_leading_zeroes(result) + b58encode(result).decode()


def pub_key_to_addr(s):
    ripemd160 = hashlib.new('ripemd160')
    hash_sha256 = hashlib.new('SHA256')
    # Perform SHA-256 hashing on the public key
    hash_sha256.update(bytes.fromhex(s))
    # Perform RIPEMD-160 hashing on the result of SHA-256
    ripemd160.update(hash_sha256.digest())
    return base58_check_encode(b'\0', ripemd160.digest())


def int_to_address(number):
    number0 = number >> 192
    number1 = (number >> 128) & 0xffffffffffffffff
    number2 = (number >> 64) & 0xffffffffffffffff
    number3 = number & 0xffffffffffffffff

    private_key = hexlify(PACKER.pack(number0, number1, number2, number3)).decode("utf-8")

    ###############################################
    print('Converting from: ' + str(int(private_key, 16)))
    ###############################################

    compressed_key = base58_check_encode(b'\x80', unhexlify(private_key), True)
    
    ###############################################
    print('Private key: ' + compressed_key)
    ###############################################

    # address
    x, y = str(g * int(private_key, 16)).split()
    len1 = len(x)
    len2 = len(y)
    if len1 != 64:
        z = 64 - len1
        x = '0'*z + x

    if len2 != 64:
        z = 64 - len2
        y = '0'*z + y
    compressed_public_key_with_out_prefix = x + y
    pk_prefix = '02'
    if not int(compressed_public_key_with_out_prefix[64:], 16) % 2 == 0:
        pk_prefix = '03'
    compressed_public_key = pk_prefix + compressed_public_key_with_out_prefix[:64]
    

    ###############################################

    print('Public key: ' + compressed_public_key)
    ###############################################

    ###############################################
    print('Bitcoin address: ' + pub_key_to_addr(compressed_public_key))
    with open('wallet.txt', "a") as f:
        f.write('Converting from: ' + str(int(private_key, 16)) +'\nPrivate key: ' + compressed_key +'\nPublic key: ' + compressed_public_key + '\nBitcoin address: ' + pub_key_to_addr(compressed_public_key)+'\n#####################################################################\n\n\n\n')
    try:
        total = blockcypher.get_total_balance(pub_key_to_addr(compressed_public_key))
    except:
        total = AddressBalance().action('btc', pub_key_to_addr(compressed_public_key))
    #stotal = blockcypher.from_satoshis(total, 'btc') 

    if 0 < total:
        print(pub_key_to_addr(compressed_public_key) + " : " + total)
        with open('wallet_with_money.txt', "a") as m:
            m.write('Converting from: ' + str(int(private_key, 16)) +'\nPrivate key: ' + compressed_key +'\nPublic key: ' + compressed_public_key + '\nBitcoin address: ' + pub_key_to_addr(compressed_public_key)+'\nBitcoin Balance: '+total+'\n#####################################################################\n\n\n\n')
    else:
        pass
    ###############################################


def wif_to_key(wif):
    slicer = 4
    if wif[0] in ['K', 'L']:
        slicer = 5
        
    return hexlify(b58decode(wif)[1:-slicer]).decode('utf-8')


def main():
    parser = argparse.ArgumentParser(description='Generates private key, public key and wallet address from number')

    parser.add_argument('number', type=int, nargs='?', default=1,
                        help='A required integer number argument')
    args = parser.parse_args()
    int_to_address(args.number)



# int_to_address(12345678900987654321)
# Donations: bc1qykc9chxvl75g3njmz7crrjj0uw59m5sxzzdsz7
main()