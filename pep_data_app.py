# -*- coding: utf-8 -*-
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import csv
from io import StringIO
from datetime import datetime, timedelta
import os

st.title("Hello! Ovi create your data")

# ========== PRICE DATA ==========
PRICE_DATA = {
    'PLN': [0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.3, 1.5, 1.8, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 12, 15, 17, 18, 20, 22, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 250],
    'EUR': [0.05, 0.05, 0.1, 0.1, 0.1, 0.15, 0.2, 0.2, 0.25, 0.25, 0.35, 0.4, 0.4, 0.45, 0.5, 0.65, 0.8, 0.9, 1, 1.2, 1.3, 1.5, 1.8, 2, 2.3, 2.5, 3, 4, 4.5, 4.5, 5, 5.5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20, 22, 23, 24, 25, 28, 30, 33, 35, 38, 40, 43, 45, 48, 50, 53],
    'BGN': [0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4, 0.5, 0.6, 0.7, 0.7, 0.8, 1, 1, 1.5, 1.5, 2, 2.3, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7, 7.5, 8, 9, 10, 15, 17, 18, 19, 20, 23, 25, 28, 30, 35, 40, 40, 40, 45, 50, 55, 58, 60, 65, 70, 75, 80, 90, 95, 100, 105],
    'BAM': [0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4, 0.5, 0.6, 0.6, 0.7, 0.8, 1, 1.25, 1.5, 1.75, 2, 2.3, 2.5, 3, 3.5, 4, 4.5, 5, 6, 8, 9, 9.5, 10, 11, 12, 15, 17, 20, 22, 23, 25, 30, 33, 35, 38, 40, 43, 45, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 125],
    'RON': [0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.3, 1.4, 1.5, 1.8, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6.5, 7.5, 8.5, 9.5, 10, 13, 16, 18, 19, 21, 25, 27, 32, 38, 43, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 220, 260],
    'CZK': [1, 2, 2, 2, 3, 4, 5, 5, 6, 6, 9, 9, 9, 12, 12, 15, 20, 22, 25, 27, 30, 35, 40, 50, 55, 60, 70, 90, 100, 110, 120, 130, 150, 180, 200, 250, 280, 300, 330, 350, 390, 420, 450, 480, 510, 540, 570, 600, 670, 740, 800, 880, 950, 1000, 1050, 1100, 1150, 1200, 1300],
    'RSD': [5, 5, 10, 15, 15, 20, 20, 25, 30, 30, 40, 45, 50, 50, 60, 70, 90, 100, 120, 130, 150, 180, 200, 250, 270, 300, 350, 450, 550, 570, 600, 650, 700, 900, 1000, 1200, 1300, 1500, 1600, 1700, 1800, 2000, 2200, 2500, 2500, 2600, 2800, 3000, 3300, 3600, 4000, 4500, 5000, 5300, 5600, 5900, 6200, 6500, 6700],
    'HUF': [12, 25, 35, 35, 45, 55, 60, 65, 75, 100, 120, 130, 150, 180, 200, 250, 300, 350, 400, 430, 450, 500, 600, 700, 800, 1000, 1200, 1500, 1600, 1700, 1800, 2000, 2300, 2500, 3000, 3500, 4000, 4500, 4800, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 25000]
}

