from abc import (
    ABC,
    abstractmethod
)

import rlp
from rlp.sedes import (
    big_endian_int,
    binary,
)

from eth_typing import (
    Address
)

from eth_hash.auto import keccak
from eth_keys.datatypes import (
    PrivateKey
)
from eth_utils import (
    ValidationError,
)

from eth.rlp.sedes import (
    address,
    hash32
)

from eth.vm.computation import (
    BaseComputation
)


class BaseXMessageMethods:
    def validate(self) -> None:
        pass


class BaseXMessageFields(rlp.Serializable):

    fields = [
        ('gas_price', big_endian_int),
        ('gas', big_endian_int),
        ('to', address),
        ('value', big_endian_int),
        ('data', binary),
        ('sender', address),
        ('shard_id', big_endian_int),
        ('base', hash32)
    ]

    @property
    def hash(self) -> bytes:
        return keccak(rlp.encode(self))


class BaseXMessage(BaseXMessageFields, BaseXMessageMethods):
    @classmethod
    def from_base_xmessage(cls, xmessage: 'BaseXMessage') -> 'BaseXMessage':
        return rlp.decode(rlp.encode(xmessage), sedes=cls)

    @property
    def sender(self) -> Address:
        """
        Convenience property for the return value of `get_sender`
        """
        return self.get_sender()

    # +-------------------------------------------------------------+
    # | API that must be implemented by all Transaction subclasses. |
    # +-------------------------------------------------------------+

    #
    # Validation
    #
    def validate(self) -> None:
        """
        Checks xmessage validity, raising a ValidationError if the xmessage
        is invalid.
        """
        raise NotImplementedError("Must be implemented by subclasses")


    @abstractmethod
    def get_sender(self) -> Address:
        """
        Get the 20-byte address which sent this xmessage.
        """
        return self.sender

    @classmethod
    def from_transaction(cls, tx, shard_id, base):
        xmessage_dict = tx.copy()
        xmessage_dict['sender'] = tx.sender
        xmessage_dict['shard_id'] = tx.shard_id
        xmessage_dict['base'] = tx.base

    def get_transaction_dict(self):
        return {
            'gas_price': self.gas_price,
            'gas': self.gas,
            'to': self.to,
            'value': self.value,
            'data': self.data
        }
