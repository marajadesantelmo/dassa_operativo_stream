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
from tokens import username, password, url_supabase, key_supabase
from supabase import create_client, Client


supabase_client = create_client(url_supabase, key_supabase)

path = "//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/"

server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

gc = gspread.service_account(filename='//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/credenciales_gsheets.json')

cursor.execute("""
    SELECT cliente AS Cliente, cantidad AS Cantidad, kilos AS Peso, volumen AS Volumen, 
            orden_ing, suborden, renglon, tipo_oper AS Tipo, env.detalle AS Envase, fecha_ing AS Ingreso
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
fecha_actual = datetime.now()
existente['Ingreso'] = pd.to_datetime(existente['Ingreso'], format='%Y-%m-%d')
existente['Dias'] = (fecha_actual - existente['Ingreso']).dt.days

cols = ['Cliente', 'Tipo', 'Envase']
for col in cols:
    existente[col] = existente[col].str.strip().str.title()

existente.rename(columns={'ubicacion': 'Ubicacion', 'ubicacion_familia': 'Ubicacion Familia'}, inplace=True)

existente = existente[['Ubicacion Familia', 'Ubicacion', 'Cliente', 'Tipo', 'Envase', 'Peso', 'Volumen',  'Cantidad', 'Ingreso',
       'Operacion',  'Dias']]

existente['Estiba OK'] = ""
existente['Alcahuete OK'] = ""
existente['Observaciones'] = ""

existente.sort_values(by=['Ubicacion Familia', 'Ubicacion'], inplace=True)

existente_plz = existente[existente['Ubicacion Familia'].isin(['Plazoleta', 'Temporal'])].copy()
existente_alm = existente[~existente['Ubicacion Familia'].isin(['Plazoleta', 'Temporal'])].copy()

sheet = gc.create('Control_Stock_DASSA_{mes}_{year}'.format(mes=datetime.now().strftime('%m'), year=datetime.now().year))
sheet.share('marajadesantelmo@gmail.com', perm_type='user', role='writer')
worksheet_plz = sheet.add_worksheet(title='Plazoleta', rows=existente_plz.shape[0] + 10, cols=existente_plz.shape[1] + 5)
set_with_dataframe(worksheet_plz, existente_plz, include_index=False)
worksheet_alm = sheet.add_worksheet(title='Almacen', rows=existente_alm.shape[0] + 10, cols=existente_alm.shape[1] + 5)
set_with_dataframe(worksheet_alm, existente_alm, include_index=False)
default_worksheet = sheet.get_worksheet(0)
sheet.del_worksheet(default_worksheet)

print(f"Spreadsheet created: {sheet.url}")

# Upload to Supabase
def upload_to_supabase(df, table_name):
    """Delete all data from table and insert new data"""
    try:
        # Delete all existing data
        print(f"Deleting existing data from {table_name}...")
        supabase_client.from_(table_name).delete().neq('id', 0).execute()
        
        # Prepare data for insertion
        # Convert DataFrame to list of dictionaries and handle data types
        df_copy = df.copy()
        
        # Keep original column names (do NOT rename to lowercase)
        # Convert datetime columns to string format
        if 'Ingreso' in df_copy.columns:
            df_copy['Ingreso'] = pd.to_datetime(df_copy['Ingreso']).dt.strftime('%Y-%m-%d')
        
        # Convert Decimal types to float for JSON serialization
        from decimal import Decimal
        for col in df_copy.columns:
            if df_copy[col].dtype == 'object':
                # Check if column contains Decimal objects
                if df_copy[col].apply(lambda x: isinstance(x, Decimal)).any():
                    df_copy[col] = df_copy[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)
        
        # Also convert numeric columns that might contain Decimals
        numeric_columns = ['Peso', 'Volumen', 'Cantidad']
        for col in numeric_columns:
            if col in df_copy.columns:
                df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
        
        # Replace NaN values with None
        df_copy = df_copy.where(pd.notna(df_copy), None)
        
        # Convert to records
        records = df_copy.to_dict('records')
        
        # Additional cleanup: ensure all Decimal values are converted to float
        import json
        for record in records:
            for key, value in record.items():
                if isinstance(value, Decimal):
                    record[key] = float(value)
        
        # Insert data in batches to avoid timeouts
        batch_size = 100
        total_records = len(records)
        
        print(f"Inserting {total_records} records into {table_name}...")
        for i in range(0, total_records, batch_size):
            batch = records[i:i + batch_size]
            supabase_client.from_(table_name).insert(batch).execute()
            print(f"Inserted batch {i//batch_size + 1}/{(total_records + batch_size - 1)//batch_size}")
        
        print(f"Successfully uploaded {total_records} records to {table_name}")
        
        # Update log
        update_log(table_name)
        
    except Exception as e:
        print(f"Error uploading to {table_name}: {e}")
        raise e

# Upload data to Supabase tables
print("\n--- Starting Supabase upload ---")
upload_to_supabase(existente_plz, 'control_stock_existente_plz')
upload_to_supabase(existente_alm, 'control_stock_existente_alm')
print("--- Supabase upload completed ---\n")
