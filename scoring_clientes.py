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
    f.[Neto Gravado], 
    f.[Neto No Gravado], 
    f.[Importe Total], 
    f.[Unitario Final]
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
facturacion['Importe Total'] = facturacion['Importe Total'].fillna(0).astype(float).round(0)
facturacion.to_excel('ver_facturacion_conceptos_ppales.xlsx')