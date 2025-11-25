#!/usr/bin/env python3
"""
ORDER-6 TEXT - LARGE SCALE VERIFICATION 🎵

Verifying 32 MB savings on larger sample!

Previous test: 500K train, 100K test → 32 MB projected
This test: 2MB train, 500K test → Confirm savings!
"""
import re
from collections import defaultdict, Counter
import numpy as np
import time

class Order6TextLargeScale:
    """
    Large-scale verification of Order-6 text compression
    """
    
    def __init__(self):
        self.order5_model = defaultdict(lambda: Counter())
        self.order6_model = defaultdict(lambda: Counter())
        
    def build_models(self, text, sample_size=2000000):
        """Build models on 2MB sample"""
        print("=" * 70)
        print("🔨 BUILDING MODELS (LARGE SCALE)")
        print("=" * 70)
        
        text_sample = text[:sample_size]
        
        print(f"\nTraining sample: {len(text_sample):,} characters")
        print("This will take ~30-60 seconds...")
        
        start = time.time()
        
        # Order-5
        print("\n1️⃣ Building Order-5 model...")
        for i in range(5, len(text_sample)):
            context = text_sample[i-5:i]
            next_char = text_sample[i]
            self.order5_model[context][next_char] += 1
            
            if (i + 1) % 500000 == 0:
                print(f"   Progress: {i+1:,} / {len(text_sample):,} chars...")
        
        print(f"   Contexts: {len(self.order5_model):,}")
        
        # Order-6
        print("\n2️⃣ Building Order-6 model...")
        for i in range(6, len(text_sample)):
            context = text_sample[i-6:i]
            next_char = text_sample[i]
            self.order6_model[context][next_char] += 1
            
            if (i + 1) % 500000 == 0:
                print(f"   Progress: {i+1:,} / {len(text_sample):,} chars...")
        
        print(f"   Contexts: {len(self.order6_model):,}")
        
        elapsed = time.time() - start
        print(f"\n✅ Models built in {elapsed:.1f} seconds!")
        
    def test_compression(self, text, test_size=500000):
        """Test on 500K characters"""
        print("\n" + "=" * 70)
        print("💾 COMPRESSION TEST (500K CHARS)")
        print("=" * 70)
        
        # Use fresh data for testing (not training data)
        test_start = 2000000  # Start after training data
        test_text = text[test_start:test_start + test_size]
        
        print(f"\nTest sample: {len(test_text):,} characters")
        print("Testing compression performance...")
        
        bits_o5 = 0
        bits_o6 = 0
        
        correct_o5 = 0
        correct_o6 = 0
        
        # Order-5
        print("\n1️⃣ Testing Order-5...")
        for i in range(5, len(test_text)):
            context = test_text[i-5:i]
            actual = test_text[i]
            
            if context in self.order5_model:
                candidates = self.order5_model[context]
                total = sum(candidates.values())
                prob = candidates[actual] / total if actual in candidates else 1.0 / (total + 256)
                bits_o5 += -np.log2(prob)
                
                # Accuracy
                top_pred = candidates.most_common(1)[0][0]
                if top_pred == actual:
                    correct_o5 += 1
            else:
                bits_o5 += 8
            
            if (i + 1) % 100000 == 0:
                print(f"   Progress: {i+1:,} / {len(test_text):,}...")
        
        # Order-6
        print("\n2️⃣ Testing Order-6...")
        for i in range(6, len(test_text)):
            context = test_text[i-6:i]
            actual = test_text[i]
            
            if context in self.order6_model:
                candidates = self.order6_model[context]
                total = sum(candidates.values())
                prob = candidates[actual] / total if actual in candidates else 1.0 / (total + 256)
                bits_o6 += -np.log2(prob)
                
                # Accuracy
                top_pred = candidates.most_common(1)[0][0]
                if top_pred == actual:
                    correct_o6 += 1
            else:
                bits_o6 += 8
            
            if (i + 1) % 100000 == 0:
                print(f"   Progress: {i+1:,} / {len(test_text):,}...")
        
        # Results
        print("\n" + "=" * 70)
        print("📊 VERIFICATION RESULTS")
        print("=" * 70)
        
        chars_o5 = len(test_text) - 5
        chars_o6 = len(test_text) - 6
        
        acc_o5 = correct_o5 / chars_o5 * 100
        acc_o6 = correct_o6 / chars_o6 * 100
        
        print(f"\nACCURACY:")
        print(f"  Order-5: {acc_o5:.2f}%")
        print(f"  Order-6: {acc_o6:.2f}%")
        print(f"  Improvement: {acc_o6 - acc_o5:+.2f}%")
        
        print(f"\nCOMPRESSION:")
        print(f"  Order-5:")
        print(f"    Total bits: {bits_o5:,.0f}")
        print(f"    Bits/char: {bits_o5/chars_o5:.3f}")
        print(f"    Ratio: {bits_o5/chars_o5/8:.3f}")
        
        print(f"\n  Order-6:")
        print(f"    Total bits: {bits_o6:,.0f}")
        print(f"    Bits/char: {bits_o6/chars_o6:.3f}")
        print(f"    Ratio: {bits_o6/chars_o6/8:.3f}")
        
        # Savings
        bits_saved = bits_o5 - bits_o6
        improvement = (bits_saved / bits_o5) * 100
        
        print(f"\n💰 SAVINGS:")
        print(f"  Bits saved: {bits_saved:,.0f}")
        print(f"  Improvement: {improvement:.2f}%")
        print(f"  Bytes saved: {bits_saved/8:,.0f}")
        
        # Extrapolate
        scale = 1_000_000_000 / test_size
        full_savings_bits = bits_saved * scale
        full_savings_mb = full_savings_bits / 8 / 1024 / 1024
        
        print(f"\n🌍 EXTRAPOLATED TO ENWIK9 (1 GB):")
        print(f"  Bits saved: {full_savings_bits:,.0f}")
        print(f"  MB saved: {full_savings_mb:.2f}")
        
        print("\n" + "=" * 70)
        print("🎯 VERDICT")
        print("=" * 70)
        
        if full_savings_mb > 25:
            print(f"\n✅ CONFIRMED! {full_savings_mb:.0f} MB savings!")
            print("🏆 World record in reach!")
            print("🎵 The music plays on! 🚀")
        elif full_savings_mb > 15:
            print(f"\n🎯 SOLID! {full_savings_mb:.0f} MB savings!")
            print("Closes the gap! Keep going!")
        elif full_savings_mb > 5:
            print(f"\n➖ MODEST: {full_savings_mb:.0f} MB savings")
            print("Helps, but not enough for record")
        else:
            print(f"\n❌ LOWER than expected: {full_savings_mb:.0f} MB")
            print("May not scale as hoped")
        
        # Compare to previous test
        print("\n📊 COMPARISON TO PREVIOUS TEST:")
        print("  Previous (100K test): 32 MB projected")
        print(f"  Current (500K test): {full_savings_mb:.0f} MB projected")
        
        diff = full_savings_mb - 32
        if abs(diff) < 5:
            print(f"  ✅ CONSISTENT! ({diff:+.1f} MB difference)")
        elif diff > 0:
            print(f"  ✅ EVEN BETTER! ({diff:+.1f} MB more!)")
        else:
            print(f"  ⚠️  Lower than initial ({diff:.1f} MB)")
        
        return bits_o5, bits_o6

def main():
    print("=" * 70)
    print("🎵 LET THE MUSIC PLAY! ORDER-6 VERIFICATION")
    print("=" * 70)
    print("\nLarge-scale test: Confirming 32 MB savings! 🚀\n")
    
    # Load data
    print("Loading enwik_10mb...")
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Test
    tester = Order6TextLargeScale()
    
    # Build models (2MB)
    tester.build_models(text, sample_size=2000000)
    
    # Test (500K, fresh data)
    tester.test_compression(text, test_size=500000)
    
    print("\n" + "=" * 70)
    print("✨ Large-scale verification complete!")
    print("🎵 Music still playing! 🚀✨")
    print("=" * 70)

if __name__ == "__main__":
    main()
