'''
Script que actualiza los correos de los clientes
'''
import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
from tokens import username, password


if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream')
elif os.path.exists('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream'):
    os.chdir('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream')
else:
    print("Se usa working directory por defecto")

path = '//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/'

### ARRIBOS ####

print('Actualizando información operativa Orden del Día DASSA')
print('Descargando datos de SQL')
server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

#Descargo contenedores IMPO a arribar
# Execute the SQL query
cursor.execute("""
SELECT clie_nro, apellido, email
FROM DEPOFIS.DASSA.[Clientes]
""")

# Fetch and print the results
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
clientes = pd.DataFrame.from_records(rows, columns=columns)

clientes['apellido'] = clientes['apellido'].str.strip()
clientes['apellido'] = clientes['apellido'].str.title()

clientes.to_csv('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/contactos_clientes.csv', index=False)

print('Datos descargados')
conn.close()

