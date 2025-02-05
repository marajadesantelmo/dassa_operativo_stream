import pandas as pd
import numpy as np
from fpdf import FPDF
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

def generar_comprobante(balanza_row):
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf = FPDF()
    pdf.add_page()

    pdf.image("logo.png", x=10, y=10, w=40)

    # Add invoice title
    pdf.set_font("Arial", style='B', size=16)
    pdf.set_text_color(0, 100, 0)  # Dark green color
    pdf.cell(200, 10, txt="Depósito Avellaneda Sur S.A.", ln=True, align="C")
    pdf.cell(200, 10, txt="Comprobante de pesaje en balanza", ln=True, align="C")
    pdf.ln(10)

    # Add invoice number and date
    pdf.set_font("Arial", style='B', size=10)
    pdf.set_text_color(0, 100, 0)  # Dark green
    pdf.cell(200, 10, txt=f"ID Pesada: {balanza_row['id Pesada']}                                                                     Date: {current_date}", ln=True, align="L")
    pdf.ln(5)

    # Add table title
    pdf.set_font("Arial", style='B', size=12)
    pdf.set_text_color(0, 100, 0)  # Dark green
    pdf.cell(200, 10, txt="Detalles de Balanza", ln=True, align="L")
    pdf.ln(3)

    # Add table header with dark green background
    pdf.set_fill_color(0, 100, 0)  # Dark green
    pdf.set_text_color(255, 255, 255)  # White
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(40, 10, txt="Field", border=1, fill=True, align="C")
    pdf.cell(150, 10, txt="Value", border=1, fill=True, align="C")
    pdf.ln()

    # Add table rows
    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.set_font("Arial", size=10)
    fields = [
        "Cliente", "Contenedor", "Entrada", "Salida", "Peso Bruto", "Peso Tara", 
        "Peso Neto", "Peso Mercadería", "Descr.", "Patente Ch", "Patente Semi", 
        "Chofer", "Obs.", "tipo_oper"
    ]
    for field in fields:
        pdf.cell(40, 10, txt=str(field), border=1, align="C")
        pdf.cell(150, 10, txt=str(balanza_row[field]), border=1, align="C")
        pdf.ln()
    pdf.ln(2)
    pdf.set_font("Arial", style='B', size=12)
    pdf.set_text_color(0, 0, 0) 
    pdf.cell(200, 3, txt="DASSA - Depósito Avellaneda Sur S.A.", ln=True, align="L")
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.multi_cell(0, 3, txt=(
        "6705 NW 36th Street\n"
        "Suite 440\n"
        "Miami, Florida 33166\n"
        "Phone Number: +1-786-264-0050\n"
        "Office Hours: Mon-Fri, 8am - 5pm\n" 
        "Email: miami@dgmflorida.com"
    ), align="L")
    pdf.ln(5)

    # Save the PDF and return it
    return pdf