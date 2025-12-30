import logging
import json
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gebanksaint_audit.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("GeBankSaint.Audit")

class AuditEvent:
    """
    Representa un evento de negocio digno de ser auditado.
    """
    def __init__(
        self, 
        action: str, 
        user_id: str, 
        target_entity: str, 
        target_id: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS"
    ):
        self.timestamp = datetime.utcnow().isoformat()
        self.action = action
        self.user_id = user_id
        self.target_entity = target_entity
        self.target_id = target_id
        self.details = details or {}
        self.status = status

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "user_id": self.user_id,
            "target_entity": self.target_entity,
            "target_id": self.target_id,
            "details": self.details,
            "status": self.status
        }

    def to_json(self):
        return json.dumps(self.to_dict())

def log_audit_event(event: AuditEvent):
    """
    Registra el evento.
    TODO: En el futuro, esto guardará en la tabla 'audit_logs' de la BD.
    Por ahora, lo guarda en un log estructurado.
    """
    # Log estructurado para herramientas de monitoreo (Datadog, Kibana, etc.)
    logger.info(f"AUDIT_EVENT: {event.to_json()}")

def audit(action: str, target_entity: str):
    """
    Decorador para auditar automáticamente la ejecución de Casos de Uso.
    
    Uso:
    @audit(action="REGISTRAR_PAGO", target_entity="PAGO")
    def execute(self, params): ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Intentar obtener el usuario del contexto (simulado por ahora)
            # En el futuro, esto vendrá del Request o del token de sesión
            user_id = "system_admin" 
            
            try:
                result = func(*args, **kwargs)
                
                # Intentar extraer ID de la entidad si el resultado lo tiene
                target_id = None
                if isinstance(result, dict) and 'id' in result:
                    target_id = str(result['id'])
                elif hasattr(result, 'id'):
                    target_id = str(result.id)
                
                event = AuditEvent(
                    action=action,
                    user_id=user_id,
                    target_entity=target_entity,
                    target_id=target_id,
                    details={"args": str(args), "kwargs": str(kwargs)},
                    status="SUCCESS"
                )
                log_audit_event(event)
                return result
            
            except Exception as e:
                event = AuditEvent(
                    action=action,
                    user_id=user_id,
                    target_entity=target_entity,
                    details={"error": str(e)},
                    status="FAILURE"
                )
                log_audit_event(event)
                raise e
        return wrapper
    return decorator
