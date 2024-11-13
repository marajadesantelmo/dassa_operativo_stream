#%% Setting
import pyodbc
import pandas as pd
import os
import gspread
from gspread_dataframe import set_with_dataframe
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import time

if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/automatizaciones'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/automatizaciones')
else:
    print("Se usa working directory por defecto")
# CONEXION SQL
print('Descargando datos de SQL')
server = '101.44.8.58\\SQLEXPRESS_X86,1436'
username = 'dassa'
password = 'Da$$a3065!'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

fecha = datetime.now().strftime('%Y-%m-%d')
fecha_ant1 = datetime.now() - timedelta(days=120)
fecha_ant1 = fecha_ant1.strftime('%Y-%m-%d')
fecha_ant = datetime.now() - timedelta(days=120)
fecha_ant = fecha_ant.strftime('%Y-%m-%d')
fecha_ant_ult3dias = datetime.now() - timedelta(days=3)
fecha_ant_ult3dias = fecha_ant_ult3dias.strftime('%Y-%m-%d')

#%% Arribos
#Descargo contenedores IMPO a arribar
cursor.execute(f"""
    SELECT c.contenedor, c.buque, c.terminal, c.fecha, c.turno,  c.peso,  c.operacion, 
           c.arribado, c.dimension, c.tipo_cnt, c.despachant, c.precinto, c.bookings,  cl.apellido AS cliente
    FROM [DEPOFIS].[DASSA].[CORDICAR] c
    JOIN DEPOFIS.DASSA.[Clientes] cl ON c.cliente = cl.clie_nro
    WHERE c.tipo_oper = 'IMPORTACION' 
    AND c.fecha > '{fecha_ant1}'
""")   
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
arribos = pd.DataFrame.from_records(rows, columns=columns)

