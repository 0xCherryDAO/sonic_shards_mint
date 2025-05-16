import random
from typing import Optional

from loguru import logger

from config import RETRIES, PAUSE_BETWEEN_RETRIES
from src.models.contracts import ClaimData
from src.utils.common.wrappers.decorators import retry
from src.utils.proxy_manager import Proxy
from src.utils.request_client.curl_cffi_client import CurlCffiClient
from src.utils.user.account import Account


class Claimer(Account, CurlCffiClient):
    def __init__(self, private_key: str, proxy: Proxy | None):
        Account.__init__(self, private_key=private_key, proxy=proxy)
        CurlCffiClient.__init__(self, proxy=proxy)

    def __str__(self) -> str:
        return f'[{self.wallet_address}] | Minting shard...'

    async def get_proof(self) -> Optional[list[str]]:
        headers = {
            'accept': '*/*',
            'accept-language': 'fr-FR,fr;q=0.9',
            'priority': 'u=1, i',
            'referer': 'https://shards.soniclabs.com/',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        response_json, status = await self.make_request(
            method="GET",
            url=f'https://shards.soniclabs.com/api/proof/{self.wallet_address}',
            headers=headers
        )
        if status == 200:
            return response_json['message']

    @retry(retries=RETRIES, delay=PAUSE_BETWEEN_RETRIES, backoff=1.5)
    async def claim(self):
        balance = await self.get_wallet_balance(is_native=True)
        if balance == 0:
            logger.error(f'[{self.wallet_address}] | Native balance is 0.')
            return None

        contract = self.web3.eth.contract(
            address=ClaimData.address,
            abi=ClaimData.abi
        )

        proof = await self.get_proof()
        if not proof:
            logger.error(f'[{self.wallet_address}] | Failed to get proof for address.')
            return None

        try:
            last_block = await self.web3.eth.get_block('latest')
            max_priority_fee_per_gas = await self.web3.eth.max_priority_fee
            base_fee = int(last_block['baseFeePerGas'] * 1.15)
            max_fee_per_gas = base_fee + max_priority_fee_per_gas

            tx = await contract.functions.mintNft(
                proof,
                random.choice([1, 2, 3])
            ).build_transaction({
                'value': 0,
                'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
                'from': self.wallet_address,
                "maxPriorityFeePerGas": max_priority_fee_per_gas,
                "maxFeePerGas": max_fee_per_gas,
            })

            tx_hash = await self.sign_transaction(tx)
            confirmed = await self.wait_until_tx_finished(tx_hash)

            if confirmed:
                logger.success(
                    f'[{self.wallet_address}] | Successfully minted shard | TX: https://sonicscan.org/tx/{tx_hash}')
                return True
        except Exception as ex:
            if 'address has already minted' in str(ex):
                logger.warning(f'[{self.wallet_address}] | This address has already minted.')
                return True
