import pandas as pd
import pyodbc

clientes = pd.read_csv('contacto_clientes.csv')
alertas_balanza = pd.read_csv('alertas_balanza.csv')

today = pd.Timestamp.today().strftime('%Y-%m-%d')

conn = pyodbc.connect('DRIVER={SQL Server};SERVER=101.44.8.58\\SQLEXPRESS_X86,1436;UID=dassa;PWD=Da$$a3065!')
cursor = conn.cursor()

cursor.execute(f"""
SELECT idpesada, idcliente, cl_nombre, idata, ata_nombre, entrada, salida, peso_bruto, peso_tara, peso_neto, contenedor
FROM DEPOFIS.DASSA.BALANZA_PESADA
WHERE fecha > '{today}'
""")

rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
balanza = pd.DataFrame.from_records(rows, columns=columns)

balanza.to_excel('ver_balanza.xlsx', index=False)

balanza.columns