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

import pandas as pd

# ========== PRICE DATA (For PEPCO) ==========
PRICE_DATA = {
    'PLN': [0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.3, 1.5, 1.8, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 12, 15, 17, 18, 20, 22, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 250],
    'EUR': [0.05, 0.05, 0.1, 0.1, 0.1, 0.15, 0.2, 0.2, 0.25, 0.25, 0.35, 0.4, 0.4, 0.45, 0.5, 0.65, 0.8, 0.9, 1, 1.2, 1.3, 1.5, 1.8, 2, 2.3, 2.5, 3, 4, 4.5, 4.5, 5, 5.5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20, 22, 23, 24, 25, 28, 30, 33, 35, 38, 40, 43, 45, 48, 50, 53],
    'BGN': [0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4, 0.5, 0.6, 0.7, 0.7, 0.8, 1, 1, 1.5, 1.5, 2, 2.3, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7, 7.5, 8, 9, 10, 15, 17, 18, 19, 20, 23, 25, 28, 30, 35, 40, 40, 40, 45, 50, 55, 58, 60, 65, 70, 75, 80, 90, 95, 100, 105],
    'BAM': [0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4, 0.4, 0.5, 0.6, 0.6, 0.7, 0.8, 1, 1.25, 1.5, 1.75, 2, 2.3, 2.5, 3, 3.5, 4, 4.5, 5, 6, 8, 9, 9.5, 10, 11, 12, 15, 17, 20, 22, 23, 25, 30, 33, 35, 38, 40, 43, 45, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 125],
    'RON': [0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.3, 1.4, 1.5, 1.8, 2, 2.5, 3, 3.5, 4.5, 5, 6, 7, 8, 9, 9.5, 10, 13, 16, 18, 19, 21, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 85, 90, 95, 100, 105, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 220, 260],
    'CZK': [1, 2, 2, 2, 3, 4, 5, 5, 6, 6, 9, 9, 9, 12, 12, 15, 20, 22, 25, 27, 30, 35, 40, 50, 55, 60, 70, 90, 100, 110, 120, 130, 150, 180, 200, 250, 280, 300, 330, 350, 390, 420, 450, 480, 510, 540, 570, 600, 670, 740, 800, 880, 950, 1000, 1050, 1100, 1150, 1200, 1300],
    'RSD': [5, 5, 10, 15, 15, 20, 20, 25, 30, 30, 40, 45, 50, 50, 60, 70, 90, 100, 120, 130, 150, 180, 200, 250, 270, 300, 350, 450, 550, 570, 600, 650, 700, 900, 1000, 1200, 1300, 1500, 1600, 1700, 1800, 2000, 2200, 2500, 2500, 2600, 2800, 3000, 3300, 3600, 4000, 4500, 5000, 5300, 5600, 5900, 6200, 6500, 6700],
    'HUF': [12, 25, 35, 35, 45, 55, 60, 65, 75, 100, 120, 130, 150, 180, 200, 250, 300, 350, 400, 430, 500, 550, 650, 750, 850, 1000, 1200, 1500, 1600, 1700, 1800, 2000, 2500, 2900, 3200, 3600, 4000, 4500, 4800, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 25000]
}

# ========== PEPCO FUNCTIONS ==========

# ✅ Google Sheet থেকে অনুবাদ লোড করার ফাংশন
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

# ✅ অনুবাদ ফরম্যাট করার ফাংশন
def format_product_translations(product_name, translation_row):
    formatted = []
    
    # দেশভিত্তিক অতিরিক্ত টেক্সট
    country_suffixes = {
        'BiH': " Sastav materijala na ušivenoj etiketi.",
        'RS': " Sastav materijala nalazi se na ušivenoj etiketi.",
    }

    # এই ভাষাগুলো বাদ যাবে
    exclude_languages = ['ES_CA', 'FR']  # 'FR' বাদ দিয়েছো, এবং 'ES_CA' কে ES এর সাথে মিশানো হবে

    for lang, value in translation_row.items():
        if lang in ['DEPARTMENT', 'PRODUCT_NAME'] or lang in exclude_languages:
            continue

        # 🇧🇦 BiH ও 🇷🇸 RS: অতিরিক্ত suffix সহ
        if lang in country_suffixes:
            base_text = value if pd.notna(value) else product_name
            if not base_text.endswith('.'):
                base_text += '.'
            formatted_value = f"{base_text}{country_suffixes[lang]}"
        
        # 🇪🇸 Spanish + Catalan
        elif lang == 'ES':
            es_value = value.strip() if pd.notna(value) else ''
            es_ca_value = translation_row.get('ES_CA', '').strip() if pd.notna(translation_row.get('ES_CA')) else ''
            if es_value and es_ca_value:
                formatted_value = f"{es_value} / {es_ca_value}"
            elif es_value:
                formatted_value = es_value
            else:
                formatted_value = product_name

        # অন্যান্য ভাষা
        else:
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

def extract_colour_from_page2(text, page_number=1):
    try:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        skip_keywords = ["PURCHASE", "COLOUR", "TOTAL", "PANTONE", "SUPPLIER", 
                        "PRICE", "ORDERED", "SIZES", "TPG", "TPX", "USD", 
                        "PEPCO", "Poland", "ul. Strzeszyńska 73A, 60-479 Poznań", 
                        "NIP 782-21-31-157"]
        
        filtered_lines = [
            line for line in lines
            if all(keyword.lower() not in line.lower() for keyword in skip_keywords)
            and not re.match(r"^[\d\s,./-]+$", line)
        ]
        
        colour = "UNKNOWN"
        if filtered_lines:
            colour = filtered_lines[0]
            # Remove numbers and special characters
            colour = re.sub(r'[\d\.\)\(]+', '', colour).strip().upper()
            
            # Check if colour contains "MANUAL"
            if "MANUAL" in colour:
                st.warning(f"⚠️ Page {page_number}: 'MANUAL' detected in colour field")
                manual_colour = st.text_input(f"Enter Colour (Page {page_number}):", 
                                            key=f"colour_{page_number}")
                return manual_colour.upper() if manual_colour else "UNKNOWN"
            
            return colour if colour else "UNKNOWN"
        
        # If no colour found at all
        st.warning(f"⚠️ Page {page_number}: Colour information not found in PDF")
        manual_colour = st.text_input(f"Enter Colour (Page {page_number}):", 
                                    key=f"colour_{page_number}")
        return manual_colour.upper() if manual_colour else "UNKNOWN"
        
    except Exception as e:
        st.error(f"Error extracting colour: {str(e)}")
        return "UNKNOWN"

