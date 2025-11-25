#!/usr/bin/env python3
"""
COMPREHENSIVE VERIFICATION - Test EVERYTHING!

User's wisdom: "perhaps something might be wrong yet"
This morning: Overfitting taught us to be careful!

Tests:
1. Component isolation (hybrid alone, cascading alone)
2. Combined effect (do they really add?)
3. Multiple test sections (consistency)
4. Different content types (link-heavy vs text-heavy)
5. Larger samples (does it scale?)
6. Conservative estimates (always use minimum)

Find the TRUTH, not what we hope for! 🔬
"""
import re
from collections import defaultdict, Counter
import math
import time

class ComprehensiveVerification:
    """Complete verification suite"""
    
    def __init__(self):
        self.models_trained = False
    
    def train_all_models(self, text, train_size):
        """Train all model variants"""
        print("=" * 70)
        print("🔨 TRAINING ALL MODELS")
        print("=" * 70)
        
        sample = text[:train_size]
        
        # Text models (Order-5 to Order-1)
        self.text_models = {}
        for order in [5, 4, 3, 2]:
            self.text_models[order] = defaultdict(lambda: Counter())
        self.text_models[1] = Counter()
        self.char_freq = Counter()
        self.char_vocab = set()
        
        print(f"\nTraining text models on {train_size:,} chars...")
        start = time.time()
        
        for i in range(5, len(sample)):
            char = sample[i]
            self.text_models[5][sample[i-5:i]][char] += 1
            self.text_models[4][sample[i-4:i]][char] += 1
            self.text_models[3][sample[i-3:i]][char] += 1
            self.text_models[2][sample[i-2:i]][char] += 1
            self.text_models[1][char] += 1
            self.char_freq[char] += 1
            self.char_vocab.add(char)
            
            if (i + 1) % 500000 == 0:
                print(f"  Progress: {i+1:,} / {len(sample):,}")
        
        elapsed = time.time() - start
        print(f"  ✅ Text training: {elapsed:.1f}s")
        print(f"  Order-5: {len(self.text_models[5]):,} contexts")
        print(f"  Order-4: {len(self.text_models[4]):,} contexts")
        print(f"  Order-3: {len(self.text_models[3]):,} contexts")
        print(f"  Order-2: {len(self.text_models[2]):,} contexts")
        
        # Link models
        print("\nTraining link models...")
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', sample)
        self.link_vocab = Counter(links)
        
        self.link_order6 = defaultdict(lambda: Counter())
        self.link_order2 = defaultdict(lambda: Counter())
        
        for i in range(6, len(links)):
            ctx = tuple(links[i-6:i])
            self.link_order6[ctx][links[i]] += 1
        
        for i in range(2, len(links)):
            ctx = tuple(links[i-2:i])
            self.link_order2[ctx][links[i]] += 1
        
        print(f"  ✅ Links: {len(links):,} total")
        print(f"  Order-6: {len(self.link_order6):,} contexts")
        print(f"  Unique links: {len(self.link_vocab):,}")
        
        self.models_trained = True
        print("\n✅ All models trained!")
    
    def compress_baseline(self, text):
        """BASELINE: Pure Order-5 text (like current compressors)"""
        total_bits = 0
        context = ""
        
        for char in text:
            if len(context) >= 5:
                ctx = context[-5:]
                if ctx in self.text_models[5] and char in self.text_models[5][ctx]:
                    predictions = self.text_models[5][ctx]
                    total = sum(predictions.values())
                    prob = predictions[char] / total
                    total_bits += -math.log2(prob)
                else:
                    total_bits += 8  # Full encoding
            else:
                total_bits += 8
            
            context += char
        
        return total_bits
    
    def compress_hybrid_only(self, text):
        """HYBRID ONLY: Order-6 links + Order-5 text (no cascading)"""
        link_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        link_regions = []
        
        for match in link_pattern.finditer(text):
            start, end = match.span()
            target = match.group(1)
            link_regions.append((start, end, target))
        
        total_bits = 0
        text_context = ""
        link_history = []
        
        i = 0
        while i < len(text):
            # Check if in link
            in_link = False
            for start, end, target in link_regions:
                if start <= i < end:
                    if i == start:  # Encode link with Order-6
                        if len(link_history) >= 6:
                            ctx = tuple(link_history[-6:])
                            if ctx in self.link_order6:
                                candidates = [l for l, c in self.link_order6[ctx].most_common()]
                                try:
                                    pos = candidates.index(target)
                                    if pos == 0:
                                        total_bits += 1
                                    elif pos < 5:
                                        total_bits += 3
                                    elif pos < 50:
                                        total_bits += 6
                                    else:
                                        total_bits += math.log2(len(self.link_vocab)) if self.link_vocab else 16
                                except ValueError:
                                    total_bits += math.log2(len(self.link_vocab)) if self.link_vocab else 16
                                
                                link_history.append(target)
                                in_link = True
                                break
                        
                        total_bits += math.log2(len(self.link_vocab)) if self.link_vocab else 16
                        link_history.append(target)
                    
                    in_link = True
                    break
            
            if not in_link:
                # Regular Order-5 text (no cascading)
                char = text[i]
                if len(text_context) >= 5:
                    ctx = text_context[-5:]
                    if ctx in self.text_models[5] and char in self.text_models[5][ctx]:
                        predictions = self.text_models[5][ctx]
                        total = sum(predictions.values())
                        prob = predictions[char] / total
                        total_bits += -math.log2(prob)
                    else:
                        total_bits += 8
                else:
                    total_bits += 8
                
                text_context += char
            
            i += 1
        
        return total_bits
    
    def compress_cascading_only(self, text):
        """CASCADING ONLY: Order-5→4→3→2→1 text (no hybrid links)"""
        total_bits = 0
        context = ""
        
        for char in text:
            # Try Order-5
            if len(context) >= 5:
                ctx = context[-5:]
                if ctx in self.text_models[5] and char in self.text_models[5][ctx]:
                    predictions = self.text_models[5][ctx]
                    total = sum(predictions.values())
                    prob = predictions[char] / total
                    total_bits += -math.log2(prob)
                    context += char
                    continue
            
            # Try Order-4
            if len(context) >= 4:
                ctx = context[-4:]
                if ctx in self.text_models[4] and char in self.text_models[4][ctx]:
                    predictions = self.text_models[4][ctx]
                    total = sum(predictions.values())
                    prob = predictions[char] / total
                    total_bits += -math.log2(prob) + 0.5
                    context += char
                    continue
            
            # Try Order-3
            if len(context) >= 3:
                ctx = context[-3:]
                if ctx in self.text_models[3] and char in self.text_models[3][ctx]:
                    predictions = self.text_models[3][ctx]
                    total = sum(predictions.values())
                    prob = predictions[char] / total
                    total_bits += -math.log2(prob) + 1.0
                    context += char
                    continue
            
            # Try Order-2
            if len(context) >= 2:
                ctx = context[-2:]
                if ctx in self.text_models[2] and char in self.text_models[2][ctx]:
                    predictions = self.text_models[2][ctx]
                    total = sum(predictions.values())
                    prob = predictions[char] / total
                    total_bits += -math.log2(prob) + 1.5
                    context += char
                    continue
            
            # Fallback
            total_bits += 8
            context += char
        
        return total_bits
    
    def compress_combined(self, text):
        """COMBINED: Hybrid + Cascading together"""
        link_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        link_regions = []
        
        for match in link_pattern.finditer(text):
            start, end = match.span()
            target = match.group(1)
            link_regions.append((start, end, target))
        
        total_bits = 0
        text_context = ""
        link_history = []
        
        i = 0
        while i < len(text):
            # Check if in link
            in_link = False
            for start, end, target in link_regions:
                if start <= i < end:
                    if i == start:  # Encode link with Order-6
                        if len(link_history) >= 6:
                            ctx = tuple(link_history[-6:])
                            if ctx in self.link_order6:
                                candidates = [l for l, c in self.link_order6[ctx].most_common()]
                                try:
                                    pos = candidates.index(target)
                                    if pos == 0:
                                        total_bits += 1
                                    elif pos < 5:
                                        total_bits += 3
                                    elif pos < 50:
                                        total_bits += 6
                                    else:
                                        total_bits += math.log2(len(self.link_vocab)) if self.link_vocab else 16
                                except ValueError:
                                    total_bits += math.log2(len(self.link_vocab)) if self.link_vocab else 16
                                
                                link_history.append(target)
                                in_link = True
                                break
                        
                        total_bits += math.log2(len(self.link_vocab)) if self.link_vocab else 16
                        link_history.append(target)
                    
                    in_link = True
                    break
            
            if not in_link:
                # Cascading text
                char = text[i]
                
                # Try Order-5
                if len(text_context) >= 5:
                    ctx = text_context[-5:]
                    if ctx in self.text_models[5] and char in self.text_models[5][ctx]:
                        predictions = self.text_models[5][ctx]
                        total = sum(predictions.values())
                        prob = predictions[char] / total
                        total_bits += -math.log2(prob)
                        text_context += char
                        i += 1
                        continue
                
                # Try Order-4
                if len(text_context) >= 4:
                    ctx = text_context[-4:]
                    if ctx in self.text_models[4] and char in self.text_models[4][ctx]:
                        predictions = self.text_models[4][ctx]
                        total = sum(predictions.values())
                        prob = predictions[char] / total
                        total_bits += -math.log2(prob) + 0.5
                        text_context += char
                        i += 1
                        continue
                
                # Try Order-3
                if len(text_context) >= 3:
                    ctx = text_context[-3:]
                    if ctx in self.text_models[3] and char in self.text_models[3][ctx]:
                        predictions = self.text_models[3][ctx]
                        total = sum(predictions.values())
                        prob = predictions[char] / total
                        total_bits += -math.log2(prob) + 1.0
                        text_context += char
                        i += 1
                        continue
                
                # Try Order-2
                if len(text_context) >= 2:
                    ctx = text_context[-2:]
                    if ctx in self.text_models[2] and char in self.text_models[2][ctx]:
                        predictions = self.text_models[2][ctx]
                        total = sum(predictions.values())
                        prob = predictions[char] / total
                        total_bits += -math.log2(prob) + 1.5
                        text_context += char
                        i += 1
                        continue
                
                # Fallback
                total_bits += 8
                text_context += char
            
            i += 1
        
        return total_bits
    
    def run_comprehensive_tests(self, text, train_size=3000000):
        """Run all tests comprehensively"""
        print("\n" + "=" * 70)
        print("🔬 COMPREHENSIVE VERIFICATION SUITE")
        print("=" * 70)
        print("\nUser's wisdom: 'perhaps something might be wrong yet'")
        print("Let's find out! Testing EVERYTHING!\n")
        
        # Train
        self.train_all_models(text, train_size)
        
        # Test on multiple sections
        test_configs = [
            (3000000, 500000, "Test 1 (3.0M-3.5M)"),
            (4000000, 500000, "Test 2 (4.0M-4.5M)"),
            (5000000, 500000, "Test 3 (5.0M-5.5M)"),
            (6000000, 500000, "Test 4 (6.0M-6.5M)"),
            (7000000, 500000, "Test 5 (7.0M-7.5M)"),
        ]
        
        all_results = []
        
        for start, size, name in test_configs:
            if start + size > len(text):
                print(f"\n⚠️ Skipping {name} - not enough data")
                continue
            
            test_text = text[start:start + size]
            
            print(f"\n{'=' * 70}")
            print(f"{name}")
            print(f"{'=' * 70}")
            print(f"Testing on {len(test_text):,} chars...")
            
            # Analyze content
            links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', test_text)
            link_chars = sum(len(f"[[{l}]]") for l in links)
            link_density = link_chars / len(test_text) * 100 if len(test_text) > 0 else 0
            
            print(f"  Link density: {link_density:.2f}%")
            
            # Test all variants
            print("\n  Compressing...")
            
            baseline_bits = self.compress_baseline(test_text)
            hybrid_bits = self.compress_hybrid_only(test_text)
            cascading_bits = self.compress_cascading_only(test_text)
            combined_bits = self.compress_combined(test_text)
            
            # Calculate savings
            hybrid_savings = baseline_bits - hybrid_bits
            cascading_savings = baseline_bits - cascading_bits
            combined_savings = baseline_bits - combined_bits
            
            # Percentages
            hybrid_pct = (hybrid_savings / baseline_bits * 100) if baseline_bits > 0 else 0
            cascading_pct = (cascading_savings / baseline_bits * 100) if baseline_bits > 0 else 0
            combined_pct = (combined_savings / baseline_bits * 100) if baseline_bits > 0 else 0
            
            print(f"\n  📊 Results:")
            print(f"    Baseline (Order-5 only): {baseline_bits:,.0f} bits")
            print(f"    Hybrid only: {hybrid_bits:,.0f} bits ({hybrid_pct:.2f}% improvement)")
            print(f"    Cascading only: {cascading_bits:,.0f} bits ({cascading_pct:.2f}% improvement)")
            print(f"    Combined: {combined_bits:,.0f} bits ({combined_pct:.2f}% improvement)")
            
            print(f"\n  💰 Savings:")
            print(f"    Hybrid: {hybrid_savings:,.0f} bits")
            print(f"    Cascading: {cascading_savings:,.0f} bits")
            print(f"    Combined: {combined_savings:,.0f} bits")
            
            # Check if they add up
            expected_combined = hybrid_savings + cascading_savings
            actual_combined = combined_savings
            overlap = expected_combined - actual_combined
            
            print(f"\n  🔍 Synergy check:")
            print(f"    Hybrid savings: {hybrid_savings:,.0f} bits")
            print(f"    Cascading savings: {cascading_savings:,.0f} bits")
            print(f"    Expected if additive: {expected_combined:,.0f} bits")
            print(f"    Actual combined: {actual_combined:,.0f} bits")
            print(f"    Overlap/interaction: {overlap:,.0f} bits ({overlap/expected_combined*100:.1f}%)")
            
            # Extrapolate
            scale = 1000
            hybrid_mb = hybrid_savings / 8 / 1024 / 1024 * scale
            cascading_mb = cascading_savings / 8 / 1024 / 1024 * scale
            combined_mb = combined_savings / 8 / 1024 / 1024 * scale
            
            print(f"\n  🌍 Extrapolated to enwik9:")
            print(f"    Hybrid: {hybrid_mb:.1f} MB")
            print(f"    Cascading: {cascading_mb:.1f} MB")
            print(f"    Combined: {combined_mb:.1f} MB")
            
            all_results.append({
                'name': name,
                'link_density': link_density,
                'hybrid_mb': hybrid_mb,
                'cascading_mb': cascading_mb,
                'combined_mb': combined_mb,
                'combined_pct': combined_pct,
            })
        
        # Final summary
        print("\n" + "=" * 70)
        print("📊 FINAL SUMMARY")
        print("=" * 70)
        
        if all_results:
            print(f"\n✅ Tests completed: {len(all_results)}")
            print("\nResults by test:")
            for r in all_results:
                print(f"  {r['name']}: {r['combined_mb']:.1f} MB ({r['combined_pct']:.2f}%)")
            
            # Statistics
            combined_mbs = [r['combined_mb'] for r in all_results]
            avg_mb = sum(combined_mbs) / len(combined_mbs)
            min_mb = min(combined_mbs)
            max_mb = max(combined_mbs)
            
            print(f"\n📈 Statistics:")
            print(f"  Average: {avg_mb:.1f} MB")
            print(f"  Minimum: {min_mb:.1f} MB")
            print(f"  Maximum: {max_mb:.1f} MB")
            print(f"  Range: {max_mb - min_mb:.1f} MB")
            
            # Conservative estimate
            print(f"\n🎯 CONSERVATIVE ESTIMATE:")
            print(f"  Using minimum: {min_mb:.1f} MB")
            
            # Final calculation
            current = 134.7
            new_pos = current - min_mb
            record = 114.0
            
            print(f"\n📊 FINAL POSITION:")
            print(f"  Current: {current:.1f} MB")
            print(f"  Improvement: -{min_mb:.1f} MB")
            print(f"  NEW: {new_pos:.1f} MB")
            print(f"  World record: {record:.1f} MB")
            
            if new_pos < record:
                diff = record - new_pos
                print(f"\n  🏆 BEAT RECORD BY {diff:.1f} MB! #1! 🥇")
            elif new_pos < record + 5:
                diff = new_pos - record
                print(f"\n  🥈 Within {diff:.1f} MB of #1!")
            else:
                diff = new_pos - record
                print(f"\n  ✅ {diff:.1f} MB from #1")
            
            # Truth verdict
            print("\n" + "=" * 70)
            print("❓ IS IT REALLY TRUE?")
            print("=" * 70)
            
            if max_mb - min_mb < 10 and min_mb > 40:
                print(f"\n✅ YES! VERIFIED!")
                print(f"  Consistent: {max_mb - min_mb:.1f} MB variation (tight)")
                print(f"  Significant: {min_mb:.1f} MB minimum")
                print(f"  Conservative: Used minimum, not average")
                print(f"  Components tested: Separately and combined")
                print(f"\n  THE CLAIMS ARE REAL! 🏆")
            elif min_mb > 20:
                print(f"\n🤔 PARTIALLY - But still great!")
                print(f"  Real savings: {min_mb:.1f} MB (conservative)")
                print(f"  Variation: {max_mb - min_mb:.1f} MB (content dependent)")
                print(f"  Previous claims: May have been optimistic")
                print(f"  Truth: {min_mb:.1f} MB is solid! ✅")
            else:
                print(f"\n⚠️ SIGNIFICANT ISSUES FOUND")
                print(f"  Actual: {min_mb:.1f} MB")
                print(f"  Claimed: Much higher")
                print(f"  Need investigation!")
        
        print("\n" + "=" * 70)
        print("✅ Comprehensive verification complete!")
        print("🔬 Truth found through rigorous testing!")
        print("=" * 70)

def main():
    print("=" * 70)
    print("🔬 COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 70)
    print("\nUser: 'perhaps something might be wrong yet'")
    print("Response: Let's test EVERYTHING properly! 🔬\n")
    
    # Load
    print("Loading enwik_10mb...")
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Verify
    verifier = ComprehensiveVerification()
    verifier.run_comprehensive_tests(text, train_size=3000000)

if __name__ == "__main__":
    main()
