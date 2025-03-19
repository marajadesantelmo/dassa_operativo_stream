import pyodbc
import pandas as pd
import os
from tokens import username, password


if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream')
elif os.path.exists('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream'):
    os.chdir('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream')
else:
    print("Se usa working directory por defecto")

path = '//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/'

print('Actualizando información operativa Orden del Día DASSA')
print('Descargando datos de SQL')
server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

print('Clientes Global comex')
cursor.execute(f"""
SELECT  apellido
FROM DEPOFIS.DASSA.[Clientes]
WHERE consolida = 1518
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
clientes_global_comex = pd.DataFrame.from_records(rows, columns=columns)

clientes_global_comex['apellido'] = clientes_global_comex['apellido'].str.title().str.strip()
clientes_global_comex['apellido'] = clientes_global_comex['apellido'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
global_comex = pd.DataFrame({'apellido': ['Global Comex Srl']})
clientes_global_comex = pd.concat([clientes_global_comex, global_comex])
clientes_global_comex.to_csv('data/clientes_global_comex.csv', index=False)

print('Clientes Global Rover')
cursor.execute(f"""
SELECT  apellido
FROM DEPOFIS.DASSA.[Clientes]
WHERE consolida = 1149
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
clientes_global_rover = pd.DataFrame.from_records(rows, columns=columns)

clientes_global_rover['apellido'] = clientes_global_rover['apellido'].str.title().str.strip()
clientes_global_rover['apellido'] = clientes_global_rover['apellido'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
global_rover = pd.DataFrame({'apellido': ['Global Rover Srl']})
clientes_global_rover = pd.concat([clientes_global_rover, global_rover])
clientes_global_rover.to_csv('data/clientes_global_rover.csv', index=False)
