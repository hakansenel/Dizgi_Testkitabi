# utils/pdf_utils.py
# PDF oluşturma ve formatlama işlemleri

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit, ImageReader
from config import DERS_RENKLERI

def kapak_sayfasi_olustur(c, ders_adi, yil, test_no):
    """Test için kapak sayfası oluşturur"""
    width, height = A4
    
    # Font ayarları - daha güvenli
    font_name = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    
    try:
        # Arial fontlarını yüklemeyi dene
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'Arialbd.ttf'))
        font_name = 'Arial'
        bold_font = 'Arial-Bold'
    except Exception as e:
        # Yükleme başarısız olursa varsayılan Helvetica kullan
        print(f"Font yükleme hatası: {e}")
        print("Varsayılan Helvetica fontları kullanılıyor.")
    
    # Ders rengini belirle - örneğe uygun renkleri ayarlayalım
    if ders_adi == "İnkılap":
        r, g, b = (0.9, 0.55, 0.05)  # Turuncu
    elif ders_adi == "Türkçe":
        r, g, b = (0.9, 0, 0)  # Kırmızı
    elif ders_adi == "Matematik":
        r, g, b = (0, 0.5, 0.9)  # Mavi
    else:
        r, g, b = DERS_RENKLERI.get(ders_adi, (0.4, 0.4, 0.4))
    
    # Üst kısım - renkli banner
    c.setFillColorRGB(r, g, b)
    c.rect(0, height - 120, width, 120, fill=1, stroke=0)
    
    # Logo ve başlık (beyaz renkte)
    c.setFillColorRGB(1, 1, 1)
    c.setFont(bold_font, 36)
    c.drawString(75, height - 65, f"LGS SORU BANKASI")
    
    # Alt başlık
    c.setFont(font_name, 24)
    c.drawString(75, height - 100, f"{ders_adi.upper()} - {yil}")
    
    # Sayfa boşluğu
    c.setFillColorRGB(1, 1, 1)
    
    # Orta kısım - Test başlığı
    c.setFillColorRGB(0, 0, 0)
    c.setFont(bold_font, 72)
    c.drawCentredString(width/2, height/2, f"TEST {test_no}")
    
    # Ders adı
    c.setFillColorRGB(r, g, b)
    c.setFont(bold_font, 48)
    c.drawCentredString(width/2, height/2 - 80, f"{ders_adi}")
    
    # Alt kısım - yayın bilgileri
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont(font_name, 12)
    c.drawCentredString(width/2, 50, "SOLOROTA YAYINLARI")
    c.drawCentredString(width/2, 30, f"© {datetime.now().year} Tüm Hakları Saklıdır")
    
    # Sayfa dışı kenarlık
    c.setStrokeColorRGB(r, g, b)
    c.setLineWidth(1.5)
    c.rect(22, 22, width-44, height-44, fill=0, stroke=1)
    
    # Kapak sayfasını tamamla
    c.showPage()

