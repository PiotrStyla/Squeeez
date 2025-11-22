#!/usr/bin/env python3
"""
Analiza templates w Wikipedia - czy są przewidywalne?
"""
import re
from collections import Counter

def analyze_templates(data):
    print("=" * 70)
    print("ANALIZA TEMPLATES")
    print("=" * 70)
    
    # Znajdź wszystkie templates
    template_pattern = re.compile(rb'\{\{([^}|]+)')
    matches = template_pattern.findall(data)
    
    templates = []
    for match in matches:
        tmpl = match.decode('utf-8', errors='ignore').strip()
        if len(tmpl) > 0 and len(tmpl) < 100:
            templates.append(tmpl)
    
    print(f"\n[1] Podstawowe statystyki:")
    print(f"    Wszystkie templates: {len(templates):,}")
    print(f"    Unikalne: {len(set(templates)):,}")
    
    if len(templates) == 0:
        print("\n❌ Brak templates do analizy")
        return
    
    # Najczęstsze
    freq = Counter(templates)
    
    print(f"\n[2] Top 20 najpopularniejszych templates:")
    for i, (tmpl, count) in enumerate(freq.most_common(20), 1):
        pct = (count / len(templates)) * 100
        print(f"    {i:2d}. {tmpl[:40]:<40} {count:>5} ({pct:>5.1f}%)")
    
    # Coverage
    print(f"\n[3] Coverage analysis:")
    for n in [10, 20, 50, 100]:
        top_n = sum(count for _, count in freq.most_common(n))
        coverage = (top_n / len(templates)) * 100
        print(f"    Top {n:>3}: {coverage:>6.1f}% coverage")
    
    # Potencjał kompresji
    print(f"\n[4] Potencjał kompresji:")
    
    # Baseline: każdy template jako plain text
    avg_len = sum(len(t.encode('utf-8')) for t in set(templates)) / len(set(templates))
    baseline_bits = len(templates) * avg_len * 8
    
    # Z dictionary: top-N jako IDs
    compressed_bits = 0
    
    # Top 100 templates jako 7-bit IDs
    top_100_count = sum(count for _, count in freq.most_common(100))
    compressed_bits += top_100_count * 7
    
    # Reszta jako full text
    rest_count = len(templates) - top_100_count
    compressed_bits += rest_count * avg_len * 8
    
    compression = (1 - compressed_bits / baseline_bits) * 100
    
    print(f"    Średnia długość template: {avg_len:.1f} bajtów")
    print(f"    Baseline: {baseline_bits:,.0f} bitów")
    print(f"    Z dictionary (top-100): {compressed_bits:,.0f} bitów")
    print(f"    Kompresja: {compression:.1f}%")
    
    # Wnioski
    print(f"\n{'=' * 70}")
    print("WNIOSKI")
    print(f"{'=' * 70}")
    
    top_20_coverage = (sum(count for _, count in freq.most_common(20)) / len(templates)) * 100
    
    if top_20_coverage > 50:
        print(f"\n✓ Templates są BARDZO przewidywalne!")
        print(f"  Top-20 pokrywa {top_20_coverage:.1f}% wystąpień")
        print(f"  Potencjał kompresji: {compression:.1f}%")
    else:
        print(f"\n⚠ Templates mało przewidywalne")
        print(f"  Top-20 pokrywa tylko {top_20_coverage:.1f}%")
    
    print("=" * 70)

def main():
    input_file = "data/enwik_10mb"
    
    print(f"Czytanie 1 MB z: {input_file}\n")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    analyze_templates(data)

if __name__ == "__main__":
    main()
