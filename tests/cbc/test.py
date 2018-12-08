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
    SHARD_IDS
)
import random
from eth.vm.forks.stretch.xmessage import StretchXMessage

klass = MiningChain.configure(
                __name__='TestChain',
                vm_configuration=(
                    (constants.GENESIS_BLOCK_NUMBER, StretchVM),
                                )
                            )

chain = klass.from_genesis(AtomicDB(), SHARDS_CONFIG[1]['GENESIS_PARAMS'])

vm = chain.get_vm()
nonce = vm.state.account_db.get_nonce(MAGIC_ADDRESS)
tx = vm.create_unsigned_transaction(
            nonce=nonce,
            gas_price=0,
            gas=100000,
            to=SHARDS_CONFIG[0]['ADDRESSES'][0],
            value=0,
            data="Test TX data".encode('utf-8'),
        )

chains = {}
vms = {}
for i in SHARD_IDS:
    chains[i] = klass.from_genesis(AtomicDB(), SHARDS_CONFIG[i]['GENESIS_PARAMS'])


# for i in SHARD_IDS:
#     print("============")
#     print("Shard ", i)
#     print("============")
#     for j in range(10):
#         sender_index = random.randint(0,5)
#         nonce = chains[i].get_vm().state.account_db.get_nonce(SHARDS_CONFIG[i]['ADDRESSES'][sender_index])
#         tx = chains[i].get_vm().create_unsigned_transaction(
#             nonce=nonce,
#             gas_price=0,
#             gas=100000,
#             to=SHARDS_CONFIG[1-i]['ADDRESSES'][j],
#             value=0,
#             data="Test TX data".encode('utf-8'),
#         )
#         signed_tx = tx.as_signed_transaction(sender_pri_key)
#         chains[i].apply_transaction(signed_tx)
#         block = chains[i].get_vm().finalize_block(chains[i].get_block())
#         nonce, mix_hash = mine_pow_nonce(
#             block.number,
#             block.header.mining_hash,
#             block.header.difficulty
#         )
#         print(chains[i].mine_block(mix_hash=mix_hash, nonce=nonce))
#         current_block = chains[i].get_block_by_header(chains[i].get_canonical_head())
#         print("Current Block:", current_block)

sender_pri_key = keys.PrivateKey(decode_hex(MAGIC_PRI_KEY))
nonce = chains[0].get_vm().state.account_db.get_nonce(SHARDS_CONFIG[0]['ADDRESSES'][0])
tx = chains[0].get_vm().create_unsigned_transaction(
    nonce=nonce,
    gas_price=0,
    gas=100000,
    to=SHARDS_CONFIG[1]['ADDRESSES'][0],
    value=0,
    data="Test TX data".encode('utf-8'),
)
signed_tx = tx.as_signed_transaction(keys.PrivateKey(decode_hex(SHARDS_CONFIG[0]['PRI_KEYS'][0])))
# chains[0].apply_transaction(signed_tx)
# block = chains[0].get_vm().finalize_block(chains[0].get_block())
# nonce, mix_hash = mine_pow_nonce(
#     block.number,
#     block.header.mining_hash,
#     block.header.difficulty
# )
# print(chains[0].mine_block(mix_hash=mix_hash, nonce=nonce))
# current_block = chains[0].get_block_by_header(chains[0].get_canonical_head())
# print("Current Block:", current_block)
# print(block.transactions)

xmessage = StretchXMessage.from_transaction(signed_tx, 1, constants.ZERO_HASH32)
chains[0].apply_xmessage_sent(xmessage)
block = chains[0].get_vm().finalize_block(chains[0].get_block())
nonce, mix_hash = mine_pow_nonce(
    block.number,
    block.header.mining_hash,
    block.header.difficulty
)
print(chains[0].mine_block(mix_hash=mix_hash, nonce=nonce))
print(block.xmessage_sent)
print(block.xmessage_sent[0].get_transaction_dict())
