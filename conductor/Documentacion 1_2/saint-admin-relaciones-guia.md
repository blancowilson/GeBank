# Saint Administrativo - GUÍA RÁPIDA DE RELACIONES
## Database Schema Reference v2.1.0

---

## 📋 RELACIONES PRIMARIAS (Tablas Maestros)

### CLIENTE → VENTAS → CUENTAS POR COBRAR
```
SACLIE (CodClie)
  ↓
  └─→ SAFACT (CodClie)
       ├─→ SAITEMFAC (NumeroD, TipoFac)
       └─→ SAACXC (CodClie)
            └─→ SAPAGCXC (NroUnico)
```

**Flujo:** Cliente compra → Se genera factura → Se crea CxC → Se registra pago aplicado

---

### PROVEEDOR → COMPRAS → CUENTAS POR PAGAR
```
SAPROV (CodProv)
  ↓
  └─→ SACOMP (CodProv)
       ├─→ SAITEMCOM (NumeroD, TipoCom)
       └─→ SAACXP (CodProv)
            └─→ SAPAGCXP (NroUnico)
```

**Flujo:** Proveedor vende → Se genera compra → Se crea CxP → Se registra pago

---

### VENDEDOR → FACTURAS
```
SAVEND (CodVend)
  ↓
  ├─→ SAFACT (CodVend)
  ├─→ SAEVEN (CodVend) [Estadísticas mensuales]
  ├─→ SACVEN (CodVend) [Tabla comisiones]
  └─→ SAITEMFAC (CodVend) [Opcional por línea]
```

---

### DEPÓSITO → MOVIMIENTOS
```
SADEPO (CodUbic)
  ↓
  ├─→ SAFACT (CodUbic) [Salidas por venta]
  ├─→ SACOMP (CodUbic) [Entradas por compra]
  ├─→ SAEXIS (CodUbic) [Existencias]
  └─→ SALOTE (CodUbic) [Lotes]
```

---

## 🌍 RELACIONES GEOGRÁFICAS (Cascada)

```
SAPAIS (Pais)
  ├─→ SAESTADO (Estado)
  │    └─→ SACIUDAD (Ciudad)
  └─→ SACLIE (Pais, Estado, Ciudad)
  └─→ SAPROV (Pais, Estado, Ciudad)
  └─→ SAVEND (Pais, Estado, Ciudad)
```

**Cada nivel es dependiente del anterior para integridad referencial**

---

## 💰 RELACIONES CONTABLES

### Ventas a Crédito
```
SAFACT (NumeroD)
  └─→ SAACXC (NumeroD, CodClie)
       ├─→ Saldo inicial = Monto factura
       └─→ SAPAGCXC (NroUnico)
            └─→ Descuenta del Saldo
```

### Compras a Crédito
```
SACOMP (NumeroD)
  └─→ SAACXP (NumeroD, CodProv)
       ├─→ Saldo inicial = Monto compra
       └─→ SAPAGCXP (NroUnico)
            └─→ Descuenta del Saldo
```

---

## 🏷️ RELACIONES DE PRECIOS Y OFERTAS

### Convenios de Precios
```
SACONV (CodConv)
  ├─→ SACLIE (CodConv) [Cliente asignado]
  └─→ SAITCV (CodConv)
       ├─ Período vigencia (Desde - Hasta)
       ├─ Precio especial por producto
       └─ Comisión asociada
```

### Ofertas y Promociones
```
SAOFER (NumeroD)
  └─→ SAITEO (NumeroD)
       ├─ Período vigencia
       ├─ Precio de oferta
       └─ Cantidad mínima requerida
```

---

## 📊 ESTADÍSTICAS Y ANÁLISIS

```
PERIODO (YYYYMM) es clave común en:
├─→ SAEVTA [Estadísticas ventas]
├─→ SAECOM [Estadísticas compras]
├─→ SAECLI [Por cliente]
├─→ SAEVEN [Por vendedor]
└─→ SAEPRV [Por proveedor]
```

---

## 🔗 RELACIONES LÓGICAS (SIN FOREIGN KEY)

Estas relaciones se hacen por **JOIN en consultas**, sin restricción en BD:

| Tabla A | Tabla B | Campo | Razón |
|---------|---------|-------|-------|
| SAVEND | SAFACT | CodVend | Flexibilidad de cambio de vendedor |
| SAMECA | SAITEMFAC | CodMeca | Servidor puede cambiar entre líneas |
| SAVEND | SAEVEN | CodVend | Estadísticas pueden inicializarse después |
| SAMECA | SACMEC | CodMeca | Comisiones dinámicas |

**Recomendación:** Implementar triggers o validaciones en aplicación para mantener integridad

---

## 🆕 TABLAS OPCIONALES INTEGRACIÓN CXC

### Flujo de Pago Externo
```
GePagos (idPago)
  ├─ Status: 1=Pendiente, 3=Aprobado, 9=Rechazado
  ├─→ GeDocumentos (idPago)
  │    ├─ Factura 1: $500
  │    ├─ Factura 2: $300
  │    └─ Total: $800
  └─→ GeInstrumentos (idPago)
       ├─ Cheque: $400
       └─ Transferencia: $400
```

**Características:**
- Un pago puede cubrir múltiples documentos
- Un pago puede estar compuesto por múltiples instrumentos
- Status 3 permite aplicación contra SAACXC

