#!/usr/bin/env python3
"""
Prosta i szybka analiza struktury enwik bez złożonych regex
"""
import time

def quick_analyze(data, chunk_size=1000):
    """
    Szybka analiza bez regex - liczy proste wzorce
    """
    print(f"Analizowanie {len(data):,} bajtów...")
    
    stats = {
        'total_bytes': len(data),
        'newlines': 0,
        'xml_tags': 0,
        'links': 0,           # [[...]]
        'templates': 0,       # {{...}}
        'headings': 0,        # == ... ==
        'entities': 0,        # &...;
        'plain_bytes': 0
    }
    
    i = 0
    start_time = time.time()
    last_report = 0
    
    while i < len(data):
        # Progress
        if i - last_report > 100000:
            pct = (i / len(data)) * 100
            elapsed = time.time() - start_time
            speed = i / (1024 * 1024 * elapsed) if elapsed > 0 else 0
            print(f"  Postęp: {pct:.1f}% ({speed:.1f} MB/s)", end='\r')
            last_report = i
        
        # Sprawdź wzorce
        if i < len(data) - 1:
            two_ch = data[i:i+2]
            
            # Link [[
            if two_ch == b'[[':
                stats['links'] += 1
                # Przewiń do ]]
                end = data.find(b']]', i + 2)
                if end != -1:
                    i = end + 2
                    continue
                else:
                    i += 2
                    continue
            
            # Template {{
            elif two_ch == b'{{':
                stats['templates'] += 1
                end = data.find(b'}}', i + 2)
                if end != -1:
                    i = end + 2
                    continue
                else:
                    i += 2
                    continue
            
            # Heading ==
            elif two_ch == b'==':
                stats['headings'] += 1
                # Zlicz = z rzędu
                j = i
                while j < len(data) and data[j:j+1] == b'=':
                    j += 1
                i = j
                continue
        
        # Single char patterns
        ch = data[i:i+1]
        
        if ch == b'\n':
            stats['newlines'] += 1
        elif ch == b'<':
            stats['xml_tags'] += 1
        elif ch == b'&':
            stats['entities'] += 1
        else:
            stats['plain_bytes'] += 1
        
        i += 1
    
    elapsed = time.time() - start_time
    print(f"\n  Ukończono w {elapsed:.2f} s ({len(data) / (1024*1024*elapsed):.1f} MB/s)")
    
    return stats

def main():
    print("=" * 70)
    print("SZYBKA ANALIZA STRUKTURY ENWIK")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    # Analizuj pierwszy 1 MB
    print(f"\n[1] Czytanie 1 MB próbki z: {input_file}")
    with open(input_file, 'rb') as f:
        sample = f.read(1024 * 1024)
    
    print(f"    Rozmiar: {len(sample):,} bajtów")
    
    # Analiza
    print(f"\n[2] Analiza wzorców...")
    stats = quick_analyze(sample)
    
    # Wyniki
    print(f"\n{'=' * 70}")
    print("WYNIKI")
    print("=" * 70)
    
    total = stats['total_bytes']
    
    print(f"\n{'Wzorzec':<20} {'Liczba':<15} {'% bajtów':<10}")
    print("-" * 50)
    
    print(f"{'Linki [[...]]':<20} {stats['links']:<15,} {'-':<10}")
    print(f"{'Templates {{{...}}}':<20} {stats['templates']:<15,} {'-':<10}")
    print(f"{'Nagłówki ==':<20} {stats['headings']:<15,} {'-':<10}")
    print(f"{'XML tagi <':<20} {stats['xml_tags']:<15,} {'-':<10}")
    print(f"{'Entities &':<20} {stats['entities']:<15,} {'-':<10}")
    print(f"{'Newlines':<20} {stats['newlines']:<15,} {(stats['newlines']/total*100):>6.2f}%")
    print(f"{'Zwykły tekst':<20} {stats['plain_bytes']:<15,} {(stats['plain_bytes']/total*100):>6.2f}%")
    
    print("-" * 50)
    print(f"{'TOTAL':<20} {total:<15,} {100.0:>6.2f}%")
    
    # Wnioski
    print(f"\n{'=' * 70}")
    print("WNIOSKI")
    print("=" * 70)
    
    plain_pct = (stats['plain_bytes'] / total) * 100
    struct_pct = 100 - plain_pct
    
    print(f"\n• Czysty tekst: {plain_pct:.1f}%")
    print(f"• Struktura (markup): {struct_pct:.1f}%")
    print(f"• Linków wiki: {stats['links']:,}")
    print(f"• Nagłówków: {stats['headings']:,}")
    print(f"• Templates: {stats['templates']:,}")
    
    print(f"\n💡 STRATEGIA wielokanałowa:")
    print(f"   1. Osobny model dla linków (przewidywalne tytuły)")
    print(f"   2. Osobny model dla nagłówków (ograniczony słownik)")
    print(f"   3. Główny Order-3 dla czystego tekstu")
    print(f"   4. Kompresja struktury markup (XML, entities)")
    
    avg_link_spacing = total / stats['links'] if stats['links'] > 0 else 0
    print(f"\n📊 Link co ~{avg_link_spacing:.0f} bajtów - duży potencjał!")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
