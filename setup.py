from setuptools import setup
import os

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, "README.md"), "r") as readme:
    long_description = readme.read()

setup(
    name="pytest-cobra",
    version='1.0.1',
    description='PyTest plugin for testing Smart Contracts for Ethereum blockchain.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    author='Meheret Tesfaye',
    author_email='meherett@zoho.com',
    url='https://github.com/cobraframework/pytest-cobra',
    python_requires='>=3.6,<3.8',
    packages=['pytest_cobra'],
    install_requires=[
        'pytest>=3.7.1,<4.0.0',
        'eth-keyfile==0.5.1',
        'eth-tester==0.1.0b33',
        'py-evm==0.2.0a33',
        'eth-abi==1.2.2',
        'py-ecc==1.4.3',
        'py-solc>=3.2.0,<4.0.0',
        'web3>=4.4.1,<5.0.0',
        'PyYAML>=3.13,<4.0'
    ],
    entry_points={
        'pytest11': [
            'name_of_plugin = pytest_cobra',
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Framework :: Pytest",
    ],
)
