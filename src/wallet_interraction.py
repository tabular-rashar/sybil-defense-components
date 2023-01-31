import json
from typing import List

from .utils.alchemy import account_transfers

def count_interractions(transfers: List, addresses: List[str]) -> int:
    """Find if any of the addresses in the 'transfers' list is in the
    'addresses' list.

    :param transfers: List of transactions that transfer tokens between addresses.
    :type transfers: List
    :param addresses: List of addresses that might be in the transfers list.
    :type addresses: List[str]
    :return: Number of times at least one of the addresses was found in the
        transfers list.
    :rtype: int
    """

    # turn addresses into lowercase characters for comparisson uniformity
    addresses = [s.lower() for s in addresses]

    count = 0
    for t in transfers:
        if t['from'].lower() in addresses or t['to'].lower() in addresses:
            count += 1
    return count

def read_interraction_spec(address_file: str) -> List:
    """Loads the data from the 'address_file' and returns a list of the
    contract addresses.

    :param address_files: File with addresses that the wallet might have
        interracted with.
    :type address_files: str
    :return: List of all the contract addresses
    :rtype: List
    """
    addresses_list = []

    with open(address_file, 'r') as f:
        data = json.loads(f.read())
        if 'contracts' in data:
            for contract in data['contracts'].keys():
                addresses_list.append(contract)
        if 'addresses' in data:
            for address in data['addresses'].keys():
                addresses_list.append(address)

    return addresses_list

def is_associated_with_addresses(wallet_address: str,
                                 addresses_list: List[str]) -> bool:
    """Retrive the transfers of the 'wallet_address'  and returns True if the
    'wallet_address' has interracted with any of addresses in the
    addresses_list.

    :param wallet_address: The address of the wallet.
    :type wallet_address: str
    :param mixer_address_file: List of files with addresses that the wallet
        might have interracted with.
    :type mixer_address_file: str
    :return: True if the wallet address has interracted with any of the
        addresses in the address_files.
    :rtype: bool
    """

    transfers = account_transfers(wallet_address, direction='to')
    transfers.extend(account_transfers(wallet_address, direction='from'))

    if count_interractions(transfers, addresses_list) > 0:
        return True
    return False
