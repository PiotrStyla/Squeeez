#!/usr/bin/env python3
"""
Test pełnego systemu Graph+Templates na 10 MB
Sprawdzamy czy approach skaluje się dobrze
"""
import time
from graph_template_compressor import GraphTemplateCompressor

def main():
    print("=" * 70)
    print("TEST PEŁNEGO SYSTEMU - 10 MB")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 10 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    print(f"Rozmiar: {len(data):,} bajtów ({len(data)/(1024*1024):.1f} MB)")
    
    print("\n⚠️ To może zająć 5-10 minut...")
    print("   (Trening modelu Order-3 na 10 MB + kodowanie)")
    
    # Kompresja
    start = time.time()
    compressor = GraphTemplateCompressor()
    result = compressor.compress(data)
    total_time = time.time() - start
    
    # Wyniki
    print(f"\n{'=' * 70}")
    print("WYNIKI - 10 MB TEST")
    print(f"{'=' * 70}")
    
    enhanced_bpb = (result['total_bytes'] * 8) / len(data)
    
    print(f"\nLinki:      {result['link_bytes']:>10,} bajtów")
    print(f"Templates:  {result['template_bytes']:>10,} bajtów")
    print(f"Tekst:      {result['text_bytes']:>10,} bajtów ({result['text_bpb']:.3f} bpb)")
    print(f"─" * 50)
    print(f"RAZEM:      {result['total_bytes']:>10,} bajtów ({enhanced_bpb:.3f} bpb)")
    
    # Porównanie
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    
    import zlib
    print(f"\nKompresja zlib (dla porównania)...")
    zlib_comp = zlib.compress(data, level=9)
    zlib_bpb = (len(zlib_comp) * 8) / len(data)
    
    baseline_bpb = 2.36  # Z wcześniejszych testów Order-3 na 10 MB
    
    print(f"\n{'Metoda':<30} {'Rozmiar':<15} {'Bity/bajt':<12}")
    print("-" * 70)
    print(f"{'zlib -9':<30} {len(zlib_comp):<15,} {zlib_bpb:<12.3f}")
    print(f"{'Baseline Order-3':<30} {'~3,094,131':<15} {baseline_bpb:<12.3f}")
    print(f"{'Graph + Templates':<30} {result['total_bytes']:<15,} {enhanced_bpb:<12.3f}")
    
    improvement = ((baseline_bpb - enhanced_bpb) / baseline_bpb) * 100
    improvement_vs_zlib = ((zlib_bpb - enhanced_bpb) / zlib_bpb) * 100
    
    print(f"\n{'=' * 70}")
    print(f"✓ Improvement vs baseline: {improvement:>+6.2f}%")
    print(f"✓ Improvement vs zlib:     {improvement_vs_zlib:>+6.2f}%")
    
    # Projekcja na enwik9
    print(f"\n{'=' * 70}")
    print("PROJEKCJA NA ENWIK9 (1 GB)")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    
    baseline_proj = int(baseline_bpb * enwik9_size / 8)
    enhanced_proj = int(enhanced_bpb * enwik9_size / 8)
    zlib_proj = int(zlib_bpb * enwik9_size / 8)
    
    print(f"\n{'Metoda':<30} {'Rozmiar':<20}")
    print("-" * 70)
    print(f"{'zlib':<30} {zlib_proj:>15,} B  ({zlib_proj/(1024*1024):>6.1f} MB)")
    print(f"{'Baseline Order-3':<30} {baseline_proj:>15,} B  ({baseline_proj/(1024*1024):>6.1f} MB)")
    print(f"{'Graph + Templates':<30} {enhanced_proj:>15,} B  ({enhanced_proj/(1024*1024):>6.1f} MB)")
    
    savings = baseline_proj - enhanced_proj
    record_gap = (enhanced_proj / (1024*1024)) - 114
    
    print(f"\nOszczędność vs baseline: {savings:>15,} B  ({savings/(1024*1024):>6.1f} MB)")
    print(f"Gap do rekordu (114 MB): {record_gap:>15.1f} MB")
    
    # Statystyki
    print(f"\n{'=' * 70}")
    print("STATYSTYKI")
    print(f"{'=' * 70}")
    
    print(f"\nCzas kompresji: {total_time:.1f} s ({total_time/60:.1f} min)")
    print(f"Prędkość: {len(data)/(1024*1024*total_time):.3f} MB/s")
    
    print(f"\nLinki:")
    for k, v in result['link_stats'].items():
        print(f"  {k}: {v:,}")
    
    print(f"\nTemplates:")
    for k, v in result['template_stats'].items():
        print(f"  {k}: {v:,}")
    
    print(f"\n{'=' * 70}")
    print("WNIOSKI")
    print(f"{'=' * 70}")
    
    if enhanced_bpb < baseline_bpb:
        print(f"\n✓ Approach DZIAŁA na większych plikach!")
        print(f"✓ Graph+Templates consistent lepsze niż baseline")
        
        if enhanced_bpb < 2.0:
            print(f"✓ PONIŻEJ 2.0 bpb - to jest ŚWIETNY wynik!")
            print(f"  Projekcja ~{enhanced_proj/(1024*1024):.0f} MB to potencjalnie top-20")
        
        if record_gap < 100:
            print(f"\n🎯 Gap do rekordu < 100 MB - realna szansa na top-10!")
    else:
        print(f"\n⚠️ Na 10 MB wynik gorszy - może potrzeba więcej danych")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
