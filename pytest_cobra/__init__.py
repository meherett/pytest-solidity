from web3.providers.eth_tester import EthereumTesterProvider
from eth_tester.exceptions import TransactionFailed
from eth_utils import event_abi_to_log_topic
from web3.utils.events import get_event_data
from functools import partial as partial_fn
from web3.contract import ImplicitContract
from solc import link_code, compile_source
from eth_tester import EthereumTester
from collections import Mapping
from os.path import basename
from os.path import join
from json import loads
from web3 import Web3
import pytest
import json
import yaml
import os


class CobraTester:

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
        if isinstance(interface['abi'], str):
            interface['abi'] = loads(interface['abi'])
        return CobraFactory(self.web3, interface)

    @property
    def accounts(self):
        return [CobraAccount(self.web3, a) for a in self.ethereum_tester.get_accounts()]

    @property
    def eth(self):
        # Return the w3 eth API
        return self.web3.eth

    @property
    def tx_fails(self):
        return CobraFailureHandler(self.ethereum_tester)

    def now(self):
        #  Get this from the Ethereum block timestamp
        return self.web3.eth.getBlock('pending')['timestamp']

    def mine_blocks(self, number=1):
        self.ethereum_tester.mine_blocks(number)


class CobraLog(Mapping):
    def __new__(cls, event, args):
        obj = super().__new__(cls)
        obj._event = event
        obj._args = args
        return obj

    def __eq__(self, other):
        if not isinstance(other, CobraLog):
            return False
        if self._event != other._event:
            return False
        return self._args == other._args

    def __iter__(self):
        return iter(self._args)

    def __len__(self):
        return len(self._args)

    def __getitem__(self, key):
        return self._args[key]


class CobraInstance:
    """Deployed instance of a contract"""

    def __init__(self, _web3: Web3, address, interface):
        self.web3 = _web3
        self.__address = address
        self.__instance = ImplicitContract(self.web3.eth.contract(self.__address, **interface))
        # Register new filter to watch for logs from this instance's address
        self.__filter = self.web3.eth.filter({
            # Include events from the deployment stage
            'fromBlock': self.web3.eth.blockNumber - 1,
            'address': self.__address
        })
        self.__event_signatures = self.get_event_signatures(interface['abi'])
        self.__event_processors = self.get_event_processors(interface['abi'])

    def __getattr__(self, name):
        """Delegates to either specialized methods or instance ABI"""
        if name in dir(self):
            # Specialized testing methods
            return getattr(self, name)
        elif name in self._events:
            return self._gen_log(name)
        else:
            # Method call of contract instance
            return getattr(self.__instance, name)

    @property
    def _events(self):
        return self.__event_signatures.keys()

    def _gen_log(self, name):
        return lambda v: CobraLog(name, v)

    @property
    def address(self):
        """This contract's address"""
        return self.__address

    @property
    def balance(self):
        """Ether balance of this contract (in wei)"""
        return self.web3.eth.getBalance(self.__address)

    @property
    def codesize(self):
        """Codesize of this contract (in bytes)"""
        return len(self.web3.eth.getCode(self.__address)[2:]) / 2

    @property
    def hascode(self):
        """Check if this contract currently has code (usually indicating suicide)"""
        return self.codesize != 0

    def process_logs(self, logs):
        processed_logs = []
        for log in logs:
            log_signature = log['topics'][0]
            if log_signature in self.__event_processors.keys():
                p_log = self.__event_processors[log_signature](log)
                processed_logs.append(CobraLog(p_log['event'], p_log['args']))
        return processed_logs

    @property
    def logs(self):
        """Returns all the event logs ever added for this contract"""
        return self.process_logs(self.__filter.get_all_entries())

    def get_event_signatures(self, abi_list):
        signatures = dict()
        for abi in abi_list:
            if abi['type'] == 'event':
                signatures[abi['name']] = event_abi_to_log_topic(abi)
        return signatures

    def get_event_processors(self, abi_list):
        processors = dict()
        for abi in abi_list:
            if abi['type'] == 'event':
                processors[event_abi_to_log_topic(abi)] = partial_fn(get_event_data, abi)
        return processors


