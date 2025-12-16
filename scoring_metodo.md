# Metodología de Scoring de Clientes

## Objetivo
Calcular un score de 0 a 100 para cada cliente basado en tres métricas clave que reflejan el valor y comportamiento del cliente.

## Métricas Utilizadas

### 1. **Volumen Total Egresado (40% del score)**
- **Fuente**: Tabla `volumen_egresado_por_cliente`
- **Campo**: `Volumen_Total_egresado_m3`
- **Criterio**: Mayor volumen = Mejor score
- **Interpretación**: Clientes que mueven más volumen (m³) son más valiosos para el negocio

### 2. **Precio Promedio (35% del score)**
- **Fuente**: Tabla `precio_promedio_por_item_cliente` 
- **Campo**: `Precio_Promedio_Item` (agregado por cliente)
- **Criterio**: Mayor precio promedio = Mejor score
- **Interpretación**: Clientes que pagan precios más altos por los servicios son más rentables

### 3. **Días Promedio a Pago (25% del score)**
- **Fuente**: Tabla `pagadores`
- **Campo**: `Promedio_dias_a_pago`
- **Criterio**: Menos días = Mejor score (invertido)
- **Interpretación**: Clientes que pagan más rápido tienen mejor comportamiento financiero

## Proceso de Cálculo

### Paso 1: Normalización Individual
Cada métrica se normaliza en una escala de 0 a 100 usando la fórmula:

**Para métricas donde "más es mejor" (Volumen, Precio):**
```
Score = ((Valor - Valor_Mínimo) / (Valor_Máximo - Valor_Mínimo)) × 100
```

**Para métricas donde "menos es mejor" (Días de pago):**
```
Score = 100 - ((Valor - Valor_Mínimo) / (Valor_Máximo - Valor_Mínimo)) × 100
```

### Paso 2: Score Ponderado
El score final se calcula como promedio ponderado de las métricas disponibles:

```
Score_Final = (Score_Volumen × 0.40) + (Score_Precio × 0.35) + (Score_Días_Pago × 0.25)
```

**Importante:** Si un cliente no tiene todas las métricas disponibles:
- Se requieren al menos 2 de las 3 métricas
- Los pesos se redistribuyen proporcionalmente entre las métricas disponibles

### Paso 3: Ranking
Los clientes se ordenan de mayor a menor score final y se les asigna un ranking.

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
2. **Cliente**: Nombre del cliente normalizado
3. **Score Final (0-100)**: Score ponderado final
4. **Score Volumen**: Score individual de volumen (0-100)
5. **Score Precio**: Score individual de precio (0-100)
6. **Score Días Pago**: Score individual de días de pago (0-100)
7. **Volumen Total (m³)**: Volumen total egresado en metros cúbicos
8. **Precio Promedio ($)**: Precio promedio pagado por servicios
9. **Promedio Días a Pago**: Días promedio desde vencimiento hasta pago efectivo
10. **Métricas Disponibles**: Cantidad de métricas con datos (de 3 posibles)

## Ventajas del Método

✅ **Objetivo**: Basado en datos reales del sistema
✅ **Normalizado**: Permite comparación justa entre clientes
✅ **Ponderado**: Refleja la importancia relativa de cada métrica
✅ **Flexible**: Funciona incluso si faltan algunas métricas
✅ **Actualizable**: Se recalcula automáticamente con nuevos datos

## Limitaciones

⚠️ **Datos históricos**: El score refleja comportamiento pasado (últimos 180 días)
⚠️ **Clientes nuevos**: Pueden tener pocas métricas disponibles
⚠️ **Estacionalidad**: No considera variaciones estacionales del negocio

## Uso Recomendado

- **Segmentación de clientes** para estrategias comerciales diferenciadas
- **Priorización** de atención y recursos comerciales
- **Identificación** de clientes de alto valor para retención
- **Detección** de clientes en riesgo o de bajo rendimiento
- **Análisis de tendencias** comparando scores en el tiempo
