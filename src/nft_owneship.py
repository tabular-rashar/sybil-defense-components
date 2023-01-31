import json
from typing import List

from .utils.alchemy import account_nfts, unique_nft_contracts

def to_lowercase(strings: List) -> List:
    return [s.lower() for s in strings]

def is_nft_owned(owned_nfts: List, nft_address: str) -> bool:
    """Verify if the 'nft_address' is in the list of 'owned_nfts'
    """
    # in case some addresses are uppercase
    owned_nfts = to_lowercase(owned_nfts)

    if nft_address.lower() in owned_nfts:
        return True
    return False

def which_nfts_owned(owned_nfts: List, nft_contract_addresses: List) -> List:
    """Verify which of the 'nft_contract_addresses' are in the 'owned_nfts'
    list and return a List of boolean values, one for each one of the
    'nft_contract_addresses'

    :param owned_nfts: NFTs owned by the wallet.
    :type owned_nfts: List
    :param nft_contract_addresses: NFT contract addresses to test.
    :type nft_contract_addresses: List
    :return: List of booleans, one for each of the 'nft_contract_addresses'.
    :rtype: List
    """
    # in case some addresses are uppercase
    owned_nfts = to_lowercase(owned_nfts)

    is_owned = []

    for nft_addr in nft_contract_addresses:
        if nft_addr.lower() in owned_nfts:
            is_owned.append(True)
        else:
            is_owned.append(False)

    return is_owned

def nft_ownership_from_list(wallet_address: str,
                            nft_contract_addresses: List) -> List:
    """Test which of the NFTs specified in the 'nft_contract_addresses'
    are owned by the 'wallet_address'.

    :param wallet_address: The wallet address as a string.
    :type wallet_address: str
    :param nft_contract_addresses: List of contract addresses for NFTs.
    :type nft_contract_addresses: List
    :return: List of True/False values based on which NFTs are owned.
    :rtype: List
    """
    owned_nfts = account_nfts(wallet_address, nft_contract_addresses)
    unique_owned_nfts = unique_nft_contracts(owned_nfts)
    return which_nfts_owned(unique_owned_nfts, nft_contract_addresses)

def minimum_owned_nfts(wallet_address: str, nft_contract_addresses: List,
                        minimum_owned_nfts: int=1) -> bool:
    """Examine if at least one of the NFTs specified in the
    'nft_contract_addresses' is owned by the 'wallet_address' and return True
    in that case. Else return False

    :param wallet_address: The wallet address as a string.
    :type wallet_address: str
    :param nft_contract_addresses: List of contract addresses for NFTs.
    :type nft_contract_addresses: List
    :param minimum_owned_nfts: Number of NFTs that need to be owned to return
        True, default 1.
    :type minimum_owned_nfts: int
    :return: True if the wallet address owns at least 'minimum_owned_nfts' of
        the NFTs specified in the 'nft_contract_addresses.
    :rtype: bool
    """
    owned_nfts = account_nfts(wallet_address, nft_contract_addresses)
    unique_owned_nfts = unique_nft_contracts(owned_nfts)
    validate_owned_nfts = which_nfts_owned(unique_owned_nfts, nft_contract_addresses)
    if sum(validate_owned_nfts) >= minimum_owned_nfts:
        return True
    else:
        return False

def read_nft_spec(nft_contract_address_file: str) -> List:
    """JSON file under `nft_ownership` directory that contains the addresses
    of the contracts.

    :param nft_contract_address_files: Filename of the JSON file
    :type nft_contract_address_files: str
    :return: List contract addresses.
    :rtype: List
    """
    nft_contract_addresses = []
    with open(nft_contract_address_file, 'r') as f:
        data = json.loads(f.read())
        if 'contracts' in data:
            for contract in data['contracts'].keys():
                nft_contract_addresses.append(contract)

    return nft_contract_addresses
