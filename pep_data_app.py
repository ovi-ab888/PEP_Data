# -*- coding: utf-8 -*-
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import csv
from io import StringIO
import csv as pycsv
from datetime import datetime, timedelta
import os

# ========== PRICE DATA (For PEPCO) ==========
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

# ========== PEPCO FUNCTIONS ==========
@st.cache_data(ttl=600)
def load_product_translations():
    sheet_id = "12QAe57IsVCa9-0D06tXYUUpfHbpRTsl2"
    sheet_name = "Sheet1"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load product translations: {str(e)}")
        return pd.DataFrame()

def format_product_translations(product_name, translation_row):
    formatted = []
    country_suffixes = {
        'BiH': " Sastav materijala na ušivenoj etiketi.",
        'RS': " Sastav materijala nalazi se na ušivenoj etiketi.",
    }
    
    # Languages to completely exclude from output
    exclude_languages = ['FR']  # Removed ES_CA from exclude since we want to use it
    
    for lang, value in translation_row.items():
        if lang in ['DEPARTMENT', 'PRODUCT_NAME'] or lang in exclude_languages:
            continue
            
        if lang in country_suffixes:
            # For BiH and RS, use the translated value if available
            base_text = value if pd.notna(value) else product_name
            # Add dot after product name if not already present
            if not base_text.endswith('.'):
                base_text += '.'
            formatted_value = f"{base_text}{country_suffixes[lang]}"
       def format_es(row):
    es = row.get('ES', '').strip() if pd.notna(row.get('ES')) else ''
    es_ca = row.get('ES_CA', '').strip() if pd.notna(row.get('ES_CA')) else ''
    product_name = row.get('product_name', '')

    if es and es_ca:
        return f"{es} / {es_ca}"
    elif es:
        return es
    else:
        return product_name

# নতুন ES কলাম তৈরি করো
df['ES'] = df.apply(format_es, axis=1)

# ES_CA বাদ দাও
df.drop(columns=['ES_CA'], inplace=True)

            # For other languages, use the translation if available
            formatted_value = value if pd.notna(value) else product_name
            
        formatted.append(f"|{lang}| {formatted_value}")
    
    return " ".join(formatted)

def format_number(value, currency):
    if currency in ['EUR', 'BGN', 'BAM', 'RON', 'PLN']:
        return f"{float(value):,.2f}".replace(".", ",")
    return str(int(float(value)))

def find_closest_price(pln_value):
    try:
        pln_value = float(pln_value)
        closest_pln = min(PRICE_DATA['PLN'], key=lambda x: abs(x - pln_value))
        idx = PRICE_DATA['PLN'].index(closest_pln)
        return {currency: format_number(values[idx], currency) for currency, values in PRICE_DATA.items() if currency != 'PLN'}
    except (ValueError, TypeError):
        return None

