import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gspread
from datetime import datetime
from gspread_dataframe import set_with_dataframe

path = "//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/"

def log(mensaje):
    gc = gspread.service_account(filename='//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/credenciales_gsheets.json')
    sheet_logs = gc.open_by_url('https://docs.google.com/spreadsheets/d/1aPUkhige3tq7_HuJezTYA1Ko7BWZ4D4W0sZJtsTyq3A')
    worksheet_logs = sheet_logs.worksheet('Logeos')
    df_logs = worksheet_logs.get_all_values()
    df_logs = pd.DataFrame(df_logs[1:], columns=df_logs[0])
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    new_log_entry = pd.DataFrame([{'Rutina': mensaje, 'Fecha y Hora': now}])
    df_logs = pd.concat([df_logs, new_log_entry], ignore_index=True)
    worksheet_logs.clear()
    set_with_dataframe(worksheet_logs, df_logs)
    print("Se registró el logeo")

# Function to send email
def send_email(row, mail):
    # Get the current time
    current_time = datetime.now().strftime('%H:%M')
    email_content = f"""
    <html>
    <body>
        <h2>Notificación de Contenedor {row['contenedor']} Arribado</h2>
        <p>Estimado cliente,</p>
        <p>Le informamos que el contenedor <strong>{row['contenedor']}</strong> del cliente <strong>{row['cliente']}</strong> arribó a las instalaciones de DASSA a las <strong>{current_time}</strong>.</p>
        <p>Saludos cordiales,</p>
        <p><strong>Alertas automáticas - Dassa Operativo</strong></p>
        <img src="https://dassa.com.ar/wp-content/uploads/elementor/thumbs/DASSA-LOGO-3.0-2024-PNG-TRANSPARENTE-qrm2px9hpjbdymy2y0xddhecbpvpa9htf30ikzgxds.png" alt="Dassa Logo" width="200">
    </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['Subject'] = 'Notificación de Contenedor Arribado'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = mail
    msg.attach(MIMEText(email_content, 'html'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("auto@dassa.com.ar", "gyctvgzuwfgvmlfu")
        server.sendmail(msg['From'], msg['To'], msg.as_string())


arribados = pd.read_csv(path + 'alertas_arribos.csv')
alertas = arribados[arribados['alerta_enviada'] == 0]
arribados = arribados[arribados['alerta_enviada'] == 1]

retirados = pd.read_csv(path + 'alertas_retiros_impo.csv')
alertas_retiros = retirados[retirados['alerta_enviada'] == 0]
retirados = retirados[retirados['alerta_enviada'] == 1]

clientes = pd.read_csv(path + 'contactos_clientes.csv')
clientes['email'] = clientes['email'].str.replace(';', ',')
clientes['email'] = clientes['email'].str.replace('"', '')
clientes['email'] = clientes['email'].apply(lambda x: [email.strip() for email in x.split(',')])

tally_bi = pd.read_csv(path + 'TallyBI.csv', sep="|")
tally_bi.columns = tally_bi.columns.str.strip()
tally_bi['cont'] = tally_bi['cont'].str.strip().str.replace(' ', '-', regex=False)
tally_bi['idcont'] = tally_bi['idcont'].str.strip()

alertas_retiros['Contenedor'] = alertas_retiros['Contenedor'].str.strip()


print('Enviando alertas arribos...')
for index in range(len(alertas)):
    row = alertas.iloc[index]
    client_emails = clientes[clientes['apellido'] == row['cliente']]['email'].values
    client_emails_list =  ", ".join(email.lower() for email in client_emails[0])
    if len(client_emails) > 0:
        try:
            send_email(row, client_emails_list)
            log(f'Enviado a {client_emails_list} CTN {row["contenedor"]} - Arribo IMPO maritimo')
            print(f'Correo enviado a {client_emails_list} para el contenedor {row["contenedor"]}')
        except Exception as e:
            log(f'Error al enviar correo Arribo IMPO Maritimo a {client_emails_list} para el contenedor {row["contenedor"]}: {e}')
            print(f'Error al enviar correo a {client_emails_list} para el contenedor {row["contenedor"]}: {e}')
        
        row['alerta_enviada'] = 1
        row_df = pd.DataFrame([row])
        arribados = pd.concat([arribados, row_df], ignore_index=True)
        arribados.to_csv(path + 'alertas_arribos.csv', index=False)
    else:
        log(f'No se encontraron correos electrónicos para el cliente {row["cliente"]}')
        row['alerta_enviada'] = 1
        row_df = pd.DataFrame([row])
        arribados = pd.concat([arribados, row_df], ignore_index=True)
        arribados.to_csv(path + 'alertas_arribos.csv', index=False)

arribados.to_csv(path + 'alertas_arribos.csv', index=False)