def cevap_anahtari_olustur(cevap_anahtari, pdf_yolu, test_no, ders_adi, yil):
    """Ayrı bir cevap anahtarı PDF'i oluşturur"""
    c = canvas.Canvas(pdf_yolu, pagesize=A4)
    
    # Font ayarları
    font_name = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'Arialbd.ttf'))
        font_name = 'Arial'
        bold_font = 'Arial-Bold'
    except Exception as e:
        print(f"Font yükleme hatası: {e}")
        print("Varsayılan Helvetica fontları kullanılıyor.")
    
    width, height = A4
    
    # Ders rengini belirle
    if ders_adi == "İnkılap":
        r, g, b = (0.9, 0.55, 0.05)  # Turuncu
    elif ders_adi == "Türkçe":
        r, g, b = (0.9, 0, 0)  # Kırmızı
    elif ders_adi == "Matematik":
        r, g, b = (0, 0.5, 0.9)  # Mavi
    else:
        r, g, b = DERS_RENKLERI.get(ders_adi, (0.4, 0.4, 0.4))
    
    # SOLOROTA filigranı ekle
    def ciz_filigran(canvas):
        canvas.saveState()
        canvas.setFont(bold_font, 80)
        canvas.setFillColorRGB(0.96, 0.96, 0.96)  # Çok açık gri
        canvas.translate(width/2, height/2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "SOLOROTA")
        canvas.restoreState()
    
    ciz_filigran(c)
    
    # Başlık
    c.setFont(bold_font, 18)
    c.setFillColorRGB(r, g, b)
    c.drawCentredString(width/2, height - 50, f"TEST {test_no} - {ders_adi} - CEVAP ANAHTARI")
    
    # Alt çizgi
    c.setLineWidth(1)
    c.line(100, height - 65, width - 100, height - 65)
    
    # Cevap anahtarı tablosu
    c.setFont(bold_font, 12)
    c.setFillColorRGB(0, 0, 0)
    
    # Her satırda 5 cevap
    cevap_sayisi = len(cevap_anahtari)
    satir_sayisi = (cevap_sayisi + 4) // 5  # 5 cevap per satır, yukarı yuvarla
    
    # Tablo başlangıç pozisyonu
    table_top = height - 100
    row_height = 40
    col_width = (width - 100) / 5
    
    for row in range(satir_sayisi):
        y_pos = table_top - row * row_height
        
        for col in range(5):
            indeks = row * 5 + col
            
            if indeks < cevap_sayisi:
                soru_no, cevap = cevap_anahtari[indeks]
                
                # Sütun x pozisyonu
                x_pos = 50 + col * col_width
                
                # Soru numarası
                c.setFont(bold_font, 14)
                c.drawCentredString(x_pos + col_width/2, y_pos, str(soru_no))
                
                # Cevap dairesi
                c.setFillColorRGB(r, g, b)
                c.circle(x_pos + col_width/2, y_pos - 20, 14, fill=1)
                
                # Cevap harfi (beyaz)
                c.setFillColorRGB(1, 1, 1)
                c.setFont(bold_font, 12)
                c.drawCentredString(x_pos + col_width/2, y_pos - 24, cevap)
    
    # Alt bilgi
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont(font_name, 8)
    c.drawCentredString(width/2, 30, f"SOLOROTA YAYINLARI - {yil}")
    
    # PDF'i kaydet
    c.save()
    print(f"✓ Cevap anahtarı PDF oluşturuldu: {pdf_yolu}")

