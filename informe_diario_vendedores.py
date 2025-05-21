import pandas as pd
import pyodbc
from datetime import datetime
from tokens import username, password
import os

server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

print('Clientes Global comex')
cursor.execute(f"""
SELECT  apellido, clie_nro, vendedor
FROM DEPOFIS.DASSA.[Clientes]
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
clientes= pd.DataFrame.from_records(rows, columns=columns)

clientes['apellido'] = clientes['apellido'].str.strip().str.title()
clientes['apellido'] = clientes['apellido'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)

dic_vendedores = pd.read_excel('diccionario_vendedores_puros_dassa.xlsx')

verificaciones_impo = pd.read_csv('data/verificaciones_impo.csv')
retiros_impo = pd.read_csv('data/retiros_impo.csv')
otros_impo = pd.read_csv('data/otros_impo.csv')

verificaciones_expo = pd.read_csv('data/verificaciones_expo.csv')
remisiones_expo = pd.read_csv('data/remisiones.csv')
consolidados_expo = pd.read_csv('data/consolidados.csv')
otros_expo = pd.read_csv('data/otros_expo.csv')

