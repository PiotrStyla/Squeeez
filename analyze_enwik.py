#!/usr/bin/env python3
"""
Analiza struktury prawdziwego enwik
"""
from wiki_parser import WikiParser

def main():
    print("=" * 70)
    print("ANALIZA STRUKTURY ENWIK")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    # Analizuj pierwszy 1 MB jako próbkę
    print(f"\n[1] Czytanie próbki (1 MB) z: {input_file}")
    with open(input_file, 'rb') as f:
        sample = f.read(1024 * 1024)
    
    print(f"    Rozmiar próbki: {len(sample):,} bajtów")
    
    # Parsuj
    print(f"\n[2] Tokenizacja...")
    parser = WikiParser()
    tokens = parser.tokenize(sample)
    
    print(f"    Znaleziono {len(tokens):,} tokenów")
    
    # Statystyki
    print(f"\n[3] Analiza rozkładu...")
    stats = parser.analyze_structure(sample, max_bytes=len(sample))
    
    print(f"\n    {'Typ tokenu':<20} {'Liczba':<12} {'Bajty':<15} {'% bajtów':<10}")
    print("    " + "-" * 65)
    
    for type_name in sorted(stats['by_type'].keys()):
        count = stats['by_type'][type_name]
        bytes_count = stats['bytes_by_type'][type_name]
        percent = (bytes_count / stats['total_bytes']) * 100
        print(f"    {type_name:<20} {count:<12,} {bytes_count:<15,} {percent:>6.2f}%")
    
    print("    " + "-" * 65)
    print(f"    {'TOTAL':<20} {stats['total_tokens']:<12,} {stats['total_bytes']:<15,} {100.0:>6.2f}%")
    
    # Kanały
    print(f"\n[4] Podział na kanały...")
    channels = parser.tokens_to_channels(tokens)
    
    total_channel_bytes = sum(len(data) for data in channels.values())
    
    print(f"\n    {'Kanał':<20} {'Rozmiar':<15} {'% całości':<10}")
    print("    " + "-" * 50)
    
    for name, data in sorted(channels.items(), key=lambda x: -len(x[1])):
        if data:
            percent = (len(data) / stats['total_bytes']) * 100
            print(f"    {name:<20} {len(data):<15,} {percent:>6.2f}%")
    
    # Przykłady z każdego kanału
    print(f"\n[5] Przykłady z kanałów...")
    
    for name, data in channels.items():
        if len(data) > 0:
            preview = data[:100].decode('utf-8', errors='replace')
            preview = preview.replace('\n', '\\n')
            print(f"\n    {name}:")
            print(f"      {preview}...")
    
    # Wnioski
    print(f"\n{'=' * 70}")
    print("WNIOSKI")
    print("=" * 70)
    
    plain_pct = (stats['bytes_by_type'].get('PLAIN_TEXT', 0) / stats['total_bytes']) * 100
    struct_pct = 100 - plain_pct
    
    print(f"\n• Czysty tekst: {plain_pct:.1f}% danych")
    print(f"• Struktura (linki, nagłówki, XML, etc.): {struct_pct:.1f}%")
    
    if 'LINK' in stats['bytes_by_type']:
        link_pct = (stats['bytes_by_type']['LINK'] / stats['total_bytes']) * 100
        print(f"• Linki zajmują {link_pct:.1f}% - to duży potencjał do specjalizacji!")
    
    if 'HEADING' in stats['bytes_by_type']:
        heading_pct = (stats['bytes_by_type']['HEADING'] / stats['total_bytes']) * 100
        print(f"• Nagłówki: {heading_pct:.1f}%")
    
    print(f"\n💡 Strategia: Osobne modele dla różnych kanałów mogą dać przewagę!")
    print(f"   - Model dla linków (przewidywalne tytuły artykułów)")
    print(f"   - Model dla nagłówków (ograniczony słownik)")
    print(f"   - Model dla czystego tekstu (najlepszy context model)")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
