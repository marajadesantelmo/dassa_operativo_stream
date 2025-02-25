import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
from tokens import username, password
from utils import rellenar_df_vacio
import gspread
from gspread_dataframe import set_with_dataframe

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

fecha = datetime.now().strftime('%Y-%m-%d')
fecha_ant = datetime.now() - timedelta(days=120)
fecha_ant = fecha_ant.strftime('%Y-%m-%d')
fecha_ant_ult3dias = datetime.now() - timedelta(days=3)
fecha_ant_ult3dias = fecha_ant_ult3dias.strftime('%Y-%m-%d')
first_day_prev_month = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
last_day_prev_month = datetime.now().replace(day=1) - timedelta(days=1)

cursor.execute(f"""
SELECT Factura, tipo, fecha_emi, fecha_vto, [Neto Gravado], [Neto No Gravado], [Importe Total], [Razon Social]
FROM DEPOFIS.DASSA.Facturacion
WHERE fecha_emi BETWEEN '{first_day_prev_month.strftime('%Y-%m-%d')}' AND '{last_day_prev_month.strftime('%Y-%m-%d')}'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
facturacion = pd.DataFrame.from_records(rows, columns=columns)

facturacion.to_excel('ver_facturacion.xlsx', index=False)

