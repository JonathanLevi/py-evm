from rlp.sedes import (
    CountableList,
)

from eth.vm.forks.byzantium.blocks import (
    ByzantiumBlock,
)


from eth.vm.forks.byzantium.transactions import (
    ByzantiumTransaction,
)

from eth.vm.forks.stretch.headers import (
    StretchBlockHeader
)

from eth.vm.forks.stretch.xmessage import (
    StretchXMessage,
    StretchXMessageReceived
)

class StretchBlock(ByzantiumBlock):
    transaction_class = ByzantiumTransaction
    xmessage_sent_class = StretchXMessage
    xmessage_received_class = StretchXMessageReceived
    fields = [
        ('header', StretchBlockHeader),
        ('transactions', CountableList(transaction_class)),
        ('xmessage_sent', CountableList(xmessage_sent_class)),
        ('xmessage_received', CountableList(xmessage_received_class)),
        ('uncles', CountableList(StretchBlockHeader))
    ]

    def __init__(self,
                 header: BlockHeader,
                 transactions: Iterable[BaseTransaction]=None,
                 xmessage_sent: Iterable[BaseXMessage]=None,
                 xmessage_received: Iterable[BaseXMessageReceived]=None,
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

        super().__init__(
            header=header,
            transactions=transactions,
            uncles=uncles,
        )

    @classmethod
    def get_xmessage_sent_class(cls) -> Type[BaseXMessage]:
        return cls.xmessage_sent_class

    @classmethod
    def get_xmessage_received_class(cls) -> Type[BaseXMessageReceived]:
        return cls.xmessage_received_class

    #
    # Header API
    #
    @classmethod
    def from_header(cls, header: StretchBlockHeader, chaindb: BaseChainDB) -> StretchBlock:
        """
        Returns the block denoted by the given block header.
        """
        if header.uncles_hash == EMPTY_UNCLE_HASH:
            uncles = []  # type: List[BlockHeader]
        else:
            uncles = chaindb.get_block_uncles(header.uncles_hash)

        transactions = chaindb.get_block_transactions(header, cls.get_transaction_class())
        xmessage_sent = chaindb.get_xmessage_sent(header, cls.get_xmessage_sent_class())
        xmessage_received = chaindb.get_xmessage_received(header, cls.get_xmessage_received_class())

        return cls(
            header=header,
            transactions=transactions,
            xmessage_sent=xmessage_sent,
            xmessage_received=xmessage_received,
            uncles=uncles,
        )
