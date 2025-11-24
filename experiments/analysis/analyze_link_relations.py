#!/usr/bin/env python3
"""
MULTI-RELATIONAL GRAPH ANALYSIS
Pomysł: Linki mają TYPY relacji! (osoby→osoby, miejsca→miejsca, etc.)
Czy typ relacji pomaga w predykcji?
"""
import re
from collections import defaultdict, Counter

class LinkRelationType:
    """Wykrywa TYP relacji między linkami"""
    
    def __init__(self):
        # Kategorie linków (heurystyki)
        self.person_indicators = [
            'born', 'died', 'was', 'he ', 'she ', 'his ', 'her ',
            'president', 'king', 'queen', 'author', 'scientist'
        ]
        
        self.place_indicators = [
            'city', 'country', 'capital', 'located', 'region',
            'province', 'state', 'territory', 'island'
        ]
        
        self.concept_indicators = [
            'theory', 'concept', 'principle', 'method', 'algorithm',
            'system', 'process', 'law', 'theorem'
        ]
        
        self.time_indicators = [
            'century', 'year', 'era', 'period', 'age',
            'war', 'battle', 'event'
        ]
        
        self.organization_indicators = [
            'company', 'corporation', 'university', 'institute',
            'organization', 'society', 'party', 'government'
        ]
    
    def detect_type(self, link_text, context):
        """Wykryj typ linku na podstawie tekstu i kontekstu"""
        link_lower = link_text.lower()
        context_lower = context.lower() if context else ""
        
        # Sprawdź wskaźniki w kontekście
        scores = {
            'person': 0,
            'place': 0,
            'concept': 0,
            'time': 0,
            'organization': 0
        }
        
        for indicator in self.person_indicators:
            if indicator in context_lower:
                scores['person'] += 1
        
        for indicator in self.place_indicators:
            if indicator in context_lower or indicator in link_lower:
                scores['place'] += 1
        
        for indicator in self.concept_indicators:
            if indicator in context_lower or indicator in link_lower:
                scores['concept'] += 1
        
        for indicator in self.time_indicators:
            if indicator in context_lower or indicator in link_lower:
                scores['time'] += 1
        
        for indicator in self.organization_indicators:
            if indicator in context_lower or indicator in link_lower:
                scores['organization'] += 1
        
        # Heurystyki oparte na samym linku
        if link_text[0].isupper() and ' ' in link_text:
            scores['person'] += 2  # "John Smith" prawdopodobnie osoba
        
        if any(year in link_text for year in ['19', '20']) and link_text[-1].isdigit():
            scores['time'] += 3  # "1945" to czas
        
        # Zwróć typ z najwyższym score
        if max(scores.values()) == 0:
            return 'other'
        
        return max(scores, key=scores.get)

