from eth.vm.forks.byzantium import ByzantiumVM
from .blocks import StretchBlock
from eth.rlp.headers import BlockHeader
from eth.vm.forks.byzantium.state import ByzantiumState
from .xmessage import (
    StretchXMessage,
    StretchXMessageReceived
)
from eth.rlp.transactions import BaseTransaction
from eth.rlp.receipts import Receipt
from eth.vm.computation import BaseComputation
from typing import (
    Tuple,
)

from eth.db.trie import make_trie_root_and_nodes


import config

class StretchVM(ByzantiumVM):
    # fork name
    fork = 'stretch'

    # classes
    block_class = StretchBlock
    _state_class = ByzantiumState

    def set_block_xmessage_received(self,
                               base_block: StretchBlock,
                               xmessage_received: Tuple[StretchXMessageReceived, ...]) -> StretchBlock:

        tx_root_hash, tx_kv_nodes = make_trie_root_and_nodes(xmessage_received)
        self.chaindb.persist_trie_data_dict(tx_kv_nodes)

        return base_block.copy(
            xmessage_received=xmessage_received,
            header=base_block.header.copy(
                xmessage_received_root=tx_root_hash,
            ),
        )

    def set_block_xmessage_sent(self,
                               base_block: StretchBlock,
                               xmessage_sent: Tuple[StretchXMessage, ...]) -> StretchBlock:

        tx_root_hash, tx_kv_nodes = make_trie_root_and_nodes(xmessage_sent)
        self.chaindb.persist_trie_data_dict(tx_kv_nodes)

        return base_block.copy(
            xmessage_sent=xmessage_sent,
            header=base_block.header.copy(
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

    def process_transaction(self, shard_id: int, transaction: BaseTransaction) -> BaseTransaction:
        """
        Process transaction to handle transactions with out-of-shard component

        :param transaction: transaction to process
        """
        print("Processing tx in shard:", shard_id)
        if transaction.sender in config.SHARDS_CONFIG[shard_id]['ADDRESSES'] or transaction.sender == config.MAGIC_ADDRESS:
            if transaction.to in config.SHARDS_CONFIG[shard_id]['ADDRESSES']:
                # In-shard address to in-shard address
                print("In-shard to in-shard")
            else:
                # In-shard address to out-of-shard address
                print("In-shard to out-of-shard")
                # print("Additional Xshard message data must be in transaction data")
                # print(transaction.data)
                # print(transaction.data.startswith(b'out-of-shard-tx'))
        else:
            # TODO: Handle these cases
            if transaction.to in config.SHARDS_CONFIG[shard_id]['ADDRESSES']:
                # Out-of-shard address to in-shard address
                print("Out-of-shard to in-shard")
                assert False, "Out-of-shard to in-shard. Don't know what to do here!"
            else:
                # Out-of-shard address to out-of-shard address
                print("Out-of-shard to out-of-shard")
                assert False, "Out-of-shard to out-of-shard. Don't know what to do here!"
        return transaction

    def apply_transaction(self,
                          header: BlockHeader,
                          transaction: BaseTransaction
                          ) -> Tuple[BlockHeader, Receipt, BaseComputation]:
        """
        Process to re-encode the shard's outgoing transactions

        :param header: header of the block before application
        :param transaction: to apply
        """
        processed_tx = self.process_transaction(header.shard_id, transaction)
        return super().apply_transaction(header, processed_tx)
