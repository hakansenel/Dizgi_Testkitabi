import os
from datetime import datetime
from collections import defaultdict

# LGS derslerine göre soru sayıları
DERS_SORU_SAYILARI = {
    "turkce": 20,
    "matematik": 20,
    "fen": 20,
    "inkilap": 10,
    "din": 10,
    "ingilizce": 10
}

# Ders adları ve kodları
DERS_BILGILERI = {
    "turkce": "Türkçe",
    "matematik": "Matematik",
    "fen": "Fen Bilimleri",
    "inkilap": "İnkılap",
    "din": "Din Kültürü",
    "ingilizce": "İngilizce"
}

# Ders renkleri (profesyonel görünüm için)
DERS_RENKLERI = {
    "Türkçe": (0.7, 0.1, 0.1),
    "Matematik": (0.1, 0.3, 0.7),
    "Fen Bilimleri": (0.1, 0.7, 0.3),
    "İnkılap": (0.7, 0.5, 0.1),
    "Din Kültürü": (0.5, 0.1, 0.5),
    "İngilizce": (0.7, 0.7, 0.1),
    "Bilinmeyen": (0.4, 0.4, 0.4)
}

# JSON to Word dönüştürücü için dosya yolları
JSON_INPUT_DIR = "C:/Users/Öykü/Desktop/claude/solorota/docs/JSON"
JSON_OUTPUT_DIR = "C:/Users/Öykü/Desktop/claude/solorota/docs/JSON_processed"
WORD_OUTPUT_DIR = "C:/Users/Öykü/Desktop/claude/solorota/docs/Word_output"

# Klasörleri oluştur (eğer yoksa)
for dir_path in [JSON_OUTPUT_DIR, WORD_OUTPUT_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)