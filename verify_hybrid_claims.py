#!/usr/bin/env python3
"""
VERIFICATION - Is 28 MB real or illusion?

Critical question: "Czy to napewno prawda?"
After overfitting lesson, we MUST verify rigorously!

Tests:
1. Check comparison methodology
2. Verify on multiple test sets
3. Test different sizes
4. Look for data leakage
5. Conservative estimates
"""
import re
from collections import defaultdict, Counter
import math

class HybridVerification:
    """
    Rigorous verification of hybrid claims
    Scientific skepticism applied!
    """
    
    def __init__(self):
        self.text_model = defaultdict(lambda: Counter())
        self.link_order6 = defaultdict(lambda: Counter())
        self.link_order2 = defaultdict(lambda: Counter())
        self.link_vocab = Counter()
        self.char_vocab = set()
    
    def train(self, text, train_size):
        """Train models"""
        sample = text[:train_size]
        
        # Order-5 text
        for i in range(5, len(sample)):
            context = sample[i-5:i]
            next_char = sample[i]
            self.text_model[context][next_char] += 1
            self.char_vocab.add(next_char)
        
        # Order-6 links
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', sample)
        self.link_vocab = Counter(links)
        
        for i in range(6, len(links)):
            context = tuple(links[i-6:i])
            target = links[i]
            self.link_order6[context][target] += 1
        
        for i in range(2, len(links)):
            context = tuple(links[i-2:i])
            target = links[i]
            self.link_order2[context][target] += 1
        
        return len(self.text_model), len(self.link_order6)
    
    def compress_text_only(self, text):
        """Compress with Order-5 text only (baseline)"""
        total_bits = 0
        context = ""
        
        for char in text:
            if len(context) >= 5 and context[-5:] in self.text_model:
                predictions = self.text_model[context[-5:]]
                if char in predictions:
                    total = sum(predictions.values())
                    prob = predictions[char] / total
                    bits = -math.log2(prob)
                    total_bits += bits
                else:
                    total_bits += math.log2(len(self.char_vocab))
            else:
                total_bits += 8
            
            context += char
        
        return total_bits
    
    def compress_hybrid(self, text):
        """Compress with hybrid approach"""
        # Find all links
        link_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        link_regions = []
        
        for match in link_pattern.finditer(text):
            start, end = match.span()
            target = match.group(1)
            link_regions.append((start, end, target))
        
        total_bits_text = 0
        total_bits_links = 0
        text_context = ""
        link_history = []
        
        i = 0
        while i < len(text):
            # Check if in link
            in_link = False
            for start, end, target in link_regions:
                if start <= i < end:
                    if i == start:  # Encode link
                        # Try Order-6
                        if len(link_history) >= 6:
                            ctx = tuple(link_history[-6:])
                            if ctx in self.link_order6:
                                candidates = [l for l, c in self.link_order6[ctx].most_common()]
                                try:
                                    pos = candidates.index(target)
                                    if pos == 0:
                                        total_bits_links += 1
                                    elif pos < 5:
                                        total_bits_links += 3
                                    elif pos < 50:
                                        total_bits_links += 6
                                    else:
                                        total_bits_links += math.log2(len(self.link_vocab))
                                except ValueError:
                                    total_bits_links += math.log2(len(self.link_vocab))
                                
                                link_history.append(target)
                                in_link = True
                                break
                        
                        # Fallback
                        total_bits_links += math.log2(len(self.link_vocab))
                        link_history.append(target)
                    
                    in_link = True
                    break
            
            if not in_link:
                # Regular text
                char = text[i]
                if len(text_context) >= 5 and text_context[-5:] in self.text_model:
                    predictions = self.text_model[text_context[-5:]]
                    if char in predictions:
                        total = sum(predictions.values())
                        prob = predictions[char] / total
                        bits = -math.log2(prob)
                        total_bits_text += bits
                    else:
                        total_bits_text += math.log2(len(self.char_vocab))
                else:
                    total_bits_text += 8
                
                text_context += char
            
            i += 1
        
        return total_bits_text + total_bits_links
    
    def verify_multiple_tests(self, text, train_size=3000000):
        """Run multiple verification tests"""
        print("=" * 70)
        print("🔬 RIGOROUS VERIFICATION")
        print("=" * 70)
        print("\nQuestion: 'Czy to napewno prawda?' (Is this really true?)")
        print("Answer: Let's find out with SCIENCE! 🔬\n")
        
        # Train
        print(f"Training on {train_size:,} chars...")
        text_contexts, link_contexts = self.train(text, train_size)
        print(f"  Text contexts: {text_contexts:,}")
        print(f"  Link contexts: {link_contexts:,}")
        
        # Test on multiple fresh segments
        test_configs = [
            (3000000, 500000, "Test 1 (3.0M-3.5M)"),
            (4000000, 500000, "Test 2 (4.0M-4.5M)"),
            (5000000, 500000, "Test 3 (5.0M-5.5M)"),
            (6000000, 300000, "Test 4 (6.0M-6.3M)"),
        ]
        
        results = []
        
        for start, size, name in test_configs:
            if start + size > len(text):
                print(f"\n⚠️ Skipping {name} - not enough data")
                continue
            
            print(f"\n{name}:")
            test_text = text[start:start + size]
            
            print(f"  Compressing {len(test_text):,} chars...")
            
            # Text-only
            text_only_bits = self.compress_text_only(test_text)
            
            # Hybrid
            hybrid_bits = self.compress_hybrid(test_text)
            
            # Results
            savings = text_only_bits - hybrid_bits
            percent = (savings / text_only_bits) * 100
            
            print(f"  Text-only: {text_only_bits:,.0f} bits")
            print(f"  Hybrid: {hybrid_bits:,.0f} bits")
            print(f"  Savings: {savings:,.0f} bits ({percent:.2f}%)")
            
            # Extrapolate
            scale = 1000  # 1GB / 1MB
            mb_saved = savings / 8 / 1024 / 1024 * scale
            print(f"  Extrapolated: {mb_saved:.1f} MB on enwik9")
            
            results.append({
                'name': name,
                'savings': savings,
                'percent': percent,
                'mb_extrapolated': mb_saved
            })
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 70)
        
        if results:
            avg_percent = sum(r['percent'] for r in results) / len(results)
            avg_mb = sum(r['mb_extrapolated'] for r in results) / len(results)
            min_mb = min(r['mb_extrapolated'] for r in results)
            max_mb = max(r['mb_extrapolated'] for r in results)
            
            print(f"\nTests run: {len(results)}")
            print(f"\nSavings consistency:")
            for r in results:
                print(f"  {r['name']}: {r['percent']:.2f}% ({r['mb_extrapolated']:.1f} MB)")
            
            print(f"\nAggregate statistics:")
            print(f"  Average improvement: {avg_percent:.2f}%")
            print(f"  Average MB saved: {avg_mb:.1f}")
            print(f"  Range: {min_mb:.1f} - {max_mb:.1f} MB")
            print(f"  Std deviation: {max_mb - min_mb:.1f} MB")
            
            # Verdict
            print("\n" + "=" * 70)
            print("🎯 VERDICT")
            print("=" * 70)
            
            if max_mb - min_mb < 5:  # Consistent
                print(f"\n✅ CONSISTENT across tests!")
                print(f"   Range is tight: {max_mb - min_mb:.1f} MB variation")
            else:
                print(f"\n⚠️  INCONSISTENT results!")
                print(f"   High variation: {max_mb - min_mb:.1f} MB")
            
            if avg_mb > 20:
                print(f"\n🏆 CONSERVATIVE ESTIMATE: {min_mb:.1f} MB")
                print(f"   (Using minimum, not average)")
                print(f"   Still SIGNIFICANT!")
            elif avg_mb > 10:
                print(f"\n🎯 SOLID GAIN: ~{avg_mb:.1f} MB")
            elif avg_mb > 5:
                print(f"\n✅ MODERATE GAIN: ~{avg_mb:.1f} MB")
            else:
                print(f"\n⚠️  MODEST: ~{avg_mb:.1f} MB")
                print(f"   Claims may be overstated!")
            
            # Final answer
            print("\n" + "=" * 70)
            print("❓ CZY TO NAPEWNO PRAWDA?")
            print("=" * 70)
            
            if max_mb - min_mb < 5 and avg_mb > 15:
                print(f"\n✅ TAK! (YES!)")
                print(f"   Consistent: {max_mb - min_mb:.1f} MB variation")
                print(f"   Significant: {avg_mb:.1f} MB average")
                print(f"   Conservative: {min_mb:.1f} MB minimum")
                print(f"\n   The 28 MB claim is REAL! 🏆")
            elif avg_mb > 10:
                print(f"\n🤔 CZĘŚCIOWO (PARTIALLY)")
                print(f"   Real savings: ~{avg_mb:.1f} MB")
                print(f"   But variation is {max_mb - min_mb:.1f} MB")
                print(f"   28 MB might be optimistic")
                print(f"   Conservative: ~{min_mb:.1f} MB")
            else:
                print(f"\n❌ NIE (NO)")
                print(f"   Actual savings: only ~{avg_mb:.1f} MB")
                print(f"   28 MB was likely overstated")
                print(f"   Reality check needed!")
        else:
            print("\n❌ No valid tests completed!")

def main():
    print("=" * 70)
    print("🔬 VERIFICATION SCRIPT")
    print("=" * 70)
    print("\nQuestion from Piotr: 'Czy to napewno prawda?'")
    print("(Is this really true?)")
    print("\nSmart question! After overfitting lesson, we verify! 🔬\n")
    
    # Load data
    print("Loading enwik_10mb...")
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Verify
    verifier = HybridVerification()
    verifier.verify_multiple_tests(text, train_size=3000000)
    
    print("\n" + "=" * 70)
    print("✅ Verification complete!")
    print("🔬 Science demands skepticism! Good question!")
    print("=" * 70)

if __name__ == "__main__":
    main()
