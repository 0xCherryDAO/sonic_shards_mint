from src.utils.runner import *

module_handlers = {
    'BRIDGE': process_upgrade_bridge,
    'MINT_NFT': process_claim,
    'RELAY_BRIDGE': process_relay_bridge
}
