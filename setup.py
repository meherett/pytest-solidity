from setuptools import setup

setup(
    name="pytest-cobra",
    version='0.0.2',
    description='PyTest plugin for testing Smart Contracts for Ethereum blockchain.',
    long_description='TODO',
    license='MIT',
    author='Meheret Tesfaye',
    author_email='meherett@zoho.com',
    url='https://github.com/Cobraframework/pytest-cobra',
    python_requires='>=3.5,<3.7',
    packages=['pytest_cobra'],
    install_requires=[
        'pytest>=3.7.1,<4.0.0',
        'eth-tester[py-evm]>=0.1.0-beta.28,<0.2.0',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Framework :: Pytest",
    ],
)
