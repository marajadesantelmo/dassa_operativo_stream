import pandas as pd
import smtplib
from email.mime.text import MIMEText

arribados = pd.read_csv('arribos_historico_horarios.csv')

alertas = arribados[arribados['alerta_enviada'] == 0]

if alertas.empty:
    print("No hay alertas para enviar")
    exit()

# Function to send email
def send_email(alertas):
    msg = MIMEText(f"El contendedor {alertas['Contenedor']} del cliente {alertas['Cliente']} ")
    msg['Subject'] = 'Contenedor Arribado'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = 'marajadesantelmo@gmail.com'

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls() 
        server.login("auto@dassa.com.ar", "gyctvgzuwfgvmlfu")
        server.sendmail(msg['From'], [msg['To']], msg.as_string())

# Send alerts for new status changes
for _, row in alertas.iterrows():
    send_email(row)

# Update historical data to mark alerts as sent
alertas['alert_sent'] = True
updated_historical_data = pd.concat([historical_data, alertas[['Contenedor', 'alert_sent']]])

# Save updated historical data
updated_historical_data.to_csv('data/historical_alerts.csv', index=False)

print("historical_alerts.csv has been created.")