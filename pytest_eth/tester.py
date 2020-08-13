#!/usr/bin/env python3

from web3 import Web3
from eth_tester import EthereumTester
from json import loads

from .account import Account
from .factory import Factory


class Tester:

    def __init__(self, _web3: Web3, _ethereum_tester: EthereumTester, compiled_interfaces=None):
        if compiled_interfaces is None:
            compiled_interfaces = dict()
        self.ethereum_tester = _ethereum_tester
        self.web3 = _web3

        self.compiled_interfaces = compiled_interfaces

    def contract(self, name):
        for compiled_interface in self.compiled_interfaces.keys():
            contract = compiled_interface.split(":")
            if contract[0] == name:
                interface = self.compiled_interfaces.get(compiled_interface)
                return self.new(interface)
            else:
                continue

    def new(self, interface):
        if isinstance(interface["abi"], str):
            interface["abi"] = loads(interface["abi"])
        return Factory(self.web3, interface)

    @property
    def accounts(self):
        return [Account(self.web3, account) 
                for account in self.ethereum_tester.get_accounts()]

    @property
    def eth(self):
        # Return the web3 eth API
        return self.web3.eth

    @property
    def tx_fails(self):
        return FailureHandler(self.ethereum_tester)

    def now(self):
        #  Get this from the Ethereum block timestamp
        return self.web3.eth.getBlock("pending")["timestamp"]

    def mine_blocks(self, number=1):
        self.ethereum_tester.mine_blocks(number)
