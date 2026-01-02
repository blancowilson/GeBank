# 📘 Guía de Arquitectura y Desarrollo: GeBankSaint

## 1. Visión General
GeBankSaint es un middleware de conciliación financiera diseñado como un sistema agnóstico que conecta un **Portal de Pagos Externo** (ej. Insytech) con un **ERP Interno** (ej. Saint, Profit). Su propósito es automatizar la validación de cobranzas reportadas contra movimientos bancarios reales antes de afectar la contabilidad oficial.

## 2. Arquitectura: Hexagonal (Ports & Adapters)
El sistema está desacoplado para permitir cambios en el ERP o el Portal sin afectar la lógica de negocio.

*   **Domain (Core):** Contiene las entidades (`GePagos`, `GeInstrumentos`), lógica pura y **Ports** (Interfaces de Repositorio).
*   **Application (Use Cases):** Orquesta los flujos de trabajo (ej. `ConciliarPagoUseCase`).
*   **Infrastructure (Adapters):** Implementaciones técnicas:
    *   `saint/`: Adaptadores para el ERP Saint.
    *   `parsers/`: Lógica de lectura de estados de cuenta (Excel/CSV).
    *   `repositories/`: Implementaciones de persistencia y configuración.
*   **Presentation:** Rutas de FastAPI (`api/` para sistemas, `web/` para humanos) y plantillas **HTMX** para interactividad moderna.

## 3. Procesamiento y Background Tasks
El sistema está diseñado para manejar grandes volúmenes de datos sin bloquear la interfaz de usuario.

### Modos de Ejecución (Celery Fallback):
El sistema soporta dos modos de ejecución configurables mediante `USE_CELERY` en el entorno:
1.  **Modo Asíncrono (Celery + Redis):** Recomendado para producción. La conciliación se delega a un worker, permitiendo al usuario seguir navegando. La interfaz usa **HTMX Polling** para actualizar el estado automáticamente cuando la tarea termina.
2.  **Modo Síncrono (Fallback):** Ejecuta la lógica directamente en la petición HTTP. Útil para entornos de desarrollo, pruebas unitarias o instalaciones donde no se desea mantener una infraestructura de Redis/Celery.

## 4. Lógica del Motor de Conciliación (The Brain)
El motor no concilia "pagos" completos, sino **instrumentos individuales** para permitir pagos compuestos (ej. un pago reportado que incluye una parte en Zelle y otra en Efectivo).

### Flujo de Procesamiento:
1.  **Traducción de Entidades:** Consulta el `BankMappingRepository` para convertir el código del portal (ej. "04") al código contable del ERP (ej. "110103").
2.  **Enrutamiento por Naturaleza:**
    *   **Caja/Efectivo (`is_cash=True`):** Omite la búsqueda en bancos y lo marca para verificación manual o aprobación por reglas de caja física. Este flujo bypassea el Staging y permite la persistencia directa en el libro de caja del ERP una vez validado.
3.  **Normalización de Moneda:**

## 4. Persistencia y Consistencia
El sistema garantiza que los cambios en el ERP y el Portal ocurran de manera coordinada.
*   **Aprobación Final:** Solo cuando todos los instrumentos de un pago son validados (vía Match o Caja), se procede a la persistencia final en las tablas de CxC (`SAACXC`) y Bancos (`SBTRAN`) del ERP.
*   **Atocimidad (En Desarrollo):** Se está trabajando en asegurar que las transacciones complejas (grandes volúmenes de documentos) se procesen bajo una sola transacción de base de datos para evitar estados parciales.

## 5. Agnosticismo y Escalabilidad

### Configuración Global (`SystemConfig`)
El sistema se adapta a diferentes entornos financieros mediante parámetros en base de datos:
*   `BASE_CURRENCY` / `REF_CURRENCY`: Define qué moneda manda (ej. USD vs VES).
*   `RATE_OPERATOR`: Define la matemática de conversión (`Base * Tasa = Ref` o `Ref / Tasa = Base`).
*   `TASA_SOURCE`: Permite alternar entre leer tasas de un archivo `JSON` o de la tabla `ExchangeRates` en DB.

### Cómo añadir un nuevo ERP (ej. Profit)
1.  Crear `app/infrastructure/profit/`.
2.  Implementar las interfaces definidas en `app/domain/repositories/` (ej. `IERPTransactionRepository`).
3.  Actualizar la inyección de dependencias en las rutas correspondientes.

## 5. Estándares Técnicos
*   **Interactividad:** Se prefiere HTMX sobre JavaScript pesado para mantener la lógica en el servidor.
*   **Logging:** Uso estricto de `loguru`. Revisar `logs/errors.log` para trazas detalladas.
*   **Persistencia:** SQLAlchemy 2.0 asíncrono.
*   **Seguridad de Datos:** Nunca usar `scripts/DANGEROUS_reset_db.py` en producción. Usar scripts de parche para alterar esquemas existentes.
