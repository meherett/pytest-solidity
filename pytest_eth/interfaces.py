#!/usr/bin/env python3

from web3 import Web3
from solcx import link_code, compile_source
from os.path import join
import pytest

from .config import Configuration


class Interfaces(Configuration):

    def __init__(self, _web3: Web3):
        super().__init__()
        self.web3 = _web3
        self.contracts = dict()

    def eth_file(self, file_name, import_remappings=None, allow_paths=None):
        # Import remapping None to empty array
        if import_remappings is None:
            import_remappings = []

        # Allow path None to current working directory path
        if allow_paths is None:
            allow_paths = str()

        # Fetching solidity file extension
        if file_name.endswith(".sol"):
            _import_remappings = ["-"]
            _import_remappings.extend(import_remappings)
            compiled_json = compile_source(
                self.file_reader(file_name),
                import_remappings=_import_remappings,
                allow_paths=allow_paths
            )
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
        # tx_hash = contract_factory.constructor().transact()
        tx_hash = contract_factory.constructor().transact(transaction={
            "gas": 12_500_000, "gasPrice": self.web3.eth.gasPrice
        })

        address = self.web3.eth.getTransactionReceipt(tx_hash)['contractAddress']
        contract = {"abi": artifact['abi'], "bytecode": linked_bytecode}
        contract_name_and_address = artifact['contractName'] + ":" + str(address)
        self.contracts.setdefault(contract_name_and_address, contract)

    def test_with_out_link(self, artifact):
        contract_factory = self.web3.eth.contract(abi=artifact['abi'], bytecode=artifact['bin'])
        # tx_hash = contract_factory.constructor().transact()
        tx_hash = contract_factory.constructor().transact(transaction={
            "gas": 12_500_000, "gasPrice": self.web3.eth.gasPrice
        })

        address = self.web3.eth.getTransactionReceipt(tx_hash)['contractAddress']
        print(address)
        contract = {"abi": artifact['abi'], "bytecode": artifact['bin']}
        contract_name_and_address = artifact['contractName'] + ":" + str(address)
        self.contracts.setdefault(contract_name_and_address, contract)
