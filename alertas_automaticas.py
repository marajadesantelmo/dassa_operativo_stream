import pandas as pd
import smtplib
from email.mime.text import MIMEText
import gspread
from datetime import datetime
from gspread_dataframe import set_with_dataframe
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

path = "//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/"

def log(mensaje):
    gc = gspread.service_account(filename='//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/credenciales_gsheets.json')
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

arribados = pd.read_csv(path + 'alertas_arribos.csv')

alertas = arribados[arribados['alerta_enviada'] == 0]

if alertas.empty:
    print("No hay alertas para enviar")
    log("Alertas automaticas: no se enviaron alertas")
    exit()


clientes = pd.read_csv(path + 'contactos_clientes.csv')
#clientes['email'] = clientes['email'].str.replace(';', ',')
#def add_space_after_comma(email):
#    return re.sub(r',(?=\S)', ', ', email)
#clientes['email'] = clientes['email'].apply(add_space_after_comma)
#clientes['email'] = clientes['email'].str.replace('"', '')


# TallyBI
tallyBi = pd.read_csv(path + 'tallybi.csv')

def send_email(alertas, mails):
    # Create the email content with a logo
    email_content = f"""
    <html>
    <body>
        <h2>Notificación automática de Contenedor Arribado</h2>
        <p>Estimado cliente,</p>
        <p>Le informamos que el contenedor <strong>{alertas['contenedor']}</strong> del cliente <strong>{alertas['cliente']}</strong> arribó a las instalaciones de DASSA.</p>
        <p>Saludos cordiales,</p>
        <p><strong>Avisos automáticos - Dassa Operativo</strong></p>
        <img src="https://dassa.com.ar/wp-content/uploads/elementor/thumbs/DASSA-LOGO-3.0-2024-PNG-TRANSPARENTE-qrm2px9hpjbdymy2y0xddhecbpvpa9htf30ikzgxds.png" alt="Dassa Logo" width="200">
    </body>
    </html>
    """

    # Create the email message
    msg = MIMEMultipart()
    msg['Subject'] = 'Notificación de Contenedor Arribado'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = mails
    msg.attach(MIMEText(email_content, 'html'))

    # Send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("auto@dassa.com.ar", "gyctvgzuwfgvmlfu")
        server.sendmail(msg['From'], [msg['To']], msg.as_string())


for _, row in alertas.iterrows():
    mails = clientes[clientes['apellido'] == row['cliente']]['email'].values[0]
    send_email(row, mails)
    log(f'Correo enviado a {mails} para el contenedor {row["contenedor"]}')

alertas['alerta_enviada'] = 1
arribados = arribados[arribados['alerta_enviada'] == 1]
arribados = pd.concat([arribados, alertas])
arribados.to_csv('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/alertas_arribos.csv', index=False)




