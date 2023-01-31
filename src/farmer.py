import json
import logging
from decimal import Decimal
from typing import Optional, Dict

from .utils.alchemy import current_eth_balance, current_token_balances, \
                            get_token_metadata
from .utils.coingecko import load_coin_data, get_token_price, get_currency_price

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

def to_decimals(token_amount, decimals):
    return Decimal(token_amount) / Decimal(10 ** decimals)

def wallet_balances(wallet_address: str) -> Dict:
    """Get the wallet's ETH balance and balance for each token the account
    holds.

    :param wallet_address: The wallet's address.
    :type wallet_address: str
    :return: Dictionary of the wallet's balances.
    :rtype: _type_
    """
    # Get the tokens hold by the wallet
    eth_balance = current_eth_balance(wallet_address)
    coins_balance = current_token_balances(wallet_address)

    return {
        "eth_balance": eth_balance,
        "coins_balance": coins_balance,
    }

def read_farmer_spec(filename: str) -> Dict:
    """Loads the data from the 'filename' specification file and returns the
    data it contains as a dictionary.
    """
    with open(filename, 'r') as f:
        data = json.loads(f.read())

    specification = {
        "minimum_total_balance": 0,
        "token_contract_amount": {}
    }

    if 'minimum_total_balance' in data:
        specification['minimum_total_balance'] = int(data['minimum_total_balance'])

    if 'token_contract_amount' in data:
        specification['token_contract_amount'] = data['token_contract_amount']

    return specification

def is_account_farmer(eth_balance: str, coins_balance: Dict ,
                        minimum_total_balance: Optional[int] = 0,
                        token_contract_amount: Optional[Dict] = {}) -> bool:
    """Validate whether the wallet address currently holds the tokens in the
    `token_contract_amount` dictionary and whether they at least the specified
    amount. Also validate if the wallet address has value of at least
    `minimum_total_balance` in USD.

    :param wallet_address: A string of the wallet address.
    :type wallet_address: str
    :param minimum_total_balance: Minimum total value, in USD, held in the
        wallet address. This includes the tokens and the ETH amount.
    :type minimum_total_balance: Optional[int]
    :param token_contract_amount: Dictonary of contract address and amount of
        tokens.
    :type token_contract_amount: Optional[Dict]
    """

    # Load the list of tokens on the ethereum network
    ethereum_token_contracts = load_coin_data("ethereum")

    # Iterate ove the tokens held by the wallet. There are 3 cases:
    # (1) The token does not exist in the CoinGecko DB. The token is not
    #       reputable and not traded so it doesn't count toward the usd_amount.
    # (2) The token exists in CoinGecko DB. If the token is in the
    #       token_contract_amount dictionary then check if the amount is
    #       greater than the minimum, else return False.
    # (3) The token exists and the amount is greater than the minimum so it
    #       counts towards the total_usd_amount held.
    total_usd_amount = 0

    required_tokens = set(token_contract_amount)

    for token_address in coins_balance.keys():

        # Check case (1) or go with the next token the address has
        if token_address in ethereum_token_contracts:

            tmd = get_token_metadata(token_address)

            # Get amount of token from hex -> int -> Decimal
            token_amount = int(coins_balance[token_address], 16)
            token_amount = to_decimals(token_amount, tmd['decimals'])

            if token_address in required_tokens:
                if token_amount < token_contract_amount[token_address]:
                    # Case (2): no required amount satisfied
                    return False

            # Case(3): there is no requirement or the wallet has the required amount
            # Get price for token based on CG data
            token_price = get_token_price(token_address)

            logger.debug('Token address: %s, amount: %s, price: %s' %
                            (token_address, token_amount, token_price))

            total_usd_amount += token_amount * Decimal(token_price)

    # Add the value of the eth held in the account
    token_price = get_currency_price()

    eth_balance = int(eth_balance, 16)
    total_usd_amount += to_decimals(eth_balance, 16) * Decimal(token_price)

    # Validate that the user has more than the requested amount
    if total_usd_amount >= minimum_total_balance:
        return True
    return False
