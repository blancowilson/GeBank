# 📊 SAINT ADMINISTRATIVO v2.1.0 - PAQUETE COMPLETO DE DOCUMENTACIÓN

## ✅ Resumen de Entregables

Se ha completado la enriquecimiento del modelo **Saint Administrativo** con:

### 📄 Archivos Generados

| # | Archivo | Tipo | Propósito |
|---|---------|------|----------|
| 1 | **modelo_saint_dbml_completo.dbml** | DBML | Definición SQL completa con relaciones explícitas |
| 2 | **diccionario_saint_2-1-0.yaml** | YAML | Diccionario de datos con tipos y validaciones |
| 3 | **saint-admin-relaciones-guia.md** | Markdown | Guía rápida visual de relaciones |
| 4 | **validar-saint-schema.sh** | Bash | Script de validación de estructura |
| 5 | **saint_estructura_resumen.csv** | CSV | Resumen tabular de categorías |

---

## 🎯 Lo Nuevo en v2.1.0

### ✨ Características Añadidas

#### 1️⃣ **TIPOS DE DATOS ESPECIFICADOS**
```
✓ varchar(N)      - Textos variables (códigos, descripciones)
✓ decimal(28,4)   - Montos con 4 decimales (máxima precisión)
✓ smallint        - Booleanos 0/1 (Activo, EsCredito)
✓ int             - Secuenciales y contadores
✓ datetime2       - Fechas y horas (100ns precisión)
✓ varchar(max)    - Textos sin límite (URLs, Base64)
```

#### 2️⃣ **RELACIONES EXPLÍCITAS EN DBML**
El archivo `.dbml` ahora incluye todas las relaciones:

```dbml
Ref: "SACLIE"."CodClie" > "SAFACT"."CodClie"
Ref: "SAFACT"."NumeroD" > "SAACXC"."NumeroD"
Ref: "SAACXC"."NroUnico" > "SAPAGCXC"."NroPpal"
... (20+ relaciones más)
```

#### 3️⃣ **TABLAS OPCIONALES PARA INTEGRACIÓN CXC**
```
GePagos
├─ Pago externo (idPago único)
├─ Status: 1=Pendiente, 3=Aprobado, 9=Rechazado
└─ Link a documento

GeDocumentos
├─ Facturas cubiertas por pago
├─ Descuentos y retenciones por doc
└─ URL comprobante de retención

GeInstrumentos
├─ Medios de pago (cheque, transferencia)
├─ Tasa de cambio
└─ Banco cliente y empresa
```

#### 4️⃣ **VALIDACIONES Y RESTRICCIONES**
- ✓ Rangos numéricos (0-100 para porcentajes)
- ✓ Reglas contables (Monto = suma componentes)
- ✓ Validaciones de fecha (FechaE ≤ FechaV ≤ FechaI)
- ✓ Estados válidos (0/1, valores específicos)

#### 5️⃣ **ÍNDICES RECOMENDADOS**
```sql
-- Performance
CREATE INDEX IDX_SAFACT_CLIENTE_FECHA 
ON SAFACT(FechaE, CodClie)

CREATE INDEX IDX_SAACXC_CLIENTE_SALDO 
ON SAACXC(CodClie, Saldo)

-- Integridad
CREATE UNIQUE INDEX IDX_GEPAGOS_IDPAGO 
ON GePagos(idPago)
```

---

## 📊 Estadísticas del Modelo

### Por Categoría
| Categoría | Tablas | Descripción |
|-----------|--------|-------------|
| 🔧 Configuration | 1 | Configuración general |
| 👥 Masters | 9 | Clientes, proveedores, ubicaciones |
| 📄 Sales | 3 | Facturas y detalles |
| 📦 Purchases | 2 | Compras y detalles |
| 💰 Accounting | 4 | CxC, CxP y pagos |
| 📋 Taxes/Operations | 3 | Impuestos e instancias |
| 🏷️ Prices/Offers | 4 | Convenios y ofertas |
| 💸 Commissions | 2 | Tablas comisiones |
| 📊 Inventory | 3 | Existencias y lotes |
| 📈 Statistics | 5 | Análisis por período |
| 🔌 Optional CxC | 3 | Integración pagos |
| **TOTAL** | **39** | **+ 9 catálogo geográfico** |

### Tipos de Datos Utilizados
| Tipo | Uso Principal | Ejemplos |
|------|---------------|----------|
| `varchar(N)` | Textos y códigos | CodClie, Email, Descrip |
| `decimal(28,4)` | Montos monetarios | Monto, Saldo, Precio |
| `smallint` | Banderas (0/1) | Activo, EsCredito |
| `int` | Secuenciales | NroUnico, NroLinea |
| `datetime2` | Fechas/horas | FechaE, FechaV, create |

### Relaciones Documentadas
- **12** Relaciones Primarias (1:N con FK)
- **8** Relaciones Lógicas (sin FK, por JOIN)
- **20** Relaciones Totales

---

## 🔗 Estructuras de Relación Principales

