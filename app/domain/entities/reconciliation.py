from dataclasses import dataclass
from typing import List, Optional, Union
from decimal import Decimal
from app.domain.entities.pago_insytech import GePagos, GeInstrumentos
from app.domain.entities.staging_transaction import StagingTransaction

@dataclass
class MatchResult:
    """Represents the result of trying to match a single financial instrument."""
    instrumento: GeInstrumentos
    staging_txn: Optional[StagingTransaction] = None
    converted_amount_usd: Optional[Decimal] = None
    match_found: bool = False
    details: str = "Pending"

@dataclass
class ReconciliationResult:
    """Contains the overall result for a complete payment packet (GePago)."""
    pago: GePagos
    instrument_matches: List[MatchResult]
    
    @property
    def is_fully_reconciled(self) -> bool:
        """A payment is fully reconciled if all its financial instruments are matched."""
        return all(match.match_found for match in self.instrument_matches)
