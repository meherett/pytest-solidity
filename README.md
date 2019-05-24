<p align="center">		
  <img src="https://raw.githubusercontent.com/Cobraframework/pytest-cobra/master/pytest-cobra.png">		
</p>

# PyTest-Cobra ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytest-cobra.svg?style=for-the-badge)

*PyTest plugin for testing Smart Contracts for Ethereum blockchain.*

![GitHub License](https://img.shields.io/github/license/cobraframework/pytest-cobra.svg)
![PyPI Version](https://img.shields.io/pypi/v/pytest-cobra.svg?color=blue)
![PyPI Version](https://img.shields.io/github/release-date/cobraframework/pytest-cobra.svg)
![PyPI Wheel](https://img.shields.io/pypi/wheel/pytest-cobra.svg)

## Requirements

#### Step 1: Install solc

```
npm install -g solc
```
##### or for Ubuntu(Linux)
```
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install solc
```

#### Step 2: Install PyTest
```bash
pip install -U pytest
```

#### Step 3: Install plugin PyTest-Cobra
```
pip install pytest-cobra
```

## Usage

###### Execute your test suite

#### 1: Testing from Solidity file (.sol)

```
pytest --cobra Contracts.sol
```

#### Optional commands

##### import_remappings
```
pytest --cobra Contracts.sol --import_remappings "=,-,=/home"
```

##### allow_paths
```
pytest --cobra Contracts.sol --allow_paths "/home/meheret,/user,/"
```

#### 2: Testing from compiled Contracts Json file (.json)

##### Compile your contracts into a package (soon to be ethPM-compliant)
```
solc --combined-json abi,bin,bin-runtime contracts/ > Contracts.json
```

##### Testing Contracts.json
```
pytest --cobra Contracts.json
```

#### 3: Testing from cobra.yaml file (.yaml) 
```Comming soon with Cobra Framework```

## Further help
##### PyTest
Go check out the [PyTest](http://pytest.org).

## Author
##### # Meheret Tesfaye [@meherett](http://github.com/meherett).

## Donation
[![Donate with Bitcoin](https://en.cryptobadges.io/badge/big/3JiPsp6bT6PkXF3f9yZsL5hrdQwtVuXXAk)](https://en.cryptobadges.io/donate/3JiPsp6bT6PkXF3f9yZsL5hrdQwtVuXXAk)
[![Donate with Ethereum](https://en.cryptobadges.io/badge/big/0xD32AAEDF28A848e21040B6F643861A9077F83106)](https://en.cryptobadges.io/donate/0xD32AAEDF28A848e21040B6F643861A9077F83106)