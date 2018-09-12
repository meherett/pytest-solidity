# MetaCoin Testing


def test_metacoin(cobra):
    # Get Contract Factory
    metacoin = cobra.contract('MetaCoin')
    # Deploying MetaCoin
    metacoin = metacoin.deploy()

    assert metacoin.getBalance(cobra.accounts[0]) == 10000
