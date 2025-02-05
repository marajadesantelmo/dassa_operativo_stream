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

def generar_comprobante(invoice_number, invoice_data):
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf = FPDF()
    pdf.add_page()

    # Add logo (uncomment if logo is available)
    # pdf.image("logo.png", x=10, y=10, w=40)

    # Add invoice title
    pdf.set_font("Arial", style='B', size=16)
    pdf.set_text_color(0, 100, 0)  # Dark green color
    pdf.cell(200, 10, txt="Dangerous Goods Management", ln=True, align="C")
    pdf.cell(200, 10, txt="Outbound Invoice", ln=True, align="C")
    pdf.ln(10)

    # Add invoice number and date
    pdf.set_font("Arial", style='B', size=10)
    pdf.set_text_color(0, 100, 0)  # Dark green
    pdf.cell(200, 10, txt=f"Invoice Number: {invoice_number}                                                                     Date: {current_date}", ln=True, align="L")
    pdf.ln(5)

    # Add table title
    pdf.set_font("Arial", style='B', size=12)
    pdf.set_text_color(0, 100, 0)  # Dark green
    pdf.cell(200, 10, txt="Invoice Details", ln=True, align="L")
    pdf.ln(3)

    # Add italic text
    pdf.set_font("Arial", style='I', size=10)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.multi_cell(0, 8, txt="Below is a detailed list of items included in this invoice.", align="L")
    pdf.ln(2)

    # Add table header with dark green background
    pdf.set_fill_color(0, 100, 0)  # Dark green
    pdf.set_text_color(255, 255, 255)  # White
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(20, 10, txt="SKU id", border=1, fill=True, align="C")
    pdf.cell(50, 10, txt="Description", border=1, fill=True, align="C")
    pdf.cell(40, 10, txt="Total Length", border=1, fill=True, align="C")
    pdf.cell(20, 10, txt="Quantity", border=1, fill=True, align="C")
    pdf.ln()

    # Add table rows
    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.set_font("Arial", size=10)
    for record in invoice_data:
        pdf.cell(20, 10, txt=str(record['sku_id']), border=1, align="C")
        pdf.cell(50, 10, txt=str(record['SKU']), border=1, align="C")
        pdf.cell(40, 10, txt=str(record['total_length']), border=1, align="C")
        pdf.cell(20, 10, txt=str(record['Quantity']), border=1, align="C")
        pdf.ln()
    pdf.ln(2)
    pdf.set_font("Arial", style='B', size=12)
    pdf.set_text_color(0, 0, 0) 
    pdf.cell(200, 3, txt="DGM - Florida", ln=True, align="L")
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