### 📈 Flujo de VENTAS
```
SACLIE (Cliente)
  ↓
  SAFACT (Factura)
    ├─ SAITEMFAC (Líneas)
    ├─ SAVEND (Vendedor)
    ├─ SADEPO (Depósito)
    └─ SAACXC (CxC)
         └─ SAPAGCXC (Pago Aplicado)
              └─ GePagos (Pago Externo)
```

### 🛒 Flujo de COMPRAS
```
SAPROV (Proveedor)
  ↓
  SACOMP (Compra)
    ├─ SAITEMCOM (Líneas)
    ├─ SADEPO (Depósito)
    └─ SAACXP (CxP)
         └─ SAPAGCXP (Pago Realizado)
```

### 💳 Flujo de PAGOS EXTERNOS (NUEVO)
```
GePagos (Pago externo)
  ├─ GeDocumentos (Facturas cubiertas)
  │   ├─ Descuentos
  │   └─ Retenciones
  └─ GeInstrumentos (Medios pago)
      ├─ Cheques
      ├─ Transferencias
      └─ Otros
```

### 🌍 Cascada GEOGRÁFICA
```
SAPAIS (País)
  ├─ SAESTADO (Estado)
  │   └─ SACIUDAD (Ciudad)
  └─ SACLIE, SAPROV, SAVEND (Ubicación)
```

---

## 🚀 Cómo Usar la Documentación

### 📍 Para Entender la Estructura Global
→ Abre **`saint-admin-relaciones-guia.md`**
- Visualiza flujos de procesos
- Consultas SQL comunes
- Checklist de implementación

### 📝 Para Detalles de Cada Campo
→ Consulta **`diccionario_saint_2-1-0.yaml`**
- Descripción completa de cada campo
- Tipos de datos
- Validaciones
- Ejemplos de valores

### 🔍 Para Implementación SQL
→ Usa **`modelo_saint_dbml_completo.dbml`**
- Copia directamente a dbdiagram.io
- Visualiza ERD completo
- Genera scripts SQL

### ✅ Para Validar Integridad
→ Ejecuta **`validar-saint-schema.sh`**
```bash
bash validar-saint-schema.sh
```
- Verifica todas las relaciones
- Valida tipos de datos
- Comprueba reglas de negocio

---

## 📋 Características por Tabla

### TABLAS OBLIGATORIAS (Fase 1)
#### Configuración y Maestros
- **SACONF** - Datos empresa
- **SACLIE** - Clientes
- **SAVEND** - Vendedores
- **SAPROV** - Proveedores
- **SADEPO** - Depósitos

#### Documentos Transaccionales
- **SAFACT** / **SAITEMFAC** - Ventas
- **SACOMP** / **SAITEMCOM** - Compras

#### Contabilidad
- **SAACXC** / **SAPAGCXC** - CxC y pagos cobrados
- **SAACXP** / **SAPAGCXP** - CxP y pagos realizados

### TABLAS EXTENDIDAS (Fase 2)
- **SACONV** / **SAITCV** - Convenios de precios
- **SAOFER** / **SAITEO** - Ofertas promocionales
- **SACVEN** / **SACMEC** - Comisiones
- **SAEXIS** / **SALOTE** / **SAINITI** - Inventario

### TABLAS OPCIONALES (Fase 3)
- **GePagos** - Pagos desde plataforma externa
- **GeDocumentos** - Documentos cubiertos
- **GeInstrumentos** - Medios de pago

---

## 🎓 Guía de Implementación

### ⏱️ Fase 1: NÚCLEO (40-60 horas)
```
1. Crear tablas maestro (SACLIE, SAVEND, etc.)
2. Crear tablas de documentos (SAFACT, SACOMP)
3. Crear tablas contables (SAACXC, SAACXP)
4. Crear índices de performance
5. Implementar validaciones básicas
```

### ⏱️ Fase 2: EXTENDIDAS (30-40 horas)
```
1. Implementar convenios y ofertas
2. Agregar tablas de inventario
3. Implementar comisiones
4. Crear vistas de análisis
5. Agregar estadísticas
```

### ⏱️ Fase 3: OPCIONALES (20-30 horas)
```
1. Integración GePagos
2. Documentos GeDocumentos
3. Instrumentos GeInstrumentos
4. Triggers de aplicación automática
5. Reportes de integración
```

---

## 🔒 Validaciones Implementadas

### ✓ Validaciones Numéricas
```
Porcentajes (Descto, IntMora): 0.00 a 100.00
Montos (decimal(28,4)): ±999,999,999.9999
Status CxC (smallint): 0 o 1
Status Pago (tinyint): 1, 3, 9
```

### ✓ Validaciones de Fecha
```
FechaE ≤ FechaV (Emisión <= Vencimiento)
FechaI ≥ FechaE (Posteo >= Emisión)
FechaV < GETDATE() = VENCIDO
```

### ✓ Validaciones Contables
```
Monto = MtoTax + TGravable + TExento + Fletes
Saldo = Monto - (CancelE + CancelC + CancelG + CancelA)
SaldoMEx = MontoMEx × Factor
```

### ✓ Validaciones de Integridad
```
codCliente debe existir en SACLIE
NumeroD debe existir en SAFACT
NroUnico debe ser único en tabla
```

