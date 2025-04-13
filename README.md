# 📦 PEP Data Extractor - PDF to CSV

A simple Streamlit web application that extracts barcodes and SKU data from a specific format of PDF and exports it as a CSV file.

Users just need to upload the PDF – the app will take care of the rest!

## 🚀 Live Demo

👉 [Click to Open the App](https://pepdata-pfnuzfqrxh3sy2pudagphq.streamlit.app/)

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** – UI and deployment
- **PyMuPDF (fitz)** – PDF text extraction
- **Pandas** – Data structuring and CSV generation

---

## ⚙️ How to Run Locally

If you want to run this app on your own machine:

```bash
# 1. Clone the repository
git clone https://github.com/ovi-ab888/PEP_Data.git
cd PEP_Data

# 2. Install required packages
pip install -r requirements.txt

# 3. Run the app
streamlit run pep_data_app.py
