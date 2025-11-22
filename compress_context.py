#!/usr/bin/env python3
"""
Kompresor z modelem kontekstowym Order-N
Znacznie lepsza kompresja niż Order-0
"""
import struct
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

def compress_file(input_path, output_path, order=2):
    """Kompresuje plik używając modelu Order-N"""
    
    print("=" * 60)
    print(f"CONTEXT MODEL - Order-{order}")
    print("=" * 60)
    
    # 1. Wczytaj dane
    print(f"\n[1] Czytanie: {input_path}")
    with open(input_path, 'rb') as f:
        original_data = f.read()
    
    data_list = list(original_data)
    original_size = len(data_list)
    print(f"    Rozmiar: {original_size:,} bajtów")
    
    # 2. Trenuj model
    print(f"\n[2] Trening modelu Order-{order}...")
    context_model = ContextModel(order=order)
    context_model.train(original_data)
    
    # 3. Koduj
    print(f"\n[3] Kodowanie z kontekstem...")
    encoder = ArithmeticEncoder(precision_bits=32)
    
    # Przygotuj model do sekwencyjnego kodowania
    context_model.start_encoding()
    
    # Koduj symbole jeden po drugim, aktualizując kontekst
    # Nie możemy użyć wrapper, który automatycznie aktualizuje,
    # bo musimy mieć pełną kontrolę nad kolejnością operacji
    
    # Zamiast tego używamy prostszego podejścia bez automatic update
    class StaticModelWrapper:
        def __init__(self, ctx_model, data):
            self.ctx_model = ctx_model
            self.data = data
            self.index = 0
        
        def get_range(self, symbol):
            # Pobierz zakres dla symbolu w bieżącym kontekście
            low, high, total = self.ctx_model.get_range(symbol)
            # Aktualizuj kontekst dla następnego symbolu
            self.ctx_model.update_context(symbol)
            return low, high, total
        
        def get_total(self):
            return self.ctx_model.get_total()
        
        def get_symbol(self, offset):
            # To nie powinno być używane w encode
            raise NotImplementedError()
    
    wrapper = StaticModelWrapper(context_model, data_list)
    encoded_data = encoder.encode(data_list, wrapper)
    
    # 4. Serializuj model
    print(f"\n[4] Serializacja modelu...")
    serialized_model = context_model.serialize()
    
    # 5. Zapisz archiwum
    print(f"\n[5] Tworzenie archiwum...")
    with open(output_path, 'wb') as f:
        # Header
        f.write(struct.pack('<I', original_size))  # długość danych
        f.write(struct.pack('<I', len(serialized_model)))  # długość modelu
        # Model
        f.write(serialized_model)
        # Dane
        f.write(encoded_data)
    
    # 6. Statystyki
    archive_size = 8 + len(serialized_model) + len(encoded_data)
    model_size = len(serialized_model)
    data_size = len(encoded_data)
    
    print(f"\n    Rozmiar modelu: {model_size:,} bajtów")
    print(f"    Rozmiar danych: {data_size:,} bajtów")
    print(f"    Całkowity rozmiar: {archive_size:,} bajtów")
    
    ratio = (1 - archive_size / original_size) * 100
    bits_per_byte = (data_size * 8) / original_size
    
    print(f"\n    Stopień kompresji: {ratio:.2f}%")
    print(f"    Bity/bajt (tylko dane): {bits_per_byte:.3f}")
    
    return archive_size, data_size, original_size

