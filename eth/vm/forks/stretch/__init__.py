from eth.vm.forks.byzantium import ByzantiumVM
from .blocks import StretchBlock
from eth.rlp.headers import BlockHeader
from eth.vm.forks.byzantium.state import ByzantiumState
from .xmessage import (
    StretchXMessage,
    StretchXMessageReceived
)
from typing import (
    Tuple,
)

from eth.db.trie import make_trie_root_and_nodes


class StretchVM(ByzantiumVM):
    # fork name
    fork = 'stretch'

    # classes
    block_class = StretchBlock
    _state_class = ByzantiumState

    def set_block_xmessage_received(self,
                               base_block: StretchBlock,
                               new_header: BlockHeader,
                               xmessage_received: Tuple[StretchXMessageReceived, ...]) -> StretchBlock:

        tx_root_hash, tx_kv_nodes = make_trie_root_and_nodes(xmessage_received)
        self.chaindb.persist_trie_data_dict(tx_kv_nodes)

        return base_block.copy(
            xmessage_received=xmessage_received,
            header=new_header.copy(
                xmessage_received_root=tx_root_hash,
            ),
        )

    def set_block_xmessage_sent(self,
                               base_block: StretchBlock,
                               new_header: BlockHeader,
                               xmessage_sent: Tuple[StretchXMessage, ...]) -> StretchBlock:

        tx_root_hash, tx_kv_nodes = make_trie_root_and_nodes(xmessage_sent)
        self.chaindb.persist_trie_data_dict(tx_kv_nodes)

        return base_block.copy(
            xmessage_sent=xmessage_sent,
            header=new_header.copy(
                xmessage_sent_root=tx_root_hash,
            ),
        )

    def set_block_xmessage(self,
                    base_block: StretchBlock,
                    new_header: BlockHeader,
                    xmessage_sent: Tuple[StretchXMessage, ...],
                    xmessage_received: Tuple[StretchXMessageReceived, ...]) -> StretchBlock:
        sent = self.set_block_xmessage_sent(base_block, new_header, xmessage_sent)
        return self.set_block_xmessage_received(sent, new_header, xmessage_received)
