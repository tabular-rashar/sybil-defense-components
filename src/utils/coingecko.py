"""
This file includes utility functions that make requests to the CoinGecko
API. More about the API on: https://www.coingecko.com/en/api/documentation
"""

import json
import logging
from typing import List, Optional

import requests

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

COINGECKO_URL = 'https://api.coingecko.com/api/v3/'
COIN_DATA_STORAGE_FILE = '%s-coin-address.json'

headers = {
    "accept": "application/json",
}

def get_token_price(contract_address: str, network: Optional[str] = 'ethereum') -> str:
    """Get current price in USD of token based on the 'contract_address' and
    the blockchain network where the contract is deployed. Use the CoinGecko
    API to fetch the current price information.

    :param contract_address: The hash of the address of the deployed contract.
    :type contract_address: str
    :param network: The name of the blockcahin network, defaults to 'ethereum'
    :type network: Optional[str], optional
    :raises Exception: When the returned response code of the request is not 200.
    :return: The exchange rate of the token in USD.
    :rtype: str
    """
    parameters = {
        'contract_addresses': contract_address,
        'vs_currencies': 'usd',
    }
    r = requests.get(COINGECKO_URL + f'simple/token_price/{network}',
                        params=parameters, headers=headers)
    if r.status_code != 200:
        logger.error('CoinGecko request returned status code %d', r.status_code)
        raise Exception('Request returned status code %s' % r.status_code)
    return r.json()[contract_address]['usd']

def get_currency_price() -> str:
    """Get the current price in USD of 1 ETH.

    :raises Exception: When the returned response code of the request is not 200.
    :return: Current price in USD of 1 ETH.
    :rtype: str
    """
    parameters = {
        'ids': 'ethereum',
        'vs_currencies': 'usd',
    }
    r = requests.get(COINGECKO_URL + f'simple/price',
                        params=parameters, headers=headers)
    if r.status_code != 200:
        logger.error('CoinGecko request returned status code %d', r.status_code)
        raise Exception('Request returned status code %s' % r.status_code)
    return r.json()['ethereum']['usd']

def fetch_coin_data():
    """Fetch the coin-related data that CoinGecko tracks. Retrieve the
    contract address for each platform and filter out the coins that are not
    on the Ethereum or Polygon chains.

    :raises Exception: When the request returns a status code other than 200,
        in which case there is no token data.
    :return: List of dictionaries where each dictionary refers to a coin on
        Ethereum and/or Polygon chain.
    :rtype: list
    """
    parameters = {
        'include_platform': 'true',
    }
    r = requests.get(COINGECKO_URL + 'coins/list', params=parameters, headers=headers)
    if r.status_code != 200:
        logger.error('CoinGecko request returned status code %d', r.status_code)
        raise Exception('Request returned status code %s' % r.status_code)

    coins = []
    for c in r.json():
        platforms = c['platforms']
        if ('ethereum' in platforms) or ('polygon-pos' in platforms):
            coin_data = {
                'id': c['id']
            }

            for p in ['ethereum', 'polygon-pos']:
                if p in platforms:
                    coin_data[p] = platforms[p]

            coins.append(coin_data)
    return coins

def fetch_coin_metadata(contract_address: str, network: str):

    r = requests.get(COINGECKO_URL + f'coins/{network}/contract/{contract_address}',
                        headers=headers)
    if r.status_code != 200:
        logger.error('CoinGecko request returned status code %d', r.status_code)
        raise Exception('Request returned status code %s' % r.status_code)

    return r.json()['detail_platforms'][network]['decimal_place']

def store_contract_data(coin_data: List, network: str):
    """Store the contract address and the associated symbol for each token.
    """
    contract_data = {}
    for cd in coin_data:
        if network in cd:
            contract_data[cd[network]] = cd['id']

    # store data
    with open(COIN_DATA_STORAGE_FILE % network, 'w') as f:
        json.dump(contract_data, f)

def load_coin_data(network: str):
    """Load the coin address and the symbol data for the `network` blockchain.
    """
    with open(COIN_DATA_STORAGE_FILE % network, 'r') as f:
        coin_data = json.load(f)
    return coin_data

if __name__ == '__main__':
    coin_data = fetch_coin_data()
    store_contract_data(coin_data, 'ethereum')
    store_contract_data(coin_data, 'polygon-pos')
