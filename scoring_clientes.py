""" Script para generación de scoring de clientes basado en facturación de conceptos principales, saldos, etc."""


from tokens import username, password
import pyodbc
from datetime import datetime, timedelta
import pandas as pd
server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()
fecha_ant = datetime.now() - timedelta(days=180)
fecha_ant= fecha_ant.strftime('%Y-%m-%d')
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
AND f.concepto IN (10001, 10002, 10003, 10111, 10112, 10113, 10114, 10115, 10116, 20001, 20002, 20003, 20004, 20005, 20006)
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
facturacion = pd.DataFrame.from_records(rows, columns=columns)
facturacion['Concepto_Detalle'] = facturacion['Concepto_Detalle'].str.strip().str.title()
facturacion['Razon Social'] = facturacion['Razon Social'].str.strip().str.title()
facturacion['Unitario Final'] = facturacion['Unitario Final'].fillna(0).round(0).astype(int)

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
egresos['Envase'] = egresos['Envase'].str.strip().str.title()
egresos['Envase'].value_counts()
egresos_mercaderia = egresos[egresos['Envase'].str.contains('Bultos|Pallets|Rollos|Cajas|Cajones', case=False, na=False)]
egresos_volumen_cliente = egresos_mercaderia.groupby('cliente').agg(
    Volumen_Total_egresado_m3=('volumen', 'sum'),
    OIs=('orden_ing', 'count')
).reset_index()
egresos_volumen_cliente['Volumen_Total_egresado_m3'] = egresos_volumen_cliente['Volumen_Total_egresado_m3'] * (-1)
egresos_volumen_cliente = egresos_volumen_cliente.sort_values(by='Volumen_Total_egresado_m3', ascending=False).reset_index(drop=True)

