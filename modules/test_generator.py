# modules/test_generator.py
# Testleri oluşturma ve PDF'e çevirme işlemleri

import os
import re
import glob
from collections import defaultdict
from config import DERS_BILGILERI, DERS_SORU_SAYILARI
from modules.question_extractor import paralel_sorulari_ayikla, json_sorulari_ayikla
from utils.pdf_utils import pdf_olustur_test, olustur_derleme_kilavuzu

# test_generator.py içinde islemi_gerceklestir fonksiyonu güncelleyin

def islemi_gerceklestir(girdi_klasor, cikti_klasor, test_sayisi=5):
    """
    Ana işlem fonksiyonu - JSON soruları tek test içine, DOCX soruları farklı testlere dağıtır
    """
    # Klasör kontrolleri
    if not os.path.exists(girdi_klasor):
        print(f"⚠️ Girdi klasörü bulunamadı: {girdi_klasor}")
        return
    
    if not os.path.exists(cikti_klasor):
        os.makedirs(cikti_klasor)
        print(f"✓ Çıktı klasörü oluşturuldu: {cikti_klasor}")
    
    # Word ve JSON dosyalarını bul
    word_dosyalari = glob.glob(os.path.join(girdi_klasor, "*.docx"))
    json_dosyalari = glob.glob(os.path.join(girdi_klasor, "*.json"))
    
    if not word_dosyalari and not json_dosyalari:
        print(f"⚠️ {girdi_klasor} klasöründe Word veya JSON dosyası bulunamadı.")
        return
    
    print(f"✓ {len(word_dosyalari)} Word dosyası, {len(json_dosyalari)} JSON dosyası bulundu.")
    
    # Soru gruplarını derslere ve yıllara göre ayır
    ders_yil_grupları = defaultdict(lambda: defaultdict(list))
    
    # Önce Word dosyalarını işle (çoklu test için)
    for dosya in word_dosyalari:
        # Word dosyası için paralel soruları çıkar
        sonuc = paralel_sorulari_ayikla(dosya)
        
        # Sonuçları al
        paralel_sorular = sonuc["sorular"]
        yil = sonuc["yil"]
        ana_soru_no = sonuc["ana_soru_no"]
        ders_adi = sonuc["ders_adi"]
        
        # Yeterli sayıda soru var mı kontrol et
        if len(paralel_sorular) > 0:
            # Dersin yıl grubuna ekle
            ders_yil_grupları[ders_adi][yil].append({
                "dosya": dosya,
                "sorular": paralel_sorular,
                "ana_soru_no": ana_soru_no,
                "dosya_tipi": "word"
            })
    
    # Şimdi JSON dosyalarını işle (tek test için)
    for dosya in json_dosyalari:
        # JSON dosyası için soruları çıkar
        sonuc = json_sorulari_ayikla(dosya)
        
        # Sonuçları al
        json_sorular = sonuc["sorular"]
        yil = sonuc["yil"]
        ders_adi = sonuc["ders_adi"]
        
        # JSON soruları varsa
        if len(json_sorular) > 0:
            # Dersin yıl grubuna ekle
            ders_yil_grupları[ders_adi][yil].append({
                "dosya": dosya,
                "sorular": json_sorular,
                "ana_soru_no": 1,  # JSON için ana soru numarası önemli değil
                "dosya_tipi": "json"
            })
    
    # Her ders ve yıl için test oluştur
    for ders_adi, yil_gruplari in ders_yil_grupları.items():
        for yil, soru_gruplari in yil_gruplari.items():
            print(f"\n=== {ders_adi} - {yil} Yılı Testleri Oluşturuluyor ===")
            
            # Dosya tiplerini ayır
            word_gruplari = [g for g in soru_gruplari if g.get("dosya_tipi") == "word"]
            json_gruplari = [g for g in soru_gruplari if g.get("dosya_tipi") == "json"]
            
            # WORD DOSYALARI İÇİN ÇOKLU TEST OLUŞTUR
            if word_gruplari:
                # Toplam soru sayısı ve test başına düşen soru adedi hesapla
                toplam_soru = len(word_gruplari)
                ders_kodu = next((k for k, v in DERS_BILGILERI.items() if v == ders_adi), ders_adi.lower())
                hedef_soru_sayisi = DERS_SORU_SAYILARI.get(ders_kodu, 10)  # Varsayılan olarak 10 soru
                
                print(f"WORD: Toplam {toplam_soru} soru bulundu. Test başına {hedef_soru_sayisi} soru hedefleniyor.")
                
                # Test gruplarını oluştur
                test_sorulari = [[] for _ in range(test_sayisi)]
                
                # Soru gruplarını soru numarasına göre sırala
                word_gruplari.sort(key=lambda x: x["ana_soru_no"])
                
                # Soru dağılımı için soru gruplarını döngüye sokuyoruz
                for soru_grubu in word_gruplari:
                    ana_sorular = soru_grubu["sorular"]
                    ana_soru_no = soru_grubu["ana_soru_no"]
                    
                    # Her paralel soruyu bir teste ekle
                    for i, soru in enumerate(ana_sorular):
                        if i < test_sayisi:  # Test sayısı kadar paralel soru varsa
                            # Soru numarasını ayarla
                            test_index = i % test_sayisi
                            
                            # Her testte aynı soru numarası yerine, testteki soru sayısına göre numara ver
                            soru_position = len(test_sorulari[test_index]) + 1
                            soru["soru_no"] = soru_position
                            
                            # Soruyu teste ekle
                            test_sorulari[test_index].append(soru)
                
                # Her test için PDF oluştur
                for i, test in enumerate(test_sorulari):
                    test_no = i + 1
                    print(f"Word Test {test_no}: {len(test)} soru içeriyor.")
                    
                    # PDF oluştur
                    if test:  # Boş değilse
                        pdf_yolu = os.path.join(cikti_klasor, f"{ders_adi}_Word_Test_{test_no}.pdf")
                        pdf_olustur_test(test, pdf_yolu, test_no, ders_adi, yil)
            
            # JSON DOSYALARI İÇİN TEK TEST OLUŞTUR
            if json_gruplari:
                # Tüm JSON sorularını birleştir
                tum_json_sorular = []
                sira = 1
                
                for json_grup in json_gruplari:
                    for soru in json_grup["sorular"]:
                        # Soru numarasını güncelle - ardışık olarak
                        soru["soru_no"] = sira
                        sira += 1
                        # Soruyu ekle
                        tum_json_sorular.append(soru)
                
                print(f"JSON: Toplam {len(tum_json_sorular)} soru birleştirildi ve tek teste ekleniyor.")
                
                # PDF oluştur
                if tum_json_sorular:  # Boş değilse
                    pdf_yolu = os.path.join(cikti_klasor, f"{ders_adi}_JSON_Test.pdf")
                    pdf_olustur_test(tum_json_sorular, pdf_yolu, 1, ders_adi, yil)
    
    # Derleme kılavuzu PDF'i oluştur
    olustur_derleme_kilavuzu(cikti_klasor, ders_yil_grupları)
    
    print("\n✓ İşlem tamamlandı!")