"""
This file includes utility functions that make requests to the Alchemy
API. More about the API on: https://www.alchemy.com/

It is required to have an API key to use the use the functions in this file.
"""
import os
import logging
from typing import Optional, List, Dict

import requests

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

ALCHEMY_API_KEY = os.environ.get('ALCHEMY_API_KEY', None)
if not ALCHEMY_API_KEY:
    raise Exception('No ALCHEMY_API_KEY key provided.')

ALCHEMY_URL = f'https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}'
ALCHEMY_NFT_URL = f'https://eth-mainnet.g.alchemy.com/nft/v2/{ALCHEMY_API_KEY}'

headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

def account_nfts(wallet_address: str,
                 nft_contract_addresses: List = [],
                 include_spam: bool=False) -> List[str]:
    """Fetch the NFTs associated with the account. Exclude SPAM NFTs. More
    about the parameters passed: https://docs.alchemy.com/reference/getnfts

    :param wallet_address: The wallet address as a string.
    :type wallet_address: str
    :param include_spam: Whether to include the NFTs categorizes as spam,
        default False
    :type include_spam: bool
    :return: A list of all the NFTs the user has.
    :rtype: List
    """
    arguments = {
        'owner': wallet_address,
        'pageSize': 100,
        'withMetadata': 'false',
    }

    if len(nft_contract_addresses) > 45:
        raise Exception('Can only test up to 45 NFT contract addresses at a time.')

    if nft_contract_addresses:
        arguments['contractAddresses[]'] = ','.join(nft_contract_addresses)

    if not include_spam:
        arguments['excludeFilters[]'] = 'SPAM'

    pageKey = None

    logger.debug('Get NFTs for address: %s', wallet_address)
    nfts = []

    while True:
        # if there are more pages with results pass the key of the next page
        if pageKey:
            arguments['pageKey'] = pageKey

        r = requests.get(ALCHEMY_NFT_URL + '/getNFTs', params=arguments,
                            headers={"accept": "application/json"})

        if r.status_code != 200:
            logger.error('Alchemy request returned status code %d, payload %s',
                            r.status_code, arguments)
            raise Exception('Request returned status code %s' % r.status_code)

        result = r.json()
        nfts.extend(result['ownedNfts'])

        # if there are more pages of tranfers to retrieve, send a request
        # with the updated 'pageKey', else all transfers have been retrieved
        if 'pageKey' in result:
            pageKey = result['pageKey']
        else:
            break

    return nfts

def unique_nft_contracts(account_nfts: List) -> List:
    """From a list of NFT-related data received by the Alchemy API, keep only
    the list of the unique NFT contract addresses.

    :param account_nfts: List of NFT-related data retrieved from Alchemy.
    :type account_nfts: List
    :return: List of unique contract addresses.
    :rtype: List
    """
    unique_nft_contract_addresses = set()
    for nft in account_nfts:
        if nft['contract']['address'] not in unique_nft_contract_addresses:
            unique_nft_contract_addresses.add(nft['contract']['address'])
    return list(unique_nft_contract_addresses)

def account_transfers(wallet_address: str, direction: Optional[str] = 'to',
                        from_block: Optional[str] = "0x0") -> List:
    # Main payload to send. Will be updated it for paginated requests.
    payload = {
        'id': 1,
        'jsonrcp': '2.0',
        'method': 'alchemy_getAssetTransfers',
    }

    params = {
        "fromBlock": from_block,
        "toBlock": "latest",
        "maxCount": "0x3e8",
        "withMetadata": True,
        "excludeZeroValue": False,
        "category": ["external"],
    }

    # choice between incoming or outgoing transfers
    if direction == 'to':
        params['toAddress'] = wallet_address
    else:
        params['fromAddress'] = wallet_address

    pageKey = None

    logger.debug('Get account transfers for address: %s', wallet_address)
    transfers = []

    while True:
        # if there are more pages with results pass the key of the next page
        if pageKey:
            params['pageKey'] = pageKey

        # update the parameters to send as payload
        payload['params'] = [params]
        r = requests.post(ALCHEMY_URL, json=payload, headers=headers)
        if r.status_code != 200:
            logger.error('Alchemy request returned status code %d, payload %s',
                            r.status_code, payload)
            raise Exception('Request returned status code %s' % r.status_code)

        result = r.json()['result']
        transfers.extend(result['transfers'])

        # if there are more pages of tranfers to retrieve, send a request
        # with the updated 'pageKey', else all transfers have been retrieved
        if 'pageKey' in result:
            pageKey = result['pageKey']
        else:
            break
    return transfers

def current_token_balances(wallet_address: str) -> Dict:
    """Get the balance for each ERC20 token that the wallet
    address currently holds.

    :param wallet_address: String of the wallet address.
    :type wallet_address: str
    :raises Exception: When the request returns a status code other than 200,
        in which case there is no token data.
    :return: A dictionary with contractAddress keys -> tokenBalance values.
    :rtype: dict
    """
    payload = {
        'id': 1,
        'jsonrcp': '2.0',
        'method': 'alchemy_getTokenBalances',
        "params": [wallet_address]
    }
    logger.debug('Get ERC20 balance for address: %s', wallet_address)
    r = requests.post(ALCHEMY_URL, json=payload, headers=headers)
    if r.status_code != 200:
        logger.error('Alchemy request returned status code %d, payload %s',
                        r.status_code, payload)
        raise Exception('Request returned status code %s' % r.status_code)

    token_balances = r.json()['result']['tokenBalances']
    ret = {}
    for tb in token_balances:
        ret[tb['contractAddress']] = tb['tokenBalance']
    return ret

def current_eth_balance(wallet_address: str):
    """Retrieve current balance of wallet's ETH.
    """
    payload = {
        'id': 1,
        'jsonrcp': '2.0',
        'method': 'eth_getBalance',
        "params": [wallet_address]
    }
    logger.debug('Get ETH balance for address: %s', wallet_address)
    r = requests.post(ALCHEMY_URL, json=payload, headers=headers)
    if r.status_code != 200:
        logger.error('Alchemy request returned status code %d, payload %s',
                        r.status_code, payload)
        raise Exception('Request returned status code %s' % r.status_code)

    return r.json()['result']

def get_token_metadata(contract_address: str):
    """Retrieve metadata for a specific contract address.
    """
    payload = {
        'id': 1,
        'jsonrcp': '2.0',
        'method': 'alchemy_getTokenMetadata',
        "params": [contract_address]
    }
    logger.debug('Get metadata for token: %s', contract_address)
    r = requests.post(ALCHEMY_URL, json=payload, headers=headers)
    if r.status_code != 200:
        logger.error('Alchemy request returned status code %d, payload %s',
                        r.status_code, payload)
        raise Exception('Request returned status code %s' % r.status_code)

    return r.json()['result']
