import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from loguru import logger

from src.database.base_models.pydantic_manager import DataBaseManagerConfig
from src.database.models import WorkingWallets, WalletsTasks
from src.database.utils.db_manager import DataBaseUtils
from config import *


async def clear_database(engine) -> None:
    async with AsyncSession(engine) as session:
        async with session.begin():
            for model in [WorkingWallets, WalletsTasks]:
                await session.execute(delete(model))
            await session.commit()
    logger.info("The database has been cleared")


async def generate_database(
        engine,
        private_keys: list[str],
        proxies: list[str],
) -> None:
    await clear_database(engine)

    tasks = []
    if BRIDGE: tasks.append('BRIDGE')
    if MINT_NFT: tasks.append('MINT_NFT')
    if RELAY_BRIDGE: tasks.append('RELAY_BRIDGE')

    has_bridge = 'BRIDGE' in tasks
    has_relay_bridge = 'RELAY_BRIDGE' in tasks

    proxy_index = 0
    for private_key in private_keys:
        other_tasks = [
            task for task in tasks if
            task not in ['BRIDGE', 'RELAY_BRIDGE']
        ]
        random.shuffle(other_tasks)

        tasks = (
                (['BRIDGE'] if has_bridge else []) +
                (['RELAY_BRIDGE'] if has_relay_bridge else []) +
                other_tasks
        )

        proxy = proxies[proxy_index]
        proxy_index = (proxy_index + 1) % len(proxies)

        proxy_url = None
        change_link = ''

        if proxy:
            if MOBILE_PROXY:
                proxy_url, change_link = proxy.split('|')
            else:
                proxy_url = proxy

        db_utils = DataBaseUtils(
            manager_config=DataBaseManagerConfig(
                action='working_wallets'
            )
        )

        await db_utils.add_to_db(
            private_key=private_key,
            proxy=f'{proxy_url}|{change_link}' if MOBILE_PROXY else proxy_url,
            status='pending',
        )

        for task in tasks:
            db_utils = DataBaseUtils(
                manager_config=DataBaseManagerConfig(
                    action='wallets_tasks'
                )
            )
            await db_utils.add_to_db(
                private_key=private_key,
                status='pending',
                task_name=task
            )
