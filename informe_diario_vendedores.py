import pandas as pd
import pyodbc
from datetime import datetime
from tokens import username, password, password_gmail 
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

path = "//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/"

def send_email_vendedor(row, mail, operations, saldos_clientes_vendedor):
    hoy = datetime.now().strftime('%d/%m/%Y')
    email_content = f"""
    <html>
    <body>
        <h2>Operaciones para el día {hoy}</h2>
        <p>Buenos días {row},</p>
        <p>A continuación te compartimos las operaciones coordinadas con tus clientes para el día de hoy:</p>
    """
    # Dynamically add operation tables
    for title, df in operations.items():
        if not df.empty:
            email_content += f"""
            <h3>{title}</h3>
            {df.to_html(index=False, border=0, justify='left')}
            """
    email_content += """<p>Información sobre saldos vencidos en el último año:</p>"""
    
    # Add saldos_clientes_vendedor table
    if not saldos_clientes_vendedor.empty:
        email_content += f"""
        <h3>Saldos vencidos</h3>
        <h3>Facturas vencidas emitidas en los últimos 365 días</h4>
        {saldos_clientes_vendedor.to_html(index=False, border=0, justify='left')}
        """

    email_content += """
        <p>Saludos cordiales,</p>
        <p><strong>Alertas automáticas - Dassa Operativo</strong></p>
        <img src="https://dassa.com.ar/wp-content/uploads/elementor/thumbs/DASSA-LOGO-3.0-2024-PNG-TRANSPARENTE-qrm2px9hpjbdymy2y0xddhecbpvpa9htf30ikzgxds.png" alt="Dassa Logo" width="200">
    </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['Subject'] = f'Operaciones de tus clientes para el día de hoy {hoy}'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = mail
    #msg['To'] = "marajadesantelmo@gmail.com"
    msg.attach(MIMEText(email_content, 'html'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("auto@dassa.com.ar", password_gmail)
        server.sendmail(msg['From'], msg['To'], msg.as_string())


def transformar_saldos(df): 
    df['saldo'] = df['debe'] - df['haber']
    df = df.groupby(['aplicacion']).agg({'tp_cpte': 'first', 
                                         'adicional': 'first', 
                                         'fecha_vto': 'first', 
                                         'saldo': 'sum'}).reset_index()
    df = df[df['saldo'] > 1]
    df['adicional'] = df['adicional'].str.strip().str.title()
    df.rename(columns={'tp_cpte': 'Tipo cpte', 
                       'adicional': 'Cliente', 
                       'fecha_vto': 'Vencimiento', 
                       'saldo': 'Saldo', 
                       'aplicacion': 'Comprobante'}, 
                       inplace=True)
    df['Vencimiento'] = pd.to_datetime(df['Vencimiento'])
    df['Dias'] = (pd.to_datetime(datetime.now().strftime('%Y-%m-%d')) - df['Vencimiento']).dt.days
    df['Dias'] = df['Dias'].apply(lambda x: x if x > 0 else 0)
    df['Comprobante'] = df['Tipo cpte'] + " " + df['Comprobante']
    df = df[['Comprobante', 'Cliente', 'Vencimiento', 'Saldo', 'Dias']]
    return df

def formato_saldos(df): 
    df['Saldo'] = df['Saldo'].apply(lambda x: f"${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if x >= 0 else f"(${abs(x):,.2f})".replace(",", "X").replace(".", ",").replace("X", "."))
    return df


server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()


cursor.execute(f"""
SELECT  apellido AS Cliente, clie_nro, vendedor
FROM DEPOFIS.DASSA.[Clientes]
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
clientes= pd.DataFrame.from_records(rows, columns=columns)
clientes['Cliente'] = clientes['Cliente'].str.strip().str.title()
clientes['Cliente'] = clientes['Cliente'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)

dic_vendedores = pd.read_excel(path + 'diccionario_vendedores_puros_dassa.xlsx')
dic_vendedores = dic_vendedores[dic_vendedores['nombre_vendedor'] != 'Otros']

