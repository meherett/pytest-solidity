def test_init(cobra):
    for acct in cobra.accounts:
        assert acct.balance > 0
        assert acct not in filter(lambda accounts: accounts != acct, cobra.accounts)


def test_transfer(cobra):
    # Ether transfers work
    starting_balance = cobra.accounts[0].balance
    assert cobra.accounts[1].balance == starting_balance

    cobra.accounts[0].transfer(cobra.accounts[1], 100)
    assert cobra.accounts[0].balance == starting_balance - 100
    assert cobra.accounts[1].balance == starting_balance + 100
    
    cobra.accounts[1].transfer(cobra.accounts[0], 100)
    assert cobra.accounts[0].balance == cobra.accounts[1].balance == starting_balance
