from eth_keys import keys
from eth_utils import decode_hex
from eth_typing import Address
from eth import constants
from eth.chains.base import MiningChain
from eth.vm.forks.stretch import StretchVM
from eth.db.atomic import AtomicDB
from eth.consensus.pow import mine_pow_nonce
from web3.auto import w3

from config import (
    SHARDS_CONFIG,
    MAGIC_PRI_KEY,
    MAGIC_ADDRESS,
    SHARD_IDS
)

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

sender_pri_key = keys.PrivateKey(decode_hex(MAGIC_PRI_KEY))


chains = {}
vms = {}
for i in SHARD_IDS:
    chains[i] = klass.from_genesis(AtomicDB(), SHARDS_CONFIG[i]['GENESIS_PARAMS'])
    vms[i] = chains[i].get_vm()


for i in SHARD_IDS:
    print("============")
    print("Shard ", i)
    print("=============")
    for j in range(1,len(SHARDS_CONFIG[i]['ADDRESSES'])):
        nonce = vms[i].state.account_db.get_nonce(MAGIC_ADDRESS)
        tx = vms[i].create_unsigned_transaction(
            nonce=nonce,
            gas_price=0,
            gas=100000,
            to=SHARDS_CONFIG[0]['ADDRESSES'][j],
            value=0,
            data="Test TX data".encode('utf-8'),
        )

        sender_address = SHARDS_CONFIG[i]['ADDRESSES'][0]
        block = vms[i].finalize_block(chains[i].get_block())
        nonce, mix_hash = mine_pow_nonce(
            block.number,
            block.header.mining_hash,
            block.header.difficulty
        )
        print(chains[i].mine_block(mix_hash=mix_hash, nonce=nonce))
        print("Sender:",sender_address)
        print("Receiver:",SHARDS_CONFIG[0]['ADDRESSES'][j])
        current_block = chains[i].get_block_by_header(chains[i].get_canonical_head())
        print("Current Block:", current_block)

