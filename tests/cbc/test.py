from eth_keys import keys
from eth_utils import encode_hex, decode_hex
from eth_typing import Address
from eth import constants
from eth.chains.base import MiningChain
from eth.vm.forks.stretch import StretchVM
from eth.vm.forks.byzantium.transactions import ByzantiumTransaction
from eth.db.atomic import AtomicDB
from eth.consensus.pow import mine_pow_nonce
from web3 import Web3
import config
from config import (
    SHARDS_CONFIG,
    MAGIC_PRI_KEY,
    MAGIC_ADDRESS,
    SHARD_IDS,
    CALLEE_ADDRESS,
    CALLEE_ABI
)
import random
from eth.vm.forks.stretch.xmessage import StretchXMessage, StretchXMessageReceived

web3 = Web3()

abi = CALLEE_ABI
contract = web3.eth.contract(address=Web3.toChecksumAddress(encode_hex(CALLEE_ADDRESS)), abi=abi)

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

# ------------------------------------------------
print("=========================================")
print("                SHARD 0                  ")
print("=========================================")
def format_transaction(tx):
# Format web3 tx into dict for ByzantiumTransaction
    return {
        "gas": tx["gas"],
        "gas_price": int(tx["gasPrice"], 16),
        "data": decode_hex(tx['data']),
        "nonce": int(tx["nonce"], 16),
        "to": decode_hex(tx["to"]),
        "value": tx["value"],
    }
nonce = chains[0].get_vm().state.account_db.get_nonce(SHARDS_CONFIG[0]['ADDRESSES'][1])
contract_call = contract.functions.setYto3().buildTransaction({ "gas": 3000000, "gasPrice": "0x2", "nonce": hex(nonce), "value": 1})
unsigned_tx = ByzantiumTransaction.create_unsigned_transaction(**format_transaction(contract_call))
# print(unsigned_tx.as_dict())
signed_tx = unsigned_tx.as_signed_transaction(keys.PrivateKey(decode_hex(SHARDS_CONFIG[0]['PRI_KEYS'][1])))
print("[*] Making a new StretchXMessage that corresponds to the transaction:")
print("\t", 'to', ":", encode_hex(signed_tx['to']))
for x in ['data', 'gas_price', 'gas', 'nonce', 'value']:
    print("\t", x, ":", signed_tx[x])
print("\t", 'sender', ":", encode_hex(signed_tx.sender))


xmessage = StretchXMessage.from_transaction(signed_tx, 1, constants.ZERO_HASH32)
print("[*] Applying XMessage to chain")
chains[0].apply_xmessage_sent(xmessage)
blockA1 = chains[0].get_vm().finalize_block(chains[0].get_block())
nonce, mix_hash = mine_pow_nonce(
    blockA1.number,
    blockA1.header.mining_hash,
    blockA1.header.difficulty
)
print("[*] Mined on Shard 0:", chains[0].mine_block(mix_hash=mix_hash, nonce=nonce))
print("\tSent Message Log", blockA1.xmessage_sent)

print("=========================================")
print("                SHARD 1                  ")
print("=========================================")
print("Storage at CALLEE_ADDRESS:", chains[1].get_vm().state.account_db.get_storage(CALLEE_ADDRESS, 0))
nonce = chains[1].get_vm().state.account_db.get_nonce(MAGIC_ADDRESS)
tx_dict = blockA1.xmessage_sent[0].get_transaction_dict()
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
xmessage_recv = StretchXMessageReceived.from_transaction(signed_tx, blockA1.xmessage_sent[0].shard_id, blockA1.xmessage_sent[0].base, 0, constants.ZERO_HASH32)
print("[*] Applying XMessageReceived to chain")
chains[1].apply_xmessage_received(xmessage_recv)
blockB1 = chains[1].get_vm().finalize_block(chains[1].get_block())
nonce, mix_hash = mine_pow_nonce(
    blockB1.number,
    blockB1.header.mining_hash,
    blockB1.header.difficulty
)
print("[*] Mined on Shard 1:", chains[1].mine_block(mix_hash=mix_hash, nonce=nonce))
print("\tReceived Message Log", blockB1.transactions)
print("\tTransaction Log", blockB1.xmessage_received[0])

print("[*] While applying XMessageReceived, this transaction was applied:")
# print(blockB0.transactions[0])
print("\t", 'to', ":", encode_hex(blockB1.transactions[0]['to']))
for x in ['data', 'gas_price', 'gas', 'nonce', 'value']:
    print("\t", x, ":", blockB1.transactions[0][x])
