# 🗺️ Roadmap de Implementación GeBankSaint

Este documento describe el progreso de alto nivel del proyecto. Para el seguimiento detallado de tareas y sprints, consulte el [Conductor de Tracks](./conductor/tracks.md).

## Estado de las Fases

### ✅ Fase 0: Infraestructura y Base [Completado]
Configuración de la arquitectura hexagonal, FastAPI, HTMX y conexiones base a SQL Server y Redis.

### ✅ Fase 1: Módulo Core de CXC (Saint) [Completado]
Implementación de la lectura de clientes y facturas directamente desde el ERP Saint.

### ✅ Fase 2: Integración Insytech y Motor Base [Completado]
Ingestión de paquetes de pago desde el portal externo y lógica de matching básica.

### 🔄 Fase 3: Motor Avanzado, Configuración y Agnósticismo [En Progreso]
Refactorización para permitir que el sistema sea independiente del ERP/Portal, gestión multimoneda y conciliación manual detallada.
- [x] Sprint 3.1: Configuración Global y Arquitectura Agnóstica.
- [x] Sprint 3.2: Mapeo dinámico de Bancos (Portal <-> ERP).
- [x] Sprint 3.3: Workspace de Conciliación Manual (Split View).
- [ ] **Sprint 3.4: Virtual Cash & Final Persistence** (Refinando persistencia atómica).

### ⏳ Fase 4: Integridad Transaccional y Resiliencia [Siguiente]
Implementación de patrones Unit of Work y mecanismos de recuperación ante fallos.

### ⏳ Fase 5: Reportes y Comisiones [Pendiente]
Cálculo de comisiones de vendedores y Dashboard ejecutivo.

### ⏳ Fase 6: Seguridad y Despliegue [Pendiente]
Autenticación, roles de usuario y optimización para producción.

---

## Metodología de Trabajo
El proyecto utiliza **Hexagonal Architecture** para garantizar la mantenibilidad y **HTMX** para una experiencia de usuario ágil. El desarrollo se divide en "Tracks" que se encuentran en el directorio `conductor/`.
