#!/usr/bin/env python3
"""
Wyświetl wyniki kompresji na podstawie istniejących plików
"""
import os

def main():
    print("\n" + "=" * 70)
    print("WYNIKI KOMPRESJI - Fragment 10 MB enwik8")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    if not os.path.exists(input_file):
        print("❌ Brak pliku wejściowego")
        return
    
    original_size = os.path.getsize(input_file)
    
    # zlib
    import zlib
    with open(input_file, 'rb') as f:
        data = f.read()
    
    zlib_size = len(zlib.compress(data, level=9))
    zlib_bpb = (zlib_size * 8) / original_size
    
    print(f"\n{'Metoda':<15} {'Rozmiar':<20} {'Bity/bajt':<12} {'vs zlib':<10}")
    print("-" * 70)
    print(f"{'Original':<15} {original_size:<20,} {8.0000:<12.4f} {'-':<10}")
    print(f"{'zlib -9':<15} {zlib_size:<20,} {zlib_bpb:<12.4f} {'baseline':<10}")
    print("-" * 70)
    
    # Order-2 i Order-3
    results = []
    
    for order in [2, 3]:
        archive_path = f"data/enwik_10mb_order{order}.ctx"
        if os.path.exists(archive_path):
            archive_size = os.path.getsize(archive_path)
            
            # Odczytaj rozmiar danych z archiwum
            import struct
            with open(archive_path, 'rb') as f:
                orig_len = struct.unpack('<I', f.read(4))[0]
                model_len = struct.unpack('<I', f.read(4))[0]
                # data_size = archive_size - 8 - model_len
            
            data_size = archive_size - 8 - model_len
            bpb = (data_size * 8) / original_size
            
            vs_zlib = ((zlib_size - data_size) / zlib_size) * 100
            sign = '+' if vs_zlib > 0 else ''
            
            print(f"{'Order-' + str(order):<15} {data_size:<20,} {bpb:<12.4f} {sign}{vs_zlib:<9.1f}%")
            
            results.append((order, bpb, data_size))
    
    print("=" * 70)
    
    if results:
        best = min(results, key=lambda x: x[1])
        print(f"\n✓ Najlepszy: Order-{best[0]} z {best[1]:.4f} bity/bajt")
        
        improvement = ((zlib_bpb - best[1]) / zlib_bpb) * 100
        print(f"✓ Poprawa vs zlib: {improvement:.2f}%")
        
        # Projekcja na enwik9
        print(f"\n{'=' * 70}")
        print("PROJEKCJA NA ENWIK9 (1 GB)")
        print("=" * 70)
        
        enwik9_size = 1_000_000_000
        
        print(f"\nPrzypuszczalny rozmiar skompresowanych danych:")
        zlib_proj = zlib_bpb * enwik9_size / 8
        print(f"  zlib:     {int(zlib_proj):>15,} bajtów ({zlib_proj / (1024*1024):>7.1f} MB)")
        
        for order, bpb, _ in results:
            proj = bpb * enwik9_size / 8
            print(f"  Order-{order}:  {int(proj):>15,} bajtów ({proj / (1024*1024):>7.1f} MB)")
        
        best_proj = best[1] * enwik9_size / 8
        improvement_bytes = zlib_proj - best_proj
        
        print(f"\n  Oszczędność vs zlib: {int(improvement_bytes):,} bajtów ({improvement_bytes / (1024*1024):.1f} MB)")
        print(f"\n⚠ To tylko projekcja na podstawie 10 MB fragmentu.")
        print(f"{'=' * 70}")

if __name__ == "__main__":
    main()
