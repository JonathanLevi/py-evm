from rlp.sedes import (
    big_endian_int,
    Binary,
    binary,
)

from eth.rlp.sedes import (
    address,
    hash32,
    uint256,
    trie_root,
)

from eth_typing import (
    Address,
    Hash32,
)

from eth.constants import (
    ZERO_ADDRESS,
    ZERO_HASH32,
    EMPTY_UNCLE_HASH,
    GENESIS_NONCE,
    GENESIS_PARENT_HASH,
    BLANK_ROOT_HASH,
)

from eth.rlp.headers import (
    MiningHeader,
    BlockHeader
)

class StretchMiningHeader(MiningHeader):
    fields = [
        ('shard_id', big_endian_int),
        ('parent_hash', hash32),
        ('uncles_hash', hash32),
        ('coinbase', address),
        ('state_root', trie_root),
        ('transaction_root', trie_root),
        ('xmessage_sent_root', trie_root),
        ('xmessage_received_root', trie_root),
        ('receipt_root', trie_root),
        ('bloom', uint256),
        ('difficulty', big_endian_int),
        ('block_number', big_endian_int),
        ('gas_limit', big_endian_int),
        ('gas_used', big_endian_int),
        ('timestamp', big_endian_int),
        ('extra_data', binary),
    ]

class StretchBlockHeader(BlockHeader):
    fields = [
        ('shard_id', big_endian_int),
        ('parent_hash', hash32),
        ('uncles_hash', hash32),
        ('coinbase', address),
        ('state_root', trie_root),
        ('transaction_root', trie_root),
        ('xmessage_sent_root', trie_root),
        ('xmessage_received_root', trie_root),
        ('receipt_root', trie_root),
        ('bloom', uint256),
        ('difficulty', big_endian_int),
        ('block_number', big_endian_int),
        ('gas_limit', big_endian_int),
        ('gas_used', big_endian_int),
        ('timestamp', big_endian_int),
        ('extra_data', binary),
        ('mix_hash', binary),
        ('nonce', Binary(8, allow_empty=True))
    ]

    def __init__(self,              # type: ignore  # noqa: F811
                 shard_id: int,
                 difficulty: int,
                 block_number: int,
                 gas_limit: int,
                 timestamp: int=None,
                 coinbase: Address=ZERO_ADDRESS,
                 parent_hash: Hash32=ZERO_HASH32,
                 uncles_hash: Hash32=EMPTY_UNCLE_HASH,
                 state_root: Hash32=BLANK_ROOT_HASH,
                 transaction_root: Hash32=BLANK_ROOT_HASH,
                 xmessage_sent_root: Hash32=BLANK_ROOT_HASH,
                 xmessage_received_root: Hash32=BLANK_ROOT_HASH,
                 receipt_root: Hash32=BLANK_ROOT_HASH,
                 bloom: int=0,
                 gas_used: int=0,
                 extra_data: bytes=b'',
                 mix_hash: Hash32=ZERO_HASH32,
                 nonce: bytes=GENESIS_NONCE) -> None:
        if timestamp is None:
            timestamp = int(time.time())
        self.shard_id = shard_id
        self.xmessage_sent_root = xmessage_sent_root
        self.xmessage_received_root = xmessage_received_root
        super().__init__(
            parent_hash=parent_hash,
            uncles_hash=uncles_hash,
            coinbase=coinbase,
            state_root=state_root,
            transaction_root=transaction_root,
            receipt_root=receipt_root,
            bloom=bloom,
            difficulty=difficulty,
            block_number=block_number,
            gas_limit=gas_limit,
            gas_used=gas_used,
            timestamp=timestamp,
            extra_data=extra_data,
            mix_hash=mix_hash,
            nonce=nonce,
        )
