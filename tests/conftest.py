from web3.providers.eth_tester import EthereumTesterProvider
from pytest_cobra import CobraTester
from eth_tester import EthereumTester
from web3 import Web3
import pytest


# Set Provider
ethereum_tester = EthereumTester()
web3 = Web3(EthereumTesterProvider(ethereum_tester))


# Return zero gas price
def zero_gas_price_strategy(web3, transaction_params=None):
    return 0


# Set Gas Price to 0
web3.eth.setGasPriceStrategy(zero_gas_price_strategy)


@pytest.fixture
def cobra():
    return CobraTester(web3, ethereum_tester)
