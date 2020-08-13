#!/usr/bin/env python3

from eth_tester import EthereumTester
from eth_tester.exceptions import TransactionFailed


class FailureHandler:

    def __init__(self, ethereum_tester: EthereumTester):
        self.ethereum_tester = ethereum_tester

    def __enter__(self):
        self.snapshot = self.ethereum_tester.take_snapshot()
        return self.snapshot

    def __exit__(self, *args):
        assert len(args) > 0 and \
               args[0] is TransactionFailed, "Didn't revert transaction."
        self.ethereum_tester.revert_to_snapshot(self.snapshot)
        return True
