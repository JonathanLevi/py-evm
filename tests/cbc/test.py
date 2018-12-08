from eth_keys import keys
from eth_utils import encode_hex, decode_hex
from eth_typing import Address
from eth import constants
from eth.chains.base import MiningChain
from eth.vm.forks.stretch import StretchVM
from eth.db.atomic import AtomicDB
from eth.consensus.pow import mine_pow_nonce
from web3.auto import w3
import config
from config import (
    SHARDS_CONFIG,
    MAGIC_PRI_KEY,
    MAGIC_ADDRESS,
    SHARD_IDS,
    CALLEE_ADDRESS
)
import random
from eth.vm.forks.stretch.xmessage import StretchXMessage, StretchXMessageReceived

klass = MiningChain.configure(
                __name__='TestChain',
                vm_configuration=(
                    (constants.GENESIS_BLOCK_NUMBER, StretchVM),
                                )
                            )

chains = {}
vms = {}
for i in SHARD_IDS:
    chains[i] = klass.from_genesis(AtomicDB(), SHARDS_CONFIG[i]['GENESIS_PARAMS'], SHARDS_CONFIG[i]['GENESIS_STATE'])

# print(chains[0].get_vm().state.account_db.get_balance(SHARDS_CONFIG[0]['ADDRESSES'][0]))
# assert False

# ------------------------------------------------
print("=========================================")
print("                SHARD 0                  ")
print("=========================================")
nonce = chains[0].get_vm().state.account_db.get_nonce(SHARDS_CONFIG[0]['ADDRESSES'][0])
tx = chains[0].get_vm().create_unsigned_transaction(
    nonce=nonce,
    gas_price=0,
    gas=100000,
    to=SHARDS_CONFIG[1]['ADDRESSES'][0],
    value=123,
    data="Test TX data".encode('utf-8'),
)
signed_tx = tx.as_signed_transaction(keys.PrivateKey(decode_hex(SHARDS_CONFIG[0]['PRI_KEYS'][0])))

print("[*] Making a new StretchXMessage that corresponds to the transaction:")
print("\t", 'to', ":", encode_hex(signed_tx['to']))
for x in ['data', 'gas_price', 'gas', 'nonce', 'value']:
    print("\t", x, ":", signed_tx[x])
print("\t", 'sender', ":", encode_hex(signed_tx.sender))

xmessage = StretchXMessage.from_transaction(signed_tx, 1, constants.ZERO_HASH32)
print("[*] Applying XMessage to chain")
chains[0].apply_xmessage_sent(xmessage)
blockA0 = chains[0].get_vm().finalize_block(chains[0].get_block())
nonce, mix_hash = mine_pow_nonce(
    blockA0.number,
    blockA0.header.mining_hash,
    blockA0.header.difficulty
)
print("[*] Mined on Shard 0:", chains[0].mine_block(mix_hash=mix_hash, nonce=nonce))
print("\tSent Message Log", blockA0.xmessage_sent)

# ------------------------------------------------
print("=========================================")
print("                SHARD 1                  ")
print("=========================================")
nonce = chains[1].get_vm().state.account_db.get_nonce(MAGIC_ADDRESS)
tx_dict = blockA0.xmessage_sent[0].get_transaction_dict()
tx = chains[1].get_vm().create_unsigned_transaction(
    nonce=nonce,
    gas_price=tx_dict['gas_price'],
    gas=tx_dict['gas'],
    to=tx_dict['to'],
    value=tx_dict['value'],
    data=tx_dict['data']
)
signed_tx = tx.as_signed_transaction(keys.PrivateKey(decode_hex(MAGIC_PRI_KEY)))
print("[*] Making a new StretchXMessageReceived that corresponds to the transaction:")
print("\t", 'to', ":", encode_hex(signed_tx['to']))
for x in ['data', 'gas_price', 'gas', 'nonce', 'value']:
    print("\t", x, ":", signed_tx[x])
# print("\t", 'sender', ":", signed_tx.sender)
xmessage_recv = StretchXMessageReceived.from_transaction(signed_tx, blockA0.xmessage_sent[0].shard_id, blockA0.xmessage_sent[0].base, 0, constants.ZERO_HASH32)
print("[*] Applying XMessageReceived to chain")
chains[1].apply_xmessage_received(xmessage_recv)
blockB0 = chains[1].get_vm().finalize_block(chains[1].get_block())
nonce, mix_hash = mine_pow_nonce(
    blockB0.number,
    blockB0.header.mining_hash,
    blockB0.header.difficulty
)
print("[*] Mined on Shard 1:", chains[1].mine_block(mix_hash=mix_hash, nonce=nonce))
print("\tReceived Message Log", blockB0.transactions)
print("\tTransaction Log", blockB0.xmessage_received[0])

print("[*] While applying XMessageReceived, this transaction was applied:")
# print(blockB0.transactions[0])
print("\t", 'to', ":", encode_hex(blockB0.transactions[0]['to']))
for x in ['data', 'gas_price', 'gas', 'nonce', 'value']:
    print("\t", x, ":", blockB0.transactions[0][x])
