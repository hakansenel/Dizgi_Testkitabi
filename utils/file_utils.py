# utils/file_utils.py
import os
import re
import glob
from collections import defaultdict

def dosya_sirala(dosya_adi):
    """Dosyaları yıl ve soru numarasına göre sıralar"""
    yil_match = re.search(r'(\d{4})', os.path.basename(dosya_adi))
    yil = int(yil_match.group(1)) if yil_match else 0
    
    soru_match = re.search(r'[Ss]oru\s*(\d+)', os.path.basename(dosya_adi))
    soru_no = int(soru_match.group(1)) if soru_match else 0
    
    return (yil, soru_no)

def word_dosyalarini_bul(girdi_klasor):
    """Girdi klasöründeki Word dosyalarını bulur ve sıralar"""
    word_dosyalari = glob.glob(os.path.join(girdi_klasor, "*.docx"))
    word_dosyalari.sort(key=dosya_sirala)
    return word_dosyalari

def klasor_kontrol(girdi_klasor, cikti_klasor):
    """Klasör varlığını kontrol eder, gerekirse oluşturur"""
    if not os.path.exists(girdi_klasor):
        raise FileNotFoundError(f"Girdi klasörü bulunamadı: {girdi_klasor}")
    
    if not os.path.exists(cikti_klasor):
        os.makedirs(cikti_klasor)
        print(f"✓ Çıktı klasörü oluşturuldu: {cikti_klasor}")
    
    return True