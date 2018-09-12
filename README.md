<p align="center">		
  <img src="https://raw.githubusercontent.com/Cobraframework/pytest-cobra/master/pytest-cobra.png">		
</p>

# PyTest-Cobra ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django.svg?style=for-the-badge)

*PyTest plugin for testing Smart Contracts for Ethereum blockchain.*

![GitHub](https://img.shields.io/github/license/mashape/apistatus.svg)

## Requirements

Step 1: Install solc

```
npm install -g solc
```
or
```
sudo add-apt-repository ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get install solc
```

Step 2: Install PyTest
```bash
pip install -U pytest
```

Step 3: Install plugin PyTest-Cobra
```
pip install pytest-cobra
```

## Usage

#### Execute your test suite

##### 1: Testing Solidity file

```
pytest --cobra Contracts.sol
```
import_remappings
```
pytest --cobra Contracts.sol --remapping ["/home/path/dir/"]
```

##### 2: Testing Contracts Json file

Compile your contracts into a package (soon to be ethPM-compliant)
```
solc --combined-json abi,bin,bin-runtime contracts/ > Contracts.json
```
Testing Contracts.json
```
pytest --cobra Contracts.json
```

##### 3: Testing Contracts yaml file 
```Comming soon with Cobra Framework```

## Further help
##### PyTest
Go check out the [PyTest](http://pytest.org).

## Donation
[![Donate with Bitcoin](https://en.cryptobadges.io/badge/big/3JiPsp6bT6PkXF3f9yZsL5hrdQwtVuXXAk)](https://en.cryptobadges.io/donate/3JiPsp6bT6PkXF3f9yZsL5hrdQwtVuXXAk)
[![Donate with Ethereum](https://en.cryptobadges.io/badge/big/0xD32AAEDF28A848e21040B6F643861A9077F83106)](https://en.cryptobadges.io/donate/0xD32AAEDF28A848e21040B6F643861A9077F83106)