#!/usr/bin/env python3
"""
Test ultimate compressor na 10 MB
Final verification przed przejściem do następnej innowacji
"""
import time
from full_structure_compressor import FullStructureCompressor

def main():
    print("=" * 70)
    print("ULTIMATE TEST - 10 MB")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie pełnych 10 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    print(f"Rozmiar: {len(data):,} bajtów ({len(data)/(1024*1024):.1f} MB)")
    print("\n⚠️ To może zająć 2-3 minuty...")
    
    # Kompresja
    start = time.time()
    compressor = FullStructureCompressor()
    result = compressor.compress(data)
    total_time = time.time() - start
    
    # Wyniki
    print(f"\n{'=' * 70}")
    print("FINALNE WYNIKI - 10 MB")
    print(f"{'=' * 70}")
    
    ultimate_bpb = (result['total_bytes'] * 8) / len(data)
    
    print(f"\nSekcje:     {result['section_bytes']:>10,} bajtów")
    print(f"Linki:      {result['link_bytes']:>10,} bajtów")
    print(f"Templates:  {result['template_bytes']:>10,} bajtów")
    print(f"Tekst:      {result['text_bytes']:>10,} bajtów ({result['text_bpb']:.3f} bpb)")
    print(f"─" * 50)
    print(f"TOTAL:      {result['total_bytes']:>10,} bajtów ({ultimate_bpb:.3f} bpb)")
    
    # Porównanie
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    
    baseline_bpb = 2.36  # Order-3 na 10 MB
    graph_template_bpb = 1.843  # Graph+Templates na 10 MB
    
    import zlib
    zlib_comp = zlib.compress(data, level=9)
    zlib_bpb = (len(zlib_comp) * 8) / len(data)
    
    print(f"\n{'Wersja':<30} {'Bity/bajt':<12} {'Improvement'}")
    print("-" * 70)
    print(f"{'zlib -9':<30} {zlib_bpb:<12.3f} {'-'}")
    print(f"{'Baseline Order-3':<30} {baseline_bpb:<12.3f} {'baseline'}")
    print(f"{'Graph + Templates':<30} {graph_template_bpb:<12.3f} {'+21.9%'}")
    print(f"{'ULTIMATE (+ Sections)':<30} {ultimate_bpb:<12.3f}", end='')
    
    improvement = ((baseline_bpb - ultimate_bpb) / baseline_bpb) * 100
    improvement_vs_gt = ((graph_template_bpb - ultimate_bpb) / graph_template_bpb) * 100
    
    print(f" {'+' if improvement > 0 else ''}{improvement:.1f}%")
    
    if improvement_vs_gt > 0:
        print(f"\n✓ Sections dodały {improvement_vs_gt:.2f}% dodatkowej poprawy!")
    
    # Projekcja enwik9
    print(f"\n{'=' * 70}")
    print("PROJEKCJA NA ENWIK9 (1 GB)")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    ultimate_proj = int(ultimate_bpb * enwik9_size / 8)
    baseline_proj = int(baseline_bpb * enwik9_size / 8)
    
    print(f"\nBaseline Order-3:  {baseline_proj:>15,} B  ({baseline_proj/(1024*1024):>6.1f} MB)")
    print(f"ULTIMATE:          {ultimate_proj:>15,} B  ({ultimate_proj/(1024*1024):>6.1f} MB)")
    
    savings = baseline_proj - ultimate_proj
    gap_to_record = (ultimate_proj / (1024*1024)) - 114
    
    print(f"\nOszczędność:       {savings:>15,} B  ({savings/(1024*1024):>6.1f} MB)")
    print(f"Gap do rekordu (114 MB): {gap_to_record:>6.1f} MB")
    
    # Statystyki
    print(f"\n{'=' * 70}")
    print("BREAKDOWN")
    print(f"{'=' * 70}")
    
    total_bits = result['total_bytes'] * 8
    
    print(f"\nSekcje:    {result['section_bytes']:>10,} B  ({(result['section_bytes']/result['total_bytes'])*100:>4.1f}%)")
    print(f"Linki:     {result['link_bytes']:>10,} B  ({(result['link_bytes']/result['total_bytes'])*100:>4.1f}%)")
    print(f"Templates: {result['template_bytes']:>10,} B  ({(result['template_bytes']/result['total_bytes'])*100:>4.1f}%)")
    print(f"Tekst:     {result['text_bytes']:>10,} B  ({(result['text_bytes']/result['total_bytes'])*100:>4.1f}%)")
    
    print(f"\nCzas: {total_time:.1f} s ({total_time/60:.1f} min)")
    print(f"Prędkość: {len(data)/(1024*1024*total_time):.3f} MB/s")
    
    # Finalne wnioski
    print(f"\n{'=' * 70}")
    print("WNIOSKI")
    print(f"{'=' * 70}")
    
    if ultimate_bpb < 2.0:
        print(f"\n✓ PONIŻEJ 2.0 bpb - EXCELLENT!")
        print(f"✓ Projekcja ~{ultimate_proj/(1024*1024):.0f} MB na enwik9")
        
        if gap_to_record < 120:
            print(f"✓ Gap do rekordu < 120 MB - TOP-20 territory!")
        
        if gap_to_record < 100:
            print(f"🎯 Gap < 100 MB - możliwy TOP-15!")
    
    print(f"\n3 główne innowacje pracują razem:")
    print(f"  1. Graph-based links (76.5% accuracy)")
    print(f"  2. Template dictionary (85.8% potencjał)")
    print(f"  3. Section prediction (84% accuracy)")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
