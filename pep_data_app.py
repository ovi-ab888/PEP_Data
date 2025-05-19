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
        },
        
         "Girls' sweatshirt": {
            "EN": "Girls' sweatshirt", "BG": "Блуза за момичета", 
            "BiH": "Dukserica za djevojčice. Sastav materijala na ušivenoj etiketi.",
            "CZ": "Dívčí blůza", "DE": "Sweatshirt für Mädchen", "EE": "Tüdrukute pluus",
            "ES": "Sudadera de niña / dessuadora nena", "GR": "Φανέλα για μωρό κορίτσι",
            "HR": "Majica za djevojčice", "HU": "Lány blúz", "IT": "Felpa per ragazze",
            "LT": "Bliuzonas mergaitėms", "LV": "Meiteņu blūze", "PL": "Bluza dziewczęca",
            "PT": "Camisola de manga comprida para rapariga", "RO": "Bluză fetițe",
            "RS": "Dukserica za devojčicu. Sastav materijala nalazi se na ušivenoj etiketi",
            "SI": "Dekliška majica, dolgi rokav", "SK": "Dievčenská mikina"
        },
        
        "Girls' shirt": {
            "EN": "Girls' shirt", "BG": "Риза за момичета",
            "BiH": "Košulja za djevojčice. Sastav materijala na ušivenoj etiketi.",
            "CZ": "Dívčí košile", "DE": "Hemd für Mädchen", "EE": "Tüdrukute särk",
            "ES": "Camisa de niña / camisa nena", "GR": "Πουκάμισο για μωρό κορίτσι",
            "HR": "Košulja za djevojčice", "HU": "Lány ing", "IT": "Camicia per ragazze",
            "LT": "Marškiniai mergaitei", "LV": "Meiteņu krekls", "PL": "Koszula dziewczęca",
            "PT": "Camisa para rapariga", "RO": "Cămașă fetițe",
            "RS": "Košulja za devojčicu. Sastav materijala nalazi se na ušivenoj etiketi",
            "SI": "Dekliška srajca", "SK": "Dievčenská košeľa"
        },
        
        "Girls' pullover sweater": {
            "EN": "Girls' pullover sweater", "BG": "Пуловер за момичета",
            "BiH": "Džemper za djevojčice. Sastav materijala na ušivenoj etiketi.",
            "CZ": "Dívčí svetr", "DE": "Pullover für Mädchen", "EE": "Tüdrukute kampsun",
            "ES": "Suéter de niña / suèter nena", "GR": "Πουλόβερ για μωρό κορίτσι",
            "HR": "Vesta za djevojčice", "HU": "Lány pulóver", "IT": "Maglione per ragazze",
            "LT": "Megztinis mergaitėms", "LV": "Meiteņu svīteris", "PL": "Sweter dziewczęcy",
            "PT": "Suéter para rapariga", "RO": "Pulover fetițe",
            "RS": "Džemper za devojčicu. Sastav materijala nalazi se na ušivenoj etiketi",
            "SI": "Dekliški pulover", "SK": "Dievčenský sveter"
        },
    },
    
    "Boys Department": {
    "boys t-shirt": {
        "EN": "Boys t-shirt",
        "BG": "Момчешка тениска",
        "BiH": "T-shirt za dječake. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Chlapecké tričko",
        "DE": "T-Shirt für Jungen",
        "EE": "Poiste T-särk",
        "ES": "Camiseta de niño / samarreta nen",
        "GR": "T-shirt για αγόρια",
        "HR": "T-shirt za dječake",
        "HU": "Fiú póló",
        "IT": "Maglietta per ragazzi",
        "LT": "Marškinėliai berniukui",
        "LV": "T-krekls zēniem",
        "PL": "T-shirt chłopięcy",
        "PT": "T-shirt para rapaz",
        "RO": "T-shirt băieți",
        "RS": "Majica za dečake. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Fantovska majica, kratki rokav",
        "SK": "Chlapčenské tričko"
    },
    "boys pajamas": {
        "EN": "Boys pajamas",
        "BG": "Пижама за момчета",
        "BiH": "Pidžama za dječake. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Chlapecké pyžamo",
        "DE": "Schlafanzug für Jungen",
        "EE": "Poiste pidžaama",
        "ES": "Pijama de niño / Pijama nen",
        "GR": "Πιτζάμα για αγόρια",
        "HR": "Pidžama za dječake",
        "HU": "Fiú pizsama",
        "IT": "Pigiama per ragazzi",
        "LT": "Pižama berniukams",
        "LV": "Zēnu pidžama",
        "PL": "Piżama chłopięca",
        "PT": "Pijama para rapaz",
        "RO": "Pijama băieți",
        "RS": "Pidžama za dečaka. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Fantovska pižama",
        "SK": "Chlapčenské pyžamo"
    },
    "boys tank top": {
        "EN": "Boys' tank top",
        "BG": "Топ за момчета",
        "BiH": "Top za dječake. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Chlapecký top",
        "DE": "Top für Jungen",
        "EE": "Poiste topp",
        "ES": "Top de niño / top nen",
        "GR": "Μπλουζάκι για μωρό αγόρι",
        "HR": "Topić za dječake",
        "HU": "Fiú top",
        "IT": "Top per ragazzi",
        "LT": "Berankoviai marškinėliai berniukui",
        "LV": "Zēnu tops",
        "PL": "Top chłopięcy",
        "PT": "Top para rapaz",
        "RO": "Top băieți",
        "RS": "Potkošulja za dečaka. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Fantovski top",
        "SK": "Chlapčenský top"
    },
    "boys pullover sweater": {
        "EN": "Boys' pullover sweater",
        "BG": "Пуловер за момчета",
        "BiH": "Džemper za dječake. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Chlapecký svetr",
        "DE": "Pullover für Jungen",
        "EE": "Poiste kampsun",
        "ES": "Suéter de niño / suèter nen",
        "GR": "Πουλόβερ για μωρό αγόρι",
        "HR": "Vesta za dječake",
        "HU": "Fiú pulóver",
        "IT": "Maglione per ragazzi",
        "LT": "Megztinis berniukui",
        "LV": "Zēnu svīteris",
        "PL": "Sweter chłopięcy",
        "PT": "Suéter para rapaz",
        "RO": "Pulover băieți",
        "RS": "Džemper za dečaka. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Fantovski pulover",
        "SK": "Chlapčenský sveter"
    },
    "boys sweatshirt": {
        "EN": "Boys' sweatshirt",
        "BG": "Блуза за момчета",
        "BiH": "Dukserica za dječake. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Chlapecká blůza",
        "DE": "Sweatshirt für Jungen",
        "EE": "Poiste pluus",
        "ES": "Sudadera de niño / dessuadora nen",
        "GR": "Μπουφάν για μωρό αγόρι",
        "HR": "Majica za dječake",
        "HU": "Fiú felső",
        "IT": "Felpa per ragazzi",
        "LT": "Bliuzonas berniukui",
        "LV": "Zēnu džemperis",
        "PL": "Bluza chłopięca",
        "PT": "Camisola de manga comprida para rapaz",
        "RO": "Bluză băieți",
        "RS": "Dukserica za dečaka. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Fantovska majica, dolgi rokav",
        "SK": "Chlapčenská mikina"
    },
    "boys pants": {
        "EN": "Boys' pants",
        "BG": "Панталони за момчета",
        "BiH": "Hlače za dječake. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Chlapecké kalhoty",
        "DE": "Hose für Jungen",
        "EE": "Poiste pikad püksid",
        "ES": "Pantalones de niño / pantalons nen",
        "GR": "Παντελόνι για μωρό αγόρι",
        "HR": "Hlače za dječake",
        "HU": "Fiú nadrág",
        "IT": "Pantaloni per ragazzi",
        "LT": "Kelnės berniukui",
        "LV": "Zēnu bikses",
        "PL": "Spodnie chłopięce",
        "PT": "Calças para rapaz",
        "RO": "Pantaloni băieți",
        "RS": "Pantalone za dečaka. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Fantovske hlače",
        "SK": "Chlapčenské nohavice"
    },
    "boys set": {
        "EN": "Boys' set",
        "BG": "Комплект за момчета",
        "BiH": "Komplet za dječake. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Chlapecký komplet",
        "DE": "Set für Jungen",
        "EE": "Poiste komplekt",
        "ES": "Conjunto de niño / conjunt nen",
        "GR": "Κοστούμι αγόρι",
        "HR": "Komplet za dječake",
        "HU": "Fiú készlet",
        "IT": "Completo per ragazzi",
        "LT": "Komplektas berniukui",
        "LV": "Zēnu komplekts",
        "PL": "Komplet chłopięcy",
        "PT": "Conjunto para rapaz",
        "RO": "Compleu băieți",
        "RS": "Komplet za dečaka. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Fantovski komplet",
        "SK": "Chlapčenský komplet"
    },
    "boys jeans": {
        "EN": "Boys' jeans",
        "BG": "Дънки за момчета",
        "BiH": "Farmerke za dječake. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Chlapecké džíny",
        "DE": "Jungen-Jeans",
        "EE": "Poiste teksad",
        "ES": "Vaqueros para niños / Texans per a nens",
        "GR": "Τζην για αγόρια",
        "HR": "Traperice za dječake",
        "HU": "Gyermek farmer",
        "IT": "Jeans da bambino",
        "LT": "Džinsai berniukams",
        "LV": "Zēnu džinsi",
        "PL": "Jeansy chłopięce",
        "PT": "Calças de ganga para rapazes",
        "RO": "Blugi pentru băieți",
        "RS": "Farmerke za dečake. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Fantovske kavbojke",
        "SK": "Chlapčenské džínsy"
    }
},
        "Baby boy Department": {
        "boys t-shirt": {
            "EN": "boys t-shirt", "BG": "Момчешка тениска", "BiH": "t-shirt za dječake. Sastav materijala na ušivenoj etiketi.",
            "CZ": "chlapecké tričko", "DE": "T-Shirt für Jungen", "EE": "Poiste T-särk",
            "ES": "camiseta de niño / samarreta nen", "GR": "t-shirt για αγόρια", "HR": "t-shirt za dječake",
            "HU": "fiú póló", "IT": "maglietta per ragazzi", "LT": "Marškinėliai berniukui",
            "LV": "T-krekls zēniem", "PL": "t-shirt chłopięcy", "PT": "T-shirt para rapaz",
            "RO": "T-shirt băieți", "RS": "majica za dečake. Sastav materijala nalazi se na ušivenoj etiketi",
            "SI": "fantovska majica, kratki rokav", "SK": "chlapčenské tričko"
        },
    },
        "Baby Girl Department": {
       {
    "baby girl t-shirt": {
        "EN": "Baby girl T-shirt",
        "BG": "бебешка тениска за момичета",
        "BiH": "t-shirt za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecký t-shirt",
        "DE": "T-Shirt für Baby Mädchen",
        "EE": "Beebi T-särk tüdrukutele",
        "ES": "camiseta de bebé para niña / samarreta per a bebè nena",
        "GR": "μπλουζάκι για μωρό κορίτσι",
        "HR": "t-shirt za bebe – djevojčice",
        "HU": "lány baba póló",
        "IT": "maglietta per bambine",
        "LT": "Kūdikių marškinėliai mergaitei",
        "LV": "bērnu t-krekls meitenēm",
        "PL": "t-shirt niemowlęcy dziewczęcy",
        "PT": "T-shirt para bebé menina",
        "RO": "T-shirt bebeluși fetițe",
        "RS": "majica za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroška majica, kratki rokav, dekliška",
        "SK": "dojčenské tričko pre dievčatko"
    },
    "baby girl tank top": {
        "EN": "Baby girl tank top",
        "BG": "бебешки топ за момичета",
        "BiH": "top za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecký top",
        "DE": "Top für Baby Mädchen",
        "EE": "Beebi topp tüdrukutele",
        "ES": "top de bebé para niña / top per a bebè nena",
        "GR": "μπλουζάκι για μωρό κορίτσι",
        "HR": "top za bebe – djevojčice",
        "HU": "lány baba top",
        "IT": "top per bambine",
        "LT": "Kūdikių berankoviai marškinėliai mergaitei",
        "LV": "bērnu tops meitenēm",
        "PL": "top niemowlęcy dziewczęcy",
        "PT": "Top para bebé menina",
        "RO": "top bebeluși fetițe",
        "RS": "top za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroški top, dekliški",
        "SK": "dojčenský top pre dievčatko"
    },
    "baby girl bodysuit": {
        "EN": "Baby girl bodysuit",
        "BG": "Бебешко боди за момичета",
        "BiH": "Bodi za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Body pro miminka dívčí",
        "DE": "Baby-Body für Mädchen",
        "EE": "Beebi bodi tüdrukutele",
        "ES": "Body de bebé para niña / Bodi per a bebè nena",
        "GR": "Ολόσωμο εσώρουχο για μωρό κορίτσι",
        "HR": "Body za bebe – djevojčice",
        "HU": "Kislány body",
        "IT": "Body per bambine",
        "LT": "kūdikių glaustinukė mergaitei",
        "LV": "Bērnu bodijs meitenēm",
        "PL": "Body niemowlęce dziewczęce",
        "PT": "body para bebé menina",
        "RO": "Body bebluși fetițe",
        "RS": "bodić za devojčicu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Otroški bodi, dekliški",
        "SK": "Dievčenské dojčenské body"
    },
    "baby girl footie": {
        "EN": "Baby girl footie",
        "BG": "Бебешки гащеризон ританки за момичета",
        "BiH": "Kombinezon za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Overal pro miminka dívčí",
        "DE": "Baby-Strampler für Mädchen",
        "EE": "Beebi sipupüksid tüdrukutele",
        "ES": "Pelele de bebé para niña / Vestit d’una peça per a bebè nena",
        "GR": "Εσώρουχο μωρού για κορίτσι",
        "HR": "Odijelce za bebe – djevojčice",
        "HU": "Kislány rugdalózó",
        "IT": "Pagliaccetto per bambine",
        "LT": "Šliaužtinukai mergaitei",
        "LV": "Zīdaiņu rāpulīši meitenēm",
        "PL": "Pajac niemowlęcy dziewczęcy",
        "PT": "macacão de manga comprida para bebé menina",
        "RO": "Salopetă bebeluși fetițe",
        "RS": "zeka za devojčicu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Otroški pajac, dekliški",
        "SK": "Dievčenské dojčenské dupačky"
    },
    "baby girl pullover sweater": {
        "EN": "Baby girl pullover sweater",
        "BG": "бебешки пуловер за момичета",
        "BiH": "džemper za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecký svetr",
        "DE": "Pullover für Baby Mädchen",
        "EE": "Beebi kampsun tüdrukutele",
        "ES": "suéter de bebé para niña / suèter per a bebè nena",
        "GR": "πουλόβερ για μωρό κορίτσι",
        "HR": "vesta za bebe – djevojčice",
        "HU": "lány baba pulóver",
        "IT": "maglione per bambine",
        "LT": "Kūdikių megztinis mergaitei",
        "LV": "bērnu svīteris meitenēm",
        "PL": "sweter niemowlęcy dziewczęcy",
        "PT": "Suéter para bebé menina",
        "RO": "pulover bebeluși fetițe",
        "RS": "džemper za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroški pulover, dekliški",
        "SK": "dojčenský svetrík pre dievčatko"
    },
    "baby girl sweatshirt": {
        "EN": "Baby girl sweatshirt",
        "BG": "бебешка блуза за момичета",
        "BiH": "majica za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecká blůzička",
        "DE": "Sweatshirt für Baby Mädchen",
        "EE": "Beebi pluus tüdrukutele",
        "ES": "blusa de bebé para niña / dessuadora per a bebè nena",
        "GR": "μπουφάν για μωρό κορίτσι",
        "HR": "majica za bebe – djevojčice",
        "HU": "lány baba felső",
        "IT": "felpa per bambine",
        "LT": "Kūdikių bliuzonas mergaitei",
        "LV": "bērnu blūze meitenēm",
        "PL": "bluza niemowlęca dziewczęca",
        "PT": "Camisola de manga comprida para bebé menina",
        "RO": "bluză bebeluși fetițe",
        "RS": "dukserica za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroška majica, dolgi rokav, dekliška",
        "SK": "dojčenská mikina pre dievčatko"
    },
    "baby girl shirt": {
        "EN": "Baby girl shirt",
        "BG": "бебешка риза за момичета",
        "BiH": "košulja za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecká košilka",
        "DE": "Hemd für Baby Mädchen",
        "EE": "Beebi särk tüdrukutele",
        "ES": "camisa de bebé para niña / camisa per a bebè nena",
        "GR": "πουκάμισο για μωρό κορίτσι",
        "HR": "košulja za bebe – djevojčice",
        "HU": "lány baba ing",
        "IT": "maglia per bambine",
        "LT": "Kūdikių marškiniai mergaitei",
        "LV": "bērnu krekls meitenēm",
        "PL": "koszula niemowlęca dziewczęca",
        "PT": "Camisa para bebé menina",
        "RO": "cămașă bebeluși fetițe",
        "RS": "košulja za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroška srajca, dekliška",
        "SK": "dojčenská košeľa pre dievčatko"
    },
    "baby girl coat": {
        "EN": "Baby girl coat",
        "BG": "бебешко палто за момичета",
        "BiH": "kaput za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecký plášť",
        "DE": "Mantel für Baby Mädchen",
        "EE": "Beebi mantel tüdrukutele",
        "ES": "abrigo de bebé para niña / abric per a bebè nena",
        "GR": "παλτό μωρού για κορίτσι",
        "HR": "kaput za bebe – djevojčice",
        "HU": "lány baba kabát",
        "IT": "cappotto per bambine",
        "LT": "Kūdikių apsiaustas mergaitei",
        "LV": "bērnu mētelis meitenēm",
        "PL": "płaszcz niemowlęcy dziewczęcy",
        "PT": "Sobretudo para bebé menina",
        "RO": "palton/pardesiu bebeluși fetițe",
        "RS": "kaput za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroški plašč, dekliški",
        "SK": "dojčenský kabátik pre dievčatko"
    },
    "baby girl pants": {
        "EN": "Baby girl pants",
        "BG": "бебешки панталони за момичета",
        "BiH": "hlače za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecké kalhoty",
        "DE": "Hose für Baby Mädchen",
        "EE": "Beebi pikad püksid tüdrukutele",
        "ES": "pantalones de bebé para niña / pantalons per a bebè nena",
        "GR": "παντελόνι για μωρό κορίτσι",
        "HR": "hlače za bebe – djevojčice",
        "HU": "lány baba nadrág",
        "IT": "pantaloni per bambine",
        "LT": "Kūdikių kelnės mergaitei",
        "LV": "bērnu bikses meitenēm",
        "PL": "spodnie niemowlęce dziewczęce",
        "PT": "Calças para bebé menina",
        "RO": "pantaloni bebeluși fetițe",
        "RS": "pantalone za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroške hlače, dekliške",
        "SK": "dojčenské nohavice pre dievčatko"
    },
    "baby girl shorts": {
        "EN": "Baby girl shorts",
        "BG": "бебешки шорти за момичета",
        "BiH": "šorts za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecké šortky",
        "DE": "Shorts für Baby Mädchen",
        "EE": "Beebi lühikesed püksid tüdrukutele",
        "ES": "pantalones cortos de bebé para niña / pantalons curts per a bebè nena",
        "GR": "Σορτς για μωρό κορίτσι",
        "HR": "kratke hlače za bebe – djevojčice",
        "HU": "lány baba rövidnadrág",
        "IT": "pantaloncini per bambine",
        "LT": "Kūdikių šortai mergaitei",
        "LV": "bērnu šorti meitenēm",
        "PL": "szorty niemowlęce dziewczęce",
        "PT": "Calções para bebé menina",
        "RO": "pantaloni scurți bebeluși fetițe",
        "RS": "šorc za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroške kratke hlače, dekliške",
        "SK": "dojčenské šortky pre dievčatko"
    },
    "baby girl skirt": {
        "EN": "Baby girl skirt",
        "BG": "бебешка пола за момичета",
        "BiH": "suknja za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecká suknička",
        "DE": "Rock für Baby Mädchen",
        "EE": "Beebi seelik tüdrukutele",
        "ES": "falda de bebé para niña / faldilla per a bebè nena",
        "GR": "φουστάνι για μωρό κορίτσι",
        "HR": "suknja za bebe – djevojčice",
        "HU": "lány baba szoknya",
        "IT": "gonna per bambine",
        "LT": "Kūdikių sijonėlis mergaitei",
        "LV": "bērnu svārki meitenēm",
        "PL": "spódnica niemowlęca dziewczęca",
        "PT": "Saia para bebé menina",
        "RO": "fustă bebeluși fetițe",
        "RS": "suknja za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroško krilo",
        "SK": "dojčenská sukňa pre dievčatko"
    },
    "baby girl jumpsuit": {
        "EN": "Baby girl jumpsuit",
        "BG": "бебешки гащеризон за момичета",
        "BiH": "kombinezon za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecká kombinéza",
        "DE": "Overall für Baby Mädchen",
        "EE": "Beebi kombinesoon tüdrukutele",
        "ES": "mono de bebé para niña / granota per a bebè nena",
        "GR": "ταγέρ για μωρό κορίτσι",
        "HR": "kombinezon za bebe – djevojčice",
        "HU": "lány baba overall",
        "IT": "tuta per bambine",
        "LT": "Kūdikių kombinezonas mergaitei",
        "LV": "bērnu kombinezons meitenēm",
        "PL": "kombinezon niemowlęcy dziewczęcy",
        "PT": "Macacão para bebé menina",
        "RO": "combinezon bebeluși fetițe",
        "RS": "kombinezon za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroški kombinezon, dekliški",
        "SK": "dojčenská kombinéza pre dievčatko"
    },
    "baby girl leggings": {
        "EN": "Baby girl leggings",
        "BG": "бебешки клинове за момичета",
        "BiH": "helanke za djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "dívčí kojenecké legíny",
        "DE": "Leggings für Baby Mädchen",
        "EE": "Beebi retuusid tüdrukutele",
        "ES": "polainas de bebé para niña / malles per a bebè nena",
        "GR": "κολάν για μωρό κορίτσι",
        "HR": "tajice za bebe – djevojčice",
        "HU": "lány baba leggings",
        "IT": "pantacollant per bambine",
        "LT": "Kūdikių tamprės mergaitei",
        "LV": "bērnu legingi meitenēm",
        "PL": "legginsy niemowlęce dziewczęce",
        "PT": "Leggings para bebé menina",
        "RO": "colanți bebeluși fetițe",
        "RS": "helanke za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroške legice, dekliške",
        "SK": "dievčenské legíny"
    },
    "baby girl set": {
        "EN": "Baby girl set",
        "BG": "бебешки комплект за момичета",
        "BiH": "komplet za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "kojenecká souprava pro holčičku",
        "DE": "Set für Baby Mädchen",
        "EE": "Beebirõivaste komplekt tüdrukutele",
        "ES": "conjunto de bebé para niña / conjunt per a bebè nena",
        "GR": "κοστούμι για μωρό κορίτσι",
        "HR": "kompletić za bebe – djevojčice",
        "HU": "lány baba készlet",
        "IT": "completo per bambine",
        "LT": "Kūdikių komplektas mergaitei",
        "LV": "bērnu komplekts meitenēm",
        "PL": "komplet niemowlęcy dziewczęcy",
        "PT": "Conjunto para bebé menina",
        "RO": "compleu pentru bebeluși fetițe",
        "RS": "komplet za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroški komplet – dekliški",
        "SK": "dievčenský komplet"
    },
    "baby girl top": {
        "EN": "Baby girl top",
        "BG": "бебешка риза за момичета",
        "BiH": "košulja za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "košilka kojenecká pro holčičku",
        "DE": "Hemdchen für Baby Mädchen",
        "EE": "Beebi särk tüdrukutele",
        "ES": "camiseta de bebé para niña / camisa per a bebè nena",
        "GR": "μπλουζάκι για μωρό κορίτσι",
        "HR": "majica za bebe – djevojčice",
        "HU": "lány baba ing",
        "IT": "camicetta per bambine",
        "LT": "Kūdikių marškinėliai mergaitei",
        "LV": "bērnu krekliņš meitenēm",
        "PL": "koszulka niemowlęca dziewczęca",
        "PT": "Camisola para bebé menina",
        "RO": "bluziță pentru bebeluși fetițe",
        "RS": "majica za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "otroška majica, dekliška",
        "SK": "košieľka dojčenská pre dievčatko"
    },
    "baby girls skirt": {
        "EN": "Baby girls skirt",
        "BG": "Бебешка пола за момичета",
        "BiH": "Suknja za bebe djevojčice. Sastav materijala na ušivenoj etiketi.",
        "CZ": "Sukně pro miminka dívčí",
        "DE": "Baby-Rock für Mädchen",
        "EE": "Beebi seelik tüdrukutele",
        "ES": "Falda de bebé para niña / Faldilla per a bebè nena",
        "GR": "Φουστάνι για μωρό κορίτσι",
        "HR": "Suknjica za bebe – djevojčice",
        "HU": "Kislány szoknya",
        "IT": "Gonna per bambine",
        "LT": "Kūdikių sijonėlis mergaitei",
        "LV": "Bērnu svārciņi meitenēm",
        "PL": "Spódniczka niemowlęca dziewczeca",
        "PT": "Saia para bebé menina",
        "RO": "Fustiță bebeluși fetițe",
        "RS": "Suknjica za žensku bebu. Sastav materijala nalazi se na ušivenoj etiketi",
        "SI": "Krilo za dojenčka dekl.",
        "SK": "Dievčenská dojčenská suknička"
    },
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
        "PRICE", "ORDERED QTY", "Sizes", "1234567890", "TPG", "TPX", "USD", ",", "PEPCO", "Poland", "ul. Strzeszyńska 73A, 60-479 Poznań", "NIP 782-21-31-157"
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
        df['product_name'] = " |".join([f"{lang}| {text}" for lang, text in translations.items()])
        
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
