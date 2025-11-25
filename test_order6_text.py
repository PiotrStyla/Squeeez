#!/usr/bin/env python3
"""
ORDER-6 TEXT COMPRESSION TEST - Ad Astra! 🚀

Morning session: Nov 25, 2025

Yesterday: Order-6 links = 100% accuracy
Today: Can Order-6 help TEXT? (98% of gap!)

Testing on real Wikipedia text to see if deeper context helps!
"""
import re
from collections import defaultdict, Counter
import numpy as np

class Order6TextCompressor:
    """
    Test Order-6 vs Order-5 on text compression
    
    Order-5: Context of 5 previous characters
    Order-6: Context of 6 previous characters
    
    Question: Does extra context help?
    """
    
    def __init__(self):
        self.order5_model = defaultdict(lambda: Counter())
        self.order6_model = defaultdict(lambda: Counter())
        
    def build_models(self, text, sample_size=500000):
        """Build both Order-5 and Order-6 models"""
        print("=" * 70)
        print("🔨 BUILDING MODELS")
        print("=" * 70)
        
        # Sample for speed (full text would take too long)
        text_sample = text[:sample_size]
        
        print(f"\nSample size: {len(text_sample):,} characters")
        
        # Build Order-5
        print("\n1️⃣ Building Order-5 model...")
        for i in range(5, len(text_sample)):
            context = text_sample[i-5:i]
            next_char = text_sample[i]
            self.order5_model[context][next_char] += 1
        
        print(f"   Contexts: {len(self.order5_model):,}")
        
        # Build Order-6
        print("\n2️⃣ Building Order-6 model...")
        for i in range(6, len(text_sample)):
            context = text_sample[i-6:i]
            next_char = text_sample[i]
            self.order6_model[context][next_char] += 1
        
        print(f"   Contexts: {len(self.order6_model):,}")
        
        print("\n✅ Models built!")
        
    def test_prediction_accuracy(self, text, test_size=100000):
        """
        Test prediction accuracy of both models
        
        Accuracy = how often TOP-1 prediction is correct
        """
        print("\n" + "=" * 70)
        print("🎯 TESTING PREDICTION ACCURACY")
        print("=" * 70)
        
        test_text = text[:test_size]
        
        stats_o5 = {'correct': 0, 'wrong': 0, 'no_context': 0}
        stats_o6 = {'correct': 0, 'wrong': 0, 'no_context': 0}
        
        print(f"\nTesting on {len(test_text):,} characters...")
        
        # Test Order-5
        print("\n1️⃣ Order-5:")
        for i in range(5, len(test_text)):
            context = test_text[i-5:i]
            actual = test_text[i]
            
            if context in self.order5_model:
                candidates = self.order5_model[context]
                top_pred = candidates.most_common(1)[0][0] if candidates else None
                
                if top_pred == actual:
                    stats_o5['correct'] += 1
                else:
                    stats_o5['wrong'] += 1
            else:
                stats_o5['no_context'] += 1
        
        total_o5 = sum(stats_o5.values())
        print(f"   Correct: {stats_o5['correct']:,} ({stats_o5['correct']/total_o5*100:.2f}%)")
        print(f"   Wrong: {stats_o5['wrong']:,} ({stats_o5['wrong']/total_o5*100:.2f}%)")
        print(f"   No context: {stats_o5['no_context']:,} ({stats_o5['no_context']/total_o5*100:.2f}%)")
        
        # Test Order-6
        print("\n2️⃣ Order-6:")
        for i in range(6, len(test_text)):
            context = test_text[i-6:i]
            actual = test_text[i]
            
            if context in self.order6_model:
                candidates = self.order6_model[context]
                top_pred = candidates.most_common(1)[0][0] if candidates else None
                
                if top_pred == actual:
                    stats_o6['correct'] += 1
                else:
                    stats_o6['wrong'] += 1
            else:
                stats_o6['no_context'] += 1
        
        total_o6 = sum(stats_o6.values())
        print(f"   Correct: {stats_o6['correct']:,} ({stats_o6['correct']/total_o6*100:.2f}%)")
        print(f"   Wrong: {stats_o6['wrong']:,} ({stats_o6['wrong']/total_o6*100:.2f}%)")
        print(f"   No context: {stats_o6['no_context']:,} ({stats_o6['no_context']/total_o6*100:.2f}%)")
        
        # Comparison
        acc_o5 = stats_o5['correct'] / total_o5 * 100
        acc_o6 = stats_o6['correct'] / total_o6 * 100
        improvement = acc_o6 - acc_o5
        
        print("\n" + "=" * 70)
        print("📊 COMPARISON")
        print("=" * 70)
        
        print(f"\nOrder-5: {acc_o5:.2f}% accuracy")
        print(f"Order-6: {acc_o6:.2f}% accuracy")
        print(f"\nImprovement: {improvement:+.2f} percentage points")
        
        if improvement > 0:
            print(f"\n✅ Order-6 BETTER by {improvement:.2f}%!")
        elif improvement < 0:
            print(f"\n❌ Order-5 better by {abs(improvement):.2f}%")
        else:
            print(f"\n➖ No difference")
        
        return stats_o5, stats_o6
    
    def estimate_compression_bits(self, text, test_size=100000):
        """
        Estimate compression bits needed
        
        Uses entropy-based estimation
        """
        print("\n" + "=" * 70)
        print("💾 COMPRESSION ESTIMATION")
        print("=" * 70)
        
        test_text = text[:test_size]
        
        bits_o5 = 0
        bits_o6 = 0
        
        print(f"\nEstimating bits for {len(test_text):,} characters...")
        
        # Order-5
        for i in range(5, len(test_text)):
            context = test_text[i-5:i]
            actual = test_text[i]
            
            if context in self.order5_model:
                candidates = self.order5_model[context]
                total = sum(candidates.values())
                prob = candidates[actual] / total if actual in candidates else 1.0 / (total + 256)
                bits_o5 += -np.log2(prob)
            else:
                bits_o5 += 8  # Full byte for unknown
        
        # Order-6
        for i in range(6, len(test_text)):
            context = test_text[i-6:i]
            actual = test_text[i]
            
            if context in self.order6_model:
                candidates = self.order6_model[context]
                total = sum(candidates.values())
                prob = candidates[actual] / total if actual in candidates else 1.0 / (total + 256)
                bits_o6 += -np.log2(prob)
            else:
                bits_o6 += 8  # Full byte for unknown
        
        # Results
        print("\n" + "=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        
        chars_o5 = len(test_text) - 5
        chars_o6 = len(test_text) - 6
        
        print(f"\nOrder-5:")
        print(f"  Total bits: {bits_o5:,.0f}")
        print(f"  Bits per char: {bits_o5/chars_o5:.3f}")
        print(f"  Bytes: {bits_o5/8:,.0f}")
        print(f"  Compression ratio: {bits_o5/chars_o5/8:.3f}")
        
        print(f"\nOrder-6:")
        print(f"  Total bits: {bits_o6:,.0f}")
        print(f"  Bits per char: {bits_o6/chars_o6:.3f}")
        print(f"  Bytes: {bits_o6/8:,.0f}")
        print(f"  Compression ratio: {bits_o6/chars_o6/8:.3f}")
        
        # Savings
        bits_saved = bits_o5 - bits_o6
        improvement_pct = (bits_saved / bits_o5) * 100 if bits_o5 > 0 else 0
        
        print(f"\n💰 SAVINGS:")
        if bits_saved > 0:
            print(f"  ✅ Order-6 saves {bits_saved:,.0f} bits!")
            print(f"  ✅ Improvement: {improvement_pct:.2f}%")
            print(f"  ✅ Bytes saved: {bits_saved/8:,.0f}")
            
            # Extrapolate to full enwik9
            # Current test: 100K chars
            # Full enwik9: 1GB = 1,000,000,000 chars
            scale_factor = 1_000_000_000 / test_size
            full_savings = bits_saved * scale_factor
            
            print(f"\n  🌍 Extrapolated to enwik9 (1 GB):")
            print(f"    Bits saved: {full_savings:,.0f}")
            print(f"    MB saved: {full_savings/8/1024/1024:.2f}")
            
            if improvement_pct > 2:
                print(f"\n  🏆 SIGNIFICANT! Worth implementing!")
            elif improvement_pct > 0.5:
                print(f"\n  🎯 Solid gain! Consider it!")
            else:
                print(f"\n  ➖ Modest gain. May not be worth complexity.")
        else:
            print(f"  ❌ Order-5 is better!")
            print(f"  → Order-6 adds overhead without benefit")
        
        return bits_o5, bits_o6

def main():
    print("=" * 70)
    print("🌅 MORNING SESSION: ORDER-6 TEXT COMPRESSION")
    print("=" * 70)
    print("\nAd astra! Testing if Order-6 helps TEXT! 🚀")
    print("(TEXT = 98% of the 20 MB gap!)\n")
    
    # Load data
    print("Loading enwik_10mb...")
    try:
        with open("data/enwik_10mb", 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print("❌ File not found!")
        return
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Initialize compressor
    compressor = Order6TextCompressor()
    
    # Build models (on 500K sample)
    compressor.build_models(text, sample_size=500000)
    
    # Test accuracy (on 100K)
    compressor.test_prediction_accuracy(text, test_size=100000)
    
    # Estimate compression (on 100K)
    compressor.estimate_compression_bits(text, test_size=100000)
    
    print("\n" + "=" * 70)
    print("✨ Order-6 text test complete!")
    print("🎯 Now we know if deeper context helps! 🚀")
    print("=" * 70)

if __name__ == "__main__":
    main()