def extract_colour_from_page2(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    skip_keywords = ["PURCHASE", "COLOUR", "TOTAL", "PANTONE", "SUPPLIER", "PRICE", "ORDERED", "SIZES", "TPG", "TPX", "USD", "PEPCO", "Poland"]
    filtered_lines = [
        line for line in lines
        if all(keyword.lower() not in line.lower() for keyword in skip_keywords)
        and not re.match(r"^[\d\s,./-]+$", line)
    ]
    colour = filtered_lines[0] if filtered_lines else "UNKNOWN"
    return re.sub(r'\d+', '', colour).strip().upper()

def extract_data_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        if len(doc) < 3:
            st.error("PDF must have at least 3 pages.")
            return None
            
        page1 = doc[0].get_text()
        style = re.search(r"\b\d{6}\b", page1)
        collection = re.search(r"Collection\s*\.{2,}\s*(.+)", page1)
        date_match = re.search(r"Handover\s*date\s*\.{2,}\s*(\d{2}/\d{2}/\d{4})", page1)
        batch = "UNKNOWN"
        if date_match:
            try:
                batch = (datetime.strptime(date_match.group(1), "%d/%m/%Y") - timedelta(days=20)).strftime("%m%Y")
            except:
                pass
        colour = extract_colour_from_page2(doc[1].get_text())
        page3 = doc[2].get_text()
        skus = re.findall(r"\b\d{8}\b", page3)
        all_barcodes = re.findall(r"\b\d{13}\b", page3)
        excluded = set(re.findall(r"barcode:\s*(\d{13});", page3))
        valid_barcodes = [b for b in all_barcodes if b not in excluded]
        
        return [{
            "COLLECTION": collection.group(1).split("-")[0].strip() if collection else "UNKNOWN",
            "COLOUR_SKU": f"{colour} • SKU {sku}",
            "STYLE": f"STYLE {style.group()} • B/S26" if style else "STYLE UNKNOWN",
            "Batch": f"Batch no. {batch}",
            "barcode": barcode
        } for sku, barcode in zip(skus, valid_barcodes)]
    except Exception as e:
        st.error(f"PDF error: {str(e)}")
        return None

# ========== PEP&CO FUNCTIONS ==========
def extract_story(page1_text):
    match = re.search(r"Story\s+(.+)", page1_text)
    return match.group(1).split("-")[0].strip() if match else "UNKNOWN"

def extract_table_from_page2(page2_text):
    entries = []
    pattern = re.compile(r"(\d{6})\s+([A-Za-z\s\-]+?:\d+)\s+(\d{13})\s+\d+\s+\d+\s+(\d{4})\s+(\d{6})")
    matches = pattern.findall(page2_text)

    for match in matches:
        sku, raw_desc, barcode, style, style_code = match
        desc_clean = raw_desc.split(":")[0].strip()
        entries.append({
            "sku": sku,
            "sku_description": desc_clean,
            "barcode": barcode,
            "style": style_code
        })
    return entries

def process_pepco_pdf(uploaded_pdf):
    translations_df = load_product_translations()
    
    if uploaded_pdf and not translations_df.empty:
        # First extract data from PDF
        result_data = extract_data_from_pdf(uploaded_pdf)
        
        if result_data:  # Only proceed if we successfully extracted data
            depts = translations_df['DEPARTMENT'].dropna().unique().tolist()
            selected_dept = st.selectbox("Select Department", options=depts)

            filtered = translations_df[translations_df['DEPARTMENT'] == selected_dept]
            products = filtered['PRODUCT_NAME'].dropna().unique().tolist()
            product_type = st.selectbox("Select Product Type", options=products)

            df = pd.DataFrame(result_data)
            product_row = filtered[filtered['PRODUCT_NAME'] == product_type]
            if not product_row.empty:
                df['product_name'] = format_product_translations(product_type, product_row.iloc[0])
            else:
                df['product_name'] = ""

            pln_price = st.number_input("Enter PLN Price", min_value=0.0, step=0.01, format="%.2f")
            if pln_price:
                currency_values = find_closest_price(pln_price)
                if currency_values:
                    for cur in ['EUR', 'BGN', 'BAM', 'RON', 'CZK', 'RSD', 'HUF']:
                        df[cur] = currency_values.get(cur, "")
                    df['PLN'] = format_number(pln_price, 'PLN')

                    final_cols = ['COLLECTION', 'COLOUR_SKU', 'STYLE', 'Batch', 'barcode',
                                  'EUR', 'BGN', 'BAM', 'RON', 'PLN', 'CZK', 'RSD', 'HUF', 'product_name']
                    df = df[final_cols]

                    st.success("✅ Done!")
                    st.subheader("Edit Before Download")

                    edited_df = st.data_editor(df)

                    csv_buffer = StringIO()
                    writer = pycsv.writer(csv_buffer, delimiter=';', quoting=pycsv.QUOTE_ALL)
                    writer.writerow(edited_df.columns)
                    for row in edited_df.itertuples(index=False):
                        writer.writerow(row)

                    st.download_button(
                        "📥 Download CSV",
                        csv_buffer.getvalue().encode('utf-8-sig'),
                        file_name=f"{os.path.splitext(uploaded_pdf.name)[0]}.csv",
                        mime="text/csv"
                    )

def process_pep_and_co_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    if len(doc) < 2:
        st.error("❌ PDF must have at least 2 pages.")
    else:
        story_text = doc[0].get_text()
        page2_text = doc[1].get_text()

        story = extract_story(story_text)
        entries = extract_table_from_page2(page2_text)

        colour = st.text_input("Enter Colour:")
        batch = st.text_input("Enter Batch No:")

        if colour and batch:
            if entries:
                for entry in entries:
                    entry["story"] = story
                    entry["COLOUR_SKU"] = f"{colour} • SKU {entry['sku']}"
                    entry["STYLE"] = f"STYLE {entry['style']} • H/W26"
                    entry["Batch"] = f"Batch no. {batch}"

                df = pd.DataFrame(entries)[["story", "sku_description", "COLOUR_SKU", "STYLE", "Batch", "barcode"]]
                
                st.success("✅ Done!")
                st.subheader("Edit Before Download")
                edited_df = st.data_editor(df)

                csv_buffer = StringIO()
                writer = pycsv.writer(csv_buffer, delimiter=';', quoting=pycsv.QUOTE_ALL)
                writer.writerow(edited_df.columns)
                for row in edited_df.itertuples(index=False):
                    writer.writerow(row)

                st.download_button(
                    "📩 Download CSV",
                    csv_buffer.getvalue().encode('utf-8-sig'),
                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}.csv",
                    mime="text/csv"
                )

# ========== MAIN APP ==========
st.title("PEPCO/PEP&CO Data Processor")

# Select which brand to process
brand = st.radio("Select Brand", ("PEPCO", "PEP&CO"))

if brand == "PEPCO":
    st.subheader("PEPCO Data Processing")
    uploaded_pdf = st.file_uploader("Upload PEPCO Data file", type=["pdf"])
    if uploaded_pdf:
        process_pepco_pdf(uploaded_pdf)
else:
    st.subheader("PEP&CO Data Processing")
    uploaded_file = st.file_uploader("Upload PEP&CO PDF", type="pdf")
    if uploaded_file:
        process_pep_and_co_pdf(uploaded_file)

st.markdown("---")
st.caption("This app developed by Ovi")
