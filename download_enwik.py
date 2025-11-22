#!/usr/bin/env python3
"""
Pobiera enwik8 (100 MB) lub enwik9 (1 GB) do testowania
"""
import urllib.request
import os

def download_file(url, output_path):
    """Pobiera plik z URL"""
    print(f"Pobieranie: {url}")
    print(f"Do: {output_path}")
    print("To może potrwać kilka minut...")
    
    def progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = (downloaded / total_size) * 100 if total_size > 0 else 0
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        print(f"\rPostęp: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='')
    
    urllib.request.urlretrieve(url, output_path, reporthook=progress)
    print("\n✓ Pobrano!")
    
    # Weryfikacja rozmiaru
    size = os.path.getsize(output_path)
    print(f"Rozmiar: {size:,} bajtów ({size / (1024 * 1024):.1f} MB)")

def main():
    data_dir = "data"
    
    # Opcje do wyboru
    print("=" * 60)
    print("POBIERANIE ENWIK")
    print("=" * 60)
    print("\nWybierz plik do pobrania:")
    print("1. enwik8 (100 MB) - szybsze do testów")
    print("2. enwik9 (1 GB) - pełny konkurs")
    print("3. Tylko mały fragment (10 MB z enwik8)")
    
    choice = input("\nWybór (1/2/3): ").strip()
    
    if choice == "1":
        url = "http://mattmahoney.net/dc/enwik8.zip"
        zip_path = os.path.join(data_dir, "enwik8.zip")
        extract_name = "enwik8"
        
        download_file(url, zip_path)
        
        print("\nRozpakowywanie...")
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        
        print(f"✓ Rozpakowano: {os.path.join(data_dir, extract_name)}")
        
    elif choice == "2":
        url = "http://mattmahoney.net/dc/enwik9.zip"
        zip_path = os.path.join(data_dir, "enwik9.zip")
        extract_name = "enwik9"
        
        print("\n⚠ UWAGA: To jest 1 GB - pobieranie może potrwać 10-30 minut!")
        confirm = input("Kontynuować? (tak/nie): ").strip().lower()
        
        if confirm in ['tak', 't', 'yes', 'y']:
            download_file(url, zip_path)
            
            print("\nRozpakowywanie...")
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(data_dir)
            
            print(f"✓ Rozpakowano: {os.path.join(data_dir, extract_name)}")
        else:
            print("Anulowano")
            
    elif choice == "3":
        # Pobierz enwik8 i wytnij fragment
        url = "http://mattmahoney.net/dc/enwik8.zip"
        zip_path = os.path.join(data_dir, "enwik8.zip")
        
        download_file(url, zip_path)
        
        print("\nRozpakowywanie...")
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        
        # Wytnij 10 MB
        enwik8_path = os.path.join(data_dir, "enwik8")
        fragment_path = os.path.join(data_dir, "enwik_10mb")
        
        print("\nWycinanie pierwszych 10 MB...")
        with open(enwik8_path, 'rb') as f_in:
            with open(fragment_path, 'wb') as f_out:
                chunk = f_in.read(10 * 1024 * 1024)
                f_out.write(chunk)
        
        print(f"✓ Utworzono: {fragment_path}")
        
    else:
        print("Nieprawidłowy wybór")
    
    print("\n" + "=" * 60)
    print("Gotowe! Teraz możesz przetestować kompresor na prawdziwych danych.")
    print("=" * 60)

if __name__ == "__main__":
    main()
