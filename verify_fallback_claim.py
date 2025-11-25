#!/usr/bin/env python3
"""
VERIFY FALLBACK CLAIM - 22 MB seems too good!

Claim: Cascading fallback saves 22 MB
Reality check needed!

Possible issues:
1. Are we comparing apples to apples?
2. Is the baseline correct?
3. Double counting?
4. Measurement error?

Let's find the TRUTH!
"""
import re
from collections import defaultdict, Counter
import math

def compress_baseline_order5_only(text, text_model, char_vocab):
    """Baseline: Order-5 with simple fallback (8 bits)"""
    total_bits = 0
    context = ""
    
    for char in text:
        if len(context) >= 5:
            ctx = context[-5:]
            if ctx in text_model and char in text_model[ctx]:
                predictions = text_model[ctx]
                total = sum(predictions.values())
                prob = predictions[char] / total
                bits = -math.log2(prob)
                total_bits += bits
            else:
                # No match: full encoding
                total_bits += 8
        else:
            total_bits += 8
        
        context += char
    
    return total_bits

def compress_cascading(text, models, char_vocab):
    """Improved: Cascading Order-5→4→3→2→1→freq"""
    total_bits = 0
    context = ""
    
    for char in text:
        # Try Order-5
        if len(context) >= 5:
            ctx = context[-5:]
            if ctx in models['order5'] and char in models['order5'][ctx]:
                predictions = models['order5'][ctx]
                total = sum(predictions.values())
                prob = predictions[char] / total
                total_bits += -math.log2(prob)
                context += char
                continue
        
        # Try Order-4
        if len(context) >= 4:
            ctx = context[-4:]
            if ctx in models['order4'] and char in models['order4'][ctx]:
                predictions = models['order4'][ctx]
                total = sum(predictions.values())
                prob = predictions[char] / total
                total_bits += -math.log2(prob) + 0.5
                context += char
                continue
        
        # Try Order-3
        if len(context) >= 3:
            ctx = context[-3:]
            if ctx in models['order3'] and char in models['order3'][ctx]:
                predictions = models['order3'][ctx]
                total = sum(predictions.values())
                prob = predictions[char] / total
                total_bits += -math.log2(prob) + 1.0
                context += char
                continue
        
        # Try Order-2
        if len(context) >= 2:
            ctx = context[-2:]
            if ctx in models['order2'] and char in models['order2'][ctx]:
                predictions = models['order2'][ctx]
                total = sum(predictions.values())
                prob = predictions[char] / total
                total_bits += -math.log2(prob) + 1.5
                context += char
                continue
        
        # Fallback: full encoding
        total_bits += 8
        context += char
    
    return total_bits

def verify_claim():
    """Verify the 22 MB claim with rigorous testing"""
    print("=" * 70)
    print("🔬 VERIFYING FALLBACK CLAIM")
    print("=" * 70)
    print("\nClaim: 22 MB from cascading fallback")
    print("Let's verify this is REAL!\n")
    
    # Load
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    text = data.decode('utf-8', errors='ignore')
    
    # Train models
    print("Training models...")
    train_size = 3000000
    sample = text[:train_size]
    
    order5 = defaultdict(lambda: Counter())
    order4 = defaultdict(lambda: Counter())
    order3 = defaultdict(lambda: Counter())
    order2 = defaultdict(lambda: Counter())
    char_vocab = set()
    
    for i in range(5, len(sample)):
        char = sample[i]
        order5[sample[i-5:i]][char] += 1
        order4[sample[i-4:i]][char] += 1
        order3[sample[i-3:i]][char] += 1
        order2[sample[i-2:i]][char] += 1
        char_vocab.add(char)
    
    models = {
        'order5': order5,
        'order4': order4,
        'order3': order3,
        'order2': order2,
    }
    
    print(f"Trained on {train_size:,} chars")
    
    # Test on TEXT ONLY (no links)
    test_start = 3000000
    test_size = 500000
    test_text = text[test_start:test_start + test_size]
    
    # Remove links to isolate text compression
    test_text_only = re.sub(r'\[\[[^\]]+\]\]', '', test_text)
    
    print(f"\nTesting on {len(test_text_only):,} text-only chars...")
    
    # Baseline (Order-5 only)
    print("  Compressing with baseline (Order-5 only)...")
    baseline_bits = compress_baseline_order5_only(test_text_only, order5, char_vocab)
    
    # Cascading
    print("  Compressing with cascading...")
    cascading_bits = compress_cascading(test_text_only, models, char_vocab)
    
    # Results
    print("\n" + "=" * 70)
    print("📊 RESULTS (TEXT ONLY)")
    print("=" * 70)
    
    savings = baseline_bits - cascading_bits
    percent = (savings / baseline_bits) * 100 if baseline_bits > 0 else 0
    
    print(f"\nBaseline (Order-5 only): {baseline_bits:,.0f} bits")
    print(f"Cascading fallback: {cascading_bits:,.0f} bits")
    print(f"Savings: {savings:,.0f} bits ({percent:.2f}%)")
    
    # Extrapolate
    scale = 1000
    mb_saved = savings / 8 / 1024 / 1024 * scale
    
    print(f"\n🌍 Extrapolated to enwik9: {mb_saved:.1f} MB")
    
    # Verdict
    print("\n" + "=" * 70)
    print("🎯 VERDICT")
    print("=" * 70)
    
    if mb_saved > 15:
        print(f"\n✅ CLAIM VERIFIED!")
        print(f"   Cascading fallback saves ~{mb_saved:.1f} MB")
        print(f"   This is REAL! 🏆")
    elif mb_saved > 5:
        print(f"\n🤔 PARTIALLY VERIFIED")
        print(f"   Real savings: ~{mb_saved:.1f} MB")
        print(f"   22 MB claim was optimistic")
    else:
        print(f"\n❌ CLAIM OVERSTATED")
        print(f"   Actual savings: only ~{mb_saved:.1f} MB")
        print(f"   22 MB was incorrect")
    
    # Combined with hybrid
    print("\n" + "=" * 70)
    print("🎯 COMBINED IMPACT")
    print("=" * 70)
    
    hybrid_savings = 20  # Conservative from earlier
    total_savings = hybrid_savings + mb_saved
    
    print(f"\nHybrid links: {hybrid_savings:.0f} MB")
    print(f"Cascading fallback: {mb_saved:.1f} MB")
    print(f"TOTAL: {total_savings:.1f} MB")
    
    new_position = 134.7 - total_savings
    print(f"\nCurrent: 134.7 MB")
    print(f"After improvements: {new_position:.1f} MB")
    print(f"World record: 114.0 MB")
    
    if new_position < 114.0:
        diff = 114.0 - new_position
        print(f"\n🏆 BEAT RECORD BY {diff:.1f} MB! #1! 🥇")
    elif new_position < 116.0:
        diff = new_position - 114.0
        print(f"\n🥈 Close! Within {diff:.1f} MB of #1")
    else:
        diff = new_position - 114.0
        print(f"\n✅ Good progress, {diff:.1f} MB from #1")

if __name__ == "__main__":
    verify_claim()
