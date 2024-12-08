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

arribados = pd.read_csv(path + 'alertas_arribos.csv')
alertas = arribados[arribados['alerta_enviada'] == 0]
arribados = arribados[arribados['alerta_enviada'] == 1]

clientes = pd.read_csv(path + 'contactos_clientes.csv')
clientes['email'] = clientes['email'].str.replace(';', ',')
clientes['email'] = clientes['email'].str.replace('"', '')
clientes['email'] = clientes['email'].apply(lambda x: [email.strip() for email in x.split(',')])


# Function to send email
def send_email(row, mail):
    # Get the current time
    current_time = datetime.now().strftime('%H:%M')

    # Create the email content with a logo
    email_content = f"""
    <html>
    <body>
        <h2>Notificación de Contenedor Arribado</h2>
        <p>Estimado cliente,</p>
        <p>Le informamos que el contenedor <strong>{row['contenedor']}</strong> del cliente <strong>{row['cliente']}</strong> arribó a las instalaciones de DASSA a las <strong>{current_time}</strong>.</p>
        <p>Saludos cordiales,</p>
        <p><strong>Alertas automáticas - Dassa Operativo</strong></p>
        <img src="https://dassa.com.ar/wp-content/uploads/elementor/thumbs/DASSA-LOGO-3.0-2024-PNG-TRANSPARENTE-qrm2px9hpjbdymy2y0xddhecbpvpa9htf30ikzgxds.png" alt="Dassa Logo" width="200">
    </body>
    </html>
    """

    # Create the email message
    msg = MIMEMultipart()
    msg['Subject'] = 'Notificación de Contenedor Arribado'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = mail
    msg.attach(MIMEText(email_content, 'html'))

    # Send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("auto@dassa.com.ar", "gyctvgzuwfgvmlfu")
        server.sendmail(msg['From'], mail, msg.as_string())

# Process each alert and send emails
for index in range(len(alertas)):
    row = alertas.iloc[index]
    client_emails = clientes[clientes['apellido'] == row['cliente']]['email'].values
    if len(client_emails) > 0:
        mails = client_emails[0]
        for mail in mails:
            try:
                send_email(row, mail)
                log(f'Correo enviado a {mail} para el contenedor {row["contenedor"]}')
                print(f'Correo enviado a {mail} para el contenedor {row["contenedor"]}')
            except Exception as e:
                log(f'Error al enviar correo a {mail} para el contenedor {row["contenedor"]}: {e}')
                print(f'Error al enviar correo a {mail} para el contenedor {row["contenedor"]}: {e}')
        
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

# Save the updated DataFrame
arribados.to_csv(path + 'alertas_arribos.csv', index=False)