class CobraFactory:
    """Factory (prototype) of a contract"""

    def __init__(self, _web3: Web3, interface):
        self.web3 = _web3
        self.interface = interface
        self.contract_factory = self.web3.eth.contract(**self.interface)

    def deploy(self, *args, **kwargs):
        """Deploy a new instance of this contract"""
        kwargs = self.clean_modifiers(kwargs)
        if 'transact' in kwargs.keys():
            kwargs['transaction'] = kwargs['transact']
            del kwargs['transact']

        tx_hash = self.contract_factory.constructor(*args).transact(**kwargs)
        address = self.web3.eth.getTransactionReceipt(tx_hash)['contractAddress']
        return CobraInstance(self.web3, address, self.interface)

    def __getattr__(self, name):
        return getattr(self.contract_factory, name)

    def clean_modifiers(self, modifiers):
        cleaned_modifiers = modifiers.copy()
        for name, modifier in modifiers.items():
            for key, value in modifier.items():
                if not isinstance(value, str) or not isinstance(value, int):
                    cleaned_modifiers[name][key] = str(value)
        return cleaned_modifiers


class CobraAccount(str):
    def __new__(cls, w3: Web3, address):
        obj = super().__new__(cls, address)
        obj._w3 = w3
        obj._address = address
        return obj

    # Send Ether
    def transfer(self, address, amount):
        self._w3.eth.sendTransaction({'to': address, 'from': self._address, 'value': amount})

    @property
    def balance(self):
        return self._w3.eth.getBalance(self._address)


class CobraFailureHandler:
    def __init__(self, eth_tester):
        self.eth_tester = eth_tester

    def __enter__(self):
        self.snapshot_id = self.eth_tester.take_snapshot()
        return self.snapshot_id

    def __exit__(self, *args):
        assert len(args) > 0 and \
               args[0] is TransactionFailed, "Didn't revert transaction."
        self.eth_tester.revert_to_snapshot(self.snapshot_id)
        return True


# Interfaces
UNDERSCORE = "_"
LINK_LENGTH = 36


