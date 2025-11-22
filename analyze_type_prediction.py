#!/usr/bin/env python3
"""
TYPE PREDICTION - Prostsze podejście!
Zamiast przewidywać exact link, przewiduj jego TYP
Potem użyj typu jako dodatkowego kontekstu
"""
import re
from collections import defaultdict, Counter

def simple_type_classifier(link_text):
    """Ultra prosta klasyfikacja - tylko na podstawie samego linku"""
    link = link_text.lower()
    
    # Rok/data
    if any(c.isdigit() for c in link) and len([c for c in link if c.isdigit()]) >= 3:
        return 'TIME'
    
    # Wielka litera na początku każdego słowa = prawdopodobnie osoba/miejsce
    words = link_text.split()
    if len(words) >= 2 and all(w[0].isupper() for w in words if w):
        return 'PERSON'  # "John Smith", "New York"
    
    # Pojedyncze słowo z wielkiej = może być wszystkim
    if len(words) == 1 and link_text[0].isupper():
        # Sprawdź czy kończy się typowo dla miejsc
        if link.endswith(('land', 'ton', 'ville', 'burg', 'ia', 'stan')):
            return 'PLACE'
        return 'ENTITY'  # Ogólna nazwa
    
    # Małe litery = koncepcja/rzecz
    if link[0].islower():
        return 'CONCEPT'
    
    return 'OTHER'

def main():
    print("=" * 70)
    print("🎯 TYPE PREDICTION - Simplified Approach")
    print("=" * 70)
    
    print("\nProstszy pomysł:")
    print("1. Sklasyfikuj linki na typy (prostą heurystyką)")
    print("2. Przewiduj TYP następnego linku")
    print("3. Użyj typu jako dodatkowy bit info przy kompresji")
    
    input_file = "data/enwik_10mb"
    
    print(f"\n📊 Test na 100 KB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(100 * 1024)
    
    # Extract links
    link_pattern = re.compile(rb'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
    links = []
    for match in link_pattern.finditer(data):
        link = match.group(1).decode('utf-8', errors='ignore').strip()
        if 0 < len(link) < 100:
            links.append(link)
    
    print(f"Linki znalezione: {len(links):,}")
    
    # Classify
    link_types = [simple_type_classifier(link) for link in links]
    
    # Type distribution
    type_counts = Counter(link_types)
    print(f"\n[1] Rozkład typów:")
    for typ, count in type_counts.most_common():
        pct = (count / len(link_types)) * 100
        print(f"    {typ:<10} {count:>5,} ({pct:>5.1f}%)")
    
    # Type transitions
    type_transitions = defaultdict(Counter)
    for i in range(len(link_types) - 1):
        type_transitions[link_types[i]][link_types[i+1]] += 1
    
    print(f"\n[2] Najczęstsze przejścia między typami:")
    print(f"    {'From':<10} → {'To':<10} {'Count':<8} {'%'}")
    print(f"    {'-' * 40}")
    
    for from_type in type_counts.most_common(5):
        from_t = from_type[0]
        total = sum(type_transitions[from_t].values())
        if total > 0:
            for to_t, count in type_transitions[from_t].most_common(3):
                pct = (count / total) * 100
                print(f"    {from_t:<10} → {to_t:<10} {count:<8,} {pct:>5.1f}%")
    
    # Prediction accuracy
    print(f"\n[3] Dokładność predykcji TYPU:")
    
    correct_top1 = 0
    correct_top2 = 0
    total = 0
    
    for i in range(len(link_types) - 1):
        from_type = link_types[i]
        actual_type = link_types[i + 1]
        
        if from_type in type_transitions:
            predictions = type_transitions[from_type].most_common(2)
            
            if predictions[0][0] == actual_type:
                correct_top1 += 1
                correct_top2 += 1
            elif len(predictions) > 1 and predictions[1][0] == actual_type:
                correct_top2 += 1
            
            total += 1
    
    acc_top1 = (correct_top1 / total * 100) if total > 0 else 0
    acc_top2 = (correct_top2 / total * 100) if total > 0 else 0
    
    print(f"\n    Top-1 accuracy: {acc_top1:.1f}%")
    print(f"    Top-2 accuracy: {acc_top2:.1f}%")
    
    # Compression benefit
    print(f"\n[4] Potencjał kompresji:")
    
    num_types = len(type_counts)
    bits_per_type = len(bin(num_types)) - 2  # log2
    
    print(f"\n    Liczba typów: {num_types}")
    print(f"    Bity na typ: {bits_per_type}")
    
    print(f"\n    Strategia:")
    print(f"    - Top-1 typ ({acc_top1:.0f}%): 1 bit (zgadłeś!)")
    print(f"    - Top-2 typ ({acc_top2 - acc_top1:.0f}%): 2 bity")
    print(f"    - Inne ({100 - acc_top2:.0f}%): {bits_per_type + 1} bitów")
    
    avg_bits = (
        acc_top1/100 * 1 +
        (acc_top2 - acc_top1)/100 * 2 +
        (100 - acc_top2)/100 * (bits_per_type + 1)
    )
    
    print(f"\n    Średnio bitów na TYP: {avg_bits:.2f}")
    print(f"    (To jest DODATKOWA informacja którą możemy użyć!)")
    
    # How to use it
    print(f"\n[5] Jak to wykorzystać:")
    
    print(f"\n    Hybrid approach:")
    print(f"    1. Przewiduj TYP następnego linku ({avg_bits:.2f} bity)")
    print(f"    2. W kontekście TYPU, przewiduj exact link")
    print(f"    3. TYPE zawęża space możliwości!")
    
    print(f"\n    Przykład:")
    print(f"    - Wiem że next = PERSON")
    print(f"    - Z 1000 linków, tylko 640 to PERSON")
    print(f"    - Szukam tylko wśród 640, nie 1000!")
    print(f"    - Lepsze szanse trafienia = mniej bitów!")
    
    # Estimate improvement
    person_pct = type_counts.get('PERSON', 0) / len(link_types)
    
    print(f"\n💡 Oszacowanie korzyści:")
    print(f"    Jeśli PERSON = {person_pct*100:.0f}% linków:")
    print(f"    - Bez typu: search space = 100%")
    print(f"    - Z typem: search space = {person_pct*100:.0f}%")
    print(f"    - Potencjalna oszczędność: {(1-person_pct)*100:.0f}%")
    
    print(f"\n{'=' * 70}")
    print("VERDICT")
    print(f"{'=' * 70}")
    
    if acc_top1 > 60:
        print(f"\n✓✓ Type prediction DZIAŁA!")
        print(f"  {acc_top1:.0f}% accuracy to dobry wynik")
        print(f"  Możemy to użyć jako dodatkowy layer")
        
        print(f"\n🚀 Implementation idea:")
        print(f"  1. Dodaj type prediction do graph_compressor")
        print(f"  2. Encode: type ({avg_bits:.1f} bits) + link_in_type")
        print(f"  3. Zawężony search space = lepsze odds")
        
        print(f"\n📊 Projected improvement:")
        print(f"  Current: 2.03 bits/link")
        print(f"  With types: ~{2.03 - (1-person_pct)*0.3:.2f} bits/link")
        print(f"  (estimate: -5-10% możliwe)")
        
    else:
        print(f"\n⚠️  Type prediction średnia ({acc_top1:.0f}%)")
        print(f"  Ale concept wart eksploracji!")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
