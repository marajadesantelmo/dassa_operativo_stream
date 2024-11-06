import pyodbc
import pandas as pd
import os
import gspread
from gspread_dataframe import set_with_dataframe
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import time
from tokens import username, password
from utils import rellenar_df_vacio
if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_streamlit'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_streamlit')
elif os.path.exists('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_streamlit'):
    os.chdir('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_streamlit')
else:
    print("Se usa working directory por defecto")

def limpiar_columnas(df):
    columns = ['cliente', 'tipo_oper', 'desc_merc', 'Envase']
    for column in columns:
        if column in df.columns:
            df[column] = df[column].str.strip()
            df[column] = df[column].str.title()
    return df

# CONEXION SQL
def limpiar_columnas(df):
    columns = ['cliente', 'tipo_oper', 'desc_merc', 'Envase']
    for column in columns:
        if column in df.columns:
            df[column] = df[column].str.strip()
            df[column] = df[column].str.title()
    return df

print('Descargando datos de SQL')
server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()
fecha = datetime.now().strftime('%Y-%m-%d')
fecha_ant = datetime.now() - timedelta(days=120)
fecha_ant = fecha_ant.strftime('%Y-%m-%d')
fecha_ant_ult3dias = datetime.now() - timedelta(days=3)
fecha_ant_ult3dias = fecha_ant_ult3dias.strftime('%Y-%m-%d')
#Existente
cursor.execute("""
    SELECT e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing, 
    e.contenedor, e.conocim1, e.desc_merc, e.dimension, e.tipo_cnt, e.volumen, env.detalle AS Envase, 
    e.cantidad, e.conocim2, e.kilos, e.bookings, e.precinto
    FROM [DEPOFIS].[DASSA].[Existente en Stock] e
    JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
existente = pd.DataFrame.from_records(rows, columns=columns)
#Descargo Ubicaciones
#Ubicaciones del exisntente
cursor.execute("""
    SELECT orden_ing, suborden, renglon, ubicacion
    FROM [DEPOFIS].[DASSA].[Ubic_St]
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ubicaciones_existente = pd.DataFrame.from_records(rows, columns=columns)
#Ubicaciones del egresado
cursor.execute(f"""
SELECT  orden_ing, suborden, renglon, ubicacion
FROM [DEPOFIS].[DASSA].[Egresadas del stock]
WHERE fecha_egr > '{fecha_ant}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ubicaciones_egresado = pd.DataFrame.from_records(rows, columns=columns)
ubicaciones = pd.concat([ubicaciones_existente, ubicaciones_egresado], ignore_index=True)

#Egresado
cursor.execute(f"""
SELECT  e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing, 
e.contenedor, e.desc_merc, e.conocim AS conocim1, e.dimension, e.tipo_cnt, e.volumen, env.detalle AS Envase, e.fecha_egr, e.cantidad, e.bookings
FROM [DEPOFIS].[DASSA].[Egresadas del stock] e
JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.fecha_egr > '{fecha_ant}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
egresado = pd.DataFrame.from_records(rows, columns=columns)
egresado['cantidad'] *= -1
egresado['volumen'] *= -1
#Verificaciones realizadas
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, fechaverif            
    FROM [DEPOFIS].[DASSA].[Todo] 
    WHERE fechaverif > '{fecha_ant}'
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
verificaciones_realizadas = pd.DataFrame.from_records(rows, columns=columns)
#Salidas validadas
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, validada          
    FROM [DEPOFIS].[DASSA].[Salidas] 
    WHERE validada > '{fecha_ant}'
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
salidas = pd.DataFrame.from_records(rows, columns=columns)
#Salidas vacios validadas
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, validada          
    FROM [DEPOFIS].[DASSA].[Vacios] 
    WHERE validada > '{fecha_ant}'
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
salidas_vacios = pd.DataFrame.from_records(rows, columns=columns)
#Turnos
cursor.execute(f"""
SELECT orden_ing, suborden, renglon, destino, dia, hora, observa, conocim2
FROM DEPOFIS.DASSA.[TURNOSSA] as e
WHERE dia >= '{fecha}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
turnos = pd.DataFrame.from_records(rows, columns=columns)
turnos['destino'] = turnos['destino'].str.strip()
turnos['Estado'] = 'Pendiente'
turnos['observa'] = turnos['observa'].str.strip()
turnos = turnos[turnos['orden_ing'] != 0]
#Genero ids para hacer matcheos
def generate_id(df):
    df['id'] = df[['orden_ing', 'suborden', 'renglon']].astype(str).agg('-'.join, axis=1)
    df.drop(columns=['orden_ing', 'suborden', 'renglon'], inplace=True)
    return df

turnos['id'] = turnos[['orden_ing', 'suborden', 'renglon']].astype(str).agg('-'.join, axis=1)
existente['id'] = existente[['orden_ing', 'suborden', 'renglon']].astype(str).agg('-'.join, axis=1)
egresado = generate_id(egresado)
verificaciones_realizadas = generate_id(verificaciones_realizadas)
salidas = generate_id(salidas)
salidas.columns = ['salida_validada', 'id']
salidas_vacios = generate_id(salidas_vacios)
salidas_vacios.columns = ['salida_vacio_validada', 'id']
ubicaciones = generate_id(ubicaciones)

turnos = limpiar_columnas(turnos)
existente = limpiar_columnas(existente)
#Separo segun tipo de turnos
verificaciones = turnos[turnos['destino'].str.contains('Verificacion', case=False, na=False)]
consolidados = turnos[turnos['destino'].str.contains('Consolidado', case=False, na=False)]
turnos = turnos[turnos['destino'].str.contains('Retiro|Remi', case=False, na=False)]

# Consolidados
existente_a_consolidar = pd.merge(consolidados, existente.drop(columns=['id', 'suborden', 'renglon', 'conocim2']), on='orden_ing', how='inner')
contenedores_a_consolidar = existente_a_consolidar[existente_a_consolidar['Envase'] == 'Contenedor']
mercaderia_a_consolidar = existente_a_consolidar[existente_a_consolidar['Envase'] != 'Contenedor']
mercaderia_a_consolidar = mercaderia_a_consolidar.groupby('orden_ing').agg({
    'volumen': 'sum',
    'cantidad': 'sum',
    'kilos': 'sum'}).reset_index()

# Join de contenedores y mercaderia
contenedores_a_consolidar.drop(columns=['volumen', 'cantidad', 'kilos'], inplace=True)

consolidados = pd.merge(contenedores_a_consolidar, mercaderia_a_consolidar, on='orden_ing', how='left')


# Quito conocimiento del existente
existente.drop(columns=['conocim2', 'orden_ing', 'suborden', 'renglon'], inplace=True)

# Retiros y remisiones (lo trato a parte porque tengo que hacer match con salidas)
turnos_egr = pd.merge(turnos, egresado, on='id', how='inner')
turnos_egr['Estado'] = 'En curso'
turnos_exist = pd.merge(turnos, existente, on='id', how='inner')
turnos_exist['Estado'] = 'Pendiente'
turnos_exist = turnos_exist[~turnos_exist['id'].isin(turnos_egr['id'])] #Se sacan casos de retiros parciales
turnos = pd.concat([turnos_egr, turnos_exist], ignore_index=True)
turnos = pd.merge(turnos, salidas, on='id', how='left')
turnos = pd.merge(turnos, salidas_vacios, on='id', how='left')
turnos['fecha_salida_validada'] = pd.to_datetime(turnos['salida_validada'], errors='coerce').dt.date
turnos['salida_validada'] = turnos.apply(
    lambda row: float('nan') if pd.notna(row['fecha_salida_validada']) and row['fecha_salida_validada'] < datetime.now().date() else row['salida_validada'],
    axis=1)
turnos.drop(columns=['fecha_salida_validada'], inplace=True)
turnos['Estado'] = turnos.apply(
    lambda row: row['salida_validada'][11:16] + ' Realizado' if pd.notna(row['salida_validada']) else row['Estado'],
    axis=1)

# Verificaciones
verificaciones= pd.merge(verificaciones, verificaciones_realizadas, on='id', how='left')
verificaciones['Estado'] = verificaciones['fechaverif'].apply(lambda x: 'Realizado' if pd.notna(x) else 'Pendiente')
verificaciones_existente = pd.merge(verificaciones, existente, on='id', how='inner')
verificaciones_egresado = pd.merge(verificaciones, egresado, on='id', how='inner')
# Verificaciones sin dato
verificaciones_sin_dato = verificaciones[
    ~verificaciones['id'].isin(verificaciones_existente['id']) &
    ~verificaciones['id'].isin(verificaciones_egresado['id'])
]
verificaciones = pd.concat([verificaciones_existente, verificaciones_egresado, verificaciones_sin_dato], ignore_index=True)
#Junto verificaciones con resto de turnos
turnos = pd.concat([turnos, verificaciones, consolidados], ignore_index=True)
#Join de ubicaciones
turnos = pd.merge(turnos, ubicaciones, on='id', how='left')
turnos = limpiar_columnas(turnos)



## Parte que estaba en la app

turnos['cliente'] = turnos['cliente'].apply(lambda x: x[:10] + "..." if len(x) > 10 else x)
turnos['desc_merc'] = turnos['desc_merc'].apply(lambda x: x[:10] + "..." if len(x) > 10 else x)
turnos['ubicacion'] = turnos['ubicacion'].str.strip()

verificaciones_expo = turnos[(turnos['tipo_oper'] == 'Exportacion') & (turnos['destino'] == 'Verificacion')]
verificaciones_expo = verificaciones_expo[['dia', 'cliente', 'desc_merc', 'contenedor', 'Envase', 'cantidad', 'ubicacion']]
verificaciones_expo = rellenar_df_vacio(verificaciones_expo)
verificaciones_expo.columns = ['Dia', 'Cliente', 'Desc. Merc.', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.']

verificaciones_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (turnos['destino'] == 'Verificacion')]
verificaciones_impo = verificaciones_impo[['dia', 'cliente', 'desc_merc', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
verificaciones_impo.columns = ['Dia', 'Cliente', 'Desc. Merc.', 'Contenedor', 'Envase', 'Cant.', 'Ubic.', 'Estado']

retiros_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (turnos['destino'] == 'Retiro')]
retiros_impo = retiros_impo[['dia', 'cliente', 'conocim1', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
retiros_impo.columns = ['Dia', 'Cliente', 'Conocim.', 'Contenedor', 'Envase', 'Cant.', 'Ubic.', 'Estado']
retiros_impo['Conocim.'] = retiros_impo['Conocim.'].str.strip()

otros_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (~turnos['destino'].isin(['Retiro', 'Verificacion']))]
otros_impo = otros_impo[['dia', 'hora', 'id', 'cliente', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
otros_impo.columns = ['Dia', 'Hora', 'Operacion', 'Cliente', 'Contenedor', 'Envase', 'Cant.', 'Ubic.', 'Estado']


retiros_expo = turnos[(turnos['tipo_oper'] == 'Exportacion') & (turnos['destino'] == 'Retiro')]
retiros_expo = retiros_expo[['dia', 'cliente', 'conocim1', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
retiros_expo.columns = ['Dia', 'Cliente', 'Conocim.', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.', 'Estado']

otros_expo = turnos[(turnos['tipo_oper'] == 'Exportacion') & (~turnos['destino'].isin(['Retiro', 'Verificacion']))]
otros_expo = otros_expo[['dia', 'hora', 'id', 'cliente', 'contenedor', 'Envase', 'cantidad', 'ubicacion']]
otros_expo.columns = ['Dia', 'Hora', 'Operacion', 'Cliente', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.']

remisiones = turnos[turnos['destino'] == 'Remision']
consolidados = turnos[turnos['destino'] == 'Consolidado']

verificaciones_expo = rellenar_df_vacio(verificaciones_expo)
retiros_expo = rellenar_df_vacio(retiros_expo)
retiros_impo = rellenar_df_vacio(retiros_impo)
otros_expo = rellenar_df_vacio(otros_expo)
remisiones = rellenar_df_vacio(remisiones)
consolidados = rellenar_df_vacio(consolidados)

verificaciones_impo = rellenar_df_vacio(verificaciones_impo)
otros_impo = rellenar_df_vacio(otros_impo)


verificaciones_expo.to_csv('data/verificaciones_expo.csv', index=False)
verificaciones_impo.to_csv('data/verificaciones_impo.csv', index=False)
retiros_expo.to_csv('data/retiros_expo.csv', index=False)
retiros_impo.to_csv('data/retiros_impo.csv', index=False)
otros_expo.to_csv('data/otros_expo.csv', index=False)
otros_impo.to_csv('data/otros_impo.csv', index=False)
remisiones.to_csv('data/remisiones.csv', index=False)
consolidados.to_csv('data/consolidados.csv', index=False)
