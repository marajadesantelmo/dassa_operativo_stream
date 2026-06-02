import pyodbc
import pandas as pd
from tokens import username, password

server = 'SQL01\\SQLEXPRESS_X86,1437'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)

CONTENEDOR = 'MRKU-728668-8'

print(f"Buscando contenedor: {CONTENEDOR}\n")

cursor = conn.cursor()
cursor.execute(f"""
SELECT e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing,
       e.contenedor, e.conocim1, e.desc_merc, e.dimension, e.tipo_cnt, e.volumen,
       env.detalle AS Envase, e.conocim2, e.kilos, e.bookings, e.precinto, e.kilos AS peso
FROM [DEPOFIS].[DASSA].[Ingresadas En Stock] e
JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.contenedor = '{CONTENEDOR}'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ingresada = pd.DataFrame.from_records(rows, columns=columns)

print(f"=== INGRESADO EN STOCK ({len(ingresada)} registros) ===")
print(ingresada.to_string(index=False) if not ingresada.empty else "Sin resultados.")

ingresada.to_csv('ver_ingresada.csv', index=False)

print()

cursor.execute(f"""
SELECT e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing,
       e.contenedor, e.desc_merc, e.conocim AS conocim1, e.dimension, e.tipo_cnt,
       env.detalle AS Envase, e.fecha_egr, e.bookings, e.volumen, e.precinto, e.kilos AS peso
FROM [DEPOFIS].[DASSA].[Egresadas del stock] e
JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.contenedor = '{CONTENEDOR}'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
egresada = pd.DataFrame.from_records(rows, columns=columns)

print(f"=== EGRESADO DEL STOCK ({len(egresada)} registros) ===")
print(egresada.to_string(index=False) if not egresada.empty else "Sin resultados.")

egresada.to_csv('ver_egresada.csv', index=False)

print()

cursor.execute(f"""
SELECT e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing,
       e.contenedor, e.conocim1, e.desc_merc, e.dimension, e.tipo_cnt, e.volumen,
       env.detalle AS Envase, e.conocim2, e.kilos, e.bookings, e.precinto, e.kilos AS peso
FROM [DEPOFIS].[DASSA].[Existente en Stock] e
JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.contenedor = '{CONTENEDOR}'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
existente = pd.DataFrame.from_records(rows, columns=columns)

print(f"=== EXISTENTE EN STOCK ({len(existente)} registros) ===")
print(existente.to_string(index=False) if not existente.empty else "Sin resultados.")

existente.to_csv('ver_existente.csv', index=False)

conn.close()
