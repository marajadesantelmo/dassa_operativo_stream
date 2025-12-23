# Metodología de Scoring de Clientes

## Objetivo
Calcular un score de 0 a 100 para cada cliente basado en tres métricas clave que reflejan el valor y comportamiento del cliente.

## Períodos de Análisis
- **Últimos 2 meses** (60 días)
- **Últimos 6 meses** (180 días)

Ambos períodos se calculan y se presentan en el reporte con una columna "Periodo" para filtrar.

## Métricas Utilizadas

### 1. **Número de Operaciones (33% del score)**
- **Fuente**: Egresos del stock
- **Campo**: `OIs` (órdenes de ingreso únicas)
- **Criterio**: Mayor número de operaciones = Mejor score
- **Interpretación**: Clientes con más operaciones son más activos

### 2. **Último Precio por Item (33% del score)**
- **Fuente**: Facturación por concepto
- **Campo**: `Ultimo_Precio` (último precio por fecha_emi)
- **Método**: Normalización item-level por concepto, luego promedio por cliente
- **Criterio**: Mayor precio = Mejor score
- **Interpretación**: Clientes que pagan precios más altos son más rentables
- **Importante**: Si el cliente no tiene facturación en el período, su score de precio es 0 y afecta el score final

### 3. **Días Promedio a Pago (34% del score)**
- **Fuente**: Análisis de pagos (CtaCcteD)
- **Campo**: `Promedio_dias_a_pago`
- **Criterio**: Menos días = Mejor score (invertido)
- **Interpretación**: Clientes que pagan más rápido tienen mejor comportamiento financiero

## Proceso de Cálculo

### Paso 1: Cálculo de Último Precio
Para cada cliente-item, se toma el precio de la última transacción (ordenado por fecha_emi descendente).

### Paso 2: Normalización Item-Level
Los precios se normalizan por concepto (0-100) usando percentiles (5-95) para manejar outliers:
```
Score_Item = ((Precio - P5) / (P95 - P5)) × 100
```
Luego se promedian todos los scores de items por cliente.

### Paso 3: Normalización de Otras Métricas
**Para métricas "más es mejor" (Operaciones):**
```
Score = ((Valor - P5) / (P95 - P5)) × 100
```

**Para métricas "menos es mejor" (Días de pago):**
```
Score = 100 - ((Valor - P5) / (P95 - P5)) × 100
```

### Paso 4: Score Ponderado Final
```
Score_Final = (Score_Operaciones × 0.33) + (Score_Precio × 0.33) + (Score_Días_Pago × 0.34)
```

**Importante:** 
- Se requieren al menos 2 de las 3 métricas
- Si falta una métrica, los pesos se redistribuyen proporcionalmente
- Scores de 0 (ej: sin facturación) se incluyen en el cálculo y bajan el score final

### Paso 5: Ranking por Período
Los clientes se ordenan de mayor a menor score final dentro de cada período.

## Interpretación del Score

| Rango de Score | Categoría | Interpretación |
|----------------|-----------|----------------|
| 80 - 100 | Clientes Premium | Alto valor: gran volumen, buenos precios, pago rápido |
| 60 - 79 | Clientes Buenos | Buen desempeño general en las métricas clave |
| 40 - 59 | Clientes Regulares | Desempeño promedio o con áreas de mejora |
| 20 - 39 | Clientes en Observación | Bajo desempeño en una o más métricas importantes |
| 0 - 19 | Clientes de Bajo Valor | Requieren evaluación para posible mejora o descontinuación |

## Columnas del Reporte

1. **Ranking**: Posición del cliente ordenado por score final
2. **Cliente**: Nombre del cliente consolidado
3. **Score Final (0-100)**: Score ponderado final
4. **Score Operaciones**: Score individual de operaciones (0-100)
5. **Score Precio**: Score individual de precio (0-100)
6. **Score Días Pago**: Score individual de días de pago (0-100)
7. **Número de Operaciones**: Cantidad de OIs únicas
8. **Precio Promedio ($)**: Promedio de últimos precios por item
9. **Ultimo Precio ($)**: Último precio de transacción del cliente
10. **Promedio Días a Pago**: Días promedio desde vencimiento hasta pago
11. **Métricas Disponibles**: Cantidad de métricas con datos (de 3 posibles)
12. **Periodo**: "Ultimos 2 meses" o "Ultimos 6 meses"

## Características Clave

✅ **Multi-período**: Análisis de 2 y 6 meses en un solo reporte
✅ **Último precio**: Usa precios más recientes en lugar de promedios históricos
✅ **Normalización robusta**: Usa percentiles para manejar outliers
✅ **Item-level**: Normaliza precios por concepto para evitar sesgos
✅ **Penalización por inactividad**: Clientes sin facturación reciben score 0 en precio
✅ **Consolidación**: Agrupa clientes relacionados automáticamente

## Limitaciones

⚠️ **Clientes nuevos**: Pueden tener pocas métricas o no aparecer en el período corto
⚠️ **Estacionalidad**: No ajusta por variaciones estacionales del negocio
⚠️ **Saldos fijos**: Análisis de pagos usa fecha fija (desde 2025-01-01)

## Uso Recomendado

- **Comparar períodos**: Usar columna "Periodo" para ver evolución 2 vs 6 meses
- **Identificar tendencias**: Clientes que mejoran/empeoran entre períodos
- **Priorización comercial**: Focus en clientes de alto score en período corto
- **Retención**: Detectar clientes con score decreciente entre períodos
