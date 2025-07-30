import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
from tokens import username, password, url_supabase, key_supabase
from supabase import create_client, Client
supabase_client = create_client(url_supabase, key_supabase)

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
global_comex['apellido'] = global_comex['apellido'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
clientes_global_comex = pd.concat([clientes_global_comex, global_comex])
clientes_global_comex['user'] = 'globalcomex'

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
global_rover['apellido'] = global_rover['apellido'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
clientes_global_rover = pd.concat([clientes_global_rover, global_rover])
clientes_global_rover['user'] = 'globalrover'

def delete_table_data_user(table_name):
    supabase_client.from_(table_name).delete().neq('user', None).execute()

