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
)

klass = MiningChain.configure(
                __name__='TestChain',
                vm_configuration=(
                    (constants.GENESIS_BLOCK_NUMBER, StretchVM),
                                )
                            )

chain = klass.from_genesis(AtomicDB(), SHARDS_CONFIG[0]['GENESIS_PARAMS'])

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

signed_tx = tx.as_signed_transaction(sender_pri_key)
chain.apply_transaction(signed_tx)

# --------------

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

signed_tx = tx.as_signed_transaction(sender_pri_key)
chain.apply_transaction(signed_tx)

# --------------

block = chain.get_vm().finalize_block(chain.get_block())
nonce, mix_hash = mine_pow_nonce(
                        block.number,
                        block.header.mining_hash,
                        block.header.difficulty
                    )
print(chain.mine_block(mix_hash=mix_hash, nonce=nonce))

current_block = chain.get_block_by_header(chain.get_canonical_head())
print("Current Block:", current_block)
