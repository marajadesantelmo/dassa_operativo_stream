import pandas as pd
import pyodbc

conn = pyodbc.connect('DRIVER={SQL Server};SERVER=101.44.8.58\\SQLEXPRESS_X86,1436;UID=dassa;PWD=Da$$a3065!')
cursor = conn.cursor()

cursor.execute(f"""
SELECT *
FROM DEPOFIS.DASSA.BALANZA_PESADA
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
balanza = pd.DataFrame.from_records(rows, columns=columns)
balanza = balanza.tail(100)
balanza.to_excel('ver_balanza.xlsx', index=False)