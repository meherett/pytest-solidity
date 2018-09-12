from eth_tester.exceptions import TransactionFailed


def test_mining(cobra):
    """
    Mining blocks works
    """
    starting_block = cobra.eth.blockNumber
    # Mining a block mines exactly one block
    cobra.mine_blocks()
    assert cobra.eth.blockNumber == starting_block + 1
    # Mining N blocks mines exactly N blocks
    cobra.mine_blocks(10)
    assert cobra.eth.blockNumber == starting_block + 11


def test_time(cobra):
    """
    cobra.now() gets the current time
    This should match the mined block time
    when the block is mined
    """
    # Check pending block time is returned
    # NOTE: pending block time is at creation
    start_time = cobra.now()
    start_block = cobra.eth.getBlock('pending')['number']
    assert start_time == cobra.now()  # Returns the same number if no mining
    # Mine a block, timestamps should match
    cobra.mine_blocks()
    assert cobra.eth.getBlock('latest')['timestamp'] == start_time
    assert cobra.now() > start_time
    # Mine another block, timestamps should still match
    cobra.mine_blocks()
    assert cobra.eth.getBlock(start_block)['timestamp'] == start_time


def test_exception(cobra):
    # Can call as many transaction failures in a row as you need
    failures = 0
    with cobra.tx_fails:
        raise TransactionFailed
    failures += 1
    with cobra.tx_fails:
        raise TransactionFailed
    failures += 1
    with cobra.tx_fails:
        raise TransactionFailed
    failures += 1
    assert failures == 3
