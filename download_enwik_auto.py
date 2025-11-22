#!/usr/bin/env python3
"""
Automatyczne pobieranie fragmentu enwik8 (10 MB) do testów
"""
import urllib.request
import os
import zipfile

def download_with_progress(url, output_path):
    """Pobiera plik z progress bar"""
    print(f"Pobieranie: {url}")
    
    def progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = (downloaded / total_size) * 100
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\rPostęp: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='')
    
    urllib.request.urlretrieve(url, output_path, reporthook=progress)
    print("\n✓ Pobrano!")

def main():
    print("=" * 60)
    print("AUTO DOWNLOAD - Fragment 10 MB z enwik8")
    print("=" * 60)
    
    data_dir = "data"
    url = "http://mattmahoney.net/dc/enwik8.zip"
    zip_path = os.path.join(data_dir, "enwik8.zip")
    enwik8_path = os.path.join(data_dir, "enwik8")
    fragment_path = os.path.join(data_dir, "enwik_10mb")
    
    # Sprawdź czy już istnieje
    if os.path.exists(fragment_path):
        size = os.path.getsize(fragment_path)
        print(f"\n✓ Fragment już istnieje: {fragment_path}")
        print(f"  Rozmiar: {size:,} bajtów ({size / (1024 * 1024):.1f} MB)")
        return
    
    # Pobierz enwik8.zip jeśli nie ma
    if not os.path.exists(enwik8_path):
        if not os.path.exists(zip_path):
            print("\n[1/3] Pobieranie enwik8.zip (ok. 36 MB)...")
            download_with_progress(url, zip_path)
        
        print("\n[2/3] Rozpakowywanie...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        print(f"✓ Rozpakowano: {enwik8_path}")
    else:
        print(f"\n✓ enwik8 już istnieje: {enwik8_path}")
    
    # Wytnij 10 MB
    print("\n[3/3] Wycinanie pierwszych 10 MB...")
    with open(enwik8_path, 'rb') as f_in:
        with open(fragment_path, 'wb') as f_out:
            chunk = f_in.read(10 * 1024 * 1024)
            f_out.write(chunk)
    
    size = os.path.getsize(fragment_path)
    print(f"✓ Utworzono: {fragment_path}")
    print(f"  Rozmiar: {size:,} bajtów ({size / (1024 * 1024):.1f} MB)")
    
    print("\n" + "=" * 60)
    print("✓ Gotowe! Możesz teraz testować na prawdziwych danych Wiki.")
    print("=" * 60)

if __name__ == "__main__":
    main()