class CobraConfiguration:

    def __init__(self):
        pass

    # File reader
    def file_reader(self, file):
        try:
            with open(file, 'r') as read_file:
                return_file = read_file.read()
                read_file.close()
                return return_file
        except FileNotFoundError:
            with pytest.raises(FileNotFoundError, message="[Cobra] FileNotFound: %s" % file):
                pass

    # YAML file loader
    def yaml_loader(self, yaml_file):
        try:
            load_compile = yaml.load(yaml_file)
            return load_compile
        except yaml.scanner.ScannerError as scannerError:
            with pytest.raises(yaml.scanner.ScannerError, message="[Cobra] YAMLScannerError: %s" % scannerError):
                pass

    # JSON file loader
    def json_loader(self, json_file):
        try:
            loaded_json = json.loads(json_file)
            return loaded_json
        except json.decoder.JSONDecodeError as jsonDecodeError:
            with pytest.raises(json.decoder.JSONDecodeError, message="[Cobra] JSONDecodeError: %s" % jsonDecodeError):
                pass

    def config_test_yaml(self, test_yaml):
        yaml_test = []
        try:
            if test_yaml['artifact_path'] and test_yaml['contracts']:
                for contract in test_yaml['contracts']:
                    try:
                        if contract['contract']['artifact']:
                            try:
                                if contract['contract']['links']:
                                    yaml_test.append(dict(
                                        artifact_path=test_yaml['artifact_path'],
                                        artifact=contract['contract']['artifact'],
                                        links=contract['contract']['links']
                                    ))
                                elif not contract['contract']['links']:
                                    yaml_test.append(dict(
                                        artifact_path=test_yaml['artifact_path'],
                                        artifact=contract['contract']['artifact'],
                                        links=None
                                    ))
                                    continue
                            except KeyError:
                                yaml_test.append(dict(
                                    artifact_path=test_yaml['artifact_path'],
                                    artifact=contract['contract']['artifact'],
                                    links=None
                                ))
                    except TypeError:
                        with pytest.raises(FileNotFoundError,
                                           message="[Cobra] There is no artifact in contract. [.yaml]"):
                            pass
        except TypeError:
            with pytest.raises(FileNotFoundError,
                               message="[Cobra] Can't find artifact_path or contracts in test [.yaml]"):
                pass
        return yaml_test

    def config_test_json(self, test_json):
        json_test = []
        for key in test_json.keys():
            contract = dict()
            artifact = test_json.get(key)
            contract_names = key.split(":")
            contract.setdefault("contractName", contract_names[0])
            contract.setdefault("abi", artifact["abi"])
            contract.setdefault("bin", artifact["bin"])
            contract.setdefault("bin-runtime", artifact["bin-runtime"])
            contract_names.remove(contract_names[0])
            if not contract_names:
                contract_names = None
                contract.setdefault("links", contract_names)
                json_test.insert(0, contract)
            else:
                contract.setdefault("links", contract_names)
                json_test.append(contract)
        return json_test

    # This cobra_converter function works to increase more read able compiled contracts
    def cobra_converter(self, compiled_contracts):
        contracts = dict()
        for compiled_contract in compiled_contracts.keys():
            contract_interface = compiled_contracts.get(compiled_contract)

            contract_link = self.links_absolute_path(contract_interface)
            if contract_link:
                contract_and_link = compiled_contract.split(":")[1] + ":" + str(":".join(
                    basename(link)[:-4] for link in contract_link))
            else:
                contract_and_link = compiled_contract.split(":")[1]

            links_from_file = self.links_from_file(contract_interface)
            if links_from_file is None:
                links_from_absolutes_file = self.links_from_absolutes_file(contract_interface)
                contracts[contract_and_link] = links_from_absolutes_file
            else:
                contracts[contract_and_link] = links_from_file
        return contracts

    # Links file path from in compiled contract interface
    def links_file_path(self, contract_interface):
        files = []
        children = contract_interface['ast']['children']
        for attributes in children:
            try:
                files.append(attributes['attributes']['file'])
            except KeyError:
                continue
        return files

    # Links absolute path from in compiled contract interface
    def links_absolute_path(self, interface):
        absolutes = []
        children = interface['ast']['children']
        for attributes in children:
            try:
                absolutes.append(attributes['attributes']['absolutePath'])
            except KeyError:
                continue
        return absolutes

    def links_from_file(self, contract_interface):
        links_file = self.links_file_path(contract_interface)
        for link_file in links_file:

            contract_name = basename(link_file)[:-4]
            contract_name_len = len(contract_name)
            link_file = link_file + ":" + contract_name
            link_file_path = link_file[:36]

            bytecode = contract_interface['bin']
            bytecode_runtime = contract_interface['bin-runtime']
            link_file_path_check = "__" + link_file_path + "__"
            link_file_path_check_two = "__" + link_file_path[2:] + "__"

            if link_file_path_check in contract_interface['bin'] and \
                    link_file_path_check in contract_interface['bin-runtime']:
                underscore_in_links = LINK_LENGTH - len(link_file_path)
                link_file_name = contract_name + \
                                 (((LINK_LENGTH - contract_name_len) - underscore_in_links) * UNDERSCORE)

                contract_interface['bin'] = bytecode.replace(link_file_path, link_file_name, 1)
                contract_interface['bin-runtime'] = bytecode_runtime.replace(link_file_path, link_file_name, 1)
            elif link_file_path_check_two in contract_interface['bin'] and \
                    link_file_path_check_two in contract_interface['bin-runtime']:
                link_file_path = link_file_path[2:]
                underscore_in_links = LINK_LENGTH - len(link_file_path)
                link_file_name = contract_name + \
                                 (((LINK_LENGTH - contract_name_len) - underscore_in_links) * UNDERSCORE)

                contract_interface['bin'] = bytecode.replace(link_file_path, link_file_name, 1)
                contract_interface['bin-runtime'] = bytecode_runtime.replace(link_file_path, link_file_name, 1)
            else:
                return None
        return contract_interface

    def links_from_absolutes_file(self, contract_interface):
        links_absolutes = self.links_absolute_path(contract_interface)
        contract_interface_bin = contract_interface['bin']
        contract_interface_bin_runtime = contract_interface['bin-runtime']
        for links_absolute in links_absolutes:
            contract_name = basename(links_absolute)[:-4]
            contract_name_len = len(contract_name)
            links_absolute = links_absolute + ":" + contract_name
            links_absolute_path = links_absolute[:36]

            split_bytecode = contract_interface_bin.split(links_absolute_path, 1)
            split_bytecode_runtime = contract_interface_bin_runtime.split(links_absolute_path, 1)
            contract_bytecode = []
            contract_bytecode_runtime = []

            for index, contract in enumerate(split_bytecode):
                if len(contract) > LINK_LENGTH and (index % 2) != 0:
                    underscore_in_links = LINK_LENGTH - len(links_absolute_path)
                    link_absolute_name = contract_name + (
                            ((LINK_LENGTH - contract_name_len) - underscore_in_links) * UNDERSCORE)
                    contract_bytecode.append(link_absolute_name)
                contract_bytecode.append(contract)
            contract_interface_bin = "".join(contract_bytecode)

            for index, contract in enumerate(split_bytecode_runtime):
                if len(contract) > LINK_LENGTH and (index % 2) != 0:
                    underscore_in_links = LINK_LENGTH - len(links_absolute_path)
                    link_absolute_name = contract_name + (
                            ((LINK_LENGTH - contract_name_len) - underscore_in_links) * UNDERSCORE)
                    contract_bytecode_runtime.append(link_absolute_name)
                contract_bytecode_runtime.append(contract)
            contract_interface_bin_runtime = "".join(contract_bytecode_runtime)

        contract_interface['bin'] = contract_interface_bin
        contract_interface['bin-runtime'] = contract_interface_bin_runtime
        return contract_interface