### Tipo de cliente
cursor.execute(f"""
SELECT *
FROM DEPOFIS.DASSA.[Clientes]
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
clientes = pd.DataFrame.from_records(rows, columns=columns)
clientes['tipo_cl'].value_counts()

### CALCULO DE SCORING DE CLIENTES ###
print("Calculando scoring de clientes...")

# Normalizar nombres de clientes para hacer merge
pagadores['Cliente_norm'] = pagadores['Cliente'].str.strip().str.title()
precio_promedio_por_item_cliente['Cliente_norm'] = precio_promedio_por_item_cliente['Razon Social'].str.strip().str.title()
egresos_volumen_cliente['Cliente_norm'] = egresos_volumen_cliente['cliente'].str.strip().str.title()

# Agregar precio promedio por cliente desde precio_promedio_por_item_cliente
precio_cliente_agg = precio_promedio_por_item_cliente.groupby('Cliente_norm').agg(
    Precio_Promedio_Cliente=('Precio_Promedio_Item', 'mean')
).reset_index()

# Merge de las tres fuentes de datos
scoring_base = pagadores[['Cliente_norm', 'Promedio_dias_a_pago']].copy()
scoring_base = scoring_base.merge(precio_cliente_agg, on='Cliente_norm', how='outer')
scoring_base = scoring_base.merge(egresos_volumen_cliente[['Cliente_norm', 'Volumen_Total_egresado_m3']], on='Cliente_norm', how='outer')

# Convertir métricas a float para evitar problemas con Decimal
scoring_base['Promedio_dias_a_pago'] = pd.to_numeric(scoring_base['Promedio_dias_a_pago'], errors='coerce')
scoring_base['Precio_Promedio_Cliente'] = pd.to_numeric(scoring_base['Precio_Promedio_Cliente'], errors='coerce')
scoring_base['Volumen_Total_egresado_m3'] = pd.to_numeric(scoring_base['Volumen_Total_egresado_m3'], errors='coerce')

# Filtrar solo clientes que tienen al menos 2 de las 3 métricas
scoring_base['Metricas_disponibles'] = scoring_base[['Promedio_dias_a_pago', 'Precio_Promedio_Cliente', 'Volumen_Total_egresado_m3']].notna().sum(axis=1)
scoring_final = scoring_base[scoring_base['Metricas_disponibles'] >= 2].copy()

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

# Calcular scores individuales (0-100)
# Días de pago: menos días = mejor score (invertir=True)
scoring_final['Score_Dias_Pago'] = normalizar_score(scoring_final['Promedio_dias_a_pago'], invertir=True)

# Precio: mayor precio = mejor score (pagan más por servicios)
scoring_final['Score_Precio'] = normalizar_score(scoring_final['Precio_Promedio_Cliente'], invertir=False)

# Volumen: mayor volumen = mejor score
scoring_final['Score_Volumen'] = normalizar_score(scoring_final['Volumen_Total_egresado_m3'], invertir=False)

# Convertir scores a float para evitar errores con Decimal
scoring_final['Score_Dias_Pago'] = pd.to_numeric(scoring_final['Score_Dias_Pago'], errors='coerce')
scoring_final['Score_Precio'] = pd.to_numeric(scoring_final['Score_Precio'], errors='coerce')
scoring_final['Score_Volumen'] = pd.to_numeric(scoring_final['Score_Volumen'], errors='coerce')

# Calcular score final como promedio ponderado de los scores disponibles
# Peso: Volumen 40%, Precio 35%, Dias Pago 25%
pesos = {
    'Score_Volumen': 0.40,
    'Score_Precio': 0.35,
    'Score_Dias_Pago': 0.25
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
    'Cliente_norm',
    'Score_Final',
    'Score_Volumen',
    'Score_Precio',
    'Score_Dias_Pago',
    'Volumen_Total_egresado_m3',
    'Precio_Promedio_Cliente',
    'Promedio_dias_a_pago',
    'Metricas_disponibles'
]].copy()

# Renombrar columnas para mejor presentación
scoring_reporte.columns = [
    'Ranking',
    'Cliente',
    'Score Final (0-100)',
    'Score Volumen',
    'Score Precio',
    'Score Días Pago',
    'Volumen Total (m³)',
    'Precio Promedio ($)',
    'Promedio Días a Pago',
    'Métricas Disponibles'
]

# Formatear valores numéricos
scoring_reporte['Volumen Total (m³)'] = scoring_reporte['Volumen Total (m³)'].round(2)
scoring_reporte['Precio Promedio ($)'] = scoring_reporte['Precio Promedio ($)'].round(0)
scoring_reporte['Promedio Días a Pago'] = scoring_reporte['Promedio Días a Pago'].round(1)

print(f"Scoring calculado para {len(scoring_reporte)} clientes")
print(f"Top 5 clientes:")
print(scoring_reporte.head(5)[['Ranking', 'Cliente', 'Score Final (0-100)']].to_string(index=False))

# Exportar a Excel con Scoring como primera hoja
with pd.ExcelWriter('Informe Scoring 2025.xlsx') as writer:
    scoring_reporte.to_excel(writer, sheet_name='Scoring', index=False)
    facturacion.to_excel(writer, sheet_name='Facturacion', index=False)
    precio_promedio_por_concepto.to_excel(writer, sheet_name='Precio_Promedio_Concepto', index=False)
    precio_promedio_por_cliente.to_excel(writer, sheet_name='Precio_Promedio_Cliente', index=False)
    precio_promedio_por_item_cliente.to_excel(writer, sheet_name='Precio_Promedio_Item_Cliente', index=False)
    concepfc.to_excel(writer, sheet_name='Conceptos', index=False)
    saldos.tail(1000).to_excel(writer, sheet_name='Saldos (utlimos 1000 mov)', index=False)
    saldos_fechas.to_excel(writer, sheet_name='Fechas de pago', index=False)
    pagadores.to_excel(writer, sheet_name='Pagadores', index=False)
    egresos.to_excel(writer, sheet_name='Egresos del stock', index=False)
    egresos_volumen_cliente.to_excel(writer, sheet_name='Volumen Egresado por Cliente', index=False)

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

