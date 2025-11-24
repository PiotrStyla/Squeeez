#!/usr/bin/env python3
"""
INNOWACYJNE PODEJŚCIE: Analiza graph'u linków Wikipedia
Sprawdzamy czy linki są przewidywalne na podstawie poprzednich linków
"""
import re
from collections import defaultdict, Counter
import time

def extract_link_graph(data, max_links=10000):
    """
    Ekstrahuje graf linków: które linki pojawiają się po których
    
    Returns:
        edges: dict[link] = Counter(następne_linki)
        all_links: lista wszystkich linków w kolejności
    """
    print("🔗 Ekstrakcja graph'u linków...")
    
    # Znajdź wszystkie linki
    link_pattern = re.compile(rb'\[\[([^\]|]+)')
    matches = link_pattern.findall(data)
    
    all_links = []
    for match in matches:
        link = match.decode('utf-8', errors='ignore').strip()
        if len(link) > 0 and len(link) < 100:  # Sensowna długość
            all_links.append(link)
    
    print(f"   Znaleziono {len(all_links):,} linków")
    print(f"   Unikalnych: {len(set(all_links)):,}")
    
    # Buduj graf: link → następny link
    edges = defaultdict(Counter)
    
    for i in range(len(all_links) - 1):
        current = all_links[i]
        next_link = all_links[i + 1]
        edges[current][next_link] += 1
    
    return edges, all_links

def analyze_predictability(edges, all_links):
    """
    Analizuje jak przewidywalne są linki
    """
    print("\n📊 Analiza przewidywalności...")
    
    # Statystyki
    total_predictions = 0
    correct_top1 = 0
    correct_top3 = 0
    correct_top10 = 0
    
    for i in range(len(all_links) - 1):
        current = all_links[i]
        actual_next = all_links[i + 1]
        
        if current in edges and len(edges[current]) > 0:
            # Najbardziej prawdopodobne następne linki
            top_predictions = edges[current].most_common(10)
            top_links = [link for link, count in top_predictions]
            
            total_predictions += 1
            
            if actual_next == top_links[0]:
                correct_top1 += 1
            if actual_next in top_links[:3]:
                correct_top3 += 1
            if actual_next in top_links[:10]:
                correct_top10 += 1
    
    if total_predictions > 0:
        acc1 = (correct_top1 / total_predictions) * 100
        acc3 = (correct_top3 / total_predictions) * 100
        acc10 = (correct_top10 / total_predictions) * 100
        
        print(f"\n   Trafności przewidywań:")
        print(f"     Top-1:  {acc1:>6.2f}% ({correct_top1:,} / {total_predictions:,})")
        print(f"     Top-3:  {acc3:>6.2f}% ({correct_top3:,} / {total_predictions:,})")
        print(f"     Top-10: {acc10:>6.2f}% ({correct_top10:,} / {total_predictions:,})")
        
        return acc1, acc3, acc10
    
    return 0, 0, 0

def calculate_compression_potential(edges, all_links, acc1, acc3, acc10):
    """
    Oszacuj potencjał kompresji przy graph-based prediction
    """
    print("\n💡 Potencjał kompresji...")
    
    # Średnia długość linka
    avg_link_len = sum(len(link.encode('utf-8')) for link in set(all_links)) / len(set(all_links))
    print(f"   Średnia długość linka: {avg_link_len:.1f} bajtów")
    
    # Baseline: każdy link jako plain text
    baseline_bits = len(all_links) * avg_link_len * 8
    
    # Z graph prediction:
    # - Top-1 hit: 1 bit (tak/nie)
    # - Top-3 hit: 2 bity (który z 3)
    # - Top-10 hit: 4 bity (który z 10)
    # - Miss: pełna nazwa
    
    predicted_bits = 0
    predicted_bits += (acc1 / 100) * len(all_links) * 1  # Top-1
    predicted_bits += ((acc3 - acc1) / 100) * len(all_links) * 2  # Top-3
    predicted_bits += ((acc10 - acc3) / 100) * len(all_links) * 4  # Top-10
    predicted_bits += ((100 - acc10) / 100) * len(all_links) * avg_link_len * 8  # Miss
    
    compression_ratio = (1 - predicted_bits / baseline_bits) * 100
    
    print(f"\n   Baseline (plain text):  {baseline_bits:,.0f} bitów")
    print(f"   Z graph prediction:     {predicted_bits:,.0f} bitów")
    print(f"   Kompresja:              {compression_ratio:>6.2f}%")
    
    return compression_ratio

def analyze_link_patterns(all_links):
    """
    Szukaj powtarzających się wzorców w linkach
    """
    print("\n🔍 Wzorce w linkach...")
    
    # Najczęstsze linki
    link_freq = Counter(all_links)
    top_links = link_freq.most_common(20)
    
    print(f"\n   Top 20 najpopularniejszych linków:")
    for i, (link, count) in enumerate(top_links[:10], 1):
        pct = (count / len(all_links)) * 100
        print(f"     {i:2d}. {link[:40]:<40} {count:>5} ({pct:>4.1f}%)")
    
    # Coverage top-N
    total = len(all_links)
    cumulative = 0
    for n in [10, 50, 100, 500, 1000]:
        cumulative = sum(count for _, count in link_freq.most_common(n))
        coverage = (cumulative / total) * 100
        print(f"\n   Top {n:>4} linków pokrywa: {coverage:>5.1f}% wszystkich wystąpień")

def main():
    print("=" * 70)
    print("INNOWACYJNA ANALIZA: Graph-based Link Prediction")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    print(f"\n[1] Czytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"    Rozmiar: {len(data):,} bajtów")
    
    # Analiza
    start = time.time()
    
    edges, all_links = extract_link_graph(data)
    
    if len(all_links) < 10:
        print("\n❌ Za mało linków do analizy")
        return
    
    # Przewidywalność
    acc1, acc3, acc10 = analyze_predictability(edges, all_links)
    
    # Potencjał kompresji
    compression_potential = calculate_compression_potential(edges, all_links, acc1, acc3, acc10)
    
    # Wzorce
    analyze_link_patterns(all_links)
    
    elapsed = time.time() - start
    
    # Wnioski
    print(f"\n{'=' * 70}")
    print("WNIOSKI")
    print(f"{'=' * 70}")
    
    if acc1 > 10:
        print(f"\n✓ Linki są PRZEWIDYWALNE! Top-1 accuracy: {acc1:.1f}%")
        print(f"✓ Potencjał kompresji linków: ~{compression_potential:.1f}%")
        print(f"\n💡 To znaczy że graph-based approach MA SENS!")
        print(f"   Możemy zakodować linki DUŻO efektywniej niż Order-N")
    else:
        print(f"\n⚠ Linki słabo przewidywalne. Top-1: {acc1:.1f}%")
        print(f"  Graph approach może nie dać dużej przewagi")
    
    print(f"\nCzas analizy: {elapsed:.2f} s")
    print("=" * 70)

if __name__ == "__main__":
    main()
