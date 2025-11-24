#!/usr/bin/env python3
"""
Analiza struktury sekcji w artykułach Wikipedia
Sprawdzamy czy kolejność i nazwy sekcji są przewidywalne
"""
import re
from collections import Counter, defaultdict

def extract_sections(data):
    """Wyodrębnia hierarchię sekcji z artykułów"""
    
    # Pattern dla nagłówków: == Title ==, === Subtitle ===, etc.
    heading_pattern = re.compile(rb'(={2,6})\s*([^=]+?)\s*\1')
    
    articles = []
    current_article = {'sections': [], 'structure': []}
    
    for match in heading_pattern.finditer(data):
        level = len(match.group(1))
        title = match.group(2).decode('utf-8', errors='ignore').strip()
        
        if len(title) > 0 and len(title) < 100:
            current_article['sections'].append((level, title))
            current_article['structure'].append(level)
    
    return current_article

def analyze_section_patterns(data):
    """Analizuje wzorce w sekcjach"""
    
    print("=" * 70)
    print("ANALIZA STRUKTURY SEKCJI")
    print("=" * 70)
    
    # Wyodrębnij sekcje
    print("\n[1] Ekstrakcja sekcji...")
    heading_pattern = re.compile(rb'(={2,6})\s*([^=]+?)\s*\1')
    matches = heading_pattern.findall(data)
    
    sections = []
    for level_str, title_bytes in matches:
        level = len(level_str)
        title = title_bytes.decode('utf-8', errors='ignore').strip()
        if len(title) > 0 and len(title) < 100:
            sections.append((level, title))
    
    print(f"    Znaleziono {len(sections):,} sekcji")
    
    if len(sections) < 10:
        print("\n❌ Za mało sekcji do analizy")
        return
    
    # Analiza nazw sekcji
    print("\n[2] Najpopularniejsze nazwy sekcji:")
    
    titles = [title for level, title in sections]
    title_freq = Counter(titles)
    
    for i, (title, count) in enumerate(title_freq.most_common(30), 1):
        pct = (count / len(titles)) * 100
        print(f"    {i:2d}. {title[:50]:<50} {count:>4} ({pct:>4.1f}%)")
    
    # Analiza poziomów
    print("\n[3] Rozkład poziomów:")
    levels = [level for level, title in sections]
    level_freq = Counter(levels)
    
    for level in sorted(level_freq.keys()):
        count = level_freq[level]
        pct = (count / len(levels)) * 100
        print(f"    Level {level}: {count:>5} ({pct:>5.1f}%)")
    
    # Analiza sekwencji
    print("\n[4] Typowe sekwencje sekcji:")
    
    # Bigrams (co po czym idzie)
    bigrams = Counter()
    for i in range(len(sections) - 1):
        _, title1 = sections[i]
        _, title2 = sections[i + 1]
        bigrams[(title1, title2)] += 1
    
    print("\n    Top 20 par sekcji:")
    for i, ((t1, t2), count) in enumerate(bigrams.most_common(20), 1):
        print(f"    {i:2d}. {t1[:25]:<25} → {t2[:25]:<25} {count:>3}x")
    
    # Analiza "standardowych" początków artykułów
    print("\n[5] Typowe początki artykułów (pierwsze 3 sekcje):")
    
    # Symulacja podziału na artykuły (h2 = nowy artykuł)
    article_starts = []
    current_start = []
    
    for level, title in sections:
        if level == 2 and len(current_start) > 0:
            if len(current_start) <= 5:
                article_starts.append(tuple(current_start))
            current_start = [title]
        else:
            if len(current_start) < 5:
                current_start.append(title)
    
    if len(article_starts) > 0:
        start_freq = Counter(article_starts)
        print(f"\n    Znaleziono {len(article_starts):,} początków artykułów")
        print(f"    Unikalnych wzorców: {len(start_freq):,}")
        
        for i, (start, count) in enumerate(start_freq.most_common(10), 1):
            print(f"\n    {i:2d}. ({count}x):")
            for j, section in enumerate(start, 1):
                print(f"        {j}. {section[:60]}")
    
    # Potencjał kompresji
    print("\n" + "=" * 70)
    print("POTENCJAŁ KOMPRESJI")
    print("=" * 70)
    
    # Top-N coverage
    top_20_coverage = sum(count for _, count in title_freq.most_common(20))
    top_50_coverage = sum(count for _, count in title_freq.most_common(50))
    coverage_20 = (top_20_coverage / len(titles)) * 100
    coverage_50 = (top_50_coverage / len(titles)) * 100
    
    print(f"\nTop-20 nazw pokrywa: {coverage_20:.1f}% sekcji")
    print(f"Top-50 nazw pokrywa: {coverage_50:.1f}% sekcji")
    
    # Baseline: każda sekcja jako plain text
    avg_len = sum(len(t.encode('utf-8')) for t in set(titles)) / len(set(titles))
    baseline_bits = len(titles) * avg_len * 8
    
    # Z dictionary: top-50 jako IDs (6 bitów), reszta full
    top_50_count = top_50_coverage
    dict_bits = top_50_count * 6 + (len(titles) - top_50_count) * avg_len * 8
    
    compression = (1 - dict_bits / baseline_bits) * 100
    
    print(f"\nŚrednia długość nazwy: {avg_len:.1f} bajtów")
    print(f"Baseline: {baseline_bits:,.0f} bitów")
    print(f"Z dictionary: {dict_bits:,.0f} bitów")
    print(f"Kompresja: {compression:.1f}%")
    
    # Sequence prediction
    print("\n[6] Predykcja sekwencji:")
    
    # Accuracy: ile razy następna sekcja jest top-1 prediction
    correct_predictions = 0
    total_predictions = 0
    
    section_graph = defaultdict(Counter)
    for i in range(len(sections) - 1):
        _, title1 = sections[i]
        _, title2 = sections[i + 1]
        section_graph[title1][title2] += 1
    
    for i in range(len(sections) - 1):
        _, current = sections[i]
        _, next_actual = sections[i + 1]
        
        if current in section_graph and len(section_graph[current]) > 0:
            top_prediction = section_graph[current].most_common(1)[0][0]
            total_predictions += 1
            if top_prediction == next_actual:
                correct_predictions += 1
    
    if total_predictions > 0:
        accuracy = (correct_predictions / total_predictions) * 100
        print(f"    Top-1 accuracy: {accuracy:.1f}%")
        
        if accuracy > 30:
            print(f"\n✓ Sekcje są przewidywalne!")
            print(f"  Możemy użyć graph-based prediction jak dla linków!")
    
    print("=" * 70)

def main():
    input_file = "data/enwik_10mb"
    
    print(f"Czytanie 1 MB z: {input_file}\n")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    analyze_section_patterns(data)

if __name__ == "__main__":
    main()