---

## 💡 Notas Importantes

⚠️ **Relaciones Lógicas Sin FK**
- Se usan para flexibilidad operativa
- Requieren validación en aplicación
- Sugerencia: Implementar triggers de auditoría

⚠️ **Tablas Opcionales CxC**
- No son obligatorias para funcionamiento
- Se integran solo si hay sistema de pagos externo
- Permiten flujo de dos direcciones

⚠️ **Campo `create`**
- Es varchar(100), no autoincremental
- Debe ser completado con timestamp en aplicación o trigger
- Formato recomendado: `YYYY-MM-DD HH:MM:SS.mmm`

⚠️ **Moneda Referencial**
- Campo Factor es decimal(28,4)
- Permite hasta 4 decimales
- Recomendación: Actualizar diario

---

## 📖 Estructura del Diccionario YAML

El archivo **diccionario_saint_2-1-0.yaml** contiene:

```yaml
version: "2.1.0"
relationships:
  primary_relationships:     # 12+ relaciones 1:N
  detail_relationships:      # Relaciones master-detalle
  accounting_relationships:  # Relaciones contables
  geographic_relationships:  # Cascada país-estado-ciudad
  logical_relationships:     # 8 relaciones por JOIN

data_types:
  varchar:      # Especificación tamaños
  decimal:      # Precisión 28,4
  smallint:     # Booleanos
  int:          # Secuenciales
  datetime2:    # Fechas/horas
  varchar_max:  # Textos sin límite

tables:
  SACONF:       # Completa con todos los campos
  SACLIE:       # Incluye validaciones
  ... (48 tablas)

optional_tables:
  GePagos:      # Con relaciones
  GeDocumentos: # Con foreign keys
  GeInstrumentos: # Con tipos de datos

recommended_indexes:      # Índices para performance
validations:              # Reglas de negocio
common_queries:           # SQL ejemplos
```

---

## 🎯 Casos de Uso Cubiertos

### ✅ Implementado
- [x] Ventas contado y crédito
- [x] Compras contado y crédito
- [x] Gestión de clientes y proveedores
- [x] Cuentas por cobrar/pagar
- [x] Aplicación de pagos
- [x] Convenios de precios
- [x] Ofertas y promociones
- [x] Comisiones vendedores
- [x] Inventario por depósito
- [x] Impuestos y retenciones
- [x] Estadísticas por período
- [x] Integración pagos externos ✨ NUEVO

### ⏸️ Extensible
- Pagos con financiamiento
- Giros y transferencias
- Devoluciones parciales
- Cambios de precio
- Auditoría de cambios

---

## 📞 Soporte y Consultas

### Si necesitas...

**Visualizar el modelo ERD:**
1. Copia contenido de `modelo_saint_dbml_completo.dbml`
2. Pega en [dbdiagram.io](https://dbdiagram.io)
3. Verás el diagrama relacional completo

**Entender una tabla específica:**
1. Busca el nombre en `diccionario_saint_2-1-0.yaml`
2. Lee descripción y campos con tipos
3. Consulta ejemplos de valores

**Implementar relaciones:**
1. Ve a `saint-admin-relaciones-guia.md`
2. Busca el flujo correspondiente
3. Copia consultas SQL ejemplo

**Validar estructura:**
1. Ejecuta `bash validar-saint-schema.sh`
2. Revisa todas las relaciones
3. Comprueba tipos de datos

---

## 📈 Próximos Pasos Recomendados

1. **Visualizar ERD**
   - Importar DBML a dbdiagram.io
   - Validar relaciones visualmente

2. **Generar Scripts SQL**
   - Exportar SQL desde dbdiagram.io
   - Ajustar a tu motor de BD

3. **Crear Base de Datos**
   - Ejecutar scripts de creación
   - Crear índices recomendados

4. **Implementar Triggers**
   - Validación de integridad
   - Auditoría de cambios
   - Cálculos automáticos

5. **Desarrollar Aplicación**
   - Mapear entidades a clases
   - Implementar validaciones
   - Crear interfaz de usuarios

6. **Pruebas**
   - Validar reglas de negocio
   - Probar aplicación de pagos
   - Verificar reportes

---

## 📊 Métricas Finales

| Métrica | Valor |
|---------|-------|
| Tablas Totales | 48+ |
| Campos Documentados | 500+ |
| Relaciones | 20 |
| Tipos de Datos | 6 |
| Validaciones | 20+ |
| Índices Recomendados | 8 |
| Archivos Generados | 5 |
| Líneas de Documentación | 3000+ |

---

## ✨ Conclusión

El modelo **Saint Administrativo v2.1.0** está **completamente documentado** y listo para:
- ✅ Visualizar en herramientas DBML
- ✅ Generar scripts SQL
- ✅ Implementar en base de datos
- ✅ Desarrollar aplicaciones
- ✅ Extender con nuevas funcionalidades

**Éxito con tu proyecto de implementación** 🚀

---

*Documentación generada: 29 de diciembre de 2025*  
*Versión: 2.1.0*  
*Ubicación: Caracas, Distrito Federal, Venezuela*
