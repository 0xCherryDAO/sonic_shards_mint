MOBILE_PROXY = False  # True - мобильные proxy/False - обычные proxy
ROTATE_IP = False  # Настройка только для мобильных proxy

SONIC_RPC = 'https://sonic.drpc.org'  # https://chainlist.org/chain/146
FANTOM_RPC = 'https://fantom.drpc.org'  # https://chainlist.org/chain/250

TG_BOT_TOKEN = ''  # str ('2282282282:AAZYB35L2PoziKsri6RFPOASdkal-z1Wi_s')
TG_USER_ID = None  # int (22822822) or None

SHUFFLE_WALLETS = False
PAUSE_BETWEEN_WALLETS = [1, 2]
PAUSE_BETWEEN_MODULES = [1, 2]
RETRIES = 3  # Сколько раз повторять 'зафейленное' действие
PAUSE_BETWEEN_RETRIES = 15  # Пауза между повторами

BRIDGE = False  # FTM -> SONIC
RELAY_BRIDGE = False  # Настройка в RelayBridgeSettings
MINT_NFT = False  # https://shards.soniclabs.com/


class RelayBridgeSettings:
    from_chain = ['BASE', 'ARB', 'OP']
    to_chain = ['SONIC']

    amount = [0.001, 0.002]  # Кол-во ETH [от, до]
    use_percentage = False  # Использовать ли процент от баланса вместо amount
    bridge_percentage = [0.01, 0.01]  # Процент от баланса. 0.1 - это 10%, 0.27 - это 27% и т.д.
    min_s_balance = 10  # Минимальный баланс в сети SONIC. Если выше, то бридж сделан не будет.
