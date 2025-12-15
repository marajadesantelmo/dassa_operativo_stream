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
SELECT fecha, fecha_alta, fecha_vto, tp_cpte, aplicacion, adicional, debe, haber
FROM DEPOFIS.DASSA.CtaCcteD
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
saldos= pd.DataFrame.from_records(rows, columns=columns)

saldos_grouped = saldos.groupby(['adicional', 'aplicacion']).apply(
    lambda group: pd.Series({
        'fecha_vto_debe': group[group['debe'] > 0]['fecha_vto'].min() if (group['debe'] > 0).any() else None,
        'fecha_haber': group[group['haber'] > 0]['fecha'].min() if (group['haber'] > 0).any() else None
    }), include_groups=False).reset_index()

saldos_grouped['dias_pago'] = (pd.to_datetime(saldos_grouped['fecha_haber']) - pd.to_datetime(saldos_grouped['fecha_vto_debe'])).dt.days
saldos_grouped = saldos_grouped.dropna(subset=['dias_pago'])
saldos_grouped = saldos_grouped[saldos_grouped['fecha_haber'].str.contains('2025-|2026-|2027-')]

promedio_dias_pago = saldos_grouped.groupby('adicional')['dias_pago'].mean().reset_index()
promedio_dias_pago.columns = ['adicional', 'promedio_dias_pago']
promedio_dias_pago = promedio_dias_pago.sort_values('promedio_dias_pago', ascending=False)

with pd.ExcelWriter('ver_facturacion_conceptos_ppales.xlsx') as writer:
    facturacion.to_excel(writer, sheet_name='Facturacion', index=False)
    concepfc.to_excel(writer, sheet_name='Conceptos', index=False)