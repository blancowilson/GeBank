# SISTEMA INTEGRAL DE INTEGRACIÓN Y VALIDACIÓN DE COBRANZAS
## Plan de Acción Técnico - Monolito Modular Hexagonal

**Versión:** 2.0  
**Fecha:** Diciembre 2025  
**Ubicación:** Venezuela  
**Estado:** Documento de Arquitectura y Planificación  
**Equipo:** 2 Desarrolladores Full-Stack

---

## TABLA DE CONTENIDOS
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Cambios Arquitectónicos Clave](#cambios-arquitectónicos-clave)
3. [Arquitectura Hexagonal del Monolito](#arquitectura-hexagonal-del-monolito)
4. [Stack Tecnológico Final](#stack-tecnológico-final)
5. [Priorización de Funcionalidades](#priorización-de-funcionalidades)
6. [Estructura del Proyecto](#estructura-del-proyecto)
7. [Plan de Desarrollo - Sprints Optimizados](#plan-de-desarrollo---sprints-optimizados)
8. [Casos de Uso Priorizados](#casos-de-uso-priorizados)
9. [Integración con Saint ERP](#integración-con-saint-erp)
10. [Métricas de Éxito](#métricas-de-éxito)

---

## RESUMEN EJECUTIVO

### Cambio de Estrategia: De Microservicios a Monolito Modular

**Razones del cambio:**
- ✅ **Equipo pequeño (2 personas)**: No justifica la complejidad operativa de microservicios
- ✅ **Transaccionalidad ACID**: Operaciones de conciliación requieren consistencia garantizada
- ✅ **Rendimiento**: Todo en memoria, sin latencia de red entre servicios
- ✅ **Simplicidad de deployment**: Un solo proceso, una sola base de datos
- ✅ **Desarrollo más rápido**: Sin necesidad de coordinar APIs entre servicios

### Arquitectura Elegida: Monolito Modular Hexagonal

```
┌─────────────────────────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                    │
│                  SSL/TLS, Static Files, Cache               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              UVICORN (ASGI Server - 4 workers)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI APPLICATION                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           PRESENTATION LAYER (UI)                     │  │
│  │  • Jinja2 Templates (SSR)                             │  │
│  │  • HTMX (Partial updates)                             │  │
│  │  • Tailwind CSS (Styling)                             │  │
│  │  • Alpine.js (Minimal JS when needed)                 │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│  ┌───────────────────────▼───────────────────────────────┐  │
│  │           APPLICATION LAYER (Use Cases)               │  │
│  │  • ConciliarPagoUseCase                               │  │
│  │  • ValidarPagoUseCase                                 │  │
│  │  • CalcularComisionesUseCase                          │  │
│  │  • GenerarReporteUseCase                              │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│  ┌───────────────────────▼───────────────────────────────┐  │
│  │              DOMAIN LAYER (Business Logic)            │  │
│  │  • Entities: Pago, Factura, Cliente, Comision        │  │
│  │  • Value Objects: Monto, Moneda, Referencia           │  │
│  │  • Domain Services: MatchingService, CXCService       │  │
│  │  • Business Rules (Pure Python)                       │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│  ┌───────────────────────▼───────────────────────────────┐  │
│  │        INFRASTRUCTURE LAYER (Adapters)                │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  SAINT ADAPTER (Anti-Corruption Layer)          │  │  │
│  │  │  • Traduce Domain ↔ Tablas Saint                │  │  │
│  │  │  • SBBANC, SBTRAN, SAACXC, SAFACT               │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  BANCO ADAPTER (File Parsing)                   │  │  │
│  │  │  • PDF Parser (pdfplumber)                      │  │  │
│  │  │  • Excel Parser (openpyxl)                      │  │  │
│  │  │  • TXT Parser (Provincial, Mercantil, etc)     │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  INSYTECH ADAPTER (Vendedor Data)               │  │  │
│  │  │  • API Client para reportes de vendedores       │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────┬────────────────────────────┬─────────────────┘
               │                            │
               ▼                            ▼
   ┌───────────────────────┐    ┌──────────────────────┐
   │  CELERY + REDIS       │    │   SQL SERVER         │
   │  (Background Tasks)   │    │   (Saint Database)   │
   │  • Parsing batch      │    │   • Schema Saint     │
   │  • Matching async     │    │   • Schema App       │
   │  • Reports generation │    │   • Transacciones    │
   └───────────────────────┘    └──────────────────────┘
```

---

## 1. Monolito Modular bajo Arquitectu Hexagonal

```
FastAPI Monolith (Single Process)
     ↓
  SQL Server (Shared with Saint)
     ↓
  Redis (Solo para Celery queues)
```

**Beneficios:**
- ✅ Una sola base de datos → Transacciones ACID nativas
- ✅ Sin latencia de red entre "servicios"
- ✅ Joins SQL directos entre tablas de Saint y App
- ✅ Deployment simplificado (1 servidor, no orquestación)

---

### 2. Frontend

```
FastAPI (Jinja2 Templates) + HTMX
     ↓
  Server-Side Rendering (SSR)
  Estado solo en backend
  HTML directo desde Python
```

**Beneficios:**
- ✅ Sin duplicación de lógica (validaciones en backend)
- ✅ Sin compilación de frontend (Tailwind CDN o build mínimo)
- ✅ SEO nativo (HTML completo desde inicio)
- ✅ Menor complejidad de deployment (no hay paso de build de Node)
- ✅ Hidratación instantánea con HTMX (sin JS framework pesado)

---

### 3. Capa Anticorrupción (ACL) para Saint

**Problema:** Saint tiene tablas con nombres crípticos (`SBBANC`, `SAACXC`) y lógica legacy.

**Solución:** Adapter Pattern que traduce entre tu dominio limpio y Saint.

**Ejemplo:**

```python
# domain/entities/pago.py (Tu código limpio)
class Pago:
    id: UUID
    cliente: Cliente
    monto: Monto  # Value Object con multimoneda
    fecha_pago: date
    estado: EstadoPago

# infrastructure/saint_adapter.py (Capa sucia que traduce)
class SaintPagoRepository:
    def guardar_pago(self, pago: Pago) -> None:
        # Traduce tu objeto limpio a las tablas de Saint
        with transaction():
            # INSERT en SBTRAN (Transacciones Bancarias)
            self.db.execute(
                "INSERT INTO SBBANC.SBTRAN (CodBanc, NOpe, ...) VALUES (...)"
            )
            # UPDATE en SAACXC (Cuentas por Cobrar)
            self.db.execute(
                "UPDATE SAACXC SET MontoCred = MontoCred + :monto WHERE ..."
            )
```

**Beneficio:** Si Saint cambia (o lo reemplazas), solo tocas el adapter. El dominio queda intacto.

---

## STACK TECNOLÓGICO FINAL

### Backend Core

```yaml
Framework: FastAPI 0.104+
  - Async/await nativo
  - Pydantic v2 (validación automática)
  - OpenAPI docs built-in
  - Dependency Injection

Templating: Jinja2 3.1+
  - Server-Side Rendering
  - Herencia de templates
  - Filtros custom
  - Macros reutilizables

Base de Datos: 
  SQL Server 2019+
    - Conexión vía pyodbc o asyncpg
    - SQLAlchemy ORM (opcional, recomendado para queries complejas)
    - Mismo servidor que Saint (schemas separados)

ORM/Query Builder:
  SQLAlchemy 2.0+ (Async)
    - Migrations con Alembic
    - Modelos separados de Entities del Domain
    - Repository pattern

Background Tasks:
  Celery 5.3+ + Redis 7+
    - Workers para parsing batch
    - Scheduled tasks (conciliación nocturna)
    - Priority queues

File Processing:
  - openpyxl (Excel)
  - pdfplumber (PDF parsing)
  - pandas (análisis de datos grandes)
```

### Frontend (SSR + Progressive Enhancement)

```yaml
Templates: Jinja2
  - Base layout con bloques
  - Componentes reutilizables (macros)
  - Partial templates para HTMX

Interactividad: HTMX 1.9+
  - hx-get, hx-post para actualizaciones parciales
  - hx-swap para reemplazar DOM
  - hx-trigger para eventos custom
  - SSE (Server-Sent Events) para actualizaciones en tiempo real

Estilos: Tailwind CSS 3.3+
  - CDN para desarrollo rápido
  - Build minificado para producción
  - Plugins: forms, typography

Minimal JS: Alpine.js 3.13+ (opcional)
  - Solo para interacciones locales (dropdowns, modales)
  - Sin framework pesado
  - < 15KB gzipped

Iconos: Material Symbols (Google)
  - CDN, sin dependencias
```

### Infrastructure

```yaml
Web Server: Nginx 1.24+
  - Reverse proxy a Uvicorn
  - Static files (CSS/JS)
  - SSL/TLS termination
  - Gzip compression

ASGI Server: Uvicorn 0.24+
  - 4 workers (1 por core CPU)
  - --proxy-headers
  - Graceful shutdown

Deployment:
  Opción 1: Docker Compose (Desarrollo/Staging)
    - Service: app (FastAPI + Uvicorn)
    - Service: celery-worker
    - Service: redis
    - Service: nginx
  
  Opción 2: Systemd (Producción Linux)
    - Unit file para FastAPI
    - Unit file para Celery
    - Nginx configura upstream

Monitoring:
  - Prometheus + Grafana (métricas)
  - Sentry (errores)
  - Logs: structlog → journald/file
```

---

## PRIORIZACIÓN DE FUNCIONALIDADES

### Prioridad 1: Módulo de Cuentas por Cobrar (CXC) 🔴

**Razón:** Es el core del negocio. Todo gira alrededor de validar pagos contra facturas pendientes.

#### Funcionalidades Críticas:
1. **Visualización de CXC por Cliente**
   - Listar facturas pendientes o notas de debitos (desde `SAACXC TIPOCXC=10` de Saint)
   - Cálculo de saldo pendiente con multimoneda (VES/USD)
   - Antigüedad de deuda (0-30, 31-60, 61-90, 90+ días)

2. **Registro de Pagos (Manual y desde Insytech)**
   - Form para registrar pago manual
   - Validación de monto contra factura
   - Manejo de pagos parciales
   - Sincronización con Insytech (API vendedores)

3. **Conciliación de Pagos con Estados de Cuenta**
   - Upload de archivo bancario
   - Matching automático (3 niveles: exacto, fuzzy, manual)
   - Validación de referencia bancaria
   - Actualización de `SAACXC` en Saint

4. **Cálculo de Comisiones (Multimoneda)**
   - Comisiones por vendedor
   - No mezclar VES con USD
   - Reporte de comisiones pagadas/pendientes

---

### Prioridad 2: Módulo de Bancos (Soporte para Conciliación) 🟡

#### Funcionalidades:
1. **Gestión de Cuentas Bancarias**
   - CRUD de bancos (tabla `SBBANC` en Saint)
   - Saldo actual por cuenta
   - Historial de movimientos

2. **Procesamiento de Estados de Cuenta**
   - Parser multi-formato (TXT Provincial, Excel Mercantil, PDF Banesco)
   - Normalización de datos bancarios
   - Detección de duplicados

3. **Transacciones Bancarias**
   - Registro de depósitos/egresos (tabla `SBTRAN`)
   - Validación contable (debe = haber)
   - Asientos contables automáticos

---

### Prioridad 3: Reportes y Dashboard 🟢

#### Funcionalidades:
1. **Dashboard Principal**
   - KPIs: Total CXC, Pagos del mes, Conciliaciones pendientes
   - Gráficos (Chart.js o ApexCharts integrados con HTMX)

2. **Reportes Exportables**
   - Estado de CXC por cliente (Excel/PDF)
   - Comisiones de vendedores (Excel)
   - Movimientos bancarios (filtros avanzados)

---

## ESTRUCTURA DEL PROYECTO

```
saint-bank-monolith/
│
├── app/
│   ├── main.py                    # Entry point FastAPI
│   ├── config.py                  # Settings (Pydantic BaseSettings)
│   │
│   ├── domain/                    # 🏛️ CAPA DE DOMINIO (Business Logic Pura)
│   │   ├── entities/
│   │   │   ├── pago.py           # Entidad Pago
│   │   │   ├── factura.py        # Entidad Factura
│   │   │   ├── cliente.py        # Entidad Cliente
│   │   │   ├── comision.py       # Entidad Comisión
│   │   │   └── banco.py          # Entidad Banco
│   │   │
│   │   ├── value_objects/
│   │   │   ├── monto.py          # Value Object con multimoneda
│   │   │   ├── moneda.py         # Enum (VES, USD)
│   │   │   ├── referencia.py     # Referencia bancaria
│   │   │   └── estado_pago.py    # Enum de estados
│   │   │
│   │   ├── services/
│   │   │   ├── matching_service.py      # Algoritmo de matching
│   │   │   ├── comision_service.py      # Cálculo de comisiones
│   │   │   └── conciliacion_service.py  # Lógica de conciliación
│   │   │
│   │   ├── repositories/         # Interfaces (Ports)
│   │   │   ├── pago_repository.py
│   │   │   ├── factura_repository.py
│   │   │   └── banco_repository.py
│   │   │
│   │   └── exceptions/
│   │       ├── pago_duplicado.py
│   │       └── monto_invalido.py
│   │
│   ├── application/               # 🎯 CASOS DE USO (Orquestación)
│   │   ├── use_cases/
│   │   │   ├── cxc/
│   │   │   │   ├── consultar_cxc_cliente.py
│   │   │   │   ├── registrar_pago.py
│   │   │   │   └── calcular_comisiones.py
│   │   │   ├── conciliacion/
│   │   │   │   ├── subir_estado_cuenta.py
│   │   │   │   ├── ejecutar_matching.py
│   │   │   │   └── aprobar_conciliacion.py
│   │   │   └── bancos/
│   │   │       ├── crear_transaccion.py
│   │   │       └── consultar_saldo.py
│   │   │
│   │   └── dto/                  # Data Transfer Objects
│   │       ├── pago_dto.py
│   │       └── factura_dto.py
│   │
│   ├── infrastructure/            # 🔌 ADAPTADORES (Implementaciones)
│   │   ├── saint/
│   │   │   ├── saint_pago_repository.py      # Traduce Pago → SBTRAN/SAACXC
│   │   │   ├── saint_factura_repository.py   # Lee SAACXC WHERE TIPOCXC=10
│   │   │   ├── saint_banco_repository.py     # Lee/Escribe SBBANC
│   │   │   └── mappers/                      # Mapeo Domain ↔ ORM
│   │   │       ├── pago_mapper.py
│   │   │       └── factura_mapper.py
│   │   │
│   │   ├── parsers/
│   │   │   ├── excel_parser.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── txt_parser.py                 # Provincial, Mercantil, etc
│   │   │   └── base_parser.py                # Interface
│   │   │
│   │   ├── insytech/
│   │   │   ├── insytech_client.py            # HTTP Client
│   │   │   └── insytech_mapper.py
│   │   │
│   │   ├── database/
│   │   │   ├── models.py                     # SQLAlchemy models (ORM)
│   │   │   ├── session.py                    # DB connection
│   │   │   └── migrations/                   # Alembic
│   │   │
│   │   └── tasks/
│   │       ├── celery_app.py
│   │       ├── conciliacion_task.py
│   │       └── reporte_task.py
│   │
│   ├── presentation/              # 🖥️ CAPA DE PRESENTACIÓN
│   │   ├── web/
│   │   │   ├── routes/
│   │   │   │   ├── cxc_routes.py             # Rutas de CXC
│   │   │   │   ├── bancos_routes.py
│   │   │   │   ├── conciliacion_routes.py
│   │   │   │   └── dashboard_routes.py
│   │   │   │
│   │   │   ├── templates/
│   │   │   │   ├── base.html                 # Layout principal
│   │   │   │   ├── components/
│   │   │   │   │   ├── navbar.html
│   │   │   │   │   ├── table.html            # Tabla reutilizable
│   │   │   │   │   └── modal.html
│   │   │   │   ├── cxc/
│   │   │   │   │   ├── listado.html
│   │   │   │   │   ├── detalle.html
│   │   │   │   │   └── registrar_pago.html
│   │   │   │   ├── bancos/
│   │   │   │   │   ├── listado.html
│   │   │   │   │   └── subir_estado.html
│   │   │   │   └── dashboard/
│   │   │   │       └── index.html
│   │   │   │
│   │   │   ├── forms/
│   │   │   │   ├── pago_form.py              # Pydantic Form validation
│   │   │   │   └── banco_form.py
│   │   │   │
│   │   │   └── dependencies.py               # FastAPI Depends injection
│   │   │
│   │   └── api/                              # API REST (opcional)
│   │       └── v1/
│   │           ├── cxc_api.py                # Endpoints JSON si necesitas
│   │           └── bancos_api.py
│   │
│   ├── shared/                    # 🛠️ UTILIDADES COMPARTIDAS
│   │   ├── utils/
│   │   │   ├── date_utils.py
│   │   │   ├── money_utils.py
│   │   │   └── string_utils.py
│   │   │
│   │   ├── exceptions/
│   │   │   └── base_exception.py
│   │   │
│   │   └── constants.py
│   │
│   └── tests/
│       ├── unit/
│       │   ├── domain/
│       │   └── application/
│       ├── integration/
│       │   └── infrastructure/
│       └── e2e/
│           └── web/
│
├── static/                        # Archivos estáticos
│   ├── css/
│   │   └── tailwind.min.css       # Build de producción
│   ├── js/
│   │   └── htmx.min.js
│   └── images/
│
├── alembic/                       # Migraciones de DB
│   ├── versions/
│   └── env.py
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
│
├── .env.example
├── pyproject.toml
└── README.md
```

---

## PLAN DE DESARROLLO - SPRINTS OPTIMIZADOS

### FASE 0: SETUP INICIAL (Semana 1)

**Sprint 0.1: Infraestructura Base (3 días)**

```
✅ Tareas:
[ ] Setup repositorio Git con estructura hexagonal
[ ] Configurar FastAPI con Jinja2
[ ] Configurar conexión a SQL Server (mismo de Saint)
[ ] Crear esquema separado en SQL Server: `AppConciliacion`
[ ] Setup Redis para Celery
[ ] Configurar Tailwind CSS (CDN + build script)
[ ] Setup HTMX (CDN)
[ ] Template base.html con navbar y layout

✅ Entregables:
- FastAPI ejecutándose en http://localhost:8000
- Jinja2 renderizando template base
- Conexión exitosa a SQL Server
- Redis funcionando

✅ Personas: 2 devs (pair programming)
```

**Sprint 0.2: Capa Anticorrupción de Saint (2 días)**

```
✅ Tareas:
[ ] Crear modelos SQLAlchemy para tablas Saint (read-only):
    - SBBANC (Bancos)
    - SBTRAN (Transacciones Bancarias)
    - SAFACT (Facturas)
    - SAACXC (Cuentas por Cobrar, Facturas, Notas de Credito y Debitos, anticipos, Retenciones de IVA e Impuesto sobre la renta)
    - SACLIE (Clientes)
[ ] Crear SaintAdapter base
[ ] Implementar SaintFacturaRepository (solo lectura)
[ ] Test de integración: Leer facturas de Saint

✅ Entregables:
- Adapter funcional que lee SAFACT Y SAACXC
- Test que muestra facturas en logs

✅ Personas: 1 dev backend
```

---

### FASE 1: MÓDULO CXC CORE (Semana 2-4)

**Sprint 1.1: Domain Layer - Entities CXC (3 días)**

```
✅ Tareas:
[ ] Crear entidades del dominio:
    - Cliente (id, nombre, rif, saldo_total)
    - Factura (id, numero, cliente, monto, saldo_pendiente, fecha_emision)
    - Pago (id, factura, monto, fecha_pago, referencia)
    - Monto (Value Object con moneda VES/USD)
[ ] Crear servicios de dominio:
    - CXCService: calcular_saldo_cliente()
    - CXCService: calcular_antiguedad_deuda()
[ ] Interfaces de repositorios (Ports)
[ ] Tests unitarios de lógica de negocio

✅ Entregables:
- Entidades con lógica pura (sin DB)
- Tests pasando al 100%

✅ Personas: 1 dev backend
```

**Sprint 1.2: Infrastructure - Saint CXC Adapter (3 días)**

```
✅ Tareas:
[ ] Implementar SaintFacturaRepository:
    - obtener_facturas_pendientes(cliente_id)
    - obtener_factura_por_id(factura_id)
[ ] Implementar SaintPagoRepository:
    - guardar_pago(pago) → INSERT SAACXC + UPDATE saldo
[ ] Mappers: Domain Entity ↔ SQLAlchemy Model
[ ] Tests de integración con DB real (test database)

✅ Entregables:
- Repositorios funcionando contra Saint
- Transacciones ACID en SQL Server

✅ Personas: 1 dev backend
```

**Sprint 1.3: Application Layer - Use Cases CXC (2 días)**

```
✅ Tareas:
[ ] Caso de Uso: ConsultarCXCClienteUseCase
    Input: cliente_id
    Output: Lista de facturas pendientes con saldos
[ ] Caso de Uso: RegistrarPagoUseCase
    Input: factura_id, monto, referencia, fecha
    Output: Pago registrado
    Validaciones: Monto no excede saldo, factura existe
[ ] DTOs (Data Transfer Objects) para pasar datos entre capas

✅ Entregables:
- Use Cases testados con mocks

✅ Personas: 1 dev backend
```

**Sprint 1.4: Presentation Layer - UI CXC (4 días)**

```
✅ Tareas:
[ ] Ruta FastAPI: GET /cxc/clientes → Listar clientes con saldo
[ ] Template: cxc/listado_clientes.html
    - Tabla con clientes
    - Columna: Saldo Pendiente (VES y USD separados)
    - HTMX: Click en fila → carga detalle en modal
[ ] Ruta FastAPI: GET /cxc/cliente/{id}/facturas → Detalle facturas
[ ] Template: cxc/detalle_facturas.html (partial para HTMX)
    - Tabla de facturas con antigüedad (0-30, 31-60, etc)
    - Botón "Registrar Pago" por factura
[ ] Ruta FastAPI: GET /cxc/pago/form/{factura_id} → Form de pago
[ ] Ruta FastAPI: POST /cxc/pago/registrar → Guardar pago
[ ] Template: cxc/form_pago.html (modal con HTMX)
    - Campos: Monto, Referencia, Fecha
    - Validación client-side con Alpine.js (opcional)
    - Submit con HTMX → Actualiza tabla sin reload

✅ Entregables:
- UI funcional para consultar CXC
- Registro de pago manual funcionando
- Todo renderizado server-side

✅ Personas: 
- 1 dev fullstack (rutas + templates)
- 1 dev frontend (Tailwind styling + HTMX)
```

---

### FASE 2: INTEGRACIÓN INSYTECH (Semana 5)

**Sprint 2.1: Adapter Insytech (3 días)**

```
✅ Tareas:
[ ] Crear InsytechClient (HTTP client con httpx)
[ ] Endpoint: obtener_pagos_reportados(vendedor_id, fecha_desde)
[ ] Mapear datos de Insytech → Domain Pago
[ ] Celery Task: sincronizar_pagos_insytech()
    - Se ejecuta cada hora
    - Trae pagos nuevos y crea registros en estado "Pendiente Validación"

✅ Entregables:
- Sincronización automática con Insytech
- Pagos visibles en tabla de validación

✅ Personas: 1 dev backend
```

**Sprint 2.2: UI Validación de Pagos Insytech (2 días)**

```
✅ Tareas:
[ ] Ruta: GET /cxc/pagos-pendientes → Tabla de pagos por validar
[ ] Template: cxc/validacion_pagos.html
    - Tabla con: Vendedor, Cliente, Monto, Banco, Referencia, Estado
    - Checkbox para selección múltiple
    - Botón "Validar Seleccionados"
[ ] Ruta: POST /cxc/pagos/validar → Aprobar pagos
    - Validación: Verifica que referencia no esté duplicada
    - Actualiza Saint (SAACXC) vía adapter

✅ Entregables:
- Flujo completo de validación funcionando
- Actualización en Saint en tiempo real

✅ Personas: 1 dev fullstack
```

---

### FASE 3: MÓDULO BANCOS Y CONCILIACIÓN (Semana 6-8)

**Sprint 3.1: Gestión de Bancos (3 días)**

```
✅ Tareas:
[ ] Entidad Domain: Banco (codigo, nombre, cuenta, saldo_actual)
[ ] SaintBancoRepository: Leer/Escribir SBBANC
[ ] Ruta: GET /bancos → Listado de bancos
[ ] Ruta: GET /bancos/{id}/movimientos → Transacciones del banco
[ ] Templates: bancos/listado.html, bancos/detalle.html

✅ Personas: 1 dev fullstack
```

**Sprint 3.2: Parseo de Estados de Cuenta (5 días)**

```
✅ Tareas:
[ ] Crear BancoParser (interface)
[ ] Implementar:
    - ProvincialTxtParser (formato TXT específico)
    - MercantilExcelParser (Excel)
    - GenericPdfParser (pdfplumber)
[ ] Normalización: Todos los parsers retornan MovimientoBancario[]
[ ] Ruta: POST /bancos/subir-estado → Upload archivo
[ ] Celery Task: procesar_estado_cuenta(archivo_id)
    - Ejecuta parser apropiado
    - Guarda en tabla intermedia: `MovimientosBancarios`
    - Detecta duplicados (referencia + fecha)

✅ Entregables:
- 3 parsers funcionando
- Archivos procesados en background
- Notificación vía HTMX cuando termina

✅ Personas: 
- 1 dev backend (parsers)
- 1 dev fullstack (UI upload)
```

**Sprint 3.3: Motor de Conciliación (6 días)**

```
✅ Tareas:
[ ] MatchingService (Domain Service):
    - matching_exacto(pago, movimientos) → score 99%
        - Monto ==, Fecha ==, Referencia contiene cliente
    - matching_fuzzy(pago, movimientos) → score 80-95%
        - Monto ± 0.01%, Fecha ± 3 días, Fuzzy string matching
    - matching_por_rango(pago, movimientos) → score 70-80%
[ ] ConciliarPagoUseCase:
    Input: pago_id
    Logic: Ejecuta 3 niveles de matching
    Output: Sugerencias ordenadas por score
[ ] Celery Task: conciliacion_batch()
    - Se ejecuta a las 3 AM
    - Procesa todos los pagos "Pendiente Conciliación"
    - Si score > 95% → Concilia automáticamente
    - Si score 80-95% → Deja en "Revisión Manual"
[ ] Ruta: GET /conciliacion/pendientes → Dashboard de conciliación
[ ] Template: conciliacion/dashboard.html
    - Split view: Izquierda pagos, Derecha movimientos sugeridos
    - HTMX: Click "Conciliar" → Asocia y actualiza estado

✅ Entregables:
- Matching automático funcionando
- UI para revisar y aprobar manualmente
- Notificación de resultados

✅ Personas: 
- 2 devs (algoritmo complejo, requiere pair programming)
```

---

### FASE 4: COMISIONES Y REPORTES (Semana 9-10)

**Sprint 4.1: Cálculo de Comisiones (4 días)**

```
✅ Tareas:
[ ] ComisionService (Domain):
    - calcular_comision_vendedor(vendedor_id, mes, año)
    - Regla: VES y USD separados
    - Regla: % comisión por tipo de pago (Zelle, efectivo, etc)
[ ] Ruta: GET /comisiones/vendedor/{id} → Reporte de comisiones
[ ] Template: comisiones/reporte.html
    - Tabla: Cliente, Monto Pago (VES/USD), Comisión Calculada
    - Total por vendedor
    - Botón "Exportar Excel"
[ ] Celery Task: generar_reporte_comisiones(mes, año)
    - Usa openpyxl para crear Excel
    - Guarda en MinIO/S3 o filesystem
    - Retorna URL de descarga

✅ Entregables:
- Cálculo de comisiones preciso
- Reporte visual y exportable

✅ Personas: 1 dev fullstack
```

**Sprint 4.2: Dashboard y Reportes Generales (3 días)**

```
✅ Tareas:
[ ] Ruta: GET /dashboard → Vista principal
[ ] Template: dashboard/index.html
    - KPIs: Total CXC (VES/USD), Pagos del mes, Pendientes de validar
    - Gráficos con Chart.js integrados vía HTMX:
        - Evolución de CXC últimos 6 meses
        - Top 10 clientes con mayor deuda
    - Tabla "Actividad Reciente" (últimos pagos)
[ ] Ruta: GET /reportes/cxc-general → Exportar Excel
[ ] Ruta: GET /reportes/movimientos-bancarios → Exportar Excel

✅ Entregables:
- Dashboard funcional
- Exportación de reportes

✅ Personas: 
- 1 dev fullstack (dashboard)
- 1 dev backend (exportaciones)
```

---

### FASE 5: AUTENTICACIÓN Y PERMISOS (Semana 11)

**Sprint 5.1: Auth con Saint (3 días)**

```
✅ Tareas:
[ ] Ruta: POST /auth/login
    - Valida contra tabla SSUSRS de Saint
    - Genera JWT (con FastAPI-Users o JWT manual)
    - Cookie httpOnly para sesión
[ ] Middleware de autenticación
[ ] Proteger rutas sensibles (Depends(current_user))
[ ] Ruta: GET /auth/logout
[ ] Template: auth/login.html (simple, sin navbar)

✅ Entregables:
- Sistema de login funcional
- Sesión persistente

✅ Personas: 1 dev backend
```

**Sprint 5.2: Permisos Basados en SSPARM (2 días)**

```
✅ Tareas:
[ ] Leer permisos de SSPARM (tabla de permisos Saint)
[ ] Dependency Injection: require_permission(modulo=801, param=31)
[ ] Ocultar botones en UI si no tiene permiso (Jinja2 conditional)
[ ] Ejemplo: Botón "Eliminar Pago" solo visible si SSPARM permite

✅ Entregables:
- Permisos granulares funcionando

✅ Personas: 1 dev backend
```

---

### FASE 6: TESTING Y DEPLOYMENT (Semana 12)

**Sprint 6.1: Testing Exhaustivo (3 días)**

```
✅ Tareas:
[ ] Tests unitarios (Pytest):
    - Domain layer (entidades, servicios)
    - Application layer (use cases con mocks)
[ ] Tests de integración:
    - Repositorios contra DB de prueba
    - Parsers con archivos de muestra
[ ] Tests E2E (Playwright):
    - Flujo: Login → Ver CXC → Registrar pago
    - Flujo: Subir estado → Conciliar automático
[ ] Cobertura mínima: 75%

✅ Personas: 2 devs (pair testing)
```

**Sprint 6.2: Deployment y Monitoring (2 días)**

```
✅ Tareas:
[ ] Dockerfile optimizado (multi-stage build)
[ ] docker-compose.yml con:
    - Service: app (FastAPI + Uvicorn)
    - Service: celery-worker
    - Service: celery-beat (scheduled tasks)
    - Service: redis
    - Service: nginx
[ ] Setup Nginx como reverse proxy
[ ] SSL/TLS con Let's Encrypt (Certbot)
[ ] Configurar Sentry para errores
[ ] Logs estructurados (structlog → journald)
[ ] Backup automático de SQL Server (script)
[ ] Documentación de deployment

✅ Entregables:
- Sistema en producción
- Monitoring activo

✅ Personas: 1 dev DevOps
```

---

## CASOS DE USO PRIORIZADOS

### CU-1: Consultar CXC por Cliente (Prioridad 1)

```yaml
ACTOR: Contador/Admin
FLUJO:
1. Usuario navega a /cxc/clientes
2. Sistema renderiza tabla con clientes (Jinja2)
3. Usuario busca cliente (HTMX auto-search)
4. Usuario hace click en fila de cliente
5. HTMX: hx-get="/cxc/cliente/{id}/facturas" hx-target="#detalle-modal"
6. Sistema ejecuta ConsultarCXCClienteUseCase
7. Renderiza partial template con facturas pendientes
8. Muestra saldos en VES y USD separados
9. Muestra antigüedad de deuda (0-30, 31-60 días)

VALIDACIONES:
- Cliente debe existir en Saint (SACLIE)
- Saldos calculados en tiempo real desde SAACXC
```

### CU-2: Registrar Pago Manual (Prioridad 1)

```yaml
ACTOR: Contador/Admin
FLUJO:
1. Desde detalle de cliente, click "Registrar Pago" en factura
2. HTMX abre modal: hx-get="/cxc/pago/form/{factura_id}"
3. Form renderizado con:
   - Monto (prellenado con saldo pendiente)
   - Referencia bancaria (input text)
   - Fecha (date picker)
   - Banco (dropdown de SBBANC)
4. Usuario llena y hace submit
5. HTMX: hx-post="/cxc/pago/registrar" hx-swap="outerHTML"
6. Sistema valida:
   - Monto <= saldo pendiente
   - Fecha no futura
   - Referencia no duplicada
7. Ejecuta RegistrarPagoUseCase
8. Adapter actualiza SAACXC en Saint (transacción ACID)
9. Retorna partial template actualizado (tabla de facturas)
10. HTMX reemplaza tabla sin page reload
11. Muestra toast "Pago registrado exitosamente"

VALIDACIONES:
- Monto > 0 y <= saldo_pendiente
- Referencia única (no existe en SAACXC)
- Factura en estado "Pendiente"
```

### CU-3: Conciliación Automática (Prioridad 1)

```yaml
ACTOR: Sistema (Celery Beat Task - 3 AM diaria)
FLUJO:
1. Celery ejecuta conciliacion_batch()
2. Obtiene pagos en estado "Pendiente Conciliación" (últimos 7 días)
3. Obtiene movimientos bancarios sin asociar (últimos 7 días)
4. Por cada pago:
   a. Ejecuta MatchingService.matching_exacto()
      - Monto == exacto
      - Fecha == exacta
      - Referencia contiene NIF cliente o nombre
      → Score 99%
   b. Si no match exacto, ejecuta matching_fuzzy()
      - Monto ± $0.01 o 0.01%
      - Fecha ± 3 días
      - Fuzzy string match en descripción (ratio > 0.85)
      → Score 85-95%
   c. Si no match fuzzy, ejecuta matching_por_rango()
      - Monto ± 0.5%
      - Fecha ± 7 días
      → Score 70-80%
5. Decisión:
   - Score > 95%: Concilia automáticamente
     - UPDATE SAACXC SET estado = 'CONCILIADO'
     - Asocia movimiento bancario
     - Notifica vía email/Slack
   - Score 80-95%: Marca "Revisión Manual"
     - Crea registro en tabla Sugerencias
     - Admin lo revisa en /conciliacion/pendientes
   - Score < 80%: No hace nada (espera intervención)
6. Registra resultado en tabla Auditoría
7. Envía reporte al email del contador:
   "Conciliación batch completada: 45 automáticas, 12 pendientes revisión"

VALIDACIONES:
- No duplicar conciliaciones (check unique constraint)
- Transacción ACID (rollback si falla)
```

### CU-4: Validar Pago de Insytech (Prioridad 2)

```yaml
ACTOR: Contador/Supervisor
FLUJO:
1. Usuario navega a /cxc/pagos-pendientes
2. Sistema muestra tabla con pagos reportados por vendedores
3. Filtros: Estado (Pendiente/Validado/Rechazado), Vendedor, Fecha
4. Usuario selecciona checkboxes de pagos a validar (HTMX checkbox)
5. Click "Validar Seleccionados"
6. HTMX: hx-post="/cxc/pagos/validar" hx-vals='{"ids": [...]}'
7. Sistema valida:
   - Referencias no duplicadas
   - Montos coherentes con facturas
   - Banco válido (existe en SBBANC)
8. Por cada pago válido:
   - Ejecuta RegistrarPagoUseCase
   - Actualiza Saint (SAACXC)
   - Marca pago como "Validado"
9. Retorna partial template con tabla actualizada
10. Muestra toast "3 pagos validados correctamente"

VALIDACIONES:
- Solo Admin/Supervisor puede validar (permiso SSPARM 801.31)
- Referencia única
- Cliente existe
```

### CU-5: Calcular Comisiones de Vendedor (Prioridad 2)

```yaml
ACTOR: Contador/Admin
FLUJO:
1. Usuario navega a /comisiones/vendedor/{id}?mes=10&año=2024
2. Sistema ejecuta ComisionService.calcular_comision_vendedor()
3. Query a SAACXC para obtener pagos del vendedor en ese período
4. Agrupa pagos por moneda:
   - Pagos en VES
   - Pagos en USD
5. Aplica % comisión según configuración:
   - Efectivo: 3%
   - Transferencia: 2.5%
   - Zelle: 1% (USD)
6. Calcula totales separados:
   - Comisión VES: $X
   - Comisión USD: $Y
7. Renderiza tabla con detalle por cliente
8. Botón "Exportar Excel"
9. Si click en exportar:
   - Celery task genera Excel con openpyxl
   - Guarda en /media/reportes/{vendedor_id}_{mes}.xlsx
   - Retorna URL de descarga
   - HTMX actualiza botón: "Descargar Excel"

VALIDACIONES:
- Vendedor debe tener pagos en ese período
- No mezclar VES y USD
- Comisión calculada solo sobre pagos "Validados"
```

---

## INTEGRACIÓN CON SAINT ERP

### Estrategia de Coexistencia

**Premisa:** Saint es el sistema master. Tu app es un complemento.

**Reglas:**
1. **Lectura:** Puedes leer todas las tablas de Saint (SELECT)
2. **Escritura:** Solo vía Adapter, con validaciones
3. **Esquemas separados:**
   - `dbo.SBBANC` (Saint) → No crear tablas ahí
   - `AppConciliacion.Conciliaciones` (Tu app) → Tablas propias

### Tablas Saint que Tocas

| Tabla Saint | Operación | Propósito |
|-------------|-----------|-----------|
| `SACLIE` | SELECT | Leer clientes |
| `SAFACT` | SELECT | Leer facturas pendientes |
| `SAACXC` | SELECT/UPDATE | Leer deudas, actualizar pagos |
| `SBBANC` | SELECT/INSERT/UPDATE | Bancos y saldos |
| `SBTRAN` | INSERT | Registrar transacciones bancarias |
| `SBDTRN` | INSERT | Detalle contable de transacciones |
| `SSUSRS` | SELECT | Autenticación |
| `SSPARM` | SELECT | Permisos |

### Ejemplo de Transacción Completa

```python
# application/use_cases/cxc/registrar_pago.py
class RegistrarPagoUseCase:
    """
    Registrar un pago y actualizarlo en Saint.
    Garantiza transacción ACID.
    """
    
    def __init__(
        self,
        pago_repository: PagoRepository,
        factura_repository: FacturaRepository,
        banco_repository: BancoRepository,
        db_session: AsyncSession
    ):
        self.pago_repo = pago_repository
        self.factura_repo = factura_repository
        self.banco_repo = banco_repository
        self.db = db_session
    
    async def execute(self, dto: RegistrarPagoDTO) -> PagoRegistrado:
        # 1. Validaciones de negocio
        factura = await self.factura_repo.obtener_por_id(dto.factura_id)
        if not factura:
            raise FacturaNoEncontrada(dto.factura_id)
        
        if dto.monto > factura.saldo_pendiente:
            raise MontoExcedeSaldo(dto.monto, factura.saldo_pendiente)
        
        # 2. Crear entidad de dominio
        pago = Pago.crear(
            factura=factura,
            monto=Monto(dto.monto, dto.moneda),
            referencia=Referencia(dto.referencia_bancaria),
            fecha_pago=dto.fecha,
            banco_id=dto.banco_id
        )
        
        # 3. Transacción ACID
        async with self.db.begin():
            # 3.1 Guardar en tabla propia
            await self.pago_repo.guardar(pago)
            
            # 3.2 Actualizar Saint (SAACXC)
            # El adapter traduce dominio → SQL de Saint
            await self.pago_repo.actualizar_cxc_saint(
                factura_id=factura.id,
                monto_abonado=pago.monto.valor
            )
            
            # 3.3 Si el pago es por transferencia, registrar en SBTRAN
            if dto.forma_pago == "transferencia":
                await self.banco_repo.registrar_transaccion(
                    banco_id=dto.banco_id,
                    monto=pago.monto.valor,
                    tipo="INGRESO",
                    referencia=dto.referencia_bancaria,
                    descripcion=f"Pago factura {factura.numero}"
                )
        
        # 4. Retornar DTO
        return PagoRegistrado(
            id=pago.id,
            factura_numero=factura.numero,
            monto=pago.monto.valor,
            nuevo_saldo=factura.saldo_pendiente - pago.monto.valor,
            fecha_registro=pago.created_at
        )
```

### Implementación del Adapter Saint

```python
# infrastructure/saint/saint_pago_repository.py
class SaintPagoRepository(PagoRepository):
    """
    Adapter que traduce operaciones de dominio
    a comandos SQL contra las tablas de Saint.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def guardar(self, pago: Pago) -> None:
        """Guarda en tu tabla propia (no en Saint)"""
        # INSERT en AppConciliacion.Pagos
        stmt = insert(PagoModel).values(
            id=pago.id,
            factura_id=pago.factura.id,
            monto=pago.monto.valor,
            moneda=pago.monto.moneda.value,
            referencia=pago.referencia.valor,
            fecha_pago=pago.fecha_pago,
            estado=pago.estado.value,
            created_at=datetime.utcnow()
        )
        await self.db.execute(stmt)
    
    async def actualizar_cxc_saint(
        self, 
        factura_id: str, 
        monto_abonado: Decimal
    ) -> None:
        """
        Actualiza la tabla SAACXC de Saint.
        ¡Aquí ocurre la magia de traducción!
        """
        # UPDATE en SAACXC (tabla de Saint)
        stmt = text("""
            UPDATE SAACXC
            SET 
                MontoCred = MontoCred + :monto,
                UltimoPago = :fecha,
                Modificado = GETDATE()
            WHERE CodFact = :factura_id
        """)
        await self.db.execute(
            stmt,
            {
                "monto": monto_abonado,
                "fecha": datetime.now(),
                "factura_id": factura_id
            }
        )
        
        # Nota: Si la factura queda saldada (MontoCred >= MontoFact),
        # también deberías actualizar el estado en SAFACT
```

### Ejemplo de Query con Join Saint + App

```python
# Puedes hacer JOINs entre tus tablas y las de Saint
async def obtener_pagos_con_detalle_cliente():
    query = text("""
        SELECT 
            p.id AS pago_id,
            p.monto,
            p.fecha_pago,
            f.NumFact AS factura_numero,
            c.NomClie AS cliente_nombre,
            c.RifClie AS cliente_rif
        FROM AppConciliacion.Pagos p
        INNER JOIN dbo.SAFACT f ON p.factura_id = f.CodFact
        INNER JOIN dbo.SACLIE c ON f.CodClie = c.CodClie
        WHERE p.estado = 'VALIDADO'
        ORDER BY p.fecha_pago DESC
    """)
    result = await db.execute(query)
    return result.fetchall()
```

---

## MÉTRICAS DE ÉXITO

### Métricas Técnicas

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| **Tiempo de Respuesta** | < 300ms p95 | Prometheus middleware en FastAPI |
| **Conciliación Automática** | > 85% de pagos sin intervención manual | Log de resultados batch |
| **Disponibilidad** | 99% uptime | Ping monitor (UptimeRobot) |
| **Errores en Producción** | < 5 por semana | Sentry dashboard |
| **Cobertura de Tests** | > 75% | pytest-cov |
| **Tiempo de Parsing** | < 10s para 1000 líneas | Celery task metrics |

### Métricas de Negocio

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| **Tiempo de Conciliación Manual** | Reducción 90% (de 8h a < 1h) | Tiempo registrado por contador |
| **Exactitud de Matching** | 95%+ en modo automático | Auditoría de falsos positivos |
| **Pagos Validados/Día** | 100+ | Contador en dashboard |
| **Comisiones Calculadas sin Error** | 100% correctas | Auditoría mensual vs cálculo manual |
| **Adopción de Usuarios** | 100% del equipo contable (2-3 personas) | Login tracking |

### Métricas de Calidad de Código

| Métrica | Objetivo | Herramienta |
|---------|----------|-------------|
| **Complejidad Ciclomática** | < 10 por función | Radon |
| **Duplicación de Código** | < 3% | pylint |
| **Type Hints Coverage** | 90%+ | mypy |
| **Deuda Técnica** | < 1 día/sprint | SonarQube (opcional) |

---

## CONSIDERACIONES ESPECIALES

### 1. Manejo de Multimoneda

**Problema:** Venezuela maneja VES (Bolívares) y USD (Dólares) simultáneamente. Saint puede tener facturas en ambas monedas.

**Solución en Código:**

```python
# domain/value_objects/monto.py
from enum import Enum
from decimal import Decimal

class Moneda(str, Enum):
    VES = "VES"
    USD = "USD"

class Monto:
    def __init__(self, valor: Decimal, moneda: Moneda):
        if valor < 0:
            raise ValueError("Monto no puede ser negativo")
        self.valor = valor
        self.moneda = moneda
    
    def __eq__(self, other: 'Monto') -> bool:
        """Solo comparar si son misma moneda"""
        if self.moneda != other.moneda:
            raise ValueError("No se pueden comparar monedas distintas")
        return self.valor == other.valor
    
    def esta_en_rango(self, otro: 'Monto', tolerancia: Decimal) -> bool:
        """Para matching fuzzy"""
        if self.moneda != otro.moneda:
            return False
        diferencia = abs(self.valor - otro.valor)
        return diferencia <= tolerancia
```

**En UI (Jinja2):**

```html+jinja
<!-- templates/cxc/detalle_facturas.html -->
<table>
    <tr>
        <th>Factura</th>
        <th>Saldo VES</th>
        <th>Saldo USD</th>
    </tr>
    {% for factura in facturas %}
    <tr>
        <td>{{ factura.numero }}</td>
        <td>
            {% if factura.moneda == "VES" %}
                Bs. {{ factura.saldo_pendiente | format_money }}
            {% else %}
                -
            {% endif %}
        </td>
        <td>
            {% if factura.moneda == "USD" %}
                $ {{ factura.saldo_pendiente | format_money }}
            {% else %}
                -
            {% endif %}
        </td>
    </tr>
    {% endfor %}
</table>
```

---

### 2. Seguridad: Prevención de SQL Injection

**Problema:** Estás escribiendo SQL directo contra Saint (no siempre vía ORM).

**Solución:**

```python
# ❌ MAL: Vulnerable a SQL Injection
async def buscar_cliente_mal(nombre: str):
    query = f"SELECT * FROM SACLIE WHERE NomClie LIKE '%{nombre}%'"
    # Si nombre = "'; DROP TABLE SACLIE; --" → DESASTRE

# ✅ BIEN: Parameterized query
async def buscar_cliente_bien(nombre: str):
    query = text("""
        SELECT * FROM SACLIE 
        WHERE NomClie LIKE :nombre
    """)
    result = await db.execute(query, {"nombre": f"%{nombre}%"})
    return result.fetchall()
```

**En FastAPI (validación automática con Pydantic):**

```python
from pydantic import BaseModel, Field, validator

class BuscarClienteForm(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    
    @validator('nombre')
    def sanitize_nombre(cls, v):
        # Remover caracteres peligrosos
        return v.replace("'", "").replace(";", "").replace("--", "")

@router.get("/clientes/buscar")
async def buscar(form: BuscarClienteForm = Depends()):
    # form.nombre ya está validado
    return await cliente_service.buscar(form.nombre)
```

---

### 3. Optimización de Performance

**Problema:** Procesar 1000 líneas de estado de cuenta puede bloquear el servidor.

**Solución: Background Tasks con Celery**

```python
# infrastructure/tasks/parsing_task.py
from celery import shared_task

@shared_task(bind=True)
def procesar_estado_cuenta(self, archivo_id: str):
    """
    Procesa archivo en background.
    Actualiza progreso en Redis.
    """
    archivo = obtener_archivo(archivo_id)
    parser = seleccionar_parser(archivo.tipo)
    
    total_lineas = contar_lineas(archivo.ruta)
    
    for i, linea in enumerate(parser.parse(archivo.ruta)):
        # Procesar linea
        guardar_movimiento(linea)
        
        # Actualizar progreso cada 50 líneas
        if i % 50 == 0:
            progreso = int((i / total_lineas) * 100)
            self.update_state(
                state='PROGRESS',
                meta={'progreso': progreso}
            )
    
    return {'status': 'completado', 'total': total_lineas}
```

**En UI con HTMX + SSE:**

```html+jinja
<!-- templates/bancos/subir_estado.html -->
<form hx-post="/bancos/subir-estado" 
      hx-encoding="multipart/form-data"
      hx-target="#resultado">
    <input type="file" name="archivo" accept=".txt,.xlsx,.pdf">
    <button type="submit">Subir</button>
</form>

<div id="resultado">
    <!-- Aquí se carga el progreso vía SSE -->
</div>

<script>
// HTMX automáticamente maneja hx-sse si configuras el endpoint
</script>
```

```python
# presentation/web/routes/bancos_routes.py
from sse_starlette.sse import EventSourceResponse

@router.post("/bancos/subir-estado")
async def subir_estado(archivo: UploadFile):
    # Guardar archivo temporalmente
    archivo_id = guardar_temporal(archivo)
    
    # Encolar tarea Celery
    task = procesar_estado_cuenta.delay(archivo_id)
    
    # Retornar HTML con SSE para seguir progreso
    return templates.TemplateResponse(
        "bancos/_progreso.html",
        {"task_id": task.id}
    )

@router.get("/bancos/progreso/{task_id}")
async def progreso_stream(task_id: str):
    """
    Server-Sent Events para streaming de progreso
    """
    async def event_generator():
        while True:
            task = AsyncResult(task_id)
            if task.state == 'PROGRESS':
                yield {
                    "event": "progress",
                    "data": json.dumps(task.info)
                }
            elif task.state == 'SUCCESS':
                yield {
                    "event": "complete",
                    "data": json.dumps(task.result)
                }
                break
            await asyncio.sleep(0.5)
    
    return EventSourceResponse(event_generator())
```

---

### 4. Testing Strategy

#### Tests Unitarios (Domain Layer)

```python
# tests/unit/domain/test_monto.py
import pytest
from domain.value_objects import Monto, Moneda

def test_monto_no_negativo():
    with pytest.raises(ValueError):
        Monto(-100, Moneda.VES)

def test_monto_igualdad():
    m1 = Monto(100, Moneda.USD)
    m2 = Monto(100, Moneda.USD)
    assert m1 == m2

def test_monto_diferentes_monedas():
    m1 = Monto(100, Moneda.USD)
    m2 = Monto(100, Moneda.VES)
    with pytest.raises(ValueError):
        m1 == m2  # No se pueden comparar
```

#### Tests de Integración (Infrastructure Layer)

```python
# tests/integration/test_saint_adapter.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def test_db():
    """Database de prueba (copia de estructura de Saint)"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # Crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_guardar_pago_actualiza_saint(test_db):
    # Arrange
    repo = SaintPagoRepository(test_db)
    factura = crear_factura_mock()
    pago = Pago.crear(factura, Monto(100, Moneda.VES), ...)
    
    # Act
    await repo.guardar(pago)
    await repo.actualizar_cxc_saint(factura.id, 100)
    
    # Assert
    resultado = await test_db.execute(
        "SELECT MontoCred FROM SAACXC WHERE CodFact = :id",
        {"id": factura.id}
    )
    assert resultado.scalar() == 100
```

#### Tests E2E (Presentation Layer)

```python
# tests/e2e/test_cxc_flow.py
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_registrar_pago_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Login
        await page.goto("http://localhost:8000/auth/login")
        await page.fill("#usuario", "admin")
        await page.fill("#password", "test123")
        await page.click("button[type=submit]")
        
        # Navegar a CXC
        await page.click("a[href='/cxc/clientes']")
        await page.wait_for_selector("table")
        
        # Click en cliente
        await page.click("tr:first-child")
        
        # Abrir form de pago (HTMX carga modal)
        await page.click("button:has-text('Registrar Pago')")
        await page.wait_for_selector("#modal-pago")
        
        # Llenar form
        await page.fill("#monto", "100.00")
        await page.fill("#referencia", "REF-123")
        await page.click("button:has-text('Guardar')")
        
        # Verificar toast de éxito
        await page.wait_for_selector(".toast:has-text('Pago registrado')")
        
        await browser.close()
```

---

### 5. Deployment Completo

#### Dockerfile Optimizado

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim as base

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

# Copiar código
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini .
COPY ./static ./static

# Stage para Celery worker
FROM base as celery-worker
CMD ["celery", "-A", "app.infrastructure.tasks.celery_app", "worker", "--loglevel=info"]

# Stage para Celery beat (scheduled tasks)
FROM base as celery-beat
CMD ["celery", "-A", "app.infrastructure.tasks.celery_app", "beat", "--loglevel=info"]

# Stage para FastAPI
FROM base as web
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Docker Compose Producción

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  web:
    build:
      context: .
      target: web
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    depends_on:
      - redis
    volumes:
      - ./static:/app/static
      - media_files:/app/media
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery-worker:
    build:
      context: .
      target: celery-worker
    restart: always
    env_file:
      - .env.prod
    depends_on:
      - redis
      - web
    volumes:
      - media_files:/app/media

  celery-beat:
    build:
      context: .
      target: celery-beat
    restart: always
    env_file:
      - .env.prod
    depends_on:
      - redis
      - celery-worker

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
      - ./static:/var/www/static
      - ./media:/var/www/media
      - certbot_data:/etc/letsencrypt
    depends_on:
      - web

volumes:
  redis_data:
  media_files:
  certbot_data:
```

#### Nginx Configuration

```nginx
# docker/nginx.conf
upstream fastapi_backend {
    server web:8000;
}

server {
    listen 80;
    server_name saintbank.tuempresa.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name saintbank.tuempresa.com;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/saintbank.tuempresa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/saintbank.tuempresa.com/privkey.pem;
    
    # SSL Config
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Gzip
    gzip on;
    gzip_types text/css application/javascript application/json;
    
    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/media/;
        expires 30d;
    }
    
    # Proxy to FastAPI
    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (para HTMX SSE)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

---

## PRÓXIMOS PASOS Y RECOMENDACIONES

### Semana 1 - Setup Inmediato

1. ✅ Crear repositorio Git con estructura hexagonal
2. ✅ Setup FastAPI + Jinja2 + HTMX (template base funcional)
3. ✅ Configurar conexión a SQL Server de Saint (read-only primero)
4. ✅ Crear primer template: Login + Dashboard simple
5. ✅ Deploy en servidor local para pruebas
6. ✅ Implementar consulta de CXC por cliente
7. ✅ Form de registro de pago manual
8. ✅ Actualizar Saint (SAACXC) vía adapter
9. ✅ Validar transacciones ACID

### Semana 2 - Conciliación

1. ✅ Parser de estados de cuenta (mínimo 1 banco)
2. ✅ Algoritmo de matching básico (exacto + fuzzy)
3. ✅ UI de aprobación manual
4. ✅ Celery task para batch nocturno

### Semana 3 - Insytech + Comisiones

1. ✅ Integración con API Insytech
2. ✅ Validación de pagos reportados
3. ✅ Cálculo de comisiones multimoneda

### Decisiones Arquitectónicas Importantes

#### ¿ORM o SQL Crudo?

**Recomendación:** Híbrido
- **ORM (SQLAlchemy)** para tus tablas nuevas (AppConciliacion.*): Migraciones automáticas, type safety
- **SQL Crudo (text())** para consultas complejas de Saint: Mayor control, mejor performance

```python
# Consulta compleja con JOIN entre schemas
query = text("""
    SELECT 
        c.NomClie,
        SUM(CASE WHEN f.CodMone = 'USD' THEN f.MontoFact - f.MontoCred ELSE 0 END) as saldo_usd,
        SUM(CASE WHEN f.CodMone = 'VES' THEN f.MontoFact - f.MontoCred ELSE 0 END) as saldo_ves
    FROM dbo.SACLIE c
    INNER JOIN dbo.SAFACT f ON c.CodClie = f.CodClie
    WHERE f.MontoCred < f.MontoFact
    GROUP BY c.NomClie
    ORDER BY saldo_usd DESC
""")
```

#### ¿Cuándo usar HTMX vs Alpine.js?

**HTMX:** Para todo lo que requiere interacción con backend
- Cargar parciales (hx-get, hx-post)
- Actualizar tablas (hx-swap)
- Submit forms sin reload (hx-post)

**Alpine.js:** Para interactividad puramente frontend
- Abrir/cerrar dropdowns
- Mostrar/ocultar secciones
- Validación visual de forms (sin enviar al backend)

```html+jinja
<!-- Ejemplo combinado -->
<div x-data="{ open: false }">
    <!-- Alpine maneja el dropdown -->
    <button @click="open = !open">Filtros</button>
    
    <div x-show="open">
        <!-- HTMX maneja el submit -->
        <form hx-post="/cxc/filtrar" hx-target="#tabla">
            <input name="fecha_desde">
            <button type="submit">Aplicar</button>
        </form>
    </div>
</div>

<div id="tabla">
    <!-- Aquí se carga el resultado -->
</div>
```

---

## CONCLUSIÓN

### Beneficios de Esta Arquitectura

✅ **Simplicidad Operativa:** 1 servidor, 1 base de datos, 1 deployment  
✅ **Performance:** Sin latencia de red entre "servicios"  
✅ **Transaccionalidad:** ACID nativo de SQL Server  
✅ **Mantenibilidad:** Arquitectura hexagonal permite cambiar Saint por otro ERP sin tocar dominio  
✅ **Escalabilidad Vertical:** Puedes escalar añadiendo más workers de Celery  
✅ **Desarrollo Rápido:** 2 personas pueden trabajar en diferentes módulos sin conflictos  

### Cuándo Migrar a Microservicios

Si en el futuro:
- El equipo crece a 10+ personas
- Necesitas escalar horizontalmente (múltiples servidores)
- Diferentes módulos requieren tecnologías distintas
- El monolito supera 100K líneas de código

Entonces considera extraer módulos a microservicios. Pero por ahora, **un monolito modular bien diseñado es la mejor opción.**

---

## DOCUMENTOS COMPLEMENTARIOS

### Archivo de Configuración (.env.example)

```bash
# .env.example
# FastAPI
SECRET_KEY=your-secret-key-here
DEBUG=false
ALLOWED_HOSTS=saintbank.tuempresa.com

# SQL Server (Saint)
DB_HOST=localhost
DB_PORT=1433
DB_NAME=SaintERP
DB_USER=saint_app_user
DB_PASSWORD=secure-password-here

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Insytech API
INSYTECH_API_URL=https://api.insytech.com
INSYTECH_API_KEY=your-insytech-key

# Email (para notificaciones)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notificaciones@tuempresa.com
SMTP_PASSWORD=email-password

# Sentry (errores)
SENTRY_DSN=https://your-sentry-dsn.ingest.sentry.io

# Storage (opcional)
STORAGE_TYPE=local  # local | s3 | minio
MEDIA_ROOT=/app/media
```

### Requirements Files

```txt
# requirements/base.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-multipart==0.0.6

# Database
sqlalchemy[asyncio]==2.0.23
pyodbc==5.0.1
alembic==1.12.1

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# Tasks
celery==5.3.4
redis==5.0.1

# File Processing
openpyxl==3.1.2
pdfplumber==0.10.3
pandas==2.1.4

# HTTP Client
httpx==0.25.2

# Utils
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dateutil==2.8.2
```

---

**DOCUMENTO PREPARADO:** Diciembre 2025  
**UBICACIÓN:** Caracas, Venezuela  
**CLASIFICACIÓN:** Interno - Confidencial  
**PRÓXIMA REVISIÓN:** Post Sprint 1.4 (Semana 2)