#Descargo EXPO a arribar
cursor.execute(f"""
    SELECT c.orden, c.contenedor, c.buque, c.terminal, c.fecha, c.turno, c.peso, c.operacion, c.arribado, 
            c.chapa_trac, c.bookings, c.tipo_oper, cl.apellido AS cliente, c.desc_merc, c.precinto, c.dimension
    FROM [DEPOFIS].[DASSA].[CORDICAR] c JOIN DEPOFIS.DASSA.[Clientes] cl ON c.cliente = cl.clie_nro 
    WHERE c.tipo_oper != 'IMPORTACION' AND c.fecha >= '{fecha_ant1}'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
arribos_expo = pd.DataFrame.from_records(rows, columns=columns)

#Descargo Contendores Ingresados
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, fecha_ing, tipo_oper, contenedor FROM DEPOFIS.DASSA.[Ingresadas En Stock]
    WHERE fecha_ing BETWEEN '{fecha_ant}' AND '{fecha}'
    AND tipo_oper = 'IMPORTACION'
    AND suborden= 0
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ingresos = pd.DataFrame.from_records(rows, columns=columns)


conn.close()

#%% Formateo y procesamiento de datos Arribos
print('Procesando datos')

def transformar(df):
    # Dimension
    df['dimension'] = pd.to_numeric(df['dimension'])
    df.loc[df['dimension'] == 20, 'dimension'] = 30
    df.loc[(df['dimension'] == 40) & (df['tipo_cnt'] == 'HC'), 'dimension'] = 70
    df.loc[(df['dimension'] == 40) & (df['tipo_cnt'] != 'HC'), 'dimension'] = 60
    df['dimension'] = df['dimension'].astype(int)
    df['dimension'] = df['dimension'].astype(str)
    # Terminal
    df['terminal'] = df['terminal'].astype(str)
    terminal_mapping = {
        '10057': 'TRP',
        '10073': 'Exolgan',
        '10068': 'Terminal 4'}
    df['terminal'] = df['terminal'].replace(terminal_mapping)
    # Contenedor
    df['contenedor'] = df['contenedor'].str.strip()
    df = df[df['contenedor'] != '']
    # Operacion
    df['operacion'] = df['operacion'].str.strip()
    return df

def crear_operacion(df): 
    df['operacion'] = (df['orden_ing'].astype(str) + '-' + df['suborden'].astype(str) + '-' + df['renglon'].astype(str))
    return(df)

# IMPO a arribar
arribos = transformar(arribos)
arribos['Turno2'] = arribos['turno'].str.strip().apply(lambda x: x[:2] + ":" + x[2:] + ":00" if x.strip() else pd.NaT)
arribos['Fecha y Hora'] = pd.to_datetime(arribos['fecha']) + pd.to_timedelta(arribos['Turno2'])
current_time = pd.Timestamp.now()
arribos['tiempo_transcurrido'] = current_time - arribos['Fecha y Hora']
arribos['tiempo_transcurrido'] = arribos['tiempo_transcurrido'].apply(lambda x: '-' if x.days < 0 else '{:02}:{:02}'.format(x.seconds // 3600, (x.seconds // 60) % 60))
arribos['cliente'] =  arribos['cliente'].str.title()
arribos['buque'] =  arribos['buque'].str.title()

# EXPO a arribar
arribos_expo['terminal'] = arribos_expo['terminal'].astype(str)
terminal_mapping = {
    '10057': 'TRP',
    '10073': 'Exolgan',
    '10068': 'Terminal 4'}
arribos_expo['terminal'] = arribos_expo['terminal'].replace(terminal_mapping)
arribos_expo['contenedor'] = arribos_expo['contenedor'].str.strip()
arribos_expo['operacion'] = arribos_expo['operacion'].str.strip()
arribos_expo['tipo_oper'] = arribos_expo['tipo_oper'].str.strip()
arribos_expo['cliente'] =  arribos_expo['cliente'].str.strip()
arribos_expo['cliente'] =  arribos_expo['cliente'].str.title()
arribos_expo['arribado'] = arribos_expo['arribado'].replace({0: 'Pendiente', 1: 'Arribado'})

arribos_expo_historico_horarios = pd.read_csv('arribos_expo_historico_horarios.csv')
arribos_expo = pd.merge(arribos_expo, arribos_expo_historico_horarios, on=['orden'], how='left')
arribos_expo['arribado'] = arribos_expo['estado'].fillna(arribos_expo['arribado'])
arribos_expo = arribos_expo.drop(columns=['estado'])

arribos_expo_carga = arribos_expo[arribos_expo['tipo_oper'] != 'VACIO']
arribos_expo_carga = arribos_expo_carga[['fecha', 'orden', 'contenedor' , 'cliente', 'bookings', 'desc_merc', 'arribado']]
arribos_expo_carga.columns = ['Fecha', 'Operacion', 'Contenedor', 'Cliente', 'Booking', 'Descripcion', 'Estado']
arribos_expo_carga['Descripcion'] = arribos_expo_carga['Descripcion'].str.strip()
arribos_expo_carga['Booking'] = arribos_expo_carga['Booking'].str.strip()

arribos_expo_ctns = arribos_expo[arribos_expo['tipo_oper'] == 'VACIO']
arribos_expo_ctns = arribos_expo_ctns[['fecha', 'orden', 'contenedor' , 'cliente', 'bookings', 'precinto', 'arribado']]
arribos_expo_ctns.columns = ['Fecha', 'Operacion', 'Contenedor', 'Cliente', 'Booking', 'Precinto', 'Estado']
arribos_expo_ctns['Booking'] = arribos_expo_ctns['Booking'].str.strip()

#Contenedores ingresados
ingresos['contenedor'] = ingresos['contenedor'].str.strip()
arribados = arribos[arribos['arribado']==1]

arribos = pd.merge(arribos, ingresos[['contenedor', 'fecha_ing']], on=['contenedor'], how='left')
arribos['Pendiente'] = arribos['fecha_ing'].isna().astype(int)

arribos = arribos[['fecha', 'turno', 'terminal', 'contenedor', 'cliente', 'bookings', 'operacion', 'fecha_ing']]
arribos.columns = ['Fecha', 'Turno', 'Terminal', 'Contenedor', 'Cliente', 'Booking', 'Operacion', 'Fecha Ingreso']
arribos['Cliente'] = arribos['Cliente'].str.strip()
arribos['Booking'] = arribos['Booking'].str.strip()
arribos['Turno'] = arribos['Turno'].str.strip().apply(lambda x: x[:2] + ":" + x[2:]  if x.strip() else pd.NaT)
arribos.to_csv('data/arribos_impo_historico.csv', index=False)

