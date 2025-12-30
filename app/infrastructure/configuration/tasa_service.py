import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal

CONFIG_FILE_PATH = "config/tasas.json"

@dataclass
class TasaConfig:
    key: str           # "TASA_OFICIAL", "TASA_ALT"
    label: str         # "Tasa BCV", "USDT"
    valor: float       # 45.50, 52.00
    icon: str          # "currency_exchange", "account_balance_wallet"
    es_referencia_divisa: bool = False # Si true, usar esta tasa equivale a pagar en divisa

class TasaService:
    def __init__(self):
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not os.path.exists("config"):
            os.makedirs("config")
        
        if not os.path.exists(CONFIG_FILE_PATH):
            default_config = [
                {
                    "key": "TASA_OFICIAL",
                    "label": "Tasa BCV",
                    "valor": 35.50,
                    "icon": "account_balance",
                    "es_referencia_divisa": False
                },
                {
                    "key": "TASA_ALT",
                    "label": "USDT / Paralelo",
                    "valor": 48.00,
                    "icon": "currency_bitcoin",
                    "es_referencia_divisa": True
                }
            ]
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(default_config, f, indent=4)

    def get_all(self) -> List[TasaConfig]:
        with open(CONFIG_FILE_PATH, 'r') as f:
            data = json.load(f)
            return [TasaConfig(**item) for item in data]

    def get_by_key(self, key: str) -> Optional[TasaConfig]:
        tasas = self.get_all()
        for t in tasas:
            if t.key == key:
                return t
        return None

    def update_tasa(self, key: str, nuevo_valor: float, label: str = None, icon: str = None):
        tasas = self.get_all()
        updated = False
        for t in tasas:
            if t.key == key:
                t.valor = nuevo_valor
                if label: t.label = label
                if icon: t.icon = icon
                updated = True
                break
        
        if updated:
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump([asdict(t) for t in tasas], f, indent=4)
