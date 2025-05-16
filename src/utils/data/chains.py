from config import SONIC_RPC, FANTOM_RPC


class Chain:
    def __init__(self, chain_id: int, rpc: str, scan: str, native_token: str) -> None:
        self.chain_id = chain_id
        self.rpc = rpc
        self.scan = scan
        self.native_token = native_token


SONIC = Chain(
    chain_id=146,
    rpc=SONIC_RPC,
    scan='https://sonicscan.org/tx',
    native_token='S'
)

FANTOM = Chain(
    chain_id=250,
    rpc=FANTOM_RPC,
    scan='https://explorer.fantom.network/transactions',
    native_token='FTM'
)

BASE = Chain(
    chain_id=8453,
    rpc='https://base.meowrpc.com',
    scan='https://basescan.org/tx',
    native_token='ETH'
)

OP = Chain(
    chain_id=10,
    rpc='https://optimism.drpc.org',
    scan='https://optimistic.etherscan.io/tx',
    native_token='ETH',
)

ARB = Chain(
    chain_id=42161,
    rpc='https://arbitrum.meowrpc.com',
    scan='https://arbiscan.io/tx',
    native_token='ETH',
)

SEPOLIA = Chain(
    chain_id=11155111,
    rpc='https://ethereum-sepolia-rpc.publicnode.com',
    scan='https://sepolia.etherscan.io/tx',
    native_token='ETH'  # sETH
)

chain_mapping = {
    'FANTOM': FANTOM,
    'BASE': BASE,
    'ARBITRUM ONE': ARB,
    'ARB': ARB,
    'OP': OP,
    'OPTIMISM': OP,
    'SEPOLIA': SEPOLIA
}
