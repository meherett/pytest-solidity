#!/usr/bin/env python3

from web3 import Web3
from web3.types import Wei
from web3.providers.eth_tester import EthereumTesterProvider
from eth_tester import EthereumTester, MockBackend

import pytest

from .interfaces import Interfaces
from .tester import Tester


# Init Ethereum tester
ethereum_tester = EthereumTester(
    backend=MockBackend()
)

# Set Provider
web3 = Web3(
    provider=EthereumTesterProvider(
        ethereum_tester=ethereum_tester
    )
)


# Return zero gas price
def zero_gas_price_strategy(_: Web3, transaction_params=None) -> Wei:
    return Wei(0)


# Set gas price to 0
web3.eth.setGasPriceStrategy(
    gas_price_strategy=zero_gas_price_strategy
)


def pytest_addoption(parser):
    group = parser.getgroup("eth", "Ethereum Smart-Contract testing support")
    group.addoption("--eth", action="store", default=None, metavar="path",
                    help="pytest --eth Contract.json")
    group.addoption("--import_remappings", action="store", default=None, metavar="path",
                    help="pytest --eth Contract.sol --import_remappings ['=', '-', '=/home']")
    group.addoption("--allow_paths", action="store", default=None, metavar="path",
                    help="pytest --eth Contract.sol --allow_paths ['/home']")


@pytest.fixture(scope="session")
def eth_file(pytestconfig):
    eth_file = dict()
    if pytestconfig.option.eth:
        interface = Interfaces(web3)
        eth_file = interface.eth_file(
            pytestconfig.option.eth,
            pytestconfig.option.import_remappings,
            pytestconfig.option.allow_paths
        )
    return eth_file


@pytest.fixture
def eth(eth_file):
    return Tester(web3, ethereum_tester, eth_file)
