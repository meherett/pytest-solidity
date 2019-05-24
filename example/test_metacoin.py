# MetaCoin Testing


# cobra is pytest fixture
def test_metacoin(cobra):
    # Getting Contract Factory by name
    metacoin = cobra.contract('MetaCoin')
    # Getting Contract Instance of MetaCoin
    metacoin = metacoin.deploy()

    assert metacoin.getBalance(cobra.accounts[0]) == 10000
