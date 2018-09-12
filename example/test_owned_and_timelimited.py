artifact_owned = {
    "abi": "[{\"constant\":true,\"inputs\":[],\"name\":\"owner\",\"outputs\":[{\"name\":\"\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"newOwner\",\"type\":\"address\"}],\"name\":\"changeOwner\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"}]",
    "bytecode": "6060604052336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550341561004f57600080fd5b6101ce8061005e6000396000f30060606040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680638da5cb5b14610051578063a6f9dae1146100a6575b600080fd5b341561005c57600080fd5b6100646100df565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b34156100b157600080fd5b6100dd600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610104565b005b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561015f57600080fd5b806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550505600a165627a7a72305820880a4056fab249ea33a384814995ed65839292e7edf737e2082462ab370b372a0029"
    }

artifact_timelimited = {
  "abi": "[{\"constant\":true,\"inputs\":[],\"name\":\"duration\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"alive\",\"outputs\":[{\"name\":\"_stuff\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[],\"name\":\"destroy\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"owner\",\"outputs\":[{\"name\":\"\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[],\"name\":\"setExpired\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"newOwner\",\"type\":\"address\"}],\"name\":\"changeOwner\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"finished\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"creationTime\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"name\":\"_duration\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"}]",
  "bytecode": "6060604052336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555042600155341561005357600080fd5b604051602080610493833981016040528080519060200190919050508080600281905550505061040b806100886000396000f30060606040526004361061008e576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680630fb5a6b414610093578063753899e9146100bc57806383197ef0146100e95780638da5cb5b146100fe578063a56fa76c14610153578063a6f9dae114610168578063bef4876b146101a1578063d8270dce146101ce575b600080fd5b341561009e57600080fd5b6100a66101f7565b6040518082815260200191505060405180910390f35b34156100c757600080fd5b6100cf6101fd565b604051808215151515815260200191505060405180910390f35b34156100f457600080fd5b6100fc610242565b005b341561010957600080fd5b610111610276565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b341561015e57600080fd5b61016661029b565b005b341561017357600080fd5b61019f600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610328565b005b34156101ac57600080fd5b6101b46103c6565b604051808215151515815260200191505060405180910390f35b34156101d957600080fd5b6101e16103d9565b6040518082815260200191505060405180910390f35b60025481565b6000600360009054906101000a900460ff1615151561021b57600080fd5b600254600154014210801561023d5750600360009054906101000a900460ff16155b905090565b600360009054906101000a900460ff16151561025d57600080fd5b3373ffffffffffffffffffffffffffffffffffffffff16ff5b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161415156102f657600080fd5b60025460015401421015151561030b57600080fd5b6001600360006101000a81548160ff021916908315150217905550565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561038357600080fd5b806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050565b600360009054906101000a900460ff1681565b600154815600a165627a7a72305820cfa24f8534068ff9caf1fc94dda21bbaf586fa7b501b0712c37a18549b783ff90029"
}


# Just use the 'cobra' fixture in your pytest_ethereum-enabled tests
def test_owned_and_timelimited(cobra):

    # Get contracts via name from your assets file (e.g. 'contracts.json')
    # NOTE: When no contract from file is selected,
    #       uses file basename e.g. 'path/to/Owned.sol:Owned'
    owned = cobra.new(artifact_owned)
    # Deploying Owned
    owned = owned.deploy()

    # You can specify a specific contract from the file
    timelimited_factory = cobra.new(artifact_timelimited)
    # You must specify the deployment args if they exist
    # NOTE: must be supplied in abi order
    timelimited = timelimited_factory.deploy(10)  # arg1: 10 blocks

    # Use normal assert syntax for testing
    # pure/view/constant functions call by default
    assert owned.owner() == cobra.accounts[0]  # Doesn't mine a block!

    # non-'constant' functions transact by default
    # NOTE: Transactions auto-mine (see eth-cobra)
    owned.changeOwner(cobra.accounts[1])  # Transaction auto-mined into block
    assert owned.owner() == cobra.accounts[1]  # No transaction here

    # Use this for asserting when a failed transaction should occur
    starting_balance = cobra.accounts[0].balance
    with cobra.tx_fails:
        owned.changeOwner(cobra.accounts[0])  # account 0 is no longer the owner!
    # We can do multiple failures in here...
    with cobra.tx_fails:
        owned.changeOwner(cobra.accounts[2])  # account 2 isn't either

    # No transactions were committed for these failures
    assert starting_balance == cobra.accounts[0].balance

    # You can supply optional transaction params
    owned.changeOwner(cobra.accounts[0],
                      transact={
                          'from': cobra.accounts[1],  # from a different sender
                          # 'value': 100,  # send 100 wei in this transaction
                          # You can also do other things... see web3.py for more info!
                      }
                      )
    assert owned.owner() == cobra.accounts[0]  # account[0] is the owner again!

    # You can mine an empty block if you want
    while timelimited.alive():  # This makes a call, so no transaction occurs
        cobra.mine_blocks()  # mines an empty block

    # You can check the current timestamp
    assert cobra.now() >= timelimited.creationTime() + timelimited.duration()
    timelimited.setExpired()
    # You can check to see if a contract still has code
    # NOTE: Implicitly calls address.codesize != 0
    assert timelimited.hascode
    timelimited.destroy()  # Calls self destruct opcode, removing code
    assert not timelimited.hascode

    # Get Ether balance of any address
    print("Account 0 has", cobra.accounts[0].balance, "Wei")
    print("Account 1 has", cobra.accounts[1].balance, "Wei")
    print("Contract 'timelimited' has", timelimited.balance, "Wei")

    # Send any address Ether
    print("Account 2 has", cobra.accounts[2].balance, "Wei")
    cobra.accounts[1].transfer(cobra.accounts[2], 100)  # send 100 wei to address 2
    print("Account 2 now has", cobra.accounts[2].balance, "Wei")
