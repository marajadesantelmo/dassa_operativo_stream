
import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
from tokens import username, password, url_supabase, key_supabase

print("Preparando entorno de trabajo...")

if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/auto'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/auto')
    print("Directorio cambiado a: //dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/auto")
elif os.path.exists('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream/auto'):
    os.chdir('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream/auto')
    print("Directorio cambiado a: C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream/auto")
else:
    print("Se usa working directory por defecto")

print("Cargando enlaces de Tally BI...")
path = '//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/auto'


### DESCARGA DE DATOS SQL ####
print('Descargando datos de SQL')
#server = '101.44.8.58\\SQLEXPRESS_X86,1436'
server = 'SQL01\\SQLEXPRESS_X86,1437'
print("Conectando a la base de datos SQL...")
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()
print("Conexión establecida con SQL Server.")

# List available tables
print("\nTablas disponibles en la base de datos:")
cursor.execute("""
    SELECT *
    FROM Moneda_Tipos_De_Cambio_Dia
""")

df = pd.read_sql_query("SELECT * FROM Moneda_Tipos_De_Cambio_Dia", conn)