---

## 📝 TIPOS DE DATOS UTILIZADOS

| Tipo | Tamaño | Uso | Ejemplos |
|------|--------|-----|----------|
| `varchar(N)` | Variable | Textos, códigos, identificadores | CodClie, Email, Descrip |
| `decimal(28,4)` | 8 bytes | Montos, precios, porcentajes | Monto, Precio, Factor |
| `smallint` | 2 bytes | Banderas booleanas (0/1) | Activo, EsCredito, EsReten |
| `int` | 4 bytes | Contadores, secuenciales | NroUnico, NroLinea, Nivel |
| `datetime2` | 8 bytes | Fechas y horas | FechaE, FechaV, create |
| `varchar(max)` | Variable | URLs y textos largos | UrlImagen, UrlRetencion |

---

## ✅ VALIDACIONES CRÍTICAS

### Reglas Contables
```
Monto = MtoTax + TGravable + TExento + Fletes
Saldo = Monto - (CancelE + CancelC + CancelG + CancelA)
SaldoMEx = MontoMEx × Factor
```

### Reglas de Fechas
```
FechaE ≤ FechaV (Emisión antes de vencimiento)
FechaI ≥ FechaE (Posteo después de emisión)
FechaV < GETDATE() = VENCIDO
```

### Montos Válidos
```
Descto: 0.00 a 100.00 (%)
IntMora: 0.00 a 100.00 (% diaria)
Saldo: ≥ 0 (No negativos normalmente)
```

---

## 🔄 CONSULTAS COMUNES CON JOINS

### CxC Vencidas por Cliente
```sql
SELECT 
    c.CodClie,
    c.Descrip,
    SUM(x.Saldo) as TotalDeuda,
    MIN(x.FechaV) as FechaVencimiento
FROM SAACXC x
INNER JOIN SACLIE c ON x.CodClie = c.CodClie
WHERE x.Saldo > 0 AND x.FechaV < GETDATE()
GROUP BY c.CodClie, c.Descrip
ORDER BY FechaVencimiento
```

### Facturas sin Cobrar
```sql
SELECT 
    f.NumeroD,
    f.FechaE,
    c.Descrip as Cliente,
    f.Monto,
    x.Saldo
FROM SAFACT f
LEFT JOIN SAACXC x ON f.NumeroD = x.NumeroD 
                   AND f.CodClie = x.CodClie
LEFT JOIN SACLIE c ON f.CodClie = c.CodClie
WHERE f.TipoFac = 'FAC' AND x.Saldo > 0
```

### Aplicación de Pagos
```sql
SELECT 
    p.idPago,
    p.MontoPago,
    d.numeroDoc,
    d.montoDoc,
    d.montoDescuento,
    i.formaPago,
    i.monto as MontoInstrumento
FROM GePagos p
LEFT JOIN GeDocumentos d ON p.idPago = d.idPago
LEFT JOIN GeInstrumentos i ON p.idPago = i.idPago
WHERE p.status = 3
```

---

## 📌 CHECKLIST IMPLEMENTACIÓN

### Fase 1: Tablas Obligatorias
- [ ] SACONF, SAPAIS, SAESTADO, SACIUDAD
- [ ] SACLIE, SAVEND, SAPROV, SADEPO
- [ ] SAINSTA, SATAXES, SAOPER
- [ ] SAFACT, SAITEMFAC
- [ ] SACOMP, SAITEMCOM
- [ ] SAACXC, SAACXP, SAPAGCXC, SAPAGCXP

### Fase 2: Tablas Extendidas
- [ ] SACONV, SAITCV (Convenios)
- [ ] SAOFER, SAITEO (Ofertas)
- [ ] SACVEN, SACMEC (Comisiones)
- [ ] SAEXIS, SALOTE, SAINITI (Inventario)

### Fase 3: Tablas Opcionales
- [ ] GePagos, GeDocumentos, GeInstrumentos (Si hay integración)
- [ ] SAEVTA, SAECOM, SAECLI, SAEVEN, SAEPRV (Estadísticas)

---

## 🎯 RELACIONES EN DBML

El archivo `modelo_saint_dbml_completo.dbml` contiene todas las relaciones en formato DBML:
```dbml
Ref: "SACLIE"."CodClie" > "SAFACT"."CodClie"
Ref: "SAFACT"."NumeroD" > "SAACXC"."NumeroD"
Ref: "SAACXC"."NroUnico" > "SAPAGCXC"."NroPpal"
```

**Simbología:**
- `>` = One-to-Many (1:N)
- `<>` = One-to-One (1:1)
- `<` = Many-to-One (N:1)

---

## 📚 RECURSOS GENERADOS

1. **modelo_saint_dbml_completo.dbml**
   - Definición SQL con tipos de datos
   - Relaciones explícitas
   - Comentarios detallados
   
2. **diccionario_saint_2-1-0.yaml**
   - Diccionario de datos completo
   - Validaciones y restricciones
   - Guía de implementación por fases

3. **Saint-Admin-Relaciones-Guia.md** (este archivo)
   - Referencia rápida visual
   - Flujos de procesos
   - Consultas comunes

---

**Última actualización:** 29 de diciembre de 2025  
**Versión del modelo:** 2.1.0  
**Estado:** Completo con tablas opcionales CxC
