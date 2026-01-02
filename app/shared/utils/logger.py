import sys
import os
from loguru import logger

def setup_logging():
    # Remover el logger por defecto
    logger.remove()

    # Directorio de logs
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configurar salida a consola
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )

    # Configurar salida a archivo rotativo
    logger.add(
        os.path.join(log_dir, "app.log"),
        rotation="10 MB",
        retention="1 month",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO"
    )

    # Log de errores crítico
    logger.add(
        os.path.join(log_dir, "errors.log"),
        rotation="10 MB",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True
    )

    return logger

# Inicializar al importar
setup_logging()
