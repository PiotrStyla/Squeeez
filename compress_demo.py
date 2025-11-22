#!/usr/bin/env python3
"""
Pierwszy mini-kompresor - demo pipeline'u kompresji
Używa zlib tylko do pokazania flow: compress -> archive -> decompress -> verify
"""
import zlib
import os

def main():
    input_file = "data/sample.txt"
    compressed_file = "data/sample.zlib"
    decompressed_file = "data/sample_restored.txt"
    
    print("=" * 60)
    print("HUTTER LAB - Kompresja Demo")
    print("=" * 60)
    
    # 1. Czytanie oryginalnego pliku
    print(f"\n[1] Czytanie: {input_file}")
    with open(input_file, 'rb') as f:
        original_data = f.read()
    
    original_size = len(original_data)
    print(f"    Rozmiar oryginalny: {original_size:,} bajtów")
    
    # 2. Kompresja
    print(f"\n[2] Kompresja (zlib, poziom 9)...")
    compressed_data = zlib.compress(original_data, level=9)
    compressed_size = len(compressed_data)
    
    print(f"    Rozmiar skompresowany: {compressed_size:,} bajtów")
    ratio = (1 - compressed_size / original_size) * 100
    print(f"    Stopień kompresji: {ratio:.2f}%")
    print(f"    Bity na bajt: {(compressed_size * 8) / original_size:.3f}")
    
    # 3. Zapis archiwum
    print(f"\n[3] Zapis archiwum: {compressed_file}")
    with open(compressed_file, 'wb') as f:
        f.write(compressed_data)
    
    # 4. Dekompresja
    print(f"\n[4] Dekompresja...")
    with open(compressed_file, 'rb') as f:
        compressed_read = f.read()
    
    decompressed_data = zlib.decompress(compressed_read)
    
    print(f"    Rozmiar zdekompresowany: {len(decompressed_data):,} bajtów")
    
    # 5. Weryfikacja
    print(f"\n[5] Weryfikacja...")
    if decompressed_data == original_data:
        print("    ✓ SUKCES: Dane identyczne!")
    else:
        print("    ✗ BŁĄD: Dane się różnią!")
        return
    
    # 6. Zapis odtworzonego pliku (opcjonalnie)
    with open(decompressed_file, 'wb') as f:
        f.write(decompressed_data)
    print(f"    Zapisano zdekompresowany plik: {decompressed_file}")
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    print(f"Oryginalny:      {original_size:>10,} bajtów")
    print(f"Skompresowany:   {compressed_size:>10,} bajtów")
    print(f"Oszczędność:     {original_size - compressed_size:>10,} bajtów ({ratio:.2f}%)")
    print(f"Bity/bajt:       {(compressed_size * 8) / original_size:>14.3f}")
    print("=" * 60)
    
    print("\n✓ Pipeline kompresji działa poprawnie!")
    print("\nNastępny krok: własny model probabilistyczny zamiast zlib")

if __name__ == "__main__":
    main()
