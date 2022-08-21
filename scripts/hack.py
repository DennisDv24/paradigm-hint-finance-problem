from brownie import Setup, HintFinanceFactory, HintFinanceVault
from brownie import accounts, chain, interface
from web3 import Web3

IERC20 = interface.IERC20
router = interface.UniswapV2RouterLike(
    '0xf164fC0Ec4E93095b804a4795bBe1e041497b92a'
)
WETH_ADDR = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

get_factory = lambda setup: HintFinanceFactory.at(setup.hintFinanceFactory())

get_vault_from_setuper = lambda setup, i: (
    HintFinanceVault.at(get_factory(setup).underlyingToVault(
        setup.underlyingTokens(i)
    ))
)

get_token_bal = lambda setup, i: (
    IERC20(setup.underlyingTokens(i)).balanceOf(
        get_vault_from_setuper(setup, i)
    )
)

get_under_tokens_bals = lambda setup: (
    get_token_bal(setup, 0),
    get_token_bal(setup, 1),
    get_token_bal(setup, 2)
)

get_formated_token_bals = lambda setup: (
    tuple(map(
        lambda x: str(Web3.fromWei(x, 'ether')), get_under_tokens_bals(setup)
    ))
)


def try_to_operate_vault(setuper):
    i = 0
    acc = accounts[0]
    token = IERC20(setuper.underlyingTokens(i))
    vault = get_vault_from_setuper(setuper, i)
    
    router.swapExactETHForTokens(
        0, [WETH_ADDR, token], acc, 2661091088,
        {'from': acc, 'value': Web3.toWei(10, 'ether')}
    )

    token.approve(token, token.balanceOf(acc))
    tx = vault.deposit(token.balanceOf(acc))
    tx.wait(1)
    tx = vault.withdraw(0.4)
    tx.wait(1)
    print(get_formated_token_bals(setuper))
    

def main():
    setuper = Setup.deploy(
        {'from': accounts[0], 'value': Web3.toWei(30, 'ether')}
    )
    print(get_formated_token_bals(setuper))
    try_to_withdraw(setuper)
    