def extract_data_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        if len(doc) < 3:
            st.error("PDF must have at least 3 pages.")
            return None

        page1 = doc[0].get_text()
        
        # Extract Merch code (with slashes) and Season
        merch_code = re.search(r"Merch\s*code\s*\.{2,}\s*([\w/]+)", page1)
        season = re.search(r"Season\s*\.{2,}\s*(\w+)?\s*(\d{2})", page1)  # Capture last 2 digits of season
        
        # Format the STYLE part
        style_code = re.search(r"\b\d{6}\b", page1)
        style_suffix = ""
        
        if merch_code and season:
            merch_value = merch_code.group(1).strip()
            season_digits = season.group(2)
            style_suffix = f"{merch_value}{season_digits}"
        elif merch_code:
            style_suffix = merch_code.group(1).strip()

        collection = re.search(r"Collection\s*\.{2,}\s*(.+)", page1)
        date_match = re.search(r"Handover\s*date\s*\.{2,}\s*(\d{2}/\d{2}/\d{4})", page1)
        batch = "UNKNOWN"
        if date_match:
            try:
                batch = (datetime.strptime(date_match.group(1), "%d/%m/%Y") - timedelta(days=20)).strftime("%m%Y")
            except:
                pass

        order_id = re.search(r"Order\s*-\s*ID\s*\.{2,}\s*(.+)", page1)
        item_class = re.search(r"Item classification\s*\.{2,}\s*(.+)", page1)
        supplier_code = re.search(r"Supplier product code\s*\.{2,}\s*(.+)", page1)
        supplier_name = re.search(r"Supplier name\s*\.{2,}\s*(.+)", page1)

        colour = extract_colour_from_page2(doc[1].get_text())
        page3 = doc[2].get_text()
        skus = re.findall(r"\b\d{8}\b", page3)
        all_barcodes = re.findall(r"\b\d{13}\b", page3)
        excluded = set(re.findall(r"barcode:\s*(\d{13});", page3))
        valid_barcodes = [b for b in all_barcodes if b not in excluded]

        result = [{
            "Order_ID": order_id.group(1).strip() if order_id else "UNKNOWN",
            "STYLE_CODE": style_code.group() if style_code else "UNKNOWN",
            "COLOUR": colour,
            "Supplier_product_code": supplier_code.group(1).strip() if supplier_code else "UNKNOWN",
            "Item_classification": item_class.group(1).strip() if item_class else "UNKNOWN",
            "Supplier_name": supplier_name.group(1).strip() if supplier_name else "UNKNOWN",
            "today_date": datetime.today().strftime('%d-%m-%Y'),
            "COLLECTION": collection.group(1).split("-")[0].strip() if collection else "UNKNOWN",
            "COLOUR_SKU": f"{colour} • SKU {sku}",
            "STYLE": f"STYLE {style_code.group()} • {style_suffix}" if style_code else "STYLE UNKNOWN",
            "Batch": f"Batch no. {batch}",
            "barcode": barcode
        } for sku, barcode in zip(skus, valid_barcodes)]

        return result

    except Exception as e:
        st.error(f"PDF error: {str(e)}")
        return None


def extract_story(page1_text):
    match = re.search(r"Story\s+(.+)", page1_text)
    return match.group(1).split("-")[0].strip() if match else "UNKNOWN"

def extract_table_from_page2(page2_text):
    lines = [line.strip() for line in page2_text.splitlines() if line.strip()]

    # Skip header lines: Find first 6-digit SKU
    data_start = next(i for i, line in enumerate(lines) if re.match(r"^\d{6}$", line))

    # Now, every 11 lines = 1 product
    entries = []
    while data_start + 10 < len(lines):
        sku = lines[data_start]
        desc = lines[data_start + 1]
        barcode = lines[data_start + 2]
        style = lines[data_start + 6]

        if re.match(r"^\d{6}$", sku) and re.match(r"^\d{13}$", barcode) and re.match(r"^\d{6}$", style):
            clean_desc = desc.split(":")[0].strip()
            entries.append({
                "sku": sku,
                "sku_description": clean_desc,
                "barcode": barcode,
                "style": style
            })

        data_start += 11  # move to next block

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

                    final_cols = [
    "Order_ID", "STYLE_CODE", "COLOUR", "Supplier_product_code", "Item_classification", "Supplier_name",
    "today_date", "COLLECTION", "COLOUR_SKU", "STYLE", "Batch", "barcode",
    "EUR", "BGN", "BAM", "PLN", "RON", "CZK", "RSD", "HUF", "product_name"
]

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

# ========== PEP&CO FUNCTIONS ==========

from datetime import datetime, timedelta

def extract_story(page1_text):
    match = re.search(r"Story\s+(.+)", page1_text)
    return match.group(1).split("-")[0].strip() if match else "UNKNOWN"

