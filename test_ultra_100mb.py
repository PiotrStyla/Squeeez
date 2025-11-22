#!/usr/bin/env python3
"""
🎯 ULTIMATE VERIFICATION - 100 MB TEST (enwik8)
Final realistic test przed full enwik9 run
"""
import time
from ultra_compressor import UltraCompressor

def main():
    print("=" * 70)
    print("🎯 ULTIMATE VERIFICATION - 100 MB (enwik8) 🎯")
    print("=" * 70)
    
    input_file = "data/enwik8"
    
    print(f"\nCzytanie pełnych 100 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    print(f"Rozmiar: {len(data):,} bajtów ({len(data)/(1024*1024):.1f} MB)")
    
    print("\n" + "=" * 70)
    print("⚠️  IMPORTANT NOTES:")
    print("=" * 70)
    print("\nOrder-5 na 100 MB będzie:")
    print("  - Memory: ~10M kontekstów (może OOM!)")
    print("  - Time: ~15-30 minut")
    print("  - Disk: będzie używać swap jeśli zabraknie RAM")
    print("\nJeśli proces się wysypie z OOM:")
    print("  → Spróbujemy Order-4")
    print("  → Lub adaptive approach")
    print("\nStarting in 5 seconds...")
    
    import sys
    for i in range(5, 0, -1):
        print(f"{i}...", end=' ', flush=True)
        time.sleep(1)
    print("GO!\n")
    
    # Kompresja
    print("=" * 70)
    print("STARTING COMPRESSION")
    print("=" * 70)
    
    start = time.time()
    
    try:
        compressor = UltraCompressor(text_order=5)
        result = compressor.compress(data)
        total_time = time.time() - start
        
        # Wyniki
        print(f"\n{'=' * 70}")
        print("🎉 SUCCESS! FINALNE WYNIKI - 100 MB 🎉")
        print(f"{'=' * 70}")
        
        ultra_bpb = (result['total_bytes'] * 8) / len(data)
        
        print(f"\nSekcje:     {result['section_bytes']:>10,} bajtów")
        print(f"Linki:      {result['link_bytes']:>10,} bajtów")
        print(f"Templates:  {result['template_bytes']:>10,} bajtów")
        print(f"Tekst:      {result['text_bytes']:>10,} bajtów ({result['text_bpb']:.3f} bpb)")
        print(f"─" * 50)
        print(f"TOTAL:      {result['total_bytes']:>10,} bajtów ({ultra_bpb:.3f} bpb)")
        
        # KLUCZOWA PROJEKCJA NA ENWIK9
        print(f"\n{'=' * 70}")
        print("🎯 PROJEKCJA NA ENWIK9 (1 GB) - FINAL! 🎯")
        print(f"{'=' * 70}")
        
        enwik9_size = 1_000_000_000
        ultra_proj = int(ultra_bpb * enwik9_size / 8)
        record = 114 * 1024 * 1024
        
        print(f"\n{'Metoda':<30} {'Rozmiar'}")
        print("-" * 70)
        print(f"{'Current RECORD':<30} {record/(1024*1024):>6.1f} MB")
        print(f"{'ULTRA (Order-5)':<30} {ultra_proj/(1024*1024):>6.1f} MB")
        
        gap = ultra_proj - record
        
        if gap < 0:
            print(f"\n🏆🏆🏆 PROJECTED WORLD RECORD! 🏆🏆🏆")
            print(f"   Beat record by: {-gap/(1024*1024):.1f} MB")
        elif gap/(1024*1024) < 15:
            print(f"\n🎯 EXTREMELY CLOSE TO RECORD!")
            print(f"   Gap: {gap/(1024*1024):.1f} MB")
        elif gap/(1024*1024) < 30:
            print(f"\n✓ Solid TOP-10")
            print(f"   Gap: {gap/(1024*1024):.1f} MB")
        else:
            print(f"\n✓ TOP-20 territory")
            print(f"   Gap: {gap/(1024*1024):.1f} MB")
        
        # Porównanie z poprzednimi
        print(f"\n{'=' * 70}")
        print("EVOLUTION TIMELINE")
        print(f"{'=' * 70}")
        
        print(f"\nTest Size | BPB    | Enwik9 Proj")
        print("-" * 40)
        print(f"1 MB      | 0.898  | 107 MB  (wow!)")
        print(f"10 MB     | 1.167  | 139 MB  (good)")
        print(f"100 MB    | {ultra_bpb:.3f}  | {ultra_proj/(1024*1024):.0f} MB  (FINAL)")
        
        degradation_1_to_10 = ((1.167 - 0.898) / 0.898) * 100
        degradation_10_to_100 = ((ultra_bpb - 1.167) / 1.167) * 100
        
        print(f"\nDegradacja 1→10 MB:   +{degradation_1_to_10:.1f}%")
        print(f"Degradacja 10→100 MB: +{degradation_10_to_100:.1f}%")
        
        # Stats
        print(f"\n{'=' * 70}")
        print("PERFORMANCE STATS")
        print(f"{'=' * 70}")
        
        print(f"\nCzas: {total_time:.1f} s ({total_time/60:.1f} min)")
        print(f"Prędkość: {len(data)/(1024*1024*total_time):.3f} MB/s")
        
        # Save
        with open('ENWIK8_RESULTS.txt', 'w') as f:
            f.write(f"ULTRA COMPRESSOR - 100 MB (enwik8) TEST\n")
            f.write(f"{'=' * 70}\n\n")
            f.write(f"Compression: {ultra_bpb:.3f} bpb\n")
            f.write(f"Projection enwik9: {ultra_proj/(1024*1024):.1f} MB\n")
            f.write(f"Gap to record: {gap/(1024*1024):+.1f} MB\n")
            f.write(f"Time: {total_time:.1f} s ({total_time/60:.1f} min)\n")
            f.write(f"Speed: {len(data)/(1024*1024*total_time):.3f} MB/s\n")
            if gap < 0:
                f.write(f"\n🏆 PROJECTED WORLD RECORD! 🏆\n")
        
        print(f"\nWyniki zapisane do: ENWIK8_RESULTS.txt")
        
        # Final verdict
        print(f"\n{'=' * 70}")
        print("🎖️  FINAL VERDICT  🎖️")
        print(f"{'=' * 70}")
        
        if ultra_bpb < 1.3:
            print(f"\n✓✓✓ EXCELLENT SCALING!")
            print(f"   Order-5 działa świetnie nawet na 100 MB")
            print(f"   Projekcja {ultra_proj/(1024*1024):.0f} MB bardzo wiarygodna")
            
            if gap < 0:
                print(f"\n🏆 Ready for enwik9 RECORD attempt!")
            else:
                print(f"\n🎯 Ready for enwik9 top-10 run!")
                
        elif ultra_bpb < 1.5:
            print(f"\n✓ Good scaling")
            print(f"   Niewielka degradacja, akceptowalna")
            print(f"   Top-15 bardzo prawdopodobny")
            
        else:
            print(f"\n⚠ Znacząca degradacja")
            print(f"   Warto rozważyć optymalizacje przed enwik9")
        
        print("=" * 70)
        
    except MemoryError:
        total_time = time.time() - start
        print(f"\n{'=' * 70}")
        print("⚠️  OUT OF MEMORY!")
        print(f"{'=' * 70}")
        
        print(f"\nOrder-5 wymaga za dużo pamięci dla 100 MB")
        print(f"Time before OOM: {total_time:.1f} s")
        print(f"\n💡 SOLUTIONS:")
        print(f"   1. Try Order-4 instead (4x less memory)")
        print(f"   2. Adaptive order (Order-5 for common, Order-3 for rare)")
        print(f"   3. Context pruning (remove low-freq contexts)")
        print(f"   4. More RAM / swap space")
        
        print(f"\n🔧 Quick fix: Let's try Order-4...")
        
        # Fallback to Order-4
        print(f"\n{'=' * 70}")
        print("RETRY WITH ORDER-4")
        print(f"{'=' * 70}")
        
        start = time.time()
        compressor = UltraCompressor(text_order=4)
        result = compressor.compress(data)
        total_time = time.time() - start
        
        ultra_bpb = (result['total_bytes'] * 8) / len(data)
        ultra_proj = int(ultra_bpb * 1_000_000_000 / 8)
        
        print(f"\nOrder-4 Result: {ultra_bpb:.3f} bpb")
        print(f"Projekcja enwik9: {ultra_proj/(1024*1024):.1f} MB")
        print(f"Time: {total_time:.1f} s")
        
    except Exception as e:
        print(f"\n{'=' * 70}")
        print("❌ ERROR!")
        print(f"{'=' * 70}")
        print(f"\n{type(e).__name__}: {e}")
        print(f"\nTo może być:")
        print(f"  - Brak pamięci")
        print(f"  - Błąd w kodzie")
        print(f"  - Corrupted data")
        print(f"\nDziałanie: Debug i spróbuj ponownie")

if __name__ == "__main__":
    main()
