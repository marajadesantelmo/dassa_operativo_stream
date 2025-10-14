import pandas as pd
import pyodbc
from datetime import datetime
from tokens import username, password, password_gmail 
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import gspread
from gspread_dataframe import set_with_dataframe

path = "//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/"

server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

gc = gspread.service_account(filename='//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/credenciales_gsheets.json')

cursor.execute("""
    SELECT cliente AS Cliente, cantidad AS Cantidad, kilos AS Peso, volumen AS Volumen, 
            orden_ing, suborden, renglon, tipo_oper AS Tipo, env.detalle AS Envase, fecha_ing AS Fecha_Ingreso
    FROM [DEPOFIS].[DASSA].[Existente en Stock] e
    JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
existente = pd.DataFrame.from_records(rows, columns=columns)

cursor.execute("""
    SELECT orden_ing, suborden, renglon, ubicacion
    FROM [DEPOFIS].[DASSA].[Ubic_St]
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ubicaciones_existente = pd.DataFrame.from_records(rows, columns=columns)

def crear_operacion(df): 
    df['Operacion'] = (df['orden_ing'].astype(str) + '-' + df['suborden'].astype(str) + '-' + df['renglon'].astype(str))
    df.drop(columns=['orden_ing', 'suborden', 'renglon'], inplace=True)
    return(df)

ubicaciones_existente = crear_operacion(ubicaciones_existente)
existente = crear_operacion(existente)
ubicaciones_existente['ubicacion'] = ubicaciones_existente['ubicacion'].str.strip()
existente = pd.merge(existente, ubicaciones_existente[['Operacion', 'ubicacion']], on='Operacion', how='left')
familias_ubicaciones = pd.read_excel('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/flias_ubicaciones.xlsx')
existente = pd.merge(existente, familias_ubicaciones[['ubicacion', 'ubicacion_familia']], on='ubicacion', how='left')

existente_plz = existente[existente['ubicacion_familia'].isin(['Plazoleta', 'Temporal'])]
existente_alm = existente[~existente['ubicacion_familia'].isin(['Plazoleta', 'Temporal'])]

sheet = gc.create('Control_Stock_DASSA_{mes}_{year}'.format(mes=datetime.now().strftime('%m'), year=datetime.now().year))
