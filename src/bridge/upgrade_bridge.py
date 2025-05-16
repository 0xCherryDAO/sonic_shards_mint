from asyncio import sleep
from typing import Optional

from loguru import logger

from config import RETRIES, PAUSE_BETWEEN_RETRIES
from src.models.contracts import UpgradeData
from src.utils.common.wrappers.decorators import retry
from src.utils.data.chains import chain_mapping
from src.utils.proxy_manager import Proxy
from src.utils.user.account import Account


class Bridge(Account):
    def __init__(
            self,
            private_key: str,
            proxy: Proxy | None
    ):
        self.proxy = proxy
        super().__init__(private_key=private_key, proxy=proxy, rpc=chain_mapping["FANTOM"].rpc)

    def __str__(self) -> str:
        return f'[{self.wallet_address}] | Bridging FTM -> SONIC...'

    @retry(retries=RETRIES, delay=PAUSE_BETWEEN_RETRIES, backoff=1.5)
    async def bridge(self) -> Optional[bool]:
        native_balance = await self.get_wallet_balance(is_native=True)
        if native_balance / 10 ** 18 < 1:
            logger.error(f'[{self.wallet_address}] | FTM balance is lower than 1.')
            return None

        contract = self.load_contract(
            address=UpgradeData.address,
            web3=self.web3,
            abi=UpgradeData.abi
        )
        to_chain_account = Account(private_key=self.private_key, proxy=self.proxy)
        balance_before_bridge = await to_chain_account.get_wallet_balance(is_native=True)

        amount = int(native_balance * 0.95)
        fee = await contract.functions.depositFee().call()
        tx = await contract.functions.deposit(
            fee
        ).build_transaction({
            'value': amount,
            'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
            'from': self.wallet_address,
            'gasPrice': int(await self.web3.eth.gas_price * 1.15)
        })
        gas_limit = await self.web3.eth.estimate_gas(tx)
        tx.update({'value': int(native_balance - (gas_limit * await self.web3.eth.gas_price * 1.25))})

        tx_hash = await self.sign_transaction(tx)
        confirmed = await self.wait_until_tx_finished(tx_hash)

        if confirmed:
            logger.success(
                f'[{self.wallet_address}] | Successfully bridged FTM -> SONIC | TX: https://explorer.fantom.network/transactions/{tx_hash}'
            )
            await self.wait_for_bridge(to_chain_account, balance_before_bridge)
            return True

    async def wait_for_bridge(self, to_chain_account: Account, balance_before_bridge: int):
        logger.debug(f'[{self.wallet_address}] | Waiting for S to arrive in chain Sonic...')
        while True:
            current_balance = await to_chain_account.get_wallet_balance(is_native=True)
            if current_balance > balance_before_bridge:
                logger.success(f'[{self.wallet_address}] | S has arrived!')
                break
            await sleep(5)
