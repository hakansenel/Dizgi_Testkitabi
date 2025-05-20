import os
from modules.test_generator import islemi_gerceklestir
# Eski hatalı import:
# from modules.json_to_word_converter import process_all_files, process_single_file

# Yeni doğru import:
from modules.json_to_word_converter import process_all_files, process_json_file, json_to_word_profesyonel, process_single_file



def main():
    print("===== LGS Test Kitabı Oluşturma Programı =====")
    print("Bu program paralel soruları farklı testlere dağıtır ve profesyonel LGS formatında PDF'ler oluşturur.")
    
    girdi_klasor = input("Soru belgelerinin bulunduğu klasör yolu: ")
    cikti_klasor = input("PDF'lerin kaydedileceği klasör yolu: ")
    
    test_sayisi_input = input("Oluşturulacak test sayısı (varsayılan: 5): ")
    test_sayisi = 5  # Varsayılan değer
    
    if test_sayisi_input.strip():
        try:
            test_sayisi = int(test_sayisi_input)
        except ValueError:
            print("⚠️ Geçersiz sayı, varsayılan değer kullanılacak (5)")
    
    # İşlemi başlat
    islemi_gerceklestir(girdi_klasor, cikti_klasor, test_sayisi)

def convert_json_to_word():
    """JSON dosyalarını Word formatına dönüştürür"""
    print("===== JSON Dosyalarını Word Formatına Dönüştürme Programı =====")
    
    # Kullanıcı seçimine göre işlem yapma
    secim = input("Tüm JSON dosyalarını işlemek için 'T', belirli bir dosyayı işlemek için dosya adını girin: ")
    
    if secim.upper() == 'T':
        # Tüm dosyaları işle
        process_all_files()
    else:
        # Belirli bir dosyayı işlemek
        from config import JSON_INPUT_DIR
        json_file = os.path.join(JSON_INPUT_DIR, secim)
        if os.path.exists(json_file):
            process_single_file(json_file)
        else:
            print(f"Hata: {json_file} dosyası bulunamadı!")

if __name__ == "__main__":
    print("===== LGS Soru Yönetim Programı =====")
    print("1. Test Kitabı Oluştur")
    print("2. JSON Dosyalarını Word'e Dönüştür")
    print("-" * 40)
    
    secim = input("Yapmak istediğiniz işlemi seçin (1-2): ")
    
    if secim == "1":
        main()
    elif secim == "2":
        convert_json_to_word()
    else:
        print("Geçersiz seçim! Program sonlandırılıyor.")