class CobraInterfaces(CobraConfiguration):

    def __init__(self, _web3: Web3):
        super().__init__()
        self.web3 = _web3
        self.contracts = dict()

    def cobra_file(self, file_name, import_remappings=None, allow_paths=None):
        # Import remapping None to empty array
        if import_remappings is None:
            import_remappings = []

        # Allow path None to current working directory path
        if allow_paths is None:
            allow_paths = str()

        # Fetching solidity file extension
        if file_name.endswith(".sol"):
            compiled_json = compile_source(
                self.file_reader(file_name),
                import_remappings=import_remappings,
                allow_paths=allow_paths)
            convert_json = self.cobra_converter(compiled_json)
            self.cobra_test_json(convert_json)
        # Fetching compiled json file extension
        elif file_name.endswith(".json"):
            read_json = self.file_reader(file_name)
            load_json = self.json_loader(read_json)
            convert_json = self.cobra_converter(load_json)
            self.cobra_test_json(convert_json)
        # Fetching yaml from cobra framework file extension
        elif file_name.endswith(".yaml"):
            read_yaml = self.file_reader(file_name)
            load_yaml = self.yaml_loader(read_yaml)
            self.cobra_test_yaml(load_yaml)
        else:
            with pytest.raises(FileNotFoundError,
                               message="[ERROR] Can't find this type of extension ['.sol', '.json' or '.yaml']"):
                pass
        return self.contracts

    def cobra_test_json(self, load_json):
        configurations_json = self.config_test_json(load_json)
        for configuration_json in configurations_json:
            if configuration_json['links'] is None:
                self.test_with_out_link(configuration_json)
            else:
                self.test_with_link(configuration_json, configuration_json['links'])
        return self.contracts

    def cobra_test_yaml(self, load_yaml):
        try:
            load_yaml_test = load_yaml['test']
            configurations_yaml = self.config_test_yaml(load_yaml_test)
            for configuration_yaml in configurations_yaml:
                file_path_json = join(configuration_yaml['artifact_path'], configuration_yaml['artifact'])
                read_json = self.file_reader(file_path_json)
                load_json = self.yaml_loader(read_json)
                if configuration_yaml['links'] is None:
                    self.test_with_out_link(load_json)
                else:
                    self.test_with_link(load_json, configuration_yaml['links'])
            return self.contracts
        except TypeError:
            with pytest.raises(FileNotFoundError, message="[Cobra] Can't find test in cobra.yaml"):
                pass

    def get_links_address(self, links):
        contract_name_and_address = dict()
        for link in links:
            for contract in self.contracts.keys():
                contract = contract.split(":")
                if contract[0] == link[:-5]:
                    contract_name_and_address.setdefault(link[:-5], contract[1])
                elif contract[0] == link:
                    contract_name_and_address.setdefault(link, contract[1])
                else:
                    continue
        return contract_name_and_address

    def test_with_link(self, artifact, links):
        unlinked_bytecode = artifact['bin']
        get_link_address = self.get_links_address(links)
        linked_bytecode = link_code(unlinked_bytecode, get_link_address)

        contract_factory = self.web3.eth.contract(abi=artifact['abi'], bytecode=linked_bytecode)
        tx_hash = contract_factory.constructor().transact()

        address = self.web3.eth.getTransactionReceipt(tx_hash)['contractAddress']
        contract = {"abi": artifact['abi'], "bytecode": linked_bytecode}
        contract_name_and_address = artifact['contractName'] + ":" + str(address)
        self.contracts.setdefault(contract_name_and_address, contract)

    def test_with_out_link(self, artifact):
        contract_factory = self.web3.eth.contract(abi=artifact['abi'], bytecode=artifact['bin'])
        tx_hash = contract_factory.constructor().transact()

        address = self.web3.eth.getTransactionReceipt(tx_hash)['contractAddress']
        contract = {"abi": artifact['abi'], "bytecode": artifact['bin']}
        contract_name_and_address = artifact['contractName'] + ":" + str(address)
        self.contracts.setdefault(contract_name_and_address, contract)


