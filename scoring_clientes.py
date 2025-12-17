""" Script para generación de scoring de clientes basado en facturación de conceptos principales, saldos, etc."""
from tokens import username, password
import pyodbc
from datetime import datetime, timedelta
import pandas as pd
server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()
fecha_ant = datetime.now() - timedelta(days=365)
fecha_ant= fecha_ant.strftime('%Y-%m-%d')
### Tipo de cliente
cursor.execute(f"""
SELECT clie_nro AS 'Nro', apellido AS 'Cliente', tipo_cl AS 'Tipo', consolida AS 'Consolida'
FROM DEPOFIS.DASSA.[Clientes]
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
clientes = pd.DataFrame.from_records(rows, columns=columns)
clientes['Cliente'] = clientes['Cliente'].str.strip().str.title()
clientes['Tipo'] = clientes['Tipo'].str.strip().str.title()

cursor.execute(f"""
SELECT 
    f.Factura, 
    f.tipo, 
    f.fecha_emi, 
    f.concepto, 
    f.[Unitario Final],
    f.[Razon Social],
    c.detalle AS Concepto_Detalle
FROM DEPOFIS.DASSA.Facturacion f
LEFT JOIN DEPOFIS.DASSA.Concepfc c ON f.concepto = c.codigo
WHERE f.fecha_emi >= '{fecha_ant}'
AND f.concepto IN (10001, 10002, 10003, 10111, 10112, 10113, 10114, 10115, 10116, 20001, 20002, 20003, 20004, 20005, 20006, 40002, 40301, 40003, 40302, 40004, 40303)
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
facturacion = pd.DataFrame.from_records(rows, columns=columns)
facturacion['Concepto_Detalle'] = facturacion['Concepto_Detalle'].str.strip().str.title()
facturacion['Razon Social'] = facturacion['Razon Social'].str.strip().str.title()
facturacion['Unitario Final'] = facturacion['Unitario Final'].fillna(0).round(0).astype(int)

# Consolidate client names based on clientes.Consolida relationships
# Create mapping: Nro -> Cliente name
nro_to_cliente = dict(zip(clientes['Nro'], clientes['Cliente']))

# Create consolidation mapping: if Consolida != 0, use the consolidated client
consolidacion_map = {}
for _, row in clientes.iterrows():
    if row['Consolida'] != 0:
        cliente_actual = row['Cliente']
        cliente_consolidado = nro_to_cliente.get(row['Consolida'], cliente_actual)
        consolidacion_map[cliente_actual] = cliente_consolidado

# Apply consolidation to facturacion
if consolidacion_map:
    print(f"Consolidando {len(consolidacion_map)} clientes en facturacion...")
    facturacion['Razon Social'] = facturacion['Razon Social'].replace(consolidacion_map)
    if 'Tech Mind S.A.' in consolidacion_map:
        print(f"Ejemplo: 'Tech Mind S.A.' -> '{consolidacion_map['Tech Mind S.A.']}'")

precio_promedio_por_concepto = facturacion.groupby(['concepto', 'Concepto_Detalle']).agg(
    Precio_Promedio_Concepto=('Unitario Final', 'mean'),
    Precio_Min_Concepto=('Unitario Final', 'min'),
    Precio_Max_Concepto=('Unitario Final', 'max'), 
    Cantidad_Facturas_Concepto=('Factura', 'count'),
    Cliente_Precio_Max=('Razon Social', lambda x: x.loc[facturacion.loc[x.index, 'Unitario Final'].idxmax()]),
    Cliente_Precio_Min=('Razon Social', lambda x: x.loc[facturacion.loc[x.index, 'Unitario Final'].idxmin()])
).reset_index()

precio_promedio_por_item_cliente = facturacion.groupby(['Razon Social', 'concepto', 'Concepto_Detalle']).agg(
    Precio_Promedio_Item=('Unitario Final', 'mean'),
    Precio_Min_Item=('Unitario Final', 'min'),
    Precio_Max_Item=('Unitario Final', 'max'), 
    Cantidad_Facturas_Item=('Factura', 'count')
).reset_index()

precio_promedio_por_cliente = precio_promedio_por_item_cliente.groupby('Razon Social').agg(
    Promedio_Precio_Cliente=('Precio_Promedio_Item', 'mean'),
    Min_Precio_Cliente=('Precio_Promedio_Item', 'min'),
    Max_Precio_Cliente=('Precio_Promedio_Item', 'max'), 
    Cantidad_Conceptos_Facturados_Cliente=('concepto', 'count')
).reset_index()

cursor.execute(f"""
SELECT codigo AS Codigo, detalle AS Concepto
FROM DEPOFIS.DASSA.Concepfc
WHERE codigo IN (10001, 10002, 10003, 10111, 10112, 10113, 10114, 10115, 10116, 20001, 20002, 20003, 20004, 20005, 20006)""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
concepfc = pd.DataFrame.from_records(rows, columns=columns)
concepfc['Concepto'] = concepfc['Concepto'].str.strip().str.title()

### Descargo Saldos
cursor.execute("""
SELECT fecha_vto AS Vto, tp_cpte AS Tipo, aplicacion AS Nro, adicional AS Cliente, debe AS Debe, haber AS Haber
FROM DEPOFIS.DASSA.CtaCcteD
WHERE fecha_vto >= '2025-01-01'
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
saldos= pd.DataFrame.from_records(rows, columns=columns)
saldos['Cliente'] = saldos['Cliente'].str.strip().str.title()

# Apply consolidation to saldos
if consolidacion_map:
    saldos['Cliente'] = saldos['Cliente'].replace(consolidacion_map)

saldos_debe = saldos[saldos['Tipo'] == 'FCA']
saldos_debe_fechas = saldos_debe[['Cliente', 'Nro', 'Vto']].drop_duplicates()
saldos_haber_fechas = saldos[saldos['Tipo'] == 'RCM'][['Nro', 'Vto']].drop_duplicates()
saldos_haber_fechas = saldos_haber_fechas.rename(columns={'Vto': 'Pago'})
saldos_fechas = saldos_debe_fechas.merge(saldos_haber_fechas, on='Nro', how='inner')

saldos_fechas['Vto'] = pd.to_datetime(saldos_fechas['Vto'])
saldos_fechas['Pago'] = pd.to_datetime(saldos_fechas['Pago'])
saldos_fechas['Dias_a_pago'] = (saldos_fechas['Pago'] - saldos_fechas['Vto']).dt.days
pagadores = saldos_fechas.groupby('Cliente').agg(Promedio_dias_a_pago=('Dias_a_pago', 'mean'),
                                              Min_dias_a_pago=('Dias_a_pago', 'min'),
                                                Max_dias_a_pago=('Dias_a_pago', 'max'),
                                                Cantidad_pagos=('Dias_a_pago', 'count')).reset_index()

pagadores = pagadores.sort_values(by='Promedio_dias_a_pago', ascending=False).reset_index(drop=True)
aplicacion_cliente = saldos_debe[['Cliente', 'Nro']].drop_duplicates()
saldos = saldos.merge(aplicacion_cliente, on='Nro', how='left', suffixes=('', '_aplicacion'))
saldos['Cliente'] = saldos['Cliente'].apply(lambda x: x if x != "" else None)
saldos['Cliente'] = saldos['Cliente'].fillna(saldos['Cliente_aplicacion'])
saldos = saldos.drop(columns=['Cliente_aplicacion'])

### Analisis de volumen

cursor.execute(f"""
SELECT  e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing, 
e.contenedor, e.desc_merc, e.conocim AS conocim1, e.dimension, e.tipo_cnt, e.volumen, env.detalle AS Envase
FROM [DEPOFIS].[DASSA].[Egresadas del stock] e
JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.fecha_egr > '{fecha_ant}'
""")
egresos = cursor.fetchall()
columns = [column[0] for column in cursor.description]
egresos = pd.DataFrame.from_records(egresos, columns=columns)
egresos['cliente'] = egresos['cliente'].str.strip().str.title()

# Apply consolidation to egresos
if consolidacion_map:
    egresos['cliente'] = egresos['cliente'].replace(consolidacion_map)

egresos['Envase'] = egresos['Envase'].str.strip().str.title()
egresos['Envase'].value_counts()
egresos_volumen_cliente = egresos.groupby('cliente').agg(
    Volumen_Total_egresado_m3=('volumen', 'sum'),
    OIs=('orden_ing', 'nunique')
).reset_index()
egresos_volumen_cliente['Volumen_Total_egresado_m3'] = egresos_volumen_cliente['Volumen_Total_egresado_m3'] * (-1)
egresos_volumen_cliente = egresos_volumen_cliente.sort_values(by='OIs', ascending=False).reset_index(drop=True)



### CALCULO DE SCORING DE CLIENTES ###
print("Calculando scoring de clientes...")

# Función para normalizar valores entre 0 y 100
def normalizar_score(serie, invertir=False):
    """
    Normaliza valores entre 0 y 100
    invertir=True: valores más bajos son mejores (ejemplo: días de pago)
    invertir=False: valores más altos son mejores (ejemplo: volumen)
    """
    if serie.isna().all():
        return serie
    
    min_val = serie.min()
    max_val = serie.max()
    
    if min_val == max_val:
        return pd.Series([50] * len(serie), index=serie.index)
    
    if invertir:
        # Invertir: valores bajos = score alto
        normalized = 100 - ((serie - min_val) / (max_val - min_val) * 100)
    else:
        # Normal: valores altos = score alto
        normalized = (serie - min_val) / (max_val - min_val) * 100
    
    return normalized

# PASO 1: Normalizar precios a nivel de ITEM (concepto)
# Para cada concepto, normalizar los precios de todos los clientes que lo usan
print("Normalizando scores de precio a nivel de item...")
precio_con_score_item = precio_promedio_por_item_cliente.copy()
precio_con_score_item['Precio_Promedio_Item'] = pd.to_numeric(precio_con_score_item['Precio_Promedio_Item'], errors='coerce')

# Normalizar por cada concepto individualmente
precio_con_score_item['Score_Item'] = precio_con_score_item.groupby('concepto')['Precio_Promedio_Item'].transform(
    lambda x: normalizar_score(x, invertir=False)
)

# PASO 2: Calcular score promedio de precio por cliente (promedio de todos sus items)
score_precio_por_cliente = precio_con_score_item.groupby('Razon Social').agg(
    Score_Precio=('Score_Item', 'mean'),
    Precio_Promedio_Cliente=('Precio_Promedio_Item', 'mean'),
    Cantidad_Items=('concepto', 'count')
).reset_index()
score_precio_por_cliente = score_precio_por_cliente.rename(columns={'Razon Social': 'Cliente'})

# Merge de las tres fuentes de datos
scoring_base = pagadores[['Cliente', 'Promedio_dias_a_pago']].copy()
scoring_base = scoring_base.merge(score_precio_por_cliente[['Cliente', 'Score_Precio', 'Precio_Promedio_Cliente']], on='Cliente', how='outer')
scoring_base = scoring_base.merge(egresos_volumen_cliente.rename(columns={'cliente': 'Cliente'})[['Cliente', 'OIs']], on='Cliente', how='outer')

# Convertir métricas a float para evitar problemas con Decimal
scoring_base['Promedio_dias_a_pago'] = pd.to_numeric(scoring_base['Promedio_dias_a_pago'], errors='coerce')
scoring_base['Precio_Promedio_Cliente'] = pd.to_numeric(scoring_base['Precio_Promedio_Cliente'], errors='coerce')
scoring_base['OIs'] = pd.to_numeric(scoring_base['OIs'], errors='coerce')
scoring_base['Score_Precio'] = pd.to_numeric(scoring_base['Score_Precio'], errors='coerce')

# Filtrar solo clientes que tienen al menos 2 de las 3 métricas
scoring_base['Metricas_disponibles'] = scoring_base[['Promedio_dias_a_pago', 'Score_Precio', 'OIs']].notna().sum(axis=1)
scoring_final = scoring_base[scoring_base['Metricas_disponibles'] >= 2].copy()

# Calcular scores individuales (0-100)
# Días de pago: menos días = mejor score (invertir=True)
scoring_final['Score_Dias_Pago'] = normalizar_score(scoring_final['Promedio_dias_a_pago'], invertir=True)

# Precio: YA CALCULADO a nivel de item y promediado por cliente (Score_Precio ya está en scoring_final)

# Operaciones: mayor número de operaciones = mejor score
scoring_final['Score_Operaciones'] = normalizar_score(scoring_final['OIs'], invertir=False)

# Convertir scores a float para evitar errores con Decimal
scoring_final['Score_Dias_Pago'] = pd.to_numeric(scoring_final['Score_Dias_Pago'], errors='coerce')
scoring_final['Score_Precio'] = pd.to_numeric(scoring_final['Score_Precio'], errors='coerce')
scoring_final['Score_Operaciones'] = pd.to_numeric(scoring_final['Score_Operaciones'], errors='coerce')

# Calcular score final como promedio ponderado de los scores disponibles
# Peso: Cada métrica tiene el mismo peso (33.33%)
pesos = {
    'Score_Operaciones': 0.33,
    'Score_Precio': 0.33,
    'Score_Dias_Pago': 0.34
}

def calcular_score_ponderado(row):
    scores = []
    weights = []
    
    for score_col, peso in pesos.items():
        if pd.notna(row[score_col]):
            scores.append(row[score_col])
            weights.append(peso)
    
    if not scores:
        return None
    
    # Normalizar pesos para que sumen 1
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    
    # Calcular promedio ponderado
    score_final = sum(s * w for s, w in zip(scores, normalized_weights))
    return round(score_final, 2)

scoring_final['Score_Final'] = scoring_final.apply(calcular_score_ponderado, axis=1)

# Ordenar por score final descendente
scoring_final = scoring_final.sort_values('Score_Final', ascending=False).reset_index(drop=True)

# Agregar ranking
scoring_final['Ranking'] = range(1, len(scoring_final) + 1)

# Seleccionar columnas finales para el reporte
scoring_reporte = scoring_final[[
    'Ranking',
    'Cliente',
    'Score_Final',
    'Score_Operaciones',
    'Score_Precio',
    'Score_Dias_Pago',
    'OIs',
    'Precio_Promedio_Cliente',
    'Promedio_dias_a_pago',
    'Metricas_disponibles'
]].copy()

# Renombrar columnas para mejor presentación
scoring_reporte.columns = [
    'Ranking',
    'Cliente',
    'Score Final (0-100)',
    'Score Operaciones',
    'Score Precio',
    'Score Días Pago',
    'Número de Operaciones',
    'Precio Promedio ($)',
    'Promedio Días a Pago',
    'Métricas Disponibles'
]

# Formatear valores numéricos
scoring_reporte['Número de Operaciones'] = scoring_reporte['Número de Operaciones'].fillna(0).astype(int)
scoring_reporte['Precio Promedio ($)'] = scoring_reporte['Precio Promedio ($)'].round(0)
scoring_reporte['Promedio Días a Pago'] = scoring_reporte['Promedio Días a Pago'].round(1)

print(f"Scoring calculado para {len(scoring_reporte)} clientes")
print(f"Top 5 clientes:")
print(scoring_reporte.head(5)[['Ranking', 'Cliente', 'Score Final (0-100)']].to_string(index=False))

# Agregar scores normalizados a las hojas individuales
print("\nAgregando scores normalizados a hojas individuales...")

# Agregar score a precio_promedio_por_cliente
precio_promedio_por_cliente_con_score = precio_promedio_por_cliente.merge(
    scoring_final[['Cliente', 'Score_Precio']].rename(columns={'Score_Precio': 'Score Normalizado (0-100)'}),
    left_on='Razon Social',
    right_on='Cliente',
    how='left'
).drop(columns=['Cliente']).sort_values(by='Score Normalizado (0-100)', ascending=False).reset_index(drop=True)

# Agregar score a precio_promedio_por_item_cliente (score individual del item)
precio_promedio_por_item_cliente_con_score = precio_promedio_por_item_cliente.merge(
    precio_con_score_item[['Razon Social', 'concepto', 'Score_Item']].rename(columns={'Score_Item': 'Score Normalizado Item (0-100)'}),
    on=['Razon Social', 'concepto'],
    how='left'
).sort_values(by='Score Normalizado Item (0-100)', ascending=False).reset_index(drop=True)

# Agregar score a pagadores
pagadores_con_score = pagadores.merge(
    scoring_final[['Cliente', 'Score_Dias_Pago']].rename(columns={'Score_Dias_Pago': 'Score Normalizado (0-100)'}),
    on='Cliente',
    how='left'
).sort_values(by='Score Normalizado (0-100)', ascending=False).reset_index(drop=True)

# Agregar score a egresos_volumen_cliente
egresos_volumen_cliente_con_score = egresos_volumen_cliente.merge(
    scoring_final[['Cliente', 'Score_Operaciones']].rename(columns={'Score_Operaciones': 'Score Normalizado (0-100)'}),
    left_on='cliente',
    right_on='Cliente',
    how='left'
).drop(columns=['Cliente']).sort_values(by='Score Normalizado (0-100)', ascending=False).reset_index(drop=True)

# Exportar a Excel con Scoring como primera hoja
with pd.ExcelWriter('Informe Scoring 2025.xlsx') as writer:
    scoring_reporte.to_excel(writer, sheet_name='Scoring', index=False)
    facturacion.to_excel(writer, sheet_name='Facturacion', index=False)
    precio_promedio_por_concepto.to_excel(writer, sheet_name='Precio_Promedio_Concepto', index=False)
    precio_promedio_por_cliente_con_score.to_excel(writer, sheet_name='Precio_Promedio_Cliente', index=False)
    precio_promedio_por_item_cliente_con_score.to_excel(writer, sheet_name='Precio_Promedio_Item_Cliente', index=False)
    concepfc.to_excel(writer, sheet_name='Conceptos', index=False)
    saldos.to_excel(writer, sheet_name='Saldos (movimientos)', index=False)
    saldos_fechas.to_excel(writer, sheet_name='Fechas de pago', index=False)
    pagadores_con_score.to_excel(writer, sheet_name='Pagadores', index=False)
    egresos.to_excel(writer, sheet_name='Egresos del stock', index=False)
    egresos_volumen_cliente_con_score.to_excel(writer, sheet_name='Volumen Egresado por Cliente', index=False)

# save all as csv in data_scoring folder
scoring_reporte.to_csv('data_scoring/scoring_clientes.csv', index=False)
facturacion.to_csv('data_scoring/facturacion.csv', index=False)
precio_promedio_por_concepto.to_csv('data_scoring/precio_promedio_por_concepto.csv', index=False)
precio_promedio_por_cliente.to_csv('data_scoring/precio_promedio_por_cliente.csv', index=False)
precio_promedio_por_item_cliente.to_csv('data_scoring/precio_promedio_por_item_cliente.csv', index=False)
concepfc.to_csv('data_scoring/conceptos.csv', index=False)
saldos.to_csv('data_scoring/saldos.csv', index=False)
saldos_fechas.to_csv('data_scoring/fechas_de_pago.csv', index=False)
pagadores.to_csv('data_scoring/pagadores.csv', index=False)
egresos.to_csv('data_scoring/egresos_del_stock.csv', index=False)
egresos_volumen_cliente.to_csv('data_scoring/volumen_egresado_por_cliente.csv', index=False)

print("\n✓ Informe de Scoring generado exitosamente: 'Informe Scoring 2025.xlsx'")
print("✓ Datos exportados a la carpeta 'data_scoring/'")

