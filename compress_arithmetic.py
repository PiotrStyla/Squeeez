#!/usr/bin/env python3
"""
Kompresor używający arithmetic coding + model Order-0
To pokazuje fundament prawdziwego kompresora "Hutter Prize style"
"""
import struct
from arithmetic_coder import ArithmeticEncoder, FrequencyModel

def compress_file(input_path, output_path):
    """Kompresuje plik używając arithmetic coding"""
    
    print("=" * 60)
    print("ARITHMETIC CODING - Model Order-0")
    print("=" * 60)
    
    # 1. Wczytaj dane
    print(f"\n[1] Czytanie: {input_path}")
    with open(input_path, 'rb') as f:
        original_data = f.read()
    
    data_list = list(original_data)  # Konwersja na listę bajtów
    original_size = len(data_list)
    print(f"    Rozmiar: {original_size:,} bajtów")
    print(f"    Unikalne symbole: {len(set(data_list))}")
    
    # 2. Zbuduj model częstotliwości
    print(f"\n[2] Budowanie modelu częstotliwości...")
    freq_model = FrequencyModel()
    freq_model.build_from_data(data_list)
    
    # Oblicz teoretyczną entropię
    import math
    entropy = 0
    freq_count = {}
    for symbol in data_list:
        freq_count[symbol] = freq_count.get(symbol, 0) + 1
    
    for count in freq_count.values():
        prob = count / original_size
        entropy -= prob * math.log2(prob)
    
    theoretical_bits = entropy * original_size
    print(f"    Entropia: {entropy:.4f} bitów/bajt")
    print(f"    Teoretyczny minimum: {theoretical_bits / 8:,.1f} bajtów")
    
    # 3. Zakoduj dane
    print(f"\n[3] Kodowanie arytmetyczne...")
    encoder = ArithmeticEncoder(precision_bits=32)
    encoded_data = encoder.encode(data_list, freq_model)
    
    # 4. Serializuj model (potrzebny do dekompresji)
    serialized_model = freq_model.serialize()
    
    # 5. Zapisz archiwum: [długość danych][model][zakodowane dane]
    print(f"\n[4] Tworzenie archiwum...")
    with open(output_path, 'wb') as f:
        # Header: długość oryginalnych danych (4 bajty)
        f.write(struct.pack('<I', original_size))
        # Długość modelu (4 bajty)
        f.write(struct.pack('<I', len(serialized_model)))
        # Model
        f.write(serialized_model)
        # Zakodowane dane
        f.write(encoded_data)
    
    # 6. Statystyki
    archive_size = 8 + len(serialized_model) + len(encoded_data)
    model_size = len(serialized_model)
    compressed_size = len(encoded_data)
    
    print(f"\n    Rozmiar modelu: {model_size:,} bajtów")
    print(f"    Rozmiar zakodowanych danych: {compressed_size:,} bajtów")
    print(f"    Całkowity rozmiar archiwum: {archive_size:,} bajtów")
    
    ratio = (1 - archive_size / original_size) * 100
    bits_per_byte = (archive_size * 8) / original_size
    
    print(f"\n    Stopień kompresji: {ratio:.2f}%")
    print(f"    Bity/bajt: {bits_per_byte:.3f}")
    print(f"    Vs teoretyczne minimum: {(archive_size / (theoretical_bits / 8)):.2f}x")
    
    return archive_size, original_size

def decompress_file(input_path, output_path):
    """Dekompresuje plik"""
    
    print("\n" + "=" * 60)
    print("DEKOMPRESJA")
    print("=" * 60)
    
    # 1. Wczytaj archiwum
    print(f"\n[1] Czytanie archiwum: {input_path}")
    with open(input_path, 'rb') as f:
        # Odczytaj długość oryginalnych danych
        original_length = struct.unpack('<I', f.read(4))[0]
        print(f"    Długość do odkodowania: {original_length:,} bajtów")
        
        # Odczytaj model
        model_length = struct.unpack('<I', f.read(4))[0]
        serialized_model = f.read(model_length)
        freq_model = FrequencyModel.deserialize(serialized_model)
        
        # Odczytaj zakodowane dane
        encoded_data = f.read()
    
    # 2. Dekoduj
    print(f"\n[2] Dekodowanie...")
    encoder = ArithmeticEncoder(precision_bits=32)
    decoded_list = encoder.decode(encoded_data, freq_model, original_length)
    decoded_data = bytes(decoded_list)
    
    # 3. Zapisz
    print(f"\n[3] Zapis: {output_path}")
    with open(output_path, 'wb') as f:
        f.write(decoded_data)
    
    print(f"    Zapisano {len(decoded_data):,} bajtów")
    
    return decoded_data

def main():
    input_file = "data/sample.txt"
    compressed_file = "data/sample.arith"
    decompressed_file = "data/sample_arith_restored.txt"
    
    # Kompresja
    archive_size, original_size = compress_file(input_file, compressed_file)
    
    # Dekompresja
    decompressed_data = decompress_file(compressed_file, decompressed_file)
    
    # Weryfikacja
    print("\n" + "=" * 60)
    print("WERYFIKACJA")
    print("=" * 60)
    
    with open(input_file, 'rb') as f:
        original_data = f.read()
    
    if decompressed_data == original_data:
        print("\n✓ SUKCES: Dane identyczne!")
    else:
        print("\n✗ BŁĄD: Dane się różnią!")
        return
    
    # Porównanie z zlib
    import zlib
    zlib_size = len(zlib.compress(original_data, level=9))
    
    print("\n" + "=" * 60)
    print("PORÓWNANIE")
    print("=" * 60)
    print(f"Oryginalny:          {original_size:>10,} bajtów")
    print(f"Arithmetic (Order-0):{archive_size:>10,} bajtów")
    print(f"zlib (poziom 9):     {zlib_size:>10,} bajtów")
    print("=" * 60)
    
    if archive_size < zlib_size:
        improvement = ((zlib_size - archive_size) / zlib_size) * 100
        print(f"\n✓ Arithmetic lepsze o {improvement:.1f}%")
    else:
        worse = ((archive_size - zlib_size) / zlib_size) * 100
        print(f"\n⚠ Arithmetic gorsze o {worse:.1f}%")
        print("  (To normalne - Order-0 jest bardzo prosty)")
    
    print("\n📊 Następny krok: dodać kontekst (n-gramy) do modelu!")

if __name__ == "__main__":
    main()
