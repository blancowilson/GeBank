import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal, getcontext
from datetime import datetime

# Set precision for Decimal calculations
getcontext().prec = 10

CONFIG_FILE_PATH = "config/tasas.json"

@dataclass
class TasaConfig:
    key: str            # e.g., "TASA_OFICIAL_VES_USD"
    label: str          # e.g., "Tasa BCV VES a USD"
    valor: Decimal      # Use Decimal for precision
    icon: str           # e.g., "currency_exchange"
    es_referencia_divisa: bool = False # If true, using this rate implies direct FX transaction
    moneda_origen: str = "VES"
    moneda_destino: str = "USD"
    fecha_vigencia: Optional[datetime] = None # For historical rates, if implemented

class TasaService:
    def __init__(self):
        self._tasas: List[TasaConfig] = [] # Initialize _tasas
        self._ensure_config_exists()
        self._load_config() # Call _load_config here to populate _tasas

    def _ensure_config_exists(self):
        if not os.path.exists("config"):
            os.makedirs("config")
        
        if not os.path.exists(CONFIG_FILE_PATH):
            default_config = [
                {
                    "key": "TASA_OFICIAL_VES_USD",
                    "label": "Tasa BCV VES a USD",
                    "valor": "35.50", # Stored as string, loaded as Decimal
                    "icon": "account_balance",
                    "es_referencia_divisa": False,
                    "moneda_origen": "VES",
                    "moneda_destino": "USD",
                    "fecha_vigencia": datetime.now().isoformat()
                },
                {
                    "key": "TASA_ALT_VES_USD",
                    "label": "USDT / Paralelo VES a USD",
                    "valor": "48.00", # Stored as string, loaded as Decimal
                    "icon": "currency_bitcoin",
                    "es_referencia_divisa": True,
                    "moneda_origen": "VES",
                    "moneda_destino": "USD",
                    "fecha_vigencia": datetime.now().isoformat()
                }
            ]
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(default_config, f, indent=4)
        
    def _load_config(self) -> List[TasaConfig]:
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                data = json.load(f)
                if not data: # Handle empty file case
                    self._tasas = []
                    return self._tasas
                
                # Convert valor to Decimal and fecha_vigencia to datetime
                loaded_tasas = []
                for item in data:
                    item['valor'] = Decimal(item['valor'])
                    if item.get('fecha_vigencia'):
                        item['fecha_vigencia'] = datetime.fromisoformat(item['fecha_vigencia'])
                    loaded_tasas.append(TasaConfig(**item))
                self._tasas = loaded_tasas
            return self._tasas
        except (json.JSONDecodeError, FileNotFoundError, KeyError, ValueError) as e:
            print(f"Error loading or parsing {CONFIG_FILE_PATH}: {e}. Reinitializing with default config.")
            self._tasas = []
            if os.path.exists(CONFIG_FILE_PATH):
                os.remove(CONFIG_FILE_PATH) # Remove malformed file
            self._ensure_config_exists() # Recreate default
            return self._load_config() # Try loading again


    def get_all(self) -> List[TasaConfig]:
        return self._tasas

    def get_by_key(self, key: str) -> Optional[TasaConfig]:
        for t in self._tasas:
            if t.key == key:
                return t
        return None

    def get_tasa(self, fecha: datetime, moneda_origen: str, moneda_destino: str) -> Optional[TasaConfig]:
        """
        Retrieves the most appropriate exchange rate for a given date and currency pair.
        For now, returns the latest configured rate as historical data is not implemented.
        """
        # In future, implement historical lookup based on fecha
        # For now, return the latest rate matching the currency pair
        for t in sorted(self._tasas, key=lambda x: x.fecha_vigencia or datetime.min, reverse=True):
            if t.moneda_origen == moneda_origen and t.moneda_destino == moneda_destino:
                return t
        return None

    def validar_conversion(self, monto_origen: Decimal, monto_destino: Decimal, tasa_a_validar: Decimal, tolerancia: Decimal = Decimal("0.01")) -> bool:
        """
        Validates if an amount in the origin currency, when converted using the provided rate,
        approximately matches the amount in the destination currency within a tolerance.
        """
        if tasa_a_validar == 0:
            return False # Avoid division by zero

        monto_convertido = monto_origen / tasa_a_validar
        return abs(monto_convertido - monto_destino) <= tolerancia
    
    def update_tasa(self, key: str, nuevo_valor: Decimal, label: str = None, icon: str = None):
        """
        Updates an existing tasa's value.
        Note: This currently overwrites the latest rate, no historical tracking.
        """
        updated = False
        for t in self._tasas:
            if t.key == key:
                t.valor = nuevo_valor
                if label: t.label = label
                if icon: t.icon = icon
                t.fecha_vigencia = datetime.now() # Update effective date
                updated = True
                break
        
        if updated:
            with open(CONFIG_FILE_PATH, 'w') as f:
                # Convert Decimal back to string for JSON serialization
                # Convert datetime to ISO format string
                serializable_tasas = []
                for t in self._tasas:
                    t_dict = asdict(t)
                    t_dict['valor'] = str(t_dict['valor'])
                    if t_dict.get('fecha_vigencia'):
                        t_dict['fecha_vigencia'] = t_dict['fecha_vigencia'].isoformat()
                    serializable_tasas.append(t_dict)
                json.dump(serializable_tasas, f, indent=4)
        else:
            raise ValueError(f"Tasa with key '{key}' not found.")