# ========== PRODUCT TRANSLATIONS ==========
DEPARTMENT_PRODUCTS = {
    "Girls Department": {
        "girls t-shirt": {
            "EN": "girls t-shirt", "BG": "Момичешка тениска", "BiH": "t-shirt za djevojčice. Sastav materijala na ušivenoj etiketi.",
            "CZ": "Dívčí t-shirt", "DE": "T-Shirt für Mädchen", "EE": "Tüdrukute T-särk",
            "ES": "Camiseta de niña / samarreta nena", "GR": "κοντομάνικα μπλουζάκια για κορίτσια", "HR": "t-shirt za djevojčice",
            "HU": "lány póló", "IT": "maglietta per ragazze", "LT": "marškinėliai mergaitei",
            "LV": "T-krekls meitenēm", "PL": "t-shirt dziewczęcy", "PT": "T-shirt para rapariga",
            "RO": "T-shirt fetițe", "RS": "potkošulja za devojčice. Sastav materijala nalazi se na ušivenoj etiketi",
            "SI": "dekliška majica, kratki rokav", "SK": "dievčenské tričko"
        }
    },
    "Boys Department": {
        "boys t-shirt": {
            "EN": "boys t-shirt", "BG": "Момчешка тениска", "BiH": "t-shirt za dječake. Sastav materijala na ušivenoj etiketi.",
            "CZ": "chlapecké tričko", "DE": "T-Shirt für Jungen", "EE": "Poiste T-särk",
            "ES": "camiseta de niño / samarreta nen", "GR": "t-shirt για αγόρια", "HR": "t-shirt za dječake",
            "HU": "fiú póló", "IT": "maglietta per ragazzi", "LT": "Marškinėliai berniukui",
            "LV": "T-krekls zēniem", "PL": "t-shirt chłopięcy", "PT": "T-shirt para rapaz",
            "RO": "T-shirt băieți", "RS": "majica za dečake. Sastav materijala nalazi se na ušivenoj etiketi",
            "SI": "fantovska majica, kratki rokav", "SK": "chlapčenské tričko"
        }
    },
    "Men's Department": {
        "Men's T-shirt": {
            "EN": "Men's T-shirt", "BG": "мъжки T-shirt", "BiH": "muški t-shirt. Sastav materijala na ušivenoj etiketi.",
            "CZ": "pánský t-shirt", "DE": "Herren-T-Shirt", "EE": "Meeste T-särk",
            "ES": "camiseta de hombre / samarreta home", "GR": "ανδρικό κοντομάνικο", "HR": "muški t-shirt",
            "HU": "férfi póló", "IT": "maglietta da uomo", "LT": "Vyriški marškinėliai",
            "LV": "Vīriešu t-krekls", "PL": "t-shirt męski", "PT": "T-shirt para homem",
            "RO": "Tricou bărbați", "RS": "muška majica. Sastav materijala nalazi se na ušivenoj etiketi",
            "SI": "moška majica", "SK": "pánske tričko"
        }
    },
    "Women's Department": {
        "Women's T-shirt": {
            "EN": "Women's T-shirt", "BG": "дамски T-shirt", "BiH": "ženska t-shirt. Sastav materijala na ušivenoj etiketi.",
            "CZ": "dámský t-shirt", "DE": "Damen-T-Shirt", "EE": "Naiste T-särk",
            "ES": "camiseta de mujer / samarreta dona", "GR": "γυναικείο μπλουζάκι", "HR": "ženski t-shirt",
            "HU": "női póló", "IT": "maglietta da donna", "LT": "Moteriški marškinėliai",
            "LV": "Sieviešu t-krekls", "PL": "t-shirt damski", "PT": "T-shirt para mulher",
            "RO": "Tricou femei", "RS": "ženska majica. Sastav materijala nalazi se na ušivenoj etiketi",
            "SI": "ženska majica", "SK": "Dámska blúzka"
        }
    }
}

# ========== HELPER FUNCTIONS ==========
def format_number(value, currency):
    """Format number based on currency type"""
    if currency in ['EUR', 'BGN', 'BAM', 'PLN', 'RON']:
        return f"{float(value):,.2f}".replace(".", ",")
    return str(int(float(value)))

def find_closest_price(pln_value):
    """Find closest PLN value in price table"""
    try:
        pln_value = float(pln_value)
        closest_pln = min(PRICE_DATA['PLN'], key=lambda x: abs(x - pln_value))
        idx = PRICE_DATA['PLN'].index(closest_pln)
        return {
            currency: format_number(values[idx], currency)
            for currency, values in PRICE_DATA.items()
            if currency != 'PLN'
        }
    except (ValueError, TypeError):
        return None

def extract_colour_from_page2(text):
    """Extract and clean color name from page 2"""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    skip_keywords = [
        "PURCHASE PRICE", "COLOUR", "PANTONE NO", "TOTAL ORDERED QUANTITY",
        "TOTAL", "TOTAL ORDERED QTY", "PURCHASE ORDER", "SUPPLIER", "PURCHASE",
        "PRICE", "ORDERED QTY", "Sizes", "1234567890", "TPG", "TPX"
    ]
    filtered_lines = [
        line for line in lines
        if all(keyword.lower() not in line.lower() for keyword in skip_keywords)
        and not re.match(r"^[\d\s,./-]+$", line)
    ]
    colour = filtered_lines[0] if filtered_lines else "UNKNOWN"
    return re.sub(r'\d+', '', colour).strip().upper()