# Load all dataframes
verificaciones_impo = pd.read_csv(path + 'data/verificaciones_impo.csv')
retiros_impo = pd.read_csv(path + 'data/retiros_impo.csv')
otros_impo = pd.read_csv(path + 'data/otros_impo.csv')
verificaciones_expo = pd.read_csv(path + 'data/verificaciones_expo.csv')
remisiones_expo = pd.read_csv(path + 'data/remisiones.csv')
#consolidados_expo = pd.read_csv(path + 'data/consolidados.csv')
otros_expo = pd.read_csv(path + 'data/otros_expo.csv')

# Fill NaN values in 'e-tally' column for each dataframe if it exists
for df in [verificaciones_impo, retiros_impo, otros_impo, verificaciones_expo, 
           remisiones_expo, otros_expo]:
    if 'e-tally' in df.columns:
        df['e-tally'].fillna('-', inplace=True)

vendedores = dic_vendedores['nombre_vendedor'].unique()

for vendedor in vendedores:
    tabla_vendedor = dic_vendedores[dic_vendedores['nombre_vendedor'] == vendedor]
    vendedor_ids = tabla_vendedor['cod_vendedor'].unique()
    clientes_vendedor = clientes[clientes['vendedor'].isin(vendedor_ids)]['Cliente'].unique()
    id_clientes_vendedor = [str(int(id_cliente)) for id_cliente in clientes[clientes['vendedor'].isin(vendedor_ids)]['clie_nro'].unique()]
    dia = (datetime.now()).strftime('%d/%m')

    # Filter operations for the vendedor
    operations = {
        "Verificaciones Importación": verificaciones_impo[(verificaciones_impo['Cliente'].isin(clientes_vendedor)) & (verificaciones_impo['Dia'] == dia)],
        "Retiros Importación": retiros_impo[(retiros_impo['Cliente'].isin(clientes_vendedor)) & (retiros_impo['Dia'] == dia)],
        "Otros Importación": otros_impo[(otros_impo['Cliente'].isin(clientes_vendedor)) & (otros_impo['Dia'] == dia)],
        "Verificaciones Exportación": verificaciones_expo[(verificaciones_expo['Cliente'].isin(clientes_vendedor)) & (verificaciones_expo['Dia'] == dia)],
        "Remisiones Exportación": remisiones_expo[(remisiones_expo['Cliente'].isin(clientes_vendedor)) & (remisiones_expo['Dia'] == dia)],
        #"Consolidados Exportación": consolidados_expo[(consolidados_expo['Cliente'].isin(clientes_vendedor)) & (consolidados_expo['Dia'] == dia)],
        "Otros Exportación": otros_expo[(otros_expo['Cliente'].isin(clientes_vendedor)) & (otros_expo['Dia'] == dia)],
    }

    ### Descargo Saldos
    clientes_str = ','.join(id_clientes_vendedor)
    cursor.execute(f"""
    SELECT fecha_vto, tp_cpte, aplicacion, adicional, debe, haber
    FROM DEPOFIS.DASSA.CtaCcteD
    WHERE Cliente IN ({clientes_str});
    """)  
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    saldos_clientes_vendedor = pd.DataFrame.from_records(rows, columns=columns)

    saldos_clientes_vendedor = transformar_saldos(saldos_clientes_vendedor)
    saldos_clientes_vendedor.sort_values(by=['Dias'], ascending=False, inplace=True)
    saldos_clientes_vendedor = saldos_clientes_vendedor[(saldos_clientes_vendedor['Dias'] > 0) & (saldos_clientes_vendedor['Dias'] < 365)]
    # Aggregate saldos by Cliente: sum Saldo, get max Dias, min Vencimiento
    saldos_clientes_vendedor_agregado = (
        saldos_clientes_vendedor
        .groupby('Cliente', as_index=False)
        .agg({
            'Saldo': 'sum',
            'Dias': 'max',
            'Vencimiento': 'min'
        })
    )
    # Format Saldo column again for display
    saldos_clientes_vendedor_agregado = formato_saldos(saldos_clientes_vendedor_agregado)

    # Check if there are operations
    if any(not df.empty for df in operations.values()):
        print(f"Hay operaciones para el vendedor {vendedor}.")
        vendedor_email = tabla_vendedor['email'].iloc[0]  # Assuming email column exists
        send_email_vendedor(vendedor, vendedor_email, operations, saldos_clientes_vendedor_agregado)
    else:
        print(f"No hay operaciones para el vendedor {vendedor}.")


