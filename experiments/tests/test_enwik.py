#!/usr/bin/env python3
"""
Test kompresora na prawdziwym fragmencie enwik
"""
import time
import struct
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

def compress_file(input_path, output_path, order=3):
    """Kompresuje plik używając modelu Order-N"""
    
    start_time = time.time()
    
    print(f"\n{'=' * 70}")
    print(f"KOMPRESJA: Order-{order}")
    print(f"{'=' * 70}")
    
    # 1. Wczytaj dane
    print(f"\n[1] Czytanie: {input_path}")
    with open(input_path, 'rb') as f:
        original_data = f.read()
    
    original_size = len(original_data)
    print(f"    Rozmiar: {original_size:,} bajtów ({original_size / (1024 * 1024):.2f} MB)")
    
    # 2. Trenuj model
    print(f"\n[2] Trening modelu Order-{order}...")
    train_start = time.time()
    
    context_model = ContextModel(order=order)
    context_model.train(original_data)
    
    train_time = time.time() - train_start
    print(f"    Czas treningu: {train_time:.2f} s")
    
    # 3. Koduj
    print(f"\n[3] Kodowanie arytmetyczne...")
    encode_start = time.time()
    
    encoder = ArithmeticEncoder(precision_bits=32)
    context_model.start_encoding()
    
    # Wrapper z progress
    class ProgressWrapper:
        def __init__(self, ctx_model, total):
            self.ctx_model = ctx_model
            self.total = total
            self.count = 0
            self.last_percent = 0
        
        def get_range(self, symbol):
            self.count += 1
            percent = (self.count / self.total) * 100
            if percent - self.last_percent >= 5:  # Co 5%
                print(f"    Postęp: {percent:.1f}%", end='\r')
                self.last_percent = percent
            
            low, high, total = self.ctx_model.get_range(symbol)
            self.ctx_model.update_context(symbol)
            return low, high, total
        
        def get_total(self):
            return self.ctx_model.get_total()
        
        def get_symbol(self, offset):
            raise NotImplementedError()
    
    wrapper = ProgressWrapper(context_model, original_size)
    data_list = list(original_data)
    encoded_data = encoder.encode(data_list, wrapper)
    
    encode_time = time.time() - encode_start
    print(f"\n    Czas kodowania: {encode_time:.2f} s")
    
    # 4. Serializuj model
    serialized_model = context_model.serialize()
    
    # 5. Zapisz
    with open(output_path, 'wb') as f:
        f.write(struct.pack('<I', original_size))
        f.write(struct.pack('<I', len(serialized_model)))
        f.write(serialized_model)
        f.write(encoded_data)
    
    # Statystyki
    total_time = time.time() - start_time
    archive_size = 8 + len(serialized_model) + len(encoded_data)
    
    print(f"\n{'=' * 70}")
    print(f"WYNIKI")
    print(f"{'=' * 70}")
    print(f"Oryginalny rozmiar:      {original_size:>15,} bajtów")
    print(f"Model:                   {len(serialized_model):>15,} bajtów")
    print(f"Zakodowane dane:         {len(encoded_data):>15,} bajtów")
    print(f"Całkowity rozmiar:       {archive_size:>15,} bajtów")
    print(f"-" * 70)
    
    ratio = (1 - archive_size / original_size) * 100
    bits_per_byte = (len(encoded_data) * 8) / original_size
    
    print(f"Stopień kompresji:       {ratio:>14.2f}%")
    print(f"Bity/bajt (dane):        {bits_per_byte:>14.4f}")
    print(f"Bity/bajt (całość):      {(archive_size * 8 / original_size):>14.4f}")
    print(f"-" * 70)
    print(f"Czas treningu:           {train_time:>14.2f} s")
    print(f"Czas kodowania:          {encode_time:>14.2f} s")
    print(f"Czas całkowity:          {total_time:>14.2f} s")
    print(f"Prędkość:                {original_size / (1024 * 1024 * total_time):>14.2f} MB/s")
    print(f"{'=' * 70}")
    
    return archive_size, len(encoded_data), original_size, bits_per_byte