def extract_data_from_pdf(file):
    """Extract data from PDF with improved barcode handling"""
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        if len(doc) < 3:
            st.error("PDF must have at least 3 pages.")
            return []

        # Page 1: Extract Style, Collection, Batch
        page1_text = doc[0].get_text()
        style_match = re.search(r"\b\d{6}\b", page1_text)
        style_value = style_match.group() if style_match else "UNKNOWN"

        collection_match = re.search(r"Collection\s*\.{2,}\s*(.+)", page1_text, re.IGNORECASE)
        collection_value = collection_match.group(1).strip().split(" - ")[0].strip() if collection_match else "UNKNOWN"

        handover_match = re.search(r"Handover\s*date\s*\.{2,}\s*(\d{2}/\d{2}/\d{4})", page1_text, re.IGNORECASE)
        if handover_match:
            try:
                handover_date = datetime.strptime(handover_match.group(1).strip(), "%d/%m/%Y")
                batch = (handover_date - timedelta(days=20)).strftime("%m%Y")
            except ValueError:
                batch = "UNKNOWN"
        else:
            batch = "UNKNOWN"

        # Page 2: Extract Colour
        colour = extract_colour_from_page2(doc[1].get_text())

        # Page 3: Extract SKUs & Barcodes
        page3 = doc[2].get_text()
        skus = re.findall(r"\b\d{8}\b", page3)
        all_barcodes = re.findall(r"\b\d{13}\b", page3)
        excluded_barcodes = set(re.findall(r"barcode:\s*(\d{13});", page3))
        valid_barcodes = [b for b in all_barcodes if b not in excluded_barcodes]
        valid_pairs = list(zip(skus, valid_barcodes))[:min(len(skus), len(valid_barcodes))]

        if len(skus) != len(valid_barcodes):
            st.warning(f"Found {len(skus)} SKUs but {len(valid_barcodes)} valid barcodes after filtering.")

        return [{
            "COLLECTION": collection_value,
            "COLOUR_SKU": f"{colour} • SKU {sku}",
            "STYLE": f"STYLE {style_value} • S/S26",
            "Batch": f"Batch no. {batch}",
            "barcode": barcode
        } for sku, barcode in valid_pairs]

    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return []

# ========== MAIN APP FLOW ==========
uploaded_pdf = st.file_uploader("Upload PDF file", type=["pdf"])

if uploaded_pdf:
    # Department and product selection
    selected_dept = st.selectbox(
        "Select Department",
        options=list(DEPARTMENT_PRODUCTS.keys()),
        index=0
    )
    product_type = st.selectbox(
        "Select Product Type",
        options=list(DEPARTMENT_PRODUCTS[selected_dept].keys()),
        index=0
    )
    
    # Process PDF data
    result_data = extract_data_from_pdf(uploaded_pdf)
    
    if result_data:
        df = pd.DataFrame(result_data)
        
        # Add translations and pricing
        translations = DEPARTMENT_PRODUCTS[selected_dept][product_type]
        df['product_name'] = " | ".join([f"{lang}| {text}" for lang, text in translations.items()])
        
        pln_price = st.number_input("Enter PLN Price", min_value=0.0, step=0.01, format="%.2f")
        
        if pln_price:
            currency_values = find_closest_price(pln_price)
            if currency_values:
                # Add currency columns
                for currency in ['EUR', 'BGN', 'BAM', 'RON', 'CZK', 'RSD', 'HUF']:
                    df[currency] = currency_values.get(currency, "")
                df['PLN'] = format_number(pln_price, 'PLN')
                
                # Reorder columns as requested
                final_columns = [
                    'COLLECTION', 'COLOUR_SKU', 'STYLE', 'Batch', 'barcode',
                    'EUR', 'BGN', 'BAM', 'RON', 'PLN', 'CZK', 'RSD', 'HUF',
                    'product_name'
                ]
                df = df[final_columns]
                
                st.success("✅ Prices and product name added successfully!")
                
                # Data editing
                st.subheader("Edit Data Before Download")
                edited_df = st.data_editor(df)
                
                # CSV generation
                csv_output = StringIO()
                edited_df.to_csv(
                    csv_output,
                    index=False,
                    sep=';',
                    encoding='utf-8',
                    quoting=csv.QUOTE_ALL,
                    quotechar='"'
                )
                
                # Download button
                st.download_button(
                    label="📥 Download",
                    data=csv_output.getvalue().encode('utf-8'),
                    file_name=f"{os.path.splitext(uploaded_pdf.name)[0]}.csv",
                    mime="text/csv",
                    help="Semicolon-delimited UTF-8 CSV with perfect column order"
                )

# Attribution
st.markdown("---")
st.caption("This app developed by Ovi")
