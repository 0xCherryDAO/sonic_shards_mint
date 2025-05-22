import random
from asyncio import sleep
from typing import Optional, List, Dict

from loguru import logger

from config import RelayBridgeSettings
from src.bridge.bridge_factory import RelayBridge
from src.bridge.upgrade_bridge import Bridge
from src.claimer.claim import Claimer
from src.models.bridge import BridgeConfig
from src.models.chain import Chain
from src.models.route import Route
from src.models.token import Token
from src.utils.data.chains import chain_mapping
from src.utils.proxy_manager import Proxy
from src.utils.request_client.curl_cffi_client import CurlCffiClient
from src.utils.user.account import Account


async def process_claim(route: Route):
    claimer = Claimer(
        private_key=route.wallet.private_key,
        proxy=route.wallet.proxy
    )
    logger.debug(claimer)

    return await claimer.claim()


async def process_upgrade_bridge(route: Route):
    bridge = Bridge(
        private_key=route.wallet.private_key,
        proxy=route.wallet.proxy
    )
    logger.debug(bridge)

    return await bridge.bridge()


async def check_if_eligible(route: Route) -> tuple[bool, str]:
    request_client = CurlCffiClient(proxy=route.wallet.proxy)
    account = Account(private_key=route.wallet.private_key, proxy=route.wallet.proxy)
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
    response_json, status = await request_client.make_request(
        method="GET",
        url=f'https://shards.soniclabs.com/api/proof/{account.wallet_address}',
        headers=headers
    )
    if status == 200:
        proof = response_json['message']
        if not proof:
            return False, account.wallet_address
        return True, account.wallet_address
    return False, account.wallet_address


async def process_relay_bridge(route: Route) -> Optional[bool]:
    eligible, address = await check_if_eligible(route)
    if not eligible:
        logger.warning(f'[{address}] | Account is not eligible. No need to bridge.')
        return None
    chains = RelayBridgeSettings.from_chain
    balances = await get_balances_for_chains(
        chains,
        route.wallet.private_key,
        route.wallet.proxy
    )
    from_chain = max(balances, key=balances.get)
    to_chain = RelayBridgeSettings.to_chain
    if isinstance(to_chain, list):
        to_chain = random.choice(to_chain)

    if to_chain == "SONIC":
        sonic_account = Account(
            private_key=route.wallet.private_key,
            rpc=chain_mapping['SONIC'].rpc,
            proxy=route.wallet.proxy
        )
        s_balance = await sonic_account.get_wallet_balance(is_native=True)
        if s_balance / 10 ** 18 >= RelayBridgeSettings.min_s_balance:
            logger.debug(
                f'[{sonic_account.wallet_address}] | В сети Sonic уже есть {round((s_balance / 10 ** 18), 5)} S. '
                f'Бридж не требуется.'
            )
            return True

    amount = random.uniform(RelayBridgeSettings.amount[0], RelayBridgeSettings.amount[1])
    use_percentage = RelayBridgeSettings.use_percentage
    bridge_percentage = RelayBridgeSettings.bridge_percentage

    super_bridge = RelayBridge(
        private_key=route.wallet.private_key,
        proxy=route.wallet.proxy,
        bridge_config=BridgeConfig(
            from_chain=Chain(
                chain_name=from_chain,
                native_token=chain_mapping[from_chain.upper()].native_token,
                rpc=chain_mapping[from_chain.upper()].rpc,
                chain_id=chain_mapping[from_chain.upper()].chain_id
            ),
            to_chain=Chain(
                chain_name=to_chain,
                native_token=chain_mapping[to_chain.upper()].native_token,
                rpc=chain_mapping[to_chain.upper()].rpc,
                chain_id=chain_mapping[to_chain.upper()].chain_id
            ),
            from_token=Token(
                chain_name=from_chain,
                name=chain_mapping[from_chain].native_token,
            ),
            to_token=Token(
                chain_name=to_chain,
                name=chain_mapping[to_chain].native_token,
            ),
            amount=amount,
            use_percentage=use_percentage,
            bridge_percentage=bridge_percentage
        )
    )

    logger.debug(super_bridge)
    bridged = await super_bridge.bridge()
    if bridged:
        return True


async def get_balances_for_chains(
        chains: List[str],
        private_key: str,
        proxy: Proxy | None = None
) -> Dict[str, int]:
    balances = {}

    for chain_name in chains:
        rpc = chain_mapping[chain_name].rpc
        account = Account(private_key=private_key, rpc=rpc, proxy=proxy)
        wallet_address = account.wallet_address

        while True:
            try:
                balance = await account.web3.eth.get_balance(wallet_address)
                break
            except Exception as ex:
                logger.info(f'Не удалось проверить баланс | {ex}')
                await sleep(2)
        balances[chain_name] = balance

    return balances
