#!/usr/bin/env python3

from os.path import basename
import pytest
import json
import yaml

# Interfaces
UNDERSCORE = "_"
LINK_LENGTH = 36


class Configuration:

    def __init__(self):
        pass

    # File reader
    @staticmethod
    def file_reader(file):
        try:
            with open(file, 'r') as read_file:
                return_file = read_file.read()
                read_file.close()
                return return_file
        except FileNotFoundError:
            with pytest.raises(FileNotFoundError, message="[Cobra] FileNotFound: %s" % file):
                pass

    # YAML file loader
    @staticmethod
    def yaml_loader(yaml_file):
        try:
            load_compile = yaml.load(yaml_file)
            return load_compile
        except yaml.scanner.ScannerError as scannerError:
            with pytest.raises(yaml.scanner.ScannerError, message="[Cobra] YAMLScannerError: %s" % scannerError):
                pass

    # JSON file loader
    @staticmethod
    def json_loader(json_file):
        try:
            loaded_json = json.loads(json_file)
            return loaded_json
        except json.decoder.JSONDecodeError as jsonDecodeError:
            with pytest.raises(json.decoder.JSONDecodeError, message="[Cobra] JSONDecodeError: %s" % jsonDecodeError):
                pass

    @staticmethod
    def config_test_yaml(test_yaml):
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

    @staticmethod
    def config_test_json(test_json):
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
    @staticmethod
    def links_file_path(contract_interface):
        files = []
        children = contract_interface['ast']['children']
        for attributes in children:
            try:
                files.append(attributes['attributes']['file'])
            except KeyError:
                continue
        return files

    # Links absolute path from in compiled contract interface
    @staticmethod
    def links_absolute_path(interface):
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
