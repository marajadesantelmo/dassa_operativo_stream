"""
Descarga TallyBI.csv y TallyBIEXPO.csv desde servidor remoto de MCUBIC
y procesa los datos para su posterior uso en Streamlit. A MODIFICAR """

import os
import paramiko
import scp
from scp import SCPClient
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from tokens import username_scp, password_scp
from datetime import datetime

if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream')
elif os.path.exists('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream'):
    os.chdir('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream')
else:
    print("Se usa working directory por defecto")

# Define the SSH client
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='155.138.154.37', username=username_scp, password=password_scp)
#ssh.connect(hostname='155.138.143.232', username=username_scp, password='password_scp')
with SCPClient(ssh.get_transport()) as scp:
    scp.get('TallyBI.csv')
    scp.get('TallyBIEXPO.csv')

# Procesamiento datos de IMPO
# Sanitizar pipes dentro de campos para evitar errores de parseo
with open('TallyBI.csv', 'r', encoding='latin1') as f:
    header = f.readline()
    n_cols = len(header.split('|'))
    clean_lines = [header]
    for lineno, line in enumerate(f, start=2):
        parts = line.split('|')
        if len(parts) > n_cols:
            # Unir las columnas extra en el campo descripcion (columna 10, indice 10)
            excess = len(parts) - n_cols
            parts[10] = '|'.join(parts[10:10+excess+1]).replace('|', '-')
            del parts[11:11+excess]
        clean_lines.append('|'.join(parts))
with open('TallyBI.csv', 'w', encoding='latin1') as f:
    f.writelines(clean_lines)

datos_tally = pd.read_csv('TallyBI.csv', sep='|', encoding='latin1', on_bad_lines='warn')
datos_tally = datos_tally.drop(index=0)
datos_tally.columns = datos_tally.columns.str.strip()
datos_tally['descripcion'] = datos_tally['descripcion'].str.strip()
datos_tally['inicio'] = datos_tally['inicio'].str.strip()
datos_tally['fecha'] = pd.to_datetime(datos_tally['inicio'], format='%d-%m-%y %H:%M', errors='coerce').dt.date
datos_tally['inicio'] = pd.to_datetime(datos_tally['inicio'], format='%d-%m-%y %H:%M', errors='coerce')
datos_tally['cierre'] = datos_tally['cierre'].str.strip()
datos_tally['cierre'] = pd.to_datetime(datos_tally['cierre'], format='%d-%m-%y %H:%M', errors='coerce')
datos_tally['duracion'] = datos_tally['cierre'] - datos_tally['inicio'] 
datos_tally['duracion_hhmmss'] = datos_tally['duracion'].astype(str).str[7:9] + ':' + \
                                 datos_tally['duracion'].astype(str).str[10:12] + ':' + \
                                 datos_tally['duracion'].astype(str).str[13:15]
datos_tally = datos_tally.dropna(subset=['inicio'])
datos_tally = datos_tally.dropna(subset=['cierre'])
datos_tally.to_csv('data/tally.csv', sep=',', encoding='latin1', index=False)

# Procesamiento datos de EXPO
# Sanitizar pipes dentro de campos para EXPO tambien
with open('TallyBIEXPO.csv', 'r', encoding='latin1') as f:
    header = f.readline()
    n_cols = len(header.split('|'))
    clean_lines = [header]
    for lineno, line in enumerate(f, start=2):
        parts = line.split('|')
        if len(parts) > n_cols:
            excess = len(parts) - n_cols
            # Buscar columna descripcion por indice en EXPO
            desc_idx = 10
            parts[desc_idx] = '-'.join(parts[desc_idx:desc_idx+excess+1])
            del parts[desc_idx+1:desc_idx+1+excess]
        clean_lines.append('|'.join(parts))
with open('TallyBIEXPO.csv', 'w', encoding='latin1') as f:
    f.writelines(clean_lines)

datos_tally_expo = pd.read_csv('TallyBIEXPO.csv', sep='|', encoding='latin1', on_bad_lines='warn')

# Logeo
gc = gspread.service_account(filename='credenciales_gsheets.json')
sheet_logs =  gc.open_by_url('https://docs.google.com/spreadsheets/d/1aPUkhige3tq7_HuJezTYA1Ko7BWZ4D4W0sZJtsTyq3A')                                           
worksheet_logs = sheet_logs.worksheet('Logeos')
df_logs = worksheet_logs.get_all_values()
df_logs = pd.DataFrame(df_logs[1:], columns=df_logs[0])
now = datetime.now().strftime('%Y-%m-%d %H:%M')
new_log_entry = pd.DataFrame([{'Rutina': 'Streamlit - Get tally BI', 'Fecha y Hora': now}])
df_logs = pd.concat([df_logs, new_log_entry], ignore_index=True)
worksheet_logs.clear()
set_with_dataframe(worksheet_logs, df_logs)
print("Se registr� el logeo")  