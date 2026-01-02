from typing import List, Optional
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import json
import os
from pydantic import BaseModel
from app.domain.repositories.config_repository import IConfigRepository

class TasaConfig(BaseModel):
    key: str = ""
    label: str = ""
    icon: str = "currency_exchange"
    moneda_origen: str
    moneda_destino: str
    tasa: Decimal
    valor: Decimal # Alias for tasa for compatibility with template
    fecha_vigencia: Optional[datetime] = None
    tipo: str = "OFICIAL"
    es_referencia_divisa: bool = False

from app.infrastructure.database.models import ExchangeRate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import asdict

class TasaService:
    def __init__(self, config_repo: Optional[IConfigRepository] = None, session: Optional[AsyncSession] = None):
        self._tasas: List[TasaConfig] = []
        self.config_repo = config_repo
        self.session = session
        self._load_config()

    def _load_config(self):
        json_path = "config/tasas.json"
        if not os.path.exists(json_path):
            return
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                self._tasas = []
                for item in data:
                    # Infer type from key if possible
                    rate_type = "OFICIAL"
                    key = item.get('key', '').upper()
                    if "ALT" in key or "PARALELO" in key:
                        rate_type = "PARALELO"
                    
                    val = Decimal(str(item['valor']))
                    self._tasas.append(TasaConfig(
                        key=item.get('key', ''),
                        label=item.get('label', ''),
                        icon=item.get('icon', 'currency_exchange'),
                        moneda_origen=item['moneda_origen'],
                        moneda_destino=item['moneda_destino'],
                        tasa=val,
                        valor=val,
                        fecha_vigencia=datetime.fromisoformat(item['fecha_vigencia']) if item.get('fecha_vigencia') else None,
                        tipo=rate_type,
                        es_referencia_divisa=item.get('es_referencia_divisa', False)
                    ))
        except Exception as e:
            print(f"Error cargando tasas desde JSON: {e}")

    async def get_tasa(self, fecha: datetime, moneda_origen: str, moneda_destino: str, tipo: str = "OFICIAL") -> Optional[TasaConfig]:
        """
        Retrieves the most appropriate exchange rate for a given date, currency pair, and type.
        Supports both JSON and DATABASE sources based on config.
        """
        source = "JSON"
        if self.config_repo:
            source = await self.config_repo.get_config("TASA_SOURCE") or "JSON"

        if source == "DATABASE" and self.session:
            stmt = select(ExchangeRate).where(
                ExchangeRate.moneda_origen == moneda_origen,
                ExchangeRate.moneda_destino == moneda_destino,
                ExchangeRate.fecha <= fecha,
                ExchangeRate.tipo_tasa == tipo
            ).order_by(ExchangeRate.fecha.desc()).limit(1)
            
            result = await self.session.execute(stmt)
            db_rate = result.scalar_one_or_none()
            if db_rate:
                return TasaConfig(
                    moneda_origen=db_rate.moneda_origen,
                    moneda_destino=db_rate.moneda_destino,
                    tasa=db_rate.tasa,
                    fecha_vigencia=db_rate.fecha,
                    tipo=db_rate.tipo_tasa
                )

        # Fallback/Default to JSON
        for t in sorted(self._tasas, key=lambda x: x.fecha_vigencia or datetime.min, reverse=True):
            if t.moneda_origen == moneda_origen and t.moneda_destino == moneda_destino and t.tipo == tipo:
                if t.fecha_vigencia is None or t.fecha_vigencia <= fecha:
                    return t
        
        # Last resort fallback: If specific type not found, try any rate? 
        # For now, strict matching.
        return None

    async def validar_conversion(
        self, 
        monto_origen: Decimal, 
        monto_destino: Decimal, 
        tasa_a_validar: Decimal, 
        tolerancia: Optional[Decimal] = None
    ) -> bool:
        """
        Valida si la conversión entre dos montos usando una tasa dada es correcta
        según el operador configurado (MULTIPLY o DIVIDE).
        La tolerancia se lee de la configuración si no se proporciona.
        """
        # 1. Obtener el operador y tolerancia de la configuración
        operador = "MULTIPLY"
        tol_config = Decimal("0.01")
        
        if self.config_repo:
            operador = await self.config_repo.get_config("RATE_OPERATOR") or "MULTIPLY"
            if tolerancia is None:
                tol_str = await self.config_repo.get_config("RECONCILIATION_TOLERANCE")
                tol_config = Decimal(tol_str) if tol_str else Decimal("0.01")
        
        target_tol = tolerancia if tolerancia is not None else tol_config

        if operador == "MULTIPLY":
            calculado = (monto_origen * tasa_a_validar).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            calculado = (monto_origen / tasa_a_validar).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        diferencia = abs(calculado - monto_destino)
        return diferencia <= target_tol

    async def convertir_a_base(self, monto_ref: Decimal, tasa: Decimal) -> Decimal:
        """
        Convierte un monto de moneda referencial a moneda base.
        """
        operador = "MULTIPLY"
        if self.config_repo:
            operador = await self.config_repo.get_config("RATE_OPERATOR") or "MULTIPLY"

        if operador == "MULTIPLY":
            # Si Base * Tasa = Ref, entonces Base = Ref / Tasa
            return (monto_ref / tasa).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            # Si Base / Tasa = Ref, entonces Base = Ref * Tasa
            return (monto_ref * tasa).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def update_tasa(self, key: str, nuevo_valor: Decimal, label: str = None, icon: str = None, es_referencia_divisa: bool = None):
        """
        Updates an existing tasa's value.
        Note: This currently overwrites the latest rate, no historical tracking.
        """
        updated = False
        for t in self._tasas:
            if t.key == key:
                t.tasa = nuevo_valor
                t.valor = nuevo_valor # Sync alias
                if label: t.label = label
                if icon: t.icon = icon
                if es_referencia_divisa is not None:
                    t.es_referencia_divisa = es_referencia_divisa
                
                t.fecha_vigencia = datetime.now() # Update effective date
                updated = True
                break
        
        if updated:
            json_path = "config/tasas.json"
            with open(json_path, 'w') as f:
                # Serialize list of Pydantic models
                serializable_tasas = []
                for t in self._tasas:
                    t_dict = t.model_dump()
                    # Convert types for JSON
                    t_dict['valor'] = str(t_dict['valor'])
                    t_dict['tasa'] = str(t_dict['tasa']) # Redundant but kept for safety
                    if t_dict.get('fecha_vigencia'):
                        t_dict['fecha_vigencia'] = t_dict['fecha_vigencia'].isoformat()
                    serializable_tasas.append(t_dict)
                json.dump(serializable_tasas, f, indent=4)
        else:
            raise ValueError(f"Tasa with key '{key}' not found.")
