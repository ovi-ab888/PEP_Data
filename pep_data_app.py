import streamlit as st

# 🔐 
def check_password():
    def password_entered():
        if st.session_state["password"] == "password":  
            st.session_state["authenticated"] = True
            del st.session_state["password"]
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.text_input("🔐 Enter password to access the app", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["authenticated"]:
        st.error("❌ wrong password")
        return False
    else:
        return True

# ✅ 
if check_password():
    st.title("😊 Hello! Ovi Convert your PDF to CSV")
    
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
from io import BytesIO
from datetime import datetime, timedelta
import os

st.title("😊 Hello! Ovi Convert your PDF to CSV")

uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])

def extract_colour_from_page2(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    skip_keywords = [
        "PURCHASE PRICE", "COLOUR", "PANTONE NO", "PURCHASE PRICE",
        "TOTAL ORDERED QUANTITY", "TOTAL", "TOTAL ORDERED QTY", "PURCHASE ORDER",
        "SUPPLIER", "PURCHASE", "PRICE", "ORDERED QTY", "Sizes"
    ]

    filtered_lines = [
        line for line in lines
        if all(keyword.lower() not in line.lower() for keyword in skip_keywords)
        and not re.match(r"^[\d\s,./-]+$", line)  # Skip pure numbers/quantities
    ]

    colour = filtered_lines[0] if filtered_lines else "UNKNOWN"
    return colour

def extract_data_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")

    if len(doc) < 3:
        st.error("PDF must have at least 3 pages.")
        return []

    # First Page: Extract COLLECTION, STYLE, BATCH
    page1_text = doc[0].get_text()

    # STYLE (6-digit)
    style_match = re.search(r"\b\d{6}\b", page1_text)
    style_value = style_match.group() if style_match else "UNKNOWN"

    # COLLECTION
    collection_match = re.search(r"Collection\s*\.{2,}\s*(.+)", page1_text, re.IGNORECASE)
    if collection_match:
        full_collection = collection_match.group(1).strip()
        collection_value = full_collection.split(" - ")[0].strip()
    else:
        collection_value = "UNKNOWN"

    # BATCH
    handover_match = re.search(r"Handover\s*date\s*\.{2,}\s*(\d{2}/\d{2}/\d{4})", page1_text, re.IGNORECASE)
    if handover_match:
        handover_str = handover_match.group(1).strip()
        try:
            handover_date = datetime.strptime(handover_str, "%d/%m/%Y")
            batch_date = handover_date - timedelta(days=20)
            batch = batch_date.strftime("%m%Y")
        except ValueError:
            batch = "UNKNOWN"
    else:
        batch = "UNKNOWN"

    # 2nd Page: Extract Colour
    page2_text = doc[1].get_text()
    colour = extract_colour_from_page2(page2_text)

    # 3rd Page: Extract SKUs & Barcodes
    page3 = doc[2].get_text()
    skus = re.findall(r"\b\d{8}\b", page3)
    barcodes = re.findall(r"\b\d{13}\b", page3)

    if len(skus) != len(barcodes):
        st.warning(f"Found {len(skus)} SKUs but {len(barcodes)} barcodes. Matching by position.")

    # Create final data
    data = []
    for i in range(min(len(skus), len(barcodes))):
        data.append({
            "COLLECTION": collection_value,
            "COLOUR_SKU": f"{colour} • SKU {skus[i]}",
            "STYLE": f"STYLE {style_value} • S/S25",
            "Batch": f"Batch No. {batch}",
            "barcode": barcodes[i]
        })

    return data

if uploaded_file:
    # Extract the base name of the uploaded file (without extension)
    uploaded_filename = uploaded_file.name
    base_filename = os.path.splitext(uploaded_filename)[0]

    result_data = extract_data_from_pdf(uploaded_file)

    if result_data:
        df = pd.DataFrame(result_data)
        st.success("✅ Data extracted successfully!")
        st.dataframe(df)

        # Download CSV with the same name as the uploaded PDF
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV file",
            data=csv,
            file_name=f"{base_filename}.csv",  # Use the base name of the uploaded PDF
            mime="text/csv"
        )
