from rlp.sedes import (
    big_endian_int,
    binary,
)

from eth.rlp.sedes import (
    address,
    hash32
)
from eth.rlp.xmessage import (
    BaseXMessage,
)


class StretchXMessage(BaseXMessage):
    def validate(self):
        assert False, "Yet to implement"

    @classmethod
    def from_transaction(cls, tx, shard_id, base):
        xmessage_dict = {
            'gas_price': tx.gas_price,
            'gas': tx.gas,
            'to': tx.to,
            'value': tx.value,
            'data': tx.data,
            'sender': tx.sender,
            'shard_id': shard_id,
            'base': base,
        }
        return cls(**xmessage_dict)


class StretchXMessageReceived(StretchXMessage):
    fields = [
        ('gas_price', big_endian_int),
        ('gas', big_endian_int),
        ('to', address),
        ('value', big_endian_int),
        ('data', binary),
        ('sender', address),
        ('shard_id', big_endian_int),
        ('base', hash32),
        ('source_shard_id', big_endian_int),
        ('source', hash32),
    ]


    @classmethod
    def from_transaction(cls, tx, shard_id, base, source_shard_id, source):
        xmessage_dict = {
            'gas_price': tx.gas_price,
            'gas': tx.gas,
            'to': tx.to,
            'value': tx.value,
            'data': tx.data,
            'sender': tx.sender,
            'shard_id': shard_id,
            'base': base,
            'source_shard_id': source_shard_id,
            'source': source
        }
        return cls(**xmessage_dict)