def decompress_file(input_path, output_path):
    """Dekompresuje plik"""
    
    print("\n" + "=" * 60)
    print("DEKOMPRESJA")
    print("=" * 60)
    
    # 1. Wczytaj archiwum
    print(f"\n[1] Czytanie: {input_path}")
    with open(input_path, 'rb') as f:
        original_length = struct.unpack('<I', f.read(4))[0]
        model_length = struct.unpack('<I', f.read(4))[0]
        serialized_model = f.read(model_length)
        encoded_data = f.read()
    
    print(f"    Długość do odkodowania: {original_length:,} bajtów")
    
    # 2. Deserializuj model
    print(f"\n[2] Ładowanie modelu...")
    context_model = ContextModel.deserialize(serialized_model)
    context_model.start_encoding()  # Reset kontekstu
    
    # 3. Dekoduj
    print(f"\n[3] Dekodowanie...")
    encoder = ArithmeticEncoder(precision_bits=32)
    
    # Wrapper dla dekodowania - MUSI mieć identyczną logikę jak encoder
    class DecoderModelWrapper:
        def __init__(self, ctx_model):
            self.ctx_model = ctx_model
            self.pending_symbol = None
        
        def get_range(self, symbol):
            # W decode: get_symbol -> get_range
            # get_range jest wywoływane DRUGĄ po get_symbol, więc tutaj aktualizujemy
            low, high, total = self.ctx_model.get_range(symbol)
            # Aktualizuj kontekst teraz (po obu wywołaniach)
            self.ctx_model.update_context(symbol)
            return low, high, total
        
        def get_total(self):
            return self.ctx_model.get_total()
        
        def get_symbol(self, offset):
            # Znajdź symbol dla danego offsetu (NIE aktualizuj tutaj)
            symbol = self.ctx_model.get_symbol(offset)
            return symbol
    
    wrapper = DecoderModelWrapper(context_model)
    decoded_list = encoder.decode(encoded_data, wrapper, original_length)
    decoded_data = bytes(decoded_list)
    
    # 4. Zapisz
    print(f"\n[4] Zapis: {output_path}")
    with open(output_path, 'wb') as f:
        f.write(decoded_data)
    
    print(f"    Zapisano {len(decoded_data):,} bajtów")
    
    return decoded_data

def test_multiple_orders():
    """Testuje różne wartości order"""
    
    input_file = "data/sample.txt"
    
    with open(input_file, 'rb') as f:
        original_data = f.read()
        original_size = len(original_data)
    
    import zlib
    zlib_size = len(zlib.compress(original_data, level=9))
    
    print("\n" + "=" * 60)
    print("PORÓWNANIE RÓŻNYCH WARTOŚCI ORDER")
    print("=" * 60)
    print(f"\nOryginalny rozmiar: {original_size:,} bajtów")
    print(f"zlib (poziom 9):    {zlib_size:,} bajtów\n")
    
    results = []
    
    for order in [0, 1, 2, 3]:
        output_path = f"data/sample_order{order}.ctx"
        decompressed_path = f"data/sample_order{order}_restored.txt"
        
        print(f"\n{'=' * 60}")
        print(f"TEST: Order-{order}")
        print(f"{'=' * 60}")
        
        # Kompresja
        archive_size, data_size, _ = compress_file(input_file, output_path, order=order)
        
        # Dekompresja
        decompressed_data = decompress_file(output_path, decompressed_path)
        
        # Weryfikacja
        if decompressed_data == original_data:
            print("\n✓ Weryfikacja: OK")
            results.append((order, archive_size, data_size))
        else:
            print("\n✗ Weryfikacja: BŁĄD!")
            return
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    print(f"\n{'Order':<10} {'Całkowity':<15} {'Tylko dane':<15} {'Bity/bajt':<10}")
    print("-" * 60)
    print(f"{'Original':<10} {original_size:<15,} {'-':<15} {8.000:.3f}")
    print(f"{'zlib':<10} {zlib_size:<15,} {'-':<15} {(zlib_size * 8 / original_size):.3f}")
    print("-" * 60)
    
    for order, archive_size, data_size in results:
        bits_per_byte = (data_size * 8) / original_size
        print(f"{'Order-' + str(order):<10} {archive_size:<15,} {data_size:<15,} {bits_per_byte:.3f}")
    
    print("=" * 60)
    
    best_order, best_size, best_data = min(results, key=lambda x: x[2])
    print(f"\n✓ Najlepszy: Order-{best_order} z {best_data:,} bajtów danych")
    
    if best_data < zlib_size:
        improvement = ((zlib_size - best_data) / zlib_size) * 100
        print(f"✓ Lepszy od zlib o {improvement:.1f}%!")
    
    print("\n📊 Następny krok: parser struktury Wikipedia (kanały)!")

if __name__ == "__main__":
    test_multiple_orders()