def pdf_olustur_test(test_sorulari, pdf_yolu, test_no, ders_adi, yil):
    """LGS formatında test PDF'i oluşturur - Yukarıdan aşağı sıralı ve görsel destekli"""
    try:
        from reportlab.lib.utils import ImageReader  # PDF'de resim kullanmak için
    except ImportError:
        print("Uyarı: ImageReader import edilemedi, resimler gösterilmeyebilir.")
    
    c = canvas.Canvas(pdf_yolu, pagesize=A4)
    
    # Font ayarları
    font_name = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    
    try:
        # Arial fontlarını yüklemeyi dene
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'Arialbd.ttf'))
        font_name = 'Arial'
        bold_font = 'Arial-Bold'
    except Exception as e:
        print(f"Font yükleme hatası: {e}")
        print("Varsayılan Helvetica fontları kullanılıyor.")
    
    width, height = A4
    margin_x, margin_y = 40, 40
    column_width = (width - 2*margin_x - 10) / 2  # İki sütun için genişlik
    line_height = 12  # Satır yüksekliği
    
    # Ders rengini belirle
    if ders_adi == "İnkılap":
        r, g, b = (0.9, 0.55, 0.05)  # Turuncu
    elif ders_adi == "Türkçe":
        r, g, b = (0.9, 0, 0)  # Kırmızı
    elif ders_adi == "Matematik":
        r, g, b = (0, 0.5, 0.9)  # Mavi
    else:
        r, g, b = DERS_RENKLERI.get(ders_adi, (0.4, 0.4, 0.4))
    
    # Kapak sayfası oluştur
    kapak_sayfasi_olustur(c, ders_adi, yil, test_no)
    
    # Soruları sıralı dizin içinde yeniden düzenle
    sirali_sorular = {}
    for soru in test_sorulari:
        sirali_sorular[soru["soru_no"]] = soru
    
    # Soru numaralarını sırala
    soru_keys = sorted(sirali_sorular.keys())
    
    # Cevap anahtarını hazırla
    cevap_anahtari = []
    
    # Sayfa sayacı
    sayfa_no = 1
    
    # Her sayfada kaç soru olacak (sol+sağ sütun toplamı)
    sorular_per_sayfa = 4  # Sayfa başına 4 soru
    
    # Kaç sayfa gerekecek hesapla
    toplam_sayfa = (len(soru_keys) + sorular_per_sayfa - 1) // sorular_per_sayfa
    
    # Soru indeksi
    soru_index = 0
    
    # Her sayfa için
    for sayfa in range(toplam_sayfa):
        # SOLOROTA filigranı ekle (her sayfaya)
        def ciz_filigran(canvas):
            canvas.saveState()
            canvas.setFont(bold_font, 80)
            canvas.setFillColorRGB(0.96, 0.96, 0.96)  # Çok açık gri
            canvas.translate(width/2, height/2)
            canvas.rotate(45)
            canvas.drawCentredString(0, 0, "SOLOROTA")
            canvas.restoreState()
        
        ciz_filigran(c)
        
        # Sayfa başlığı
        c.setFont(bold_font, 12)
        c.setFillColorRGB(r, g, b)
        c.drawString(margin_x, height - 20, f"TEST {test_no} - {ders_adi} - {yil}")
        
        # SOLOROTA ve ders adı başlıkları
        c.setFont(font_name, 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(width/4, height - 40, "SOLOROTA") 
        c.drawCentredString(width*3/4, height - 40, f"{ders_adi.upper()}")
        
        # Sayfanın üst kısmına ince bir çizgi çek
        c.setStrokeColorRGB(r, g, b)
        c.setLineWidth(0.5)
        c.line(margin_x, height - 45, width - margin_x, height - 45)
        
        # Ortaya dikey çizgi çiz
        c.setStrokeColorRGB(0.7, 0.7, 0.7)  # Açık gri
        c.setLineWidth(0.5)
        c.line(width/2, margin_y, width/2, height - margin_y)
        
        # Sol ve sağ sütunların başlangıç Y pozisyonları
        y_pos = height - margin_y - 60  # Başlık için ek alan
        
        # Sütunlar için x pozisyonları
        col_positions = [margin_x, margin_x + column_width + 10]
        
        # Bu sayfada kaç soru gösterileceğini hesapla
        sayfa_soru_sayisi = min(sorular_per_sayfa, len(soru_keys) - soru_index)
        
        # Sol sütunda gösterilecek soru sayısı (yukarıdan aşağı sıralama için)
        sol_sutun_soru_sayisi = (sayfa_soru_sayisi + 1) // 2  # Üst yuvarlama
        
        # Her sütun için
        for col in range(2):  # 0: sol sütun, 1: sağ sütun
            # Bu sütunda gösterilecek sorular
            if col == 0:  # Sol sütun
                baslangic = soru_index
                bitis = min(soru_index + sol_sutun_soru_sayisi, len(soru_keys))
            else:  # Sağ sütun
                baslangic = soru_index + sol_sutun_soru_sayisi
                bitis = min(soru_index + sayfa_soru_sayisi, len(soru_keys))
            
            # Bu sütundaki her soru için
            y = y_pos
            for i in range(baslangic, bitis):
                if i >= len(soru_keys):
                    break
                    
                soru_no = soru_keys[i]
                soru = sirali_sorular[soru_no]
                
                # Mevcut X pozisyonu
                x = col_positions[col]
                current_column_width = column_width
                
                # Soru metni, cümlesi ve seçenekleri al
                soru_metni = soru.get('soru_metni', '')
                soru_cumlesi = soru.get('soru_cumlesi', '')
                secenekler = soru.get('secenekler', [])
                dogru_cevap = soru.get('dogru_cevap', '')
                resimler = soru.get('resimler', [])
                
                # Cevap anahtarına ekle
                cevap_anahtari.append((soru_no, dogru_cevap))
                
                # Soru numarasını yaz
                c.setFont(bold_font, 10)
                c.setFillColorRGB(0, 0, 0)
                
                # Güzel bir soru numaralandırma
                c.drawString(x, y, f"{soru_no}.")
                soru_no_width = c.stringWidth(f"{soru_no}.", bold_font, 10)
                
                # Soru metnini yazdır
                c.setFont(font_name, 9)
                
                # Metin genişliğini hesapla
                metin_width = current_column_width - soru_no_width - 5
                
                # Soru metnini satırlara böl
                if soru_metni:
                    wrapped_text = simpleSplit(soru_metni, font_name, 9, metin_width)
                    
                    # İlk satırı soru numarasının yanına yaz
                    if wrapped_text:
                        c.drawString(x + soru_no_width + 3, y, wrapped_text[0])
                        y -= line_height
                        
                        # Kalan satırları yaz
                        for line in wrapped_text[1:]:
                            c.drawString(x, y, line)
                            y -= line_height
                
                # Görsel varsa ekleyelim (sırayı bozmadan)
                if resimler and len(resimler) > 0:
                    for resim_yolu in resimler:
                        try:
                            if os.path.exists(resim_yolu):
                                # Resmi yükle ve boyutlarını al
                                img = ImageReader(resim_yolu)
                                img_width, img_height = img.getSize()
                                
                                # Resmi sütuna sığdır
                                max_img_width = current_column_width * 0.9  # Sütunun %90'ı
                                scale = min(1.0, max_img_width / img_width)
                                
                                # Yükseklik kontrolü
                                if scale * img_height > 150:  # Maksimum 150 piksel yükseklik
                                    scale = min(scale, 150 / img_height)
                                
                                # Ölçeklendirilmiş boyutlar
                                scaled_width = img_width * scale
                                scaled_height = img_height * scale
                                
                                # Resmin konumu - sütuna ortalı
                                resim_x = x + (current_column_width - scaled_width) / 2
                                
                                # Resmi çiz
                                c.drawImage(img, resim_x, y - scaled_height, width=scaled_width, height=scaled_height)
                                
                                # Y pozisyonunu güncelle
                                y -= (scaled_height + 10)
                                
                                # Görselin varlığını belirt
                                c.setFont(font_name, 8)
                                c.setFillColorRGB(0.5, 0.5, 0.5)
                                c.drawString(x, y, "[Görsel: {}]".format(os.path.basename(resim_yolu)))
                                y -= line_height
                            else:
                                print(f"⚠️ Resim dosyası bulunamadı: {resim_yolu}")
                        except Exception as e:
                            print(f"⚠️ Resim eklenirken hata: {str(e)}")
                
                # Soru cümlesi varsa kalın yaz
                if soru_cumlesi:
                    c.setFont(bold_font, 9)
                    wrapped_text = simpleSplit(soru_cumlesi, bold_font, 9, current_column_width)
                    for line in wrapped_text:
                        c.drawString(x, y, line)
                        y -= line_height
                
                # Şıkları yaz
                for j, secenek in enumerate(secenekler):
                    # Şık bilgilerini güvenli bir şekilde al
                    if not secenek:
                        continue
                    
                    # A) kısmını çıkar
                    sik_harfi = secenek[:1] if secenek else ""
                    sik_metni = secenek[2:].strip() if len(secenek) > 2 else ""
                    
                    # Şık harfini kalın yaz
                    c.setFont(bold_font, 9)
                    c.drawString(x, y, f"{sik_harfi})")
                    sik_harfi_width = c.stringWidth(f"{sik_harfi})", bold_font, 9)
                    
                    # Şık metnini yaz
                    if sik_metni:
                        c.setFont(font_name, 9)
                        
                        # Şık metnini satırlara böl
                        wrapped_sik = simpleSplit(sik_metni, font_name, 9, current_column_width - sik_harfi_width - 5)
                        
                        # İlk satırı şık harfinin yanına yaz
                        if wrapped_sik:
                            c.drawString(x + sik_harfi_width + 3, y, wrapped_sik[0])
                            y -= line_height
                            
                            # Kalan satırları yaz
                            for line in wrapped_sik[1:]:
                                c.drawString(x + sik_harfi_width + 3, y, line)
                                y -= line_height
                    else:
                        y -= line_height
                
                # Soru sonu boşluğu - daha fazla boşluk bırak
                y -= 20  # Artırılmış boşluk (önceki 8'den 20'ye)
        
        # Soru indeksini güncelle
        soru_index += sayfa_soru_sayisi
        
        # Sayfa numarası
        c.setFont(font_name, 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawCentredString(width / 2, 20, str(sayfa_no))
        
        # Sayfayı tamamla
        c.showPage()
        sayfa_no += 1
    
    # PDF'i kaydet
    c.save()
    print(f"✓ Test PDF oluşturuldu: {pdf_yolu}")
    
    # Cevap anahtarını ayrı bir PDF olarak oluştur
    cevap_anahtari_olustur(cevap_anahtari, os.path.splitext(pdf_yolu)[0] + "_cevap_anahtari.pdf", test_no, ders_adi, yil)

def olustur_derleme_kilavuzu(cikti_klasor, ders_yil_grupları):
    """Tüm testlerin bir listesini içeren derleme kılavuzu PDF'i oluşturur"""
    pdf_yolu = os.path.join(cikti_klasor, "Derleme_Kilavuzu.pdf")
    c = canvas.Canvas(pdf_yolu, pagesize=A4)
    
    # Font ayarları - daha güvenli bir yöntem
    font_name = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    
    # Arial veya Verdana fontlarını kaydetmeyi dene, ama hata olursa Helvetica kullan
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'Arialbd.ttf'))
        font_name = 'Arial'
        bold_font = 'Arial-Bold'
    except:
        # Eğer Arial yüklenemezse, varsayılan olarak Helvetica kullan
        print("Arial fontu yüklenemedi, varsayılan Helvetica kullanılıyor.")
    
    width, height = A4
    
    # SOLOROTA filigranı ekle
    def ciz_filigran(canvas):
        canvas.saveState()
        canvas.setFont(bold_font, 80)
        canvas.setFillColorRGB(0.96, 0.96, 0.96)  # Çok açık gri
        canvas.translate(width/2, height/2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "SOLOROTA")
        canvas.restoreState()
    
    ciz_filigran(c)
    
    # Başlık
    c.setFont(bold_font, 18)  # Font kullanımı
    c.drawCentredString(width/2, height - 50, "LGS SORU BANKASI DERLEME KILAVUZU")
    
    # Alt çizgi
    c.setLineWidth(1)
    c.line(100, height - 65, width - 100, height - 65)
    
    # Açıklama
    c.setFont(font_name, 12)  # Font kullanımı
    c.drawCentredString(width/2, height - 85, "Bu kılavuz, oluşturulan tüm testlerin listesini içerir.")
    
    # İçerik tablosu
    y = height - 120
    c.setFont(bold_font, 14)  # Font kullanımı
    c.drawString(50, y, "İÇİNDEKİLER")
    y -= 25
    
    # Her ders ve yıl için test listesi
    for ders_adi, yil_gruplari in ders_yil_grupları.items():
        c.setFont(bold_font, 12)  # Font kullanımı
        
        # Ders rengini belirle
        if ders_adi == "İnkılap":
            r, g, b = (0.9, 0.55, 0.05)  # Turuncu
        elif ders_adi == "Türkçe":
            r, g, b = (0.9, 0, 0)  # Kırmızı
        elif ders_adi == "Matematik":
            r, g, b = (0, 0.5, 0.9)  # Mavi
        else:
            r, g, b = DERS_RENKLERI.get(ders_adi, (0.4, 0.4, 0.4))
            
        c.setFillColorRGB(r, g, b)
        c.drawString(50, y, f"{ders_adi}")
        y -= 20
        
        for yil, soru_gruplari in yil_gruplari.items():
            # Test sayısını hesapla
            test_sayisi = min(len(soru_gruplari), 5)  # Varsayılan olarak maksimum 5 test
            
            c.setFont(font_name, 10)  # Font kullanımı
            c.setFillColorRGB(0, 0, 0)
            c.drawString(70, y, f"{test_sayisi} Test")
            
            # Test dosya adlarını liste olarak ekle
            for i in range(test_sayisi):
                y -= 15
                test_no = i + 1
                dosya_adi = f"{ders_adi}_Test_{test_no}.pdf"
                cevap_adi = f"{ders_adi}_Test_{test_no}_cevap_anahtari.pdf"
                
                c.drawString(90, y, f"Test {test_no}: {dosya_adi}")
                y -= 15
                c.drawString(90, y, f"Cevap Anahtarı: {cevap_adi}")
            
            y -= 25
            y -= 10
        
        # Yeni sayfa kontrolü
        if y < 100:
            c.showPage()
            # Yeni sayfada da filigran ekle
            ciz_filigran(c)
            y = height - 50
    
    # Tarih ve yayın bilgisi
    c.setFont(font_name, 8)  # Font kullanımı
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width/2, 30, f"SOLOROTA YAYINLARI - Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y')}")
    
    c.save()
    print(f"✓ Derleme kılavuzu oluşturuldu: {pdf_yolu}")