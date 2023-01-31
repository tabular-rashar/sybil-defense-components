from pathlib import Path

from fastapi import FastAPI

from src.farmer import is_account_farmer, wallet_balances, read_farmer_spec
from src.wallet_interraction import is_associated_with_addresses, read_interraction_spec
from src.nft_owneship import read_nft_spec, minimum_owned_nfts, nft_ownership_from_list

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Navigate to '/docs' path to interact with the API's GUI"}

@app.get("/farmer/totalview/{wallet_address}/{spec_file}")
async def root(wallet_address: str, spec_file: str):

    file_path = Path(f'./specfiles/farmer/{spec_file}')
    if not file_path.is_file():
        return {"error": "There is no such spec file"}

    spec = read_farmer_spec(file_path)
    balances = wallet_balances(wallet_address)

    return {"is_farmer": is_account_farmer(**balances, **spec)}

@app.get("/interraction/{wallet_address}/{spec_file}")
async def root(wallet_address: str, spec_file: str):

    file_path = Path(f'./specfiles/interractions/{spec_file}')
    if not file_path.is_file():
        return {"error": "There is no such spec file"}

    spec = read_interraction_spec(file_path)

    return {
        "is_associated_with": is_associated_with_addresses(wallet_address, spec)
    }

@app.get("/money-mixer/{wallet_address}")
async def root(wallet_address: str):

    file_path = Path(f'./specfiles/money_mixer_addresses/tornado_addresses_ethereum.json')
    if not file_path.is_file():
        return {"error": "There is no such spec file"}

    contract_addresses = read_interraction_spec(file_path)

    return {
        "interracted_with_money_mixers": is_associated_with_addresses(wallet_address, contract_addresses)
    }

@app.get("/min-nft-ownership/{wallet_address}/{spec_file}/{minimum_owned}")
async def root(wallet_address: str, spec_file: str, minimum_owned: int):

    file_path = Path(f'./specfiles/nft_ownership/{spec_file}')
    if not file_path.is_file():
        return {"error": "There is no such spec file"}

    nft_addresses = read_nft_spec(file_path)

    if minimum_owned == 1:
        message = 'is_at_least_1_nft_owned'
    else:
        message = f'are_at_least_{minimum_owned}_owned'

    return {
        message: minimum_owned_nfts(wallet_address, nft_addresses, minimum_owned)
    }