def main():
    import os
    
    input_file = "data/enwik_10mb"
    
    if not os.path.exists(input_file):
        print("❌ Plik nie istnieje. Najpierw uruchom: python download_enwik_auto.py")
        return
    
    with open(input_file, 'rb') as f:
        original_data = f.read()
        original_size = len(original_data)
    
    # Test zlib dla porównania
    print("\n" + "=" * 70)
    print("BASELINE: zlib")
    print("=" * 70)
    
    import zlib
    zlib_start = time.time()
    zlib_data = zlib.compress(original_data, level=9)
    zlib_time = time.time() - zlib_start
    zlib_size = len(zlib_data)
    zlib_bpb = (zlib_size * 8) / original_size
    
    print(f"\nRozmiar skompresowany:   {zlib_size:>15,} bajtów")
    print(f"Bity/bajt:               {zlib_bpb:>14.4f}")
    print(f"Czas:                    {zlib_time:>14.2f} s")
    print(f"Prędkość:                {original_size / (1024 * 1024 * zlib_time):>14.2f} MB/s")
    
    # Test różnych Order
    results = []
    
    for order in [2, 3]:  # Testujemy tylko 2 i 3 (0 i 1 są słabe)
        output_path = f"data/enwik_10mb_order{order}.ctx"
        
        archive_size, data_size, orig_size, bpb = compress_file(
            input_file, output_path, order=order
        )
        
        results.append((order, archive_size, data_size, bpb))
    
    # Podsumowanie
    print("\n" + "=" * 70)
    print("PODSUMOWANIE - Fragment 10 MB enwik8")
    print("=" * 70)
    print(f"\n{'Metoda':<15} {'Rozmiar':<20} {'Bity/bajt':<12} {'vs zlib':<10}")
    print("-" * 70)
    print(f"{'Original':<15} {original_size:<20,} {8.0000:<12.4f} {'-':<10}")
    print(f"{'zlib -9':<15} {zlib_size:<20,} {zlib_bpb:<12.4f} {'baseline':<10}")
    print("-" * 70)
    
    for order, archive_size, data_size, bpb in results:
        vs_zlib = ((zlib_size - data_size) / zlib_size) * 100
        sign = '+' if vs_zlib > 0 else ''
        print(f"{'Order-' + str(order):<15} {data_size:<20,} {bpb:<12.4f} {sign}{vs_zlib:<9.1f}%")
    
    print("=" * 70)
    
    # Najlepszy wynik
    best = min(results, key=lambda x: x[3])
    print(f"\n✓ Najlepszy: Order-{best[0]} z {best[3]:.4f} bity/bajt")
    
    improvement = ((zlib_bpb - best[3]) / zlib_bpb) * 100
    print(f"✓ Poprawa vs zlib: {improvement:.2f}%")
    
    # Projekcja na enwik9
    print(f"\n{'=' * 70}")
    print("PROJEKCJA NA ENWIK9 (1 GB)")
    print("=" * 70)
    
    enwik9_size = 1_000_000_000
    
    print(f"\nPrzypuszczalny rozmiar archiwum (tylko dane):")
    print(f"  zlib:     {int(zlib_bpb * enwik9_size / 8):>15,} bajtów ({zlib_bpb * 1000 / 8:,.1f} MB)")
    
    for order, _, _, bpb in results:
        compressed_size = int(bpb * enwik9_size / 8)
        print(f"  Order-{order}:  {compressed_size:>15,} bajtów ({bpb * 1000 / 8:,.1f} MB)")
    
    print(f"\n⚠ Uwaga: To tylko projekcja. Rzeczywiste wyniki mogą się różnić.")
    print(f"{'=' * 70}")
    
    print("\n📊 Następny krok: Parser struktury Wiki + wielokanałowe modelowanie!")

if __name__ == "__main__":
    main()
