from dataclasses import dataclass


@dataclass
class ERC20:
    abi: str = open('./assets/abi/erc20.json', 'r').read()


@dataclass
class ClaimData:
    address: str = '0xE9b1ab504A60Ed64Bd9646b062705B0404Eb4c81'
    abi: str = open('./assets/abi/claim.json', 'r').read()


@dataclass
class UpgradeData:
    address: str = '0x3561607590e28e0848ba3B67074C676D6D1C9953'
    abi: str = open('./assets/abi/upgrade.json', 'r').read()
