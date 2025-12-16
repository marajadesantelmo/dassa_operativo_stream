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
    Cantidad_Facturas_Concepto=('Factura', 'count')
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


with pd.ExcelWriter('ver_facturacion_conceptos_ppales.xlsx') as writer:
    facturacion.to_excel(writer, sheet_name='Facturacion', index=False)
    precio_promedio_por_concepto.to_excel(writer, sheet_name='Precio_Promedio_Concepto', index=False)
    precio_promedio_por_cliente.to_excel(writer, sheet_name='Precio_Promedio_Cliente', index=False)
    precio_promedio_por_item_cliente.to_excel(writer, sheet_name='Precio_Promedio_Item_Cliente', index=False)
    concepfc.to_excel(writer, sheet_name='Conceptos', index=False)
    saldos.tail(1000).to_excel(writer, sheet_name='Saldos (utlimos 1000 mov)', index=False)
    saldos_fechas.to_excel(writer, sheet_name='Fechas de pago', index=False)
    pagadores.to_excel(writer, sheet_name='Pagadores', index=False)