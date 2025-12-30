from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, case, and_, literal_column, Float
from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.entities.cliente import Cliente
from app.domain.value_objects.monto import Monto, Moneda
from app.infrastructure.database.models import SaClie, SaAcxc
from decimal import Decimal

class SaintClienteRepository(ClienteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_risk_score_subquery(self):
        """
        Builds the subquery to calculate the risk score for each client
        based on their pending accounts receivable (SAACXC).
        """
        datediff_expr = func.datediff(literal_column("day"), SaAcxc.FechaV, func.getdate())

        risk_score_logic = case(
            (datediff_expr <= 0, 1.0),
            (and_(datediff_expr > 0, datediff_expr <= 15), 1.5),
            (and_(datediff_expr > 15, datediff_expr <= 30), 2.0),
            else_=3.0
        )

        subquery = (
            select(
                SaAcxc.CodClie,
                (
                    func.sum(SaAcxc.Saldo * risk_score_logic) / 
                    func.cast(func.sum(SaAcxc.Saldo), Float)
                ).label("score_riesgo")
            )
            .where(
                SaAcxc.Saldo > 0,
                SaAcxc.TipoCXC.in_(['10', '20']) # 10=Factura, 20=Nota de Débito
            )
            .group_by(SaAcxc.CodClie)
            .subquery()
        )
        return subquery

    async def _fetch_clients_with_risk_score(
        self, sort_by: str = "score_riesgo", order: str = "desc", search_query: Optional[str] = None, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Tuple], int]:
        risk_score_subquery = self._get_risk_score_subquery()
        
        base_join = SaClie.__table__.outerjoin(
            risk_score_subquery, SaClie.CodClie == risk_score_subquery.c.CodClie
        )

        where_clause = None
        if search_query:
            where_clause = or_(
                SaClie.Descrip.ilike(f"%{search_query}%"),
                SaClie.ID3.ilike(f"%{search_query}%"),
                SaClie.CodClie.ilike(f"%{search_query}%")
            )

        count_stmt = select(func.count(SaClie.CodClie)).select_from(base_join)
        if where_clause is not None:
            count_stmt = count_stmt.where(where_clause)
            
        total_count_result = await self.session.execute(count_stmt)
        total_count = total_count_result.scalar_one()

        query_columns = [
            SaClie.CodClie, SaClie.Descrip, SaClie.ID3, SaClie.Saldo, SaClie.Activo,
            func.isnull(risk_score_subquery.c.score_riesgo, 1.0).label("score_riesgo")
        ]
        
        final_stmt = select(*query_columns).select_from(base_join)
        
        if where_clause is not None:
            final_stmt = final_stmt.where(where_clause)

        sort_map = {
            "score_riesgo": literal_column("score_riesgo"), "deuda": SaClie.Saldo,
            "codigo": SaClie.CodClie, "nombre": SaClie.Descrip,
        }
        sort_column = sort_map.get(sort_by, SaClie.Saldo)

        final_stmt = final_stmt.order_by(sort_column.desc() if order == "desc" else sort_column.asc())
        final_stmt = final_stmt.offset(skip).limit(limit)

        result = await self.session.execute(final_stmt)
        return result.all(), total_count

    async def obtener_todos(self, skip: int = 0, limit: int = 20, sort_by: str = "score_riesgo", order: str = "desc") -> Tuple[List[Cliente], int]:
        client_data, total_count = await self._fetch_clients_with_risk_score(sort_by=sort_by, order=order, skip=skip, limit=limit)
        return [self._map_to_domain(c) for c in client_data], total_count

    async def obtener_por_id(self, cliente_id: str) -> Optional[Cliente]:
        stmt = select(SaClie).where(SaClie.CodClie == cliente_id)
        result = await self.session.execute(stmt)
        sa_cliente = result.scalar_one_or_none()
        if not sa_cliente:
            return None
        return self._map_to_domain_simple(sa_cliente)

    async def buscar_por_nombre(self, query: str, skip: int = 0, limit: int = 20, sort_by: str = "score_riesgo", order: str = "desc") -> Tuple[List[Cliente], int]:
        client_data, total_count = await self._fetch_clients_with_risk_score(sort_by=sort_by, order=order, search_query=query, skip=skip, limit=limit)
        return [self._map_to_domain(c) for c in client_data], total_count
    
    
    def _map_to_domain_simple(self, sa_cliente: SaClie) -> Cliente:
        # Simplified mapper without risk score
        return Cliente(
            id=sa_cliente.CodClie,
            descripcion=sa_cliente.Descrip,
            rif=sa_cliente.ID3,
            saldo_usd=Monto(valor=sa_cliente.Saldo or Decimal("0.00"), moneda=Moneda.USD),
            activo=sa_cliente.Activo == 1
        )

    def _map_to_domain(self, client_data: Tuple) -> Cliente:
        cod_clie, descrip, id3, saldo, activo, score_riesgo = client_data
        
        score_riesgo = float(score_riesgo) if score_riesgo is not None else 1.0
        
        if score_riesgo <= 1.0:
            medicion = "Buena"
        elif score_riesgo < 1.5:
            medicion = "Regular"
        else:
            medicion = "Critica"

        return Cliente(
            id=cod_clie,
            descripcion=descrip,
            rif=id3,
            saldo_usd=Monto(valor=saldo or Decimal("0.00"), moneda=Moneda.USD),
            score_riesgo=score_riesgo,
            medicion_deuda=medicion,
            activo=activo == 1
        )
