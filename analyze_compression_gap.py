#!/usr/bin/env python3
"""
COMPRESSION GAP ANALYSIS - Where's the 20 MB?

Current: 134.7 MB (TOP-10)
Target: 114 MB (World Record)
Gap: 20.7 MB

Let's find WHERE this gap is and WHAT to attack next! 🎯
"""
import re
from collections import Counter, defaultdict
import numpy as np

class CompressionGapAnalyzer:
    """
    Analyze where compression savings are still possible
    """
    
    def __init__(self):
        self.stats = {}
        
    def extract_all_content(self, text):
        """Extract and categorize all content types"""
        print("=" * 70)
        print("📊 EXTRACTING CONTENT TYPES")
        print("=" * 70)
        
        # 1. Links
        link_pattern = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
        links = link_pattern.findall(text)
        link_texts = [(target, display if display else target) for target, display in links]
        
        print(f"\n1️⃣ Links: {len(links):,}")
        print(f"   Unique targets: {len(set([t for t, d in link_texts])):,}")
        print(f"   With display text: {sum(1 for t, d in link_texts if t != d):,}")
        
        # 2. Templates
        template_pattern = re.compile(r'\{\{([^}]+)\}\}')
        templates = template_pattern.findall(text)
        
        print(f"\n2️⃣ Templates: {len(templates):,}")
        print(f"   Unique: {len(set(templates)):,}")
        
        # 3. XML Tags
        tag_pattern = re.compile(r'<([^>]+)>')
        tags = tag_pattern.findall(text)
        
        print(f"\n3️⃣ XML Tags: {len(tags):,}")
        print(f"   Unique: {len(set(tags)):,}")
        
        # 4. Remove all structured content to see raw text
        text_only = text
        text_only = link_pattern.sub('', text_only)
        text_only = template_pattern.sub('', text_only)
        text_only = tag_pattern.sub('', text_only)
        
        # 5. Analyze text
        words = re.findall(r'\w+', text_only.lower())
        
        print(f"\n4️⃣ Raw Text:")
        print(f"   Words: {len(words):,}")
        print(f"   Unique words: {len(set(words)):,}")
        print(f"   Characters: {len(text_only):,}")
        
        # 6. Numbers
        numbers = re.findall(r'\b\d+\b', text)
        
        print(f"\n5️⃣ Numbers: {len(numbers):,}")
        print(f"   Unique: {len(set(numbers)):,}")
        
        # 7. Dates (years)
        years = [n for n in numbers if len(n) == 4 and n.startswith(('1', '2'))]
        
        print(f"\n6️⃣ Years: {len(years):,}")
        print(f"   Unique: {len(set(years)):,}")
        
        return {
            'links': links,
            'link_texts': link_texts,
            'templates': templates,
            'tags': tags,
            'words': words,
            'numbers': numbers,
            'years': years,
            'text_only': text_only,
        }
    
    def estimate_current_compression(self, data):
        """Estimate current compression for each component"""
        print("\n" + "=" * 70)
        print("💾 CURRENT COMPRESSION ESTIMATES")
        print("=" * 70)
        
        estimates = {}
        
        # Links (we know this: bi-gram = 15.6 KB, Order-6 = 14.9 KB)
        estimates['links'] = {
            'current': 15.6,  # KB
            'order6': 14.9,
            'potential_saved': 0.7,
            'note': 'Already highly optimized (97.8% → 100% accuracy)'
        }
        
        # Templates (current: 10.4 KB)
        templates_unique = len(set(data['templates']))
        templates_total = len(data['templates'])
        templates_entropy = self.estimate_entropy(data['templates'])
        
        estimates['templates'] = {
            'current': 10.4,  # KB
            'ideal_entropy': templates_entropy * templates_total / 8 / 1024,
            'potential_saved': 10.4 - (templates_entropy * templates_total / 8 / 1024),
            'note': f'{templates_unique:,} unique, entropy {templates_entropy:.2f} bits'
        }
        
        # XML Tags (current: ~3.6 KB for sections)
        tags_entropy = self.estimate_entropy(data['tags'])
        
        estimates['tags'] = {
            'current': 3.6,
            'ideal_entropy': tags_entropy * len(data['tags']) / 8 / 1024,
            'potential_saved': 3.6 - (tags_entropy * len(data['tags']) / 8 / 1024),
            'note': f'Mostly structural, limited savings'
        }
        
        # Text (Order-5 PPM: ~1.45 MB on 10 MB)
        # This is 98% of the data!
        text_bytes = len(data['text_only'].encode('utf-8', errors='ignore'))
        text_current_ratio = 1.45 / 10  # 14.5% compression
        
        estimates['text'] = {
            'current': 1450,  # KB (on 10 MB)
            'current_ratio': text_current_ratio,
            'note': 'Order-5 PPM, main compression target (98% of data!)'
        }
        
        print("\n📊 Component-wise estimates (10 MB test data):")
        
        for component, est in estimates.items():
            print(f"\n{component.upper()}:")
            print(f"  Current: {est['current']:.1f} KB")
            if 'ideal_entropy' in est:
                print(f"  Ideal (entropy): {est['ideal_entropy']:.1f} KB")
            if 'potential_saved' in est:
                print(f"  Potential saved: {est['potential_saved']:.1f} KB")
            print(f"  Note: {est['note']}")
        
        return estimates
    
    def estimate_entropy(self, items):
        """Estimate Shannon entropy in bits"""
        if not items:
            return 0
        
        counter = Counter(items)
        total = len(items)
        
        entropy = 0
        for count in counter.values():
            prob = count / total
            entropy -= prob * np.log2(prob)
        
        return entropy
    
    def analyze_text_patterns(self, text):
        """Deep dive into text compression opportunities"""
        print("\n" + "=" * 70)
        print("🔍 TEXT PATTERN ANALYSIS")
        print("=" * 70)
        
        # Character-level analysis
        char_freq = Counter(text)
        total_chars = len(text)
        
        # Most common characters
        print("\n📝 Character Distribution:")
        print("  Top 10 characters:")
        for char, count in char_freq.most_common(10):
            pct = count / total_chars * 100
            print(f"    '{char}': {count:,} ({pct:.1f}%)")
        
        # Space vs non-space
        spaces = char_freq.get(' ', 0)
        non_spaces = total_chars - spaces
        print(f"\n  Spaces: {spaces:,} ({spaces/total_chars*100:.1f}%)")
        print(f"  Non-spaces: {non_spaces:,} ({non_spaces/total_chars*100:.1f}%)")
        
        # Character entropy
        char_entropy = self.estimate_entropy(list(text))
        print(f"\n  Character entropy: {char_entropy:.3f} bits/char")
        print(f"  Theoretical limit: {total_chars * char_entropy / 8 / 1024:.1f} KB")
        print(f"  (But context models do much better!)")
        
        # N-gram analysis
        print("\n📊 N-gram Analysis:")
        
        # Bigrams
        bigrams = [text[i:i+2] for i in range(len(text)-1)]
        bigram_entropy = self.estimate_entropy(bigrams)
        print(f"  Bi-gram entropy: {bigram_entropy:.3f} bits/char")
        
        # Trigrams
        trigrams = [text[i:i+3] for i in range(len(text)-2)]
        trigram_entropy = self.estimate_entropy(trigrams)
        print(f"  Tri-gram entropy: {trigram_entropy:.3f} bits/char")
        
        # 5-grams (our current Order-5)
        fivegrams = [text[i:i+5] for i in range(len(text)-4)]
        fivegram_entropy = self.estimate_entropy(fivegrams)
        print(f"  5-gram entropy: {fivegram_entropy:.3f} bits/char")
        
        print("\n  → Context models capture these patterns!")
        print("  → Order-5 PPM uses up to 5 chars of context")
        
        return {
            'char_entropy': char_entropy,
            'bigram_entropy': bigram_entropy,
            'trigram_entropy': trigram_entropy,
            'fivegram_entropy': fivegram_entropy,
        }
    
    def identify_opportunities(self, data, estimates, text_stats):
        """Identify where the 20 MB gap is"""
        print("\n" + "=" * 70)
        print("🎯 WHERE IS THE 20 MB GAP?")
        print("=" * 70)
        
        print("\nCurrent state (extrapolated to 1 GB):")
        print("  Total: 134.7 MB")
        print("  Target: 114.0 MB")
        print("  Gap: 20.7 MB")
        
        print("\n📊 Gap breakdown:")
        
        # Text is 98% of data, so 98% of gap
        text_gap = 20.7 * 0.98
        print(f"\n1️⃣ TEXT (98% of data):")
        print(f"  Current: ~131.9 MB")
        print(f"  Gap contribution: ~{text_gap:.1f} MB")
        print(f"  Current: Order-5 PPM")
        print(f"  Opportunities:")
        print(f"    • Order-6 context (6-char lookback)")
        print(f"    • Order-7+ context (diminishing returns?)")
        print(f"    • Secondary models (capitalization, digits)")
        print(f"    • Specialized models (XML, templates)")
        print(f"    • Modern: Neural/transformer models")
        
        # Links
        link_gap = estimates['links']['potential_saved'] * 100  # Scale to 1 GB
        print(f"\n2️⃣ LINKS (1% of data):")
        print(f"  Current: ~1.56 MB (bi-gram)")
        print(f"  Gap contribution: ~{link_gap/1024:.2f} MB")
        print(f"  Opportunities:")
        print(f"    • Order-6: saves ~65 KB ✓ (already tested!)")
        print(f"    • Graph-based prediction")
        print(f"    • Semantic embeddings")
        
        # Templates
        template_gap = estimates['templates']['potential_saved'] * 100 / 1024
        print(f"\n3️⃣ TEMPLATES (1% of data):")
        print(f"  Current: ~1.04 MB")
        print(f"  Gap contribution: ~{template_gap:.2f} MB")
        print(f"  Opportunities:")
        print(f"    • Template grammar compression")
        print(f"    • Parameter prediction")
        print(f"    • Pattern mining")
        
        print("\n" + "=" * 70)
        print("💡 PRIORITIZED TARGETS")
        print("=" * 70)
        
        print("\n🥇 HIGHEST PRIORITY: TEXT COMPRESSION")
        print(f"  Potential: ~{text_gap:.1f} MB (98% of gap!)")
        print("  Current: Order-5 PPM")
        print("  Next steps:")
        print("    1. Test Order-6 text compression")
        print("    2. Analyze what Order-5 misses")
        print("    3. Add specialized models")
        print("    4. Consider neural approaches")
        
        print("\n🥈 MEDIUM PRIORITY: STRUCTURED ELEMENTS")
        print(f"  Potential: ~0.5 MB (2% of gap)")
        print("  Elements: Links, templates, tags")
        print("  Next steps:")
        print("    1. Implement Order-6 links (65 KB known gain)")
        print("    2. Improve template compression")
        print("    3. Better XML tag encoding")
        
        print("\n🥉 LOWER PRIORITY: EXOTIC APPROACHES")
        print("  Potential: Unknown")
        print("  Ideas:")
        print("    • Dictionary learning")
        print("    • Preprocessing (normalization)")
        print("    • Post-processing (bit-packing)")
        
        return {
            'text_gap': text_gap,
            'link_gap': link_gap / 1024,
            'template_gap': template_gap,
        }
    
    def recommend_next_experiments(self, gaps):
        """Recommend what to test next"""
        print("\n" + "=" * 70)
        print("🚀 RECOMMENDED NEXT EXPERIMENTS")
        print("=" * 70)
        
        experiments = [
            {
                'name': 'Order-6 Text Compression',
                'target': 'Text (98% of data)',
                'potential': f'~{gaps["text_gap"] * 0.1:.1f} MB (10% of text gap)',
                'effort': 'High (slow, complex)',
                'priority': 'HIGH',
                'rationale': 'Text is 98% of data. Even 1% improvement = 1.3 MB!',
            },
            {
                'name': 'Context Mixing',
                'target': 'Text (blending multiple models)',
                'potential': f'~{gaps["text_gap"] * 0.15:.1f} MB (15% of text gap)',
                'effort': 'Very High',
                'priority': 'HIGH',
                'rationale': 'PAQ/cmix use this. Proven approach.',
            },
            {
                'name': 'Implement Order-6 Links',
                'target': 'Links',
                'potential': '~65 KB (tested!)',
                'effort': 'Low (already tested)',
                'priority': 'QUICK WIN',
                'rationale': '100% accuracy achieved. Just implement it!',
            },
            {
                'name': 'Template Grammar',
                'target': 'Templates',
                'potential': f'~{gaps["template_gap"] * 0.3:.2f} MB',
                'effort': 'Medium',
                'priority': 'MEDIUM',
                'rationale': 'Templates have structure. Could exploit it.',
            },
            {
                'name': 'Analyze Order-5 Failures',
                'target': 'Text (specific patterns)',
                'potential': 'Unknown (diagnostic)',
                'effort': 'Low',
                'priority': 'DIAGNOSTIC',
                'rationale': 'Find what Order-5 misses, fix specifically.',
            },
        ]
        
        for i, exp in enumerate(experiments, 1):
            print(f"\n{i}. {exp['name']}")
            print(f"   Priority: {exp['priority']}")
            print(f"   Target: {exp['target']}")
            print(f"   Potential: {exp['potential']}")
            print(f"   Effort: {exp['effort']}")
            print(f"   Rationale: {exp['rationale']}")
        
        print("\n" + "=" * 70)
        print("🎯 TONIGHT'S RECOMMENDATION")
        print("=" * 70)
        
        print("\n💡 Quick Win: Implement Order-6 Links")
        print("   • Already tested (100% accuracy)")
        print("   • Known savings (~65 KB)")
        print("   • Low effort")
        print("   • Can do in 1 hour!")
        
        print("\n🔬 Research: Analyze Order-5 Text Failures")
        print("   • Find specific patterns Order-5 misses")
        print("   • Could lead to targeted improvements")
        print("   • Medium effort")
        print("   • High learning value")
        
        print("\n🧪 Ambitious: Test Order-6 Text Compression")
        print("   • Text is 98% of data")
        print("   • Even small % = big MB!")
        print("   • High effort (slow to run)")
        print("   • But highest potential impact!")

def main():
    print("=" * 70)
    print("🌙 NIGHT SESSION: COMPRESSION GAP ANALYSIS")
    print("=" * 70)
    print("\nWhere is the 20 MB gap? Let's find out! 🔍\n")
    
    # Load data
    print("Loading enwik_10mb...")
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Analyze
    analyzer = CompressionGapAnalyzer()
    
    content_data = analyzer.extract_all_content(text)
    estimates = analyzer.estimate_current_compression(content_data)
    text_stats = analyzer.analyze_text_patterns(content_data['text_only'])
    gaps = analyzer.identify_opportunities(content_data, estimates, text_stats)
    analyzer.recommend_next_experiments(gaps)
    
    print("\n" + "=" * 70)
    print("✨ Gap analysis complete!")
    print("🎯 Now we know where to focus! 🚀")
    print("=" * 70)

if __name__ == "__main__":
    main()