# Set Provider
ethereum_tester = EthereumTester()
web3 = Web3(EthereumTesterProvider(ethereum_tester))


# Return zero gas price
def zero_gas_price_strategy(web3, transaction_params=None):
    return 0


# Set Gas Price to 0
web3.eth.setGasPriceStrategy(zero_gas_price_strategy)


def pytest_addoption(parser):
    group = parser.getgroup('Cobra', 'Ethereum Smart-Contract testing support')
    group.addoption('--cobra', action='store', default=None, metavar='path',
                    help='pytest --cobra Contract.json')
    group.addoption('--import_remappings', action='store', default=None, metavar='path',
                    help='pytest --cobra Contract.sol --import_remappings ["=", "-", "=/home"]')
    group.addoption('--allow_paths', action='store', default=None, metavar='path',
                    help='pytest --cobra Contract.sol --allow_paths ["/home"]')


@pytest.fixture(scope='session')
def cobra_file(pytestconfig):
    cobra_file = dict()
    if pytestconfig.option.cobra:
        cobra_interface = CobraInterfaces(web3)
        cobra_file = cobra_interface.cobra_file(pytestconfig.option.cobra,
                                                pytestconfig.option.import_remappings,
                                                pytestconfig.option.allow_paths)
    return cobra_file


@pytest.fixture
def cobra(cobra_file):
    return CobraTester(web3, ethereum_tester, cobra_file)
