from eth_keys import keys
from eth_utils import decode_hex, encode_hex, to_wei
from eth_typing import Address
from eth import constants
from web3.auto import w3

def convert_pri_key_to_address(pri_key):
    return Address(keys.PrivateKey(decode_hex(pri_key)).public_key.to_canonical_address())

MAGIC_PRI_KEY = w3.eth.account.create().privateKey.hex()
MAGIC_ADDRESS = convert_pri_key_to_address(MAGIC_PRI_KEY)
MAGIC_FUNDS = to_wei(100000, 'ether')

SHARDS_CONFIG = {
    0: {
        'GENESIS_PARAMS': {
                    # 'shard_id': 0,
                    'parent_hash': constants.GENESIS_PARENT_HASH,
                    'uncles_hash': constants.EMPTY_UNCLE_HASH,
                    'coinbase': constants.ZERO_ADDRESS,
                    'transaction_root': constants.BLANK_ROOT_HASH,
                    # 'xmessage_sent_root': constants.BLANK_ROOT_HASH,
                    # 'xmessage_received_root': constants.BLANK_ROOT_HASH,
                    'receipt_root': constants.BLANK_ROOT_HASH,
                    'difficulty': 1,
                    'block_number': constants.GENESIS_BLOCK_NUMBER,
                    'gas_limit': 1000000,
                    'timestamp': 1544286352,
                    'extra_data': constants.GENESIS_EXTRA_DATA,
                    'nonce': constants.GENESIS_NONCE
                },
        'GENESIS_STATE': {
            MAGIC_ADDRESS: {
                'balance': MAGIC_FUNDS,
                'nonce': 0,
                'code': b'',
                'storage': {}
            }
        },
        'PRI_KEYS': [w3.eth.account.create().privateKey.hex() for x in range(5)],
    },
    1: {
        'GENESIS_PARAMS': {
                    # 'shard_id': 1,
                    'parent_hash': constants.GENESIS_PARENT_HASH,
                    'uncles_hash': constants.EMPTY_UNCLE_HASH,
                    'coinbase': constants.ZERO_ADDRESS,
                    'transaction_root': constants.BLANK_ROOT_HASH,
                    # 'xmessage_sent_root': constants.BLANK_ROOT_HASH,
                    # 'xmessage_received_root': constants.BLANK_ROOT_HASH,
                    'receipt_root': constants.BLANK_ROOT_HASH,
                    'difficulty': 1,
                    'block_number': constants.GENESIS_BLOCK_NUMBER,
                    'gas_limit': 1000000,
                    'timestamp': 1544286352,
                    'extra_data': constants.GENESIS_EXTRA_DATA,
                    'nonce': constants.GENESIS_NONCE
                },
        'GENESIS_STATE': {
            MAGIC_ADDRESS: {
                'balance': MAGIC_FUNDS,
                'nonce': 0,
                'code': b'',
                'storage': {}
            }
        },
        'PRI_KEYS': [w3.eth.account.create().privateKey.hex() for x in range(5)],
    }
}

SHARD_IDS = SHARDS_CONFIG.keys()

for shard_id in SHARD_IDS:
    SHARDS_CONFIG[shard_id]['ADDRESSES'] = [ convert_pri_key_to_address(x) for x in SHARDS_CONFIG[shard_id]['PRI_KEYS'] ]

for shard_id in SHARD_IDS:
    for address in SHARDS_CONFIG[shard_id]['ADDRESSES']:
        SHARDS_CONFIG[shard_id]['GENESIS_STATE'][address] = {
            'balance': to_wei(10, 'ether'),
            'nonce': 0,
            'code': b'',
            'storage': {}
        }