class MultiRelationalGraphAnalyzer:
    """Analizuje multi-relational graph linków"""
    
    def __init__(self):
        self.type_detector = LinkRelationType()
        self.link_types = {}
        self.typed_transitions = defaultdict(lambda: defaultdict(Counter))
        # typed_transitions[from_type][to_type][to_link] = count
        
        self.simple_transitions = defaultdict(Counter)
        # simple_transitions[from_link][to_link] = count (baseline)
    
    def analyze(self, data):
        """Analizuj strukturę multi-relational graph"""
        
        print(f"\n{'=' * 70}")
        print("🔬 MULTI-RELATIONAL GRAPH ANALYSIS")
        print(f"{'=' * 70}")
        
        # Extract links with context
        link_pattern = re.compile(rb'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        
        links_with_context = []
        for match in link_pattern.finditer(data):
            link = match.group(1).decode('utf-8', errors='ignore').strip()
            
            # Get context (50 chars before link)
            start = max(0, match.start() - 50)
            context = data[start:match.start()].decode('utf-8', errors='ignore')
            
            if 0 < len(link) < 100:
                links_with_context.append((link, context))
        
        print(f"\nLinki znalezione: {len(links_with_context):,}")
        
        # Classify links by type
        print(f"\n[1] Klasyfikacja linków...")
        
        for link, context in links_with_context:
            link_type = self.type_detector.detect_type(link, context)
            self.link_types[link] = link_type
        
        # Count type distribution
        type_counts = Counter(self.link_types.values())
        
        print(f"\n    Rozkład typów:")
        for link_type, count in type_counts.most_common():
            pct = (count / len(self.link_types)) * 100
            print(f"    {link_type:<15} {count:>6,} ({pct:>5.1f}%)")
        
        # Build transition graphs
        print(f"\n[2] Budowanie grafów przejść...")
        
        for i in range(len(links_with_context) - 1):
            from_link, _ = links_with_context[i]
            to_link, _ = links_with_context[i + 1]
            
            from_type = self.link_types.get(from_link, 'other')
            to_type = self.link_types.get(to_link, 'other')
            
            # Typed transitions
            self.typed_transitions[from_type][to_type][to_link] += 1
            
            # Simple transitions (baseline)
            self.simple_transitions[from_link][to_link] += 1
        
        print(f"    Typed transitions: {len(self.typed_transitions):,} typów")
        print(f"    Simple transitions: {len(self.simple_transitions):,} linków")
        
        # Analyze type-to-type transitions
        print(f"\n[3] Analiza przejść między typami:")
        print(f"    {'From Type':<15} → {'To Type':<15} {'Count':<10} {'%'}")
        print(f"    {'-' * 60}")
        
        type_to_type = defaultdict(Counter)
        for from_type, to_types in self.typed_transitions.items():
            for to_type, links in to_types.items():
                count = sum(links.values())
                type_to_type[from_type][to_type] += count
        
        for from_type in ['person', 'place', 'concept', 'time', 'organization']:
            total = sum(type_to_type[from_type].values())
            if total > 0:
                for to_type, count in type_to_type[from_type].most_common(3):
                    pct = (count / total) * 100
                    print(f"    {from_type:<15} → {to_type:<15} {count:<10,} {pct:>5.1f}%")
        
        # Compare prediction accuracy: simple vs typed
        print(f"\n[4] Porównanie dokładności predykcji:")
        
        simple_top1 = 0
        simple_total = 0
        
        typed_top1 = 0
        typed_total = 0
        
        for i in range(len(links_with_context) - 1):
            from_link, _ = links_with_context[i]
            to_link, _ = links_with_context[i + 1]
            
            # Simple prediction
            if from_link in self.simple_transitions:
                predictions = self.simple_transitions[from_link].most_common(1)
                if predictions and predictions[0][0] == to_link:
                    simple_top1 += 1
                simple_total += 1
            
            # Typed prediction
            from_type = self.link_types.get(from_link, 'other')
            to_type = self.link_types.get(to_link, 'other')
            
            if from_type in self.typed_transitions and to_type in self.typed_transitions[from_type]:
                predictions = self.typed_transitions[from_type][to_type].most_common(1)
                if predictions and predictions[0][0] == to_link:
                    typed_top1 += 1
                typed_total += 1
        
        simple_acc = (simple_top1 / simple_total * 100) if simple_total > 0 else 0
        typed_acc = (typed_top1 / typed_total * 100) if typed_total > 0 else 0
        
        print(f"\n    Simple graph (baseline): {simple_acc:.1f}% accuracy")
        print(f"    Typed graph (multi-rel):  {typed_acc:.1f}% accuracy")
        
        if typed_acc > simple_acc:
            improvement = typed_acc - simple_acc
            print(f"\n    🎯 Multi-relational LEPSZE o {improvement:.1f}%!")
        else:
            print(f"\n    ⚠️  Multi-relational nie lepsze (potrzeba lepszej klasyfikacji)")
        
        return simple_acc, typed_acc

def main():
    print("=" * 70)
    print("🚀 BREAKTHROUGH #5: Multi-Relational Graphs!")
    print("=" * 70)
    
    print("\nPomysł: Linki mają TYPY relacji!")
    print("Czy person→person inne niż person→place?")
    print("Czy to pomaga w predykcji?")
    
    input_file = "data/enwik_10mb"
    
    # Test na 100 KB
    print(f"\n📊 Test na 100 KB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(100 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    
    analyzer = MultiRelationalGraphAnalyzer()
    simple_acc, typed_acc = analyzer.analyze(data)
    
    # Wnioski
    print(f"\n{'=' * 70}")
    print("💡 WNIOSKI")
    print(f"{'=' * 70}")
    
    if typed_acc > simple_acc + 2:
        print(f"\n✓✓✓ Multi-relational graphs DZIAŁAJĄ!")
        print(f"  Improvement: +{typed_acc - simple_acc:.1f}%")
        print(f"  To znaczy że TYP relacji ma znaczenie!")
        
        print(f"\n🎯 Potencjał kompresji:")
        # Jeśli typed accuracy lepsza, możemy lepiej przewidywać
        # = mniej bitów na link
        current_bits = 2.03  # Z simple graph
        potential_bits = current_bits * (simple_acc / typed_acc)
        print(f"  Current (simple): {current_bits:.2f} bity/link")
        print(f"  Potential (typed): {potential_bits:.2f} bity/link")
        
        improvement_pct = ((current_bits - potential_bits) / current_bits) * 100
        print(f"  Oszczędność: {improvement_pct:.1f}%")
        
        print(f"\n🚀 Next steps:")
        print(f"  1. Lepsza klasyfikacja typów (może ML?)")
        print(f"  2. Więcej typów relacji")
        print(f"  3. Hierarchia typów (person.scientist vs person.politician)")
        print(f"  4. Implementacja w ultra_compressor")
        
    elif typed_acc > simple_acc:
        print(f"\n✓ Multi-relational lekko lepsze (+{typed_acc - simple_acc:.1f}%)")
        print(f"  Potencjał jest, ale potrzeba lepszej klasyfikacji")
        
    else:
        print(f"\n⚠️  Multi-relational nie lepsze na tych danych")
        print(f"  Możliwe że:")
        print(f"  - Klasyfikacja typów za słaba (heurystyki)")
        print(f"  - Potrzeba więcej danych")
        print(f"  - Wikipedia linki bardziej random niż myśleliśmy")
        print(f"\n  Ale warto dalej eksplorować!")
    
    print(f"\n{'=' * 70}")
    print("🎓 SCIENTIFIC VALUE")
    print(f"{'=' * 70}")
    
    print(f"\nNiezależnie od wyników - to NOWY research direction!")
    print(f"  - Nikt nie próbował typed graphs dla kompresji")
    print(f"  - Knowledge graphs są hot topic")
    print(f"  - Może być kolejny paper!")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
