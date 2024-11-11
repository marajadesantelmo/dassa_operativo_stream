import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from datetime import datetime

def highlight(row):
    if "Realizado" in row['Estado']:
        return ['background-color: darkgreen; color: black' for _ in row]
    elif "En curso" in row['Estado']:
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    elif row['Estado'] == "Vacio":
        return ['background-color: #be1e2d; color: black' for _ in row]
    elif "Arribado" in row['Estado']:
        return ['background-color: darkgreen; color: black' for _ in row]
    elif row['Estado'] == "Pendiente ingreso":
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    else:
        return ['' for _ in row]

def rellenar_df_vacio(df):
    if df.empty:
        df = pd.DataFrame([['-'] * len(df.columns)], columns=df.columns)
    return df

def logging(mensaje): 
    gc = gspread.service_account(filename='credenciales_gsheets.json')
    sheet_logs =  gc.open_by_url('https://docs.google.com/spreadsheets/d/1aPUkhige3tq7_HuJezTYA1Ko7BWZ4D4W0sZJtsTyq3A')                                           
    worksheet_logs = sheet_logs.worksheet('Logeos')
    df_logs = worksheet_logs.get_all_values()
    df_logs = pd.DataFrame(df_logs[1:], columns=df_logs[0])
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    new_log_entry = pd.DataFrame([{'Rutina': mensaje, 'Fecha y Hora': now}])
    df_logs = pd.concat([df_logs, new_log_entry], ignore_index=True)
    worksheet_logs.clear()
    set_with_dataframe(worksheet_logs, df_logs)
    print("Se registró el logeo")