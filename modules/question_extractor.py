# modules/question_extractor.py
# Word dosyalarından soru ve görselleri çıkarma fonksiyonları

import os
import re
import json
import random
import zipfile
import shutil
from docx import Document
from config import DERS_BILGILERI

def paralel_sorulari_ayikla(dosya_adi):
    """Word belgesinden paralel soruları ve resimleri çıkarır"""
    try:
        document = Document(dosya_adi)
        
        # Dosya adından yıl ve soru numarasını çıkar
        yil_match = re.search(r'(\d{4})', os.path.basename(dosya_adi))
        yil = yil_match.group(1) if yil_match else "0000"
        
        soru_match = re.search(r'[Ss]oru\s*(\d+)', os.path.basename(dosya_adi))
        ana_soru_no = int(soru_match.group(1)) if soru_match else 0
        
        # Ders adını belirle
        dosya_adi_lower = os.path.basename(dosya_adi).lower()
        ders_adi = None
        for kod, bilgi in DERS_BILGILERI.items():
            if kod in dosya_adi_lower or bilgi.lower() in dosya_adi_lower:
                ders_adi = bilgi
                break
        
        if not ders_adi:
            # Klasör adından ders adını çıkar
            klasor_adi = os.path.basename(os.path.dirname(dosya_adi))
            if klasor_adi:
                # Klasör adındaki ilk harfi büyük, diğerlerini küçük yap
                ders_adi = klasor_adi.capitalize()
            else:
                # Klasör adı yoksa dosya adından alabilir ya da 
                # bir varsayılan değer kullanabilirsiniz
                ders_adi = os.path.splitext(os.path.basename(dosya_adi))[0].capitalize()
        
        # Belgenin tüm paragraflarını al ve soru bölümlerini belirle
        paragraflar = []
        paragraf_konumlari = []  # Paragraf konumlarını takip etmek için
        
        for i, para in enumerate(document.paragraphs):
            paragraflar.append(para.text)
            paragraf_konumlari.append(i)
        
        # Resimleri geçici bir klasöre kaydet
        temp_dir = os.path.join(os.path.dirname(dosya_adi), "temp_images")
        os.makedirs(temp_dir, exist_ok=True)

        image_files = []  # Çıkarılan resim dosyalarının yollarını tutacak
        try:
            with zipfile.ZipFile(dosya_adi, 'r') as zip_ref:
                # Media klasörünü ara
                media_files = [f for f in zip_ref.namelist() if f.startswith('word/media/')]
                
                print(f"ZIP içinde {len(media_files)} media dosyası bulundu")
                
                # Tüm media dosyalarını çıkar
                for i, media_file in enumerate(media_files):
                    # Geçici klasöre çıkar
                    zip_ref.extract(media_file, temp_dir)
                    
                    # Dosyayı yeniden adlandır
                    src_path = os.path.join(temp_dir, media_file)
                    _, ext = os.path.splitext(media_file)  # Dosya uzantısını koru
                    new_filename = f"soru{ana_soru_no}_resim{i+1}{ext}"
                    dst_path = os.path.join(temp_dir, new_filename)
                    
                    # Geçici klasörde yeniden adlandır
                    if os.path.exists(src_path):
                        try:
                            shutil.copy2(src_path, dst_path)
                            image_files.append(dst_path)
                        except Exception as e:
                            print(f"Dosya kopyalama hatası: {e}")
        except Exception as e:
            print(f"ZIP açma hatası: {e}")
            
            # ZIP açılamazsa eski yöntemi dene
            try:
                for rel in document.part.rels.values():
                    if "image" in rel.target_ref:
                        try:
                            resim_sayaci = len(image_files) + 1
                            image_blob = rel.target_part.blob
                            image_filename = f"soru{ana_soru_no}_resim{resim_sayaci}.png"
                            image_path = os.path.join(temp_dir, image_filename)
                            
                            with open(image_path, "wb") as img_file:
                                img_file.write(image_blob)
                            
                            image_files.append(image_path)
                        except Exception as e:
                            print(f"⚠️ Resim kaydedilirken hata: {str(e)}")
            except Exception as e:
                print(f"⚠️ Yedek resim çıkarma yöntemi hatası: {str(e)}")
                print(f"Toplam {len(image_files)} resim dosyası çıkarıldı ve kaydedildi.")
        
        # Şimdi soruları ve resimleri eşleştirelim
        sorular = []
        current_soru = {}
        
        i = 0
        while i < len(paragraflar):
            # Soru numarası kontrolü - 1., 2. gibi başlayan paragrafları tespit et
            if re.match(r'^\d+\.', paragraflar[i].strip()):
                # Yeni soru başlangıcı
                if current_soru and 'soru_metni' in current_soru and 'secenekler' in current_soru and len(current_soru['secenekler']) == 4:
                    sorular.append(current_soru)
                
                # Mevcut paragraf pozisyonu
                current_position = i
                
                # Bu pozisyona en yakın olan resimleri bul
                current_soru = {
                    'soru_metni': '',
                    'soru_cumlesi': '',
                    'secenekler': [],
                    'soru_no': ana_soru_no,
                    'dogru_cevap': '',  # Doğru cevap bilgisi için yeni alan
                    'resimler': []  # Resimler için yeni alan
                }
                
                # Soru numarasını kaldır
                metin = re.sub(r'^\d+\.', '', paragraflar[i].strip())
                current_soru['soru_metni'] = metin.strip()
                
                # Sonraki paragraflara bak
                j = i + 1
                
                # Seçeneklere kadar ilerle
                while j < len(paragraflar) and not re.match(r'^[A-D]\)', paragraflar[j].strip()):
                    # Boş olmayan paragrafları soru metnine ekle
                    if paragraflar[j].strip():
                        current_soru['soru_metni'] += ' ' + paragraflar[j].strip()
                    # Eğer boş satır varsa, soru cümlesi olabilir
                    elif j+1 < len(paragraflar) and paragraflar[j+1].strip() and not re.match(r'^[A-D]\)', paragraflar[j+1].strip()):
                        # Boş satırdan sonraki metni soru cümlesi olarak al
                        current_soru['soru_cumlesi'] = paragraflar[j+1].strip()
                        # Soru cümlesini atla
                        j += 1
                    j += 1
                
                # Şıkları topla
                while j < len(paragraflar) and len(current_soru['secenekler']) < 4:
                    if re.match(r'^[A-D]\)', paragraflar[j].strip()):
                        current_soru['secenekler'].append(paragraflar[j].strip())
                    j += 1
                
                # Soru cümlesi henüz bulunmadıysa, soru metninin son cümlesini kontrol et
                if not current_soru['soru_cumlesi']:
                    cumle_deseni = re.compile(r'([^.!?]+[.!?]+)\s*$')
                    match = cumle_deseni.search(current_soru['soru_metni'])
                    if match:
                        current_soru['soru_cumlesi'] = match.group(1).strip()
                        # Soru metninden soru cümlesini çıkar
                        current_soru['soru_metni'] = current_soru['soru_metni'].replace(current_soru['soru_cumlesi'], '').strip()
                
                # Rastgele bir doğru cevap belirle (test amaçlı, gerçek uygulamada kaldırılabilir)
                current_soru['dogru_cevap'] = random.choice(["A", "B", "C", "D"])
                
                i = j
            else:
                i += 1
        
        # Son soruyu ekle
        if current_soru and 'soru_metni' in current_soru and 'secenekler' in current_soru and len(current_soru['secenekler']) == 4:
            sorular.append(current_soru)
        
        # YENİ: Resimleri sorulara daha akıllı bir şekilde dağıt
        if len(sorular) > 0 and len(image_files) > 0:
            # Resim sayısı ve soru sayısı arasındaki ilişkiyi belirle
            resim_soru_orani = len(image_files) / len(sorular)
            
            if resim_soru_orani >= 1:
                # Her soruya en az bir resim düşebilir
                resim_per_soru = len(image_files) // len(sorular)
                kalan_resim = len(image_files) % len(sorular)
                
                baslangic_indeks = 0
                for i, soru in enumerate(sorular):
                    # Bu sorunun alacağı resim sayısı
                    bu_soru_resim_sayisi = resim_per_soru
                    if i < kalan_resim:
                        bu_soru_resim_sayisi += 1
                    
                    # Resimleri ekle
                    soru['resimler'] = image_files[baslangic_indeks:baslangic_indeks + bu_soru_resim_sayisi]
                    baslangic_indeks += bu_soru_resim_sayisi
            else:
                # Resim sayısı az, her resim bir soruya gidecek
                for i, img_path in enumerate(image_files):
                    if i < len(sorular):
                        sorular[i]['resimler'] = [img_path]
        
        print(f"✅ {dosya_adi} dosyasından {len(sorular)} paralel soru ve {len(image_files)} resim çıkarıldı. (Yıl: {yil}, Soru No: {ana_soru_no}, Ders: {ders_adi})")
        
        return {
            "sorular": sorular, 
            "yil": yil, 
            "ana_soru_no": ana_soru_no, 
            "ders_adi": ders_adi
        }
    
    except Exception as e:
        print(f"⚠️ {dosya_adi} dosyası işlenirken hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"sorular": [], "yil": "0000", "ana_soru_no": 0, "ders_adi": "Bilinmeyen"}
# question_extractor.py içine ekleyin

import json

def json_sorulari_ayikla(json_dosya_adi):
    """JSON dosyasından soruları çıkarır - Hem dizi hem de tekil nesne formatını destekler"""
    try:
        # JSON dosyasını oku
        with open(json_dosya_adi, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # JSON formatını kontrol et: Dizi mi yoksa tekil nesne mi?
        if isinstance(json_data, list):
            # Dizi formatı (birden fazla soru)
            sorular_json = json_data
        else:
            # Tekil nesne formatı (tek soru)
            sorular_json = [json_data]
        
        # Dönüştürülmüş soruları tutacak liste
        sorular = []
        
        # Ders adını dosya adından tahmin etmeye çalış
        dosya_adi = os.path.basename(json_dosya_adi)
        ders_adi = "Bilinmeyen"
        
        # Dosya adında ders bilgisi olabilir
        dersler = ["Matematik", "Türkçe", "Fen", "İngilizce", "İnkılap", "Din"]
        for ders in dersler:
            if ders.lower() in dosya_adi.lower():
                ders_adi = ders
                break
        
        # JSON'dan bilgileri çıkar
        for i, soru_json in enumerate(sorular_json):
            # Eğer nesne içinde ders bilgisi varsa, onu kullan
            if "ders" in soru_json:
                ders_adi = soru_json.get("ders")
            
            # Soru metni ve şıklar
            soru_metni = soru_json.get("soruMetni", "")
            if not soru_metni and "soru" in soru_json:
                # Alternatif alan adı
                soru_metni = soru_json.get("soru", "")
            
            # Görsel varsa bunu işle
            gorsel_path = soru_json.get("gorsel", "")
            resimler = []
            if gorsel_path and os.path.exists(gorsel_path):
                resimler.append(gorsel_path)
            
            # Şıkları ayarla
            secenekler = soru_json.get("secenekler", {})
            secenekler_liste = []
            
            # Eğer secenekler farklı bir formatta ise
            if not secenekler and "siklar" in soru_json:
                secenekler = soru_json.get("siklar", {})
            
            # Şıklar bir sözlük mü yoksa liste mi kontrol et
            if isinstance(secenekler, dict):
                for harf in ["A", "B", "C", "D"]:
                    if harf in secenekler:
                        secenekler_liste.append(f"{harf}) {secenekler[harf]}")
            elif isinstance(secenekler, list):
                # Liste formatındaki şıklar için
                for j, secenek in enumerate(secenekler[:4]):  # En fazla 4 şık
                    harf = chr(65 + j)  # A, B, C, D
                    secenekler_liste.append(f"{harf}) {secenek}")
            
            # Doğru cevabı al
            dogru_cevap = soru_json.get("dogruCevap", "")
            if not dogru_cevap and "dogruCevap" in soru_json:
                # Alternatif alan adı
                dogru_cevap = soru_json.get("cevap", "A")
            
            # Soruyu uygun formatta hazırla
            soru = {
                'soru_metni': soru_metni,
                'soru_cumlesi': "",  # JSON'da ayrı soru cümlesi yok, gerekirse ayırılabilir
                'secenekler': secenekler_liste,
                'soru_no': i + 1,  # Sıralı numara ver
                'dogru_cevap': dogru_cevap,
                'resimler': resimler
            }
            
            # Şıklar tamam ise soruyu ekle
            if len(secenekler_liste) == 4:
                sorular.append(soru)
        
        # Yıl bilgisi için JSON dosyasının adından veya mevcut tarihten al
        yil_match = re.search(r'(\d{4})', os.path.basename(json_dosya_adi))
        if yil_match:
            yil = yil_match.group(1)
        else:
            from datetime import datetime
            yil = str(datetime.now().year)
        
        print(f"✅ {json_dosya_adi} dosyasından {len(sorular)} soru çıkarıldı. (Ders: {ders_adi})")
        
        return {
            "sorular": sorular, 
            "yil": yil, 
            "ana_soru_no": 1,  # JSON'da belirtilmiyorsa varsayılan değer 
            "ders_adi": ders_adi
        }
    
    except Exception as e:
        print(f"⚠️ {json_dosya_adi} dosyası işlenirken hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"sorular": [], "yil": "0000", "ana_soru_no": 0, "ders_adi": "Bilinmeyen"}