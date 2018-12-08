from typing import (
    Iterable,
    Type
)

import rlp
from rlp.sedes import (
    CountableList,
)

from eth.constants import EMPTY_UNCLE_HASH

from eth.rlp.headers import BlockHeader
from eth.rlp.blocks import BaseBlock
from eth.rlp.transactions import BaseTransaction

from eth.vm.forks.byzantium.blocks import (
    ByzantiumBlock,
)

from eth.db.chain import BaseChainDB

from eth.vm.forks.byzantium.transactions import (
    ByzantiumTransaction,
)

from eth.vm.forks.stretch.xmessage import (
    StretchXMessage,
    StretchXMessageReceived
)

from eth_bloom import (
    BloomFilter,
)

class StretchBlock(ByzantiumBlock):
    transaction_class = ByzantiumTransaction
    xmessage_sent_class = StretchXMessage
    xmessage_received_class = StretchXMessageReceived
    fields = [
        ('header', BlockHeader),
        ('transactions', CountableList(transaction_class)),
        ('xmessage_sent', CountableList(xmessage_sent_class)),
        ('xmessage_received', CountableList(xmessage_received_class)),
        ('uncles', CountableList(BlockHeader))
    ]

    def __init__(self,
                 header: BlockHeader,
                 transactions: Iterable[BaseTransaction]=None,
                 xmessage_sent: Iterable[StretchXMessage]=None,
                 xmessage_received: Iterable[StretchXMessageReceived]=None,
                 uncles: Iterable[BlockHeader]=None) -> None:
        if transactions is None:
            transactions = []
        if xmessage_sent is None:
            xmessage_sent = []
        if xmessage_received is None:
            xmessage_received = []
        if uncles is None:
            uncles = []

        self.bloom_filter = BloomFilter(header.bloom)

        rlp.Serializable.__init__(
            self,
            header=header,
            transactions=transactions,
            xmessage_sent=xmessage_sent,
            xmessage_received=xmessage_received,
            uncles=uncles,
        )

    @classmethod
    def get_xmessage_sent_class(cls) -> Type[StretchXMessage]:
        return cls.xmessage_sent_class

    @classmethod
    def get_xmessage_received_class(cls) -> Type[StretchXMessageReceived]:
        return cls.xmessage_received_class

    #
    # Header API
    #
    @classmethod
    def from_header(cls, header: BlockHeader, chaindb: BaseChainDB) -> BaseBlock:
        """
        Returns the block denoted by the given block header.
        """
        if header.uncles_hash == EMPTY_UNCLE_HASH:
            uncles = []  # type: List[BlockHeader]
        else:
            uncles = chaindb.get_block_uncles(header.uncles_hash)

        transactions = chaindb.get_block_transactions(header, cls.get_transaction_class())
        xmessage_sent = chaindb.get_block_xmessage_sent(header, cls.get_xmessage_sent_class())
        xmessage_received = chaindb.get_block_xmessage_received(header, cls.get_xmessage_received_class())

        return cls(
            header=header,
            transactions=transactions,
            xmessage_sent=xmessage_sent,
            xmessage_received=xmessage_received,
            uncles=uncles,
        )
