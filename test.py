import unittest

from src.wallet_interraction import count_interractions, is_associated_with_addresses, \
                                read_interraction_spec
from src.nft_owneship import which_nfts_owned, minimum_owned_nfts

class AccountInterractionTests(unittest.TestCase):

    def test_account_has_not_interracted(self):
        transfers=[
            {
                'from': 'ABC',
                'to': 'CDF'
            },
            {
                'from': 'ABC',
                'to': 'GQL'
            },
            {
                'from': 'GQL',
                'to': 'ABC',

            }
        ]
        addresses=['ZZZ']
        self.assertEqual(count_interractions(transfers, addresses), 0)

    def test_account_has_interracted(self):
        transfers=[
            {
                'from': 'ABC',
                'to': 'CDF'
            },
            {
                'from': 'ABC',
                'to': 'gQl'
            },
            {
                'from': 'gQl',
                'to': 'ABC',

            }
        ]
        addresses=['GQL', 'AAA']
        self.assertEqual(count_interractions(transfers, addresses), 2)

    def test_account_has_interracted_with_tornado_cash(self):
        """Test that an address that has interracted with one of the Tornado
        Cash addresses returns true.

        WARNING: This test case makes API calls.
        """
        wallet_address = "0x36DD7b862746fdD3eDd3577c8411f1B76FDC2Af5"
        tornado_cash_addresses_file = './specfiles/money_mixer_addresses/tornado_addresses_ethereum.json'

        tornado_addresses = read_interraction_spec(tornado_cash_addresses_file)
        self.assertTrue(
            is_associated_with_addresses(wallet_address, tornado_addresses)
        )

class NFTOwnershipTests(unittest.TestCase):

    def test_which_nfts_owned_when_not_owning_nfts(self):
        owned_nfts = [
            '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',
            '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB'
        ]

        nft_contract_addresses =[
            '0x8a90cab2b38dba80c64b7734e58ee1db38b8992e',
            '0x23581767a106ae21c074b2276D25e5C3e136a68b'
        ]

        owned = which_nfts_owned(owned_nfts, nft_contract_addresses)
        for o in owned:
            self.assertFalse(o)

    def test_which_nfts_owned_when_owning_nfts(self):
        owned_nfts = [
            '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',
            '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB',
            '0x8a90cab2b38dba80c64b7734e58ee1db38b8992e',
            '0x23581767a106ae21c074b2276D25e5C3e136a68b'
        ]

        nft_contract_addresses =[
            '0x8a90cab2b38dba80c64b7734e58ee1db38b8992e',
            '0x23581767a106ae21c074b2276D25e5C3e136a68b'
        ]

        owned = which_nfts_owned(owned_nfts, nft_contract_addresses)
        for o in owned:
            self.assertTrue(o)

    def test_nft_ownership_is_above_minimum_when_it_is(self):
        """
        WARNING: This test case makes API calls.
        """

        nft_contract_addresses = [
            '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85'    # ENS
        ]

        is_over_minimum = minimum_owned_nfts('vitalik.eth', nft_contract_addresses, 1)
        self.assertTrue(is_over_minimum)

    def test_nft_ownership_is_above_minimum_when_it_is_not(self):
        """
        WARNING: This test case makes API calls.
        """

        nft_contract_addresses = [
            '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D'    # BAYC
        ]

        is_over_minimum = minimum_owned_nfts('vitalik.eth', nft_contract_addresses, 1)
        self.assertFalse(is_over_minimum)


if __name__ == '__main__':
    unittest.main()