def extract_pack_details(text):
    details = {}

    order = re.search(r"Order Number\s+(\d+)", text)
    details["Order Number"] = order.group(1).strip() if order else "UNKNOWN"

    supplier = re.search(r"Supplier name\s+([^\n]+)", text)
    details["Supplier name"] = supplier.group(1).strip() if supplier else "UNKNOWN"

    handover = re.search(r"Handover Date\s+(\d{4}-\d{2}-\d{2})", text)
    details["_handover_date"] = handover.group(1) if handover else None  # internal only, not for CSV

    sku_match = re.search(r"\b(\d{6})\b", text)
    details["Pack SKU"] = sku_match.group(1) if sku_match else "UNKNOWN"

    barcode_match = re.search(r"\b(\d{13})\b", text)
    details["Pack Barcode"] = barcode_match.group(1) if barcode_match else "UNKNOWN"

    return details

def extract_table_from_page2(page2_text):
    lines = [line.strip() for line in page2_text.splitlines() if line.strip()]
    data_start = next(i for i, line in enumerate(lines) if re.match(r"^\d{6}$", line))

    entries = []
    while data_start + 10 < len(lines):
        sku = lines[data_start]
        desc = lines[data_start + 1]
        barcode = lines[data_start + 2]
        style = lines[data_start + 6]

        if re.match(r"^\d{6}$", sku) and re.match(r"^\d{13}$", barcode) and re.match(r"^\d{6}$", style):
            clean_desc = desc.split(":")[0].strip()
            entries.append({
                "sku": sku,
                "sku_description": clean_desc,
                "barcode": barcode,
                "style": style
            })

        data_start += 11

    return entries

def process_pep_and_co_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    if len(doc) < 2:
        st.error("\u274c PDF must have at least 2 pages.")
        return

    story_text = doc[0].get_text()
    page2_text = doc[1].get_text()

    story = extract_story(story_text)
    details = extract_pack_details(story_text)
    entries = extract_table_from_page2(page2_text)

    colour = st.text_input("Enter Colour:")
    sku_description_input = st.text_input("Enter Description:")

    group_options = [
        "KIDSWEAR / BABY CLOTHING",
        "KIDSWEAR / KIDS CLOTHING",
        "MENSWEAR / MENS CLOTHING",
        "WOMENSWEAR / WOMENS CLOTHING",
        "KIDSWEAR / BABY ESSENTIALS",
        "KIDSWEAR / KIDS ESSENTIALS",
        "MENSWEAR / MENS ESSENTIALS",
        "WOMENSWEAR / WOMENS ESSENTIALS"
    ]
    selected_group = st.selectbox("Select Department", options=group_options)

    batch_options = ["Order Number", "Handover Date"]
    batch_choice = st.selectbox("Select Batch Source", options=batch_options)

    if colour and sku_description_input:
        if entries:
            for entry in entries:
                entry["sku_description"] = sku_description_input
                entry["story"] = story
                entry["COLOUR_SKU"] = f"{colour} • SKU {entry['sku']}"
                entry["STYLE"] = f"STYLE {entry['style']} • H/W26"
                entry["STYLE_code"] = entry['style']  # শুধুমাত্র STYLE code (যেমন: 123456)
                entry["today_date"] = datetime.today().strftime('%d/%m/%Y')
                entry["colour"] = colour

                if batch_choice == "Order Number":
                    entry["Batch"] = f"Batch no. {details['Order Number']}"
                else:
                    try:
                        handover_date = datetime.strptime(details["_handover_date"], "%Y-%m-%d")
                        batch_date = handover_date - timedelta(days=20)
                        entry["Batch"] = f"Batch no. {batch_date.strftime('%m%Y')}"
                    except:
                        entry["Batch"] = "Batch no. UNKNOWN"

                entry.update({
                    "Order Number": details["Order Number"],
                    "Supplier name": details["Supplier name"],
                    "Pack SKU": details["Pack SKU"],
                    "Pack Barcode": details["Pack Barcode"],
                    "Department": selected_group
                })

            df = pd.DataFrame(entries)[[
                "Order Number", "Supplier name", "today_date",
                "Pack SKU", "Pack Barcode", "Department",
                "story", "sku_description", "COLOUR_SKU", "STYLE", "STYLE_code", "Batch", "barcode",
                "colour"
            ]]

            st.success("\u2705 Done!")
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
