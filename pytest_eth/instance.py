#!/usr/bin/env python3

from web3 import Web3
from web3._utils.events import get_event_data
from web3.contract import ImplicitContract
from eth_utils import event_abi_to_log_topic
from functools import partial as partial_fn
from eth_typing import Address

from .log import Log


class Instance:
    """Deployed instance of a contract"""

    def __init__(self, _web3: Web3, address: Address, interface):
        self.web3 = _web3
        self.address = address
        self.interface = ImplicitContract(
            classic_contract=self.web3.eth.contract(self.address, **interface)
        )
        # Register new filter to watch for logs from this instance"s address
        self.__filter = self.web3.eth.filter({
            # Include events from the deployment stage
            "fromBlock": self.web3.eth.blockNumber - 1,
            "address": self.address
        })
        self.event_signatures = self.get_event_signatures(interface["abi"])
        self.event_processors = self.get_event_processors(interface["abi"])

    def __getattr__(self, name):
        """Delegates to either specialized methods or instance ABI"""
        if name in dir(self):
            # Specialized testing methods
            return getattr(self, name)
        elif name in self.event_signatures.keys():
            return lambda args: Log(name, args)
        else:
            # Method call of contract instance
            return getattr(self.interface, name)

    @property
    def balance(self):
        """Ether balance of this contract (in wei)"""
        return self.web3.eth.getBalance(self.address)

    @property
    def code_size(self):
        """Code size of this contract (in bytes)"""
        return len(self.web3.eth.getCode(self.address)[2:]) / 2

    @property
    def has_code(self):
        """Check if this contract currently has code (usually indicating suicide)"""
        return self.code_size != 0

    def process_logs(self, logs):
        processed_logs = []
        for log in logs:
            log_signature = log["topics"][0]
            if log_signature in self.event_processors.keys():
                p_log = self.event_processors[log_signature](log)
                processed_logs.append(Log(p_log["event"], p_log["args"]))
        return processed_logs

    @property
    def logs(self):
        """Returns all the event logs ever added for this contract"""
        return self.process_logs(self.__filter.get_all_entries())

    @staticmethod
    def get_event_signatures(abi_list):
        signatures = dict()
        for abi in abi_list:
            if abi["type"] == "event":
                signatures[abi["name"]] = event_abi_to_log_topic(abi)
        return signatures

    @staticmethod
    def get_event_processors(abi_list):
        processors = dict()
        for abi in abi_list:
            if abi["type"] == "event":
                processors[event_abi_to_log_topic(abi)] = partial_fn(get_event_data, abi)
        return processors
