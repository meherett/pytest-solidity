#!/usr/bin/env python3

from web3 import Web3
from eth_typing import Address


class Account(str):
    
    def __new__(cls, web3: Web3, address: Address):
        obj = super().__new__(cls, address)
        obj.web3 = web3
        obj.address = address
        return obj

    def transfer(self, address: Address, amount: int):
        self.web3.eth.sendTransaction(transaction={
            "to": address, "from": self.address, "value": amount
        })

    @property
    def balance(self):
        return self.web3.eth.getBalance(account=self.address)
