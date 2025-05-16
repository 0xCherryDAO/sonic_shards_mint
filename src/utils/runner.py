from loguru import logger

from src.bridge.upgrade_bridge import Bridge
from src.claimer.claim import Claimer
from src.models.route import Route


async def process_claim(route: Route):
    claimer = Claimer(
        private_key=route.wallet.private_key,
        proxy=route.wallet.proxy
    )
    logger.debug(claimer)

    return await claimer.claim()


async def process_bridge(route: Route):
    bridge = Bridge(
        private_key=route.wallet.private_key,
        proxy=route.wallet.proxy
    )
    logger.debug(bridge)

    return await bridge.bridge()
