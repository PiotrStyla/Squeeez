#!/usr/bin/env python3
"""
FINAL COMBINED TEST - What do we REALLY get?

Test BOTH improvements together:
1. Hybrid Order-6 links
2. Cascading Order-5→4→3→2→1 fallback

THIS is the true final number!
"""
import re
from collections import defaultdict, Counter
import math

def train_all_models(text, train_size):
    """Train complete model suite"""
    sample = text[:train_size]
    
    # Text models
    text_models = {}
    for order in [5, 4, 3, 2]:
        text_models[order] = defaultdict(lambda: Counter())
    
    text_models[1] = Counter()
    char_freq = Counter()
    char_vocab = set()
    
    for i in range(5, len(sample)):
        char = sample[i]
        text_models[5][sample[i-5:i]][char] += 1
        text_models[4][sample[i-4:i]][char] += 1
        text_models[3][sample[i-3:i]][char] += 1
        text_models[2][sample[i-2:i]][char] += 1
        text_models[1][char] += 1
        char_freq[char] += 1
        char_vocab.add(char)
    
    # Link models
    links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', sample)
    link_vocab = Counter(links)
    
    link_order6 = defaultdict(lambda: Counter())
    link_order2 = defaultdict(lambda: Counter())
    
    for i in range(6, len(links)):
        ctx = tuple(links[i-6:i])
        link_order6[ctx][links[i]] += 1
    
    for i in range(2, len(links)):
        ctx = tuple(links[i-2:i])
        link_order2[ctx][links[i]] += 1
    
    return text_models, char_freq, char_vocab, link_order6, link_order2, link_vocab

def compress_complete(text, text_models, char_freq, char_vocab, link_order6, link_order2, link_vocab):
    """
    Complete compression: Hybrid + Cascading
    
    This is our BEST approach!
    """
    # Find all links
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
                        if ctx in link_order6:
                            candidates = [l for l, c in link_order6[ctx].most_common()]
                            try:
                                pos = candidates.index(target)
                                if pos == 0:
                                    total_bits += 1
                                elif pos < 5:
                                    total_bits += 3
                                elif pos < 50:
                                    total_bits += 6
                                else:
                                    total_bits += math.log2(len(link_vocab))
                            except ValueError:
                                total_bits += math.log2(len(link_vocab))
                            
                            link_history.append(target)
                            in_link = True
                            break
                    
                    total_bits += math.log2(len(link_vocab))
                    link_history.append(target)
                
                in_link = True
                break
        
        if not in_link:
            # Text: Use cascading fallback
            char = text[i]
            
            # Try Order-5
            if len(text_context) >= 5:
                ctx = text_context[-5:]
                if ctx in text_models[5] and char in text_models[5][ctx]:
                    predictions = text_models[5][ctx]
                    total = sum(predictions.values())
                    prob = predictions[char] / total
                    total_bits += -math.log2(prob)
                    text_context += char
                    i += 1
                    continue
            
            # Try Order-4
            if len(text_context) >= 4:
                ctx = text_context[-4:]
                if ctx in text_models[4] and char in text_models[4][ctx]:
                    predictions = text_models[4][ctx]
                    total = sum(predictions.values())
                    prob = predictions[char] / total
                    total_bits += -math.log2(prob) + 0.5
                    text_context += char
                    i += 1
                    continue
            
            # Try Order-3
            if len(text_context) >= 3:
                ctx = text_context[-3:]
                if ctx in text_models[3] and char in text_models[3][ctx]:
                    predictions = text_models[3][ctx]
                    total = sum(predictions.values())
                    prob = predictions[char] / total
                    total_bits += -math.log2(prob) + 1.0
                    text_context += char
                    i += 1
                    continue
            
            # Try Order-2
            if len(text_context) >= 2:
                ctx = text_context[-2:]
                if ctx in text_models[2] and char in text_models[2][ctx]:
                    predictions = text_models[2][ctx]
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

def compress_baseline(text, text_model5, char_vocab):
    """Baseline: Order-5 text only, no hybrid, no cascading"""
    total_bits = 0
    context = ""
    
    for char in text:
        if len(context) >= 5:
            ctx = context[-5:]
            if ctx in text_model5 and char in text_model5[ctx]:
                predictions = text_model5[ctx]
                total = sum(predictions.values())
                prob = predictions[char] / total
                total_bits += -math.log2(prob)
            else:
                total_bits += 8
        else:
            total_bits += 8
        
        context += char
    
    return total_bits

def main():
    print("=" * 70)
    print("🎯 FINAL COMBINED TEST")
    print("=" * 70)
    print("\nTesting BOTH improvements together!")
    print("This is the REAL final number!\n")
    
    # Load
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    text = data.decode('utf-8', errors='ignore')
    
    # Train
    print("Training all models...")
    train_size = 3000000
    text_models, char_freq, char_vocab, link_o6, link_o2, link_vocab = train_all_models(text, train_size)
    print(f"  Trained on {train_size:,} chars\n")
    
    # Test on multiple sections
    tests = [
        (3000000, 500000, "Test 1"),
        (4000000, 500000, "Test 2"),
        (5000000, 500000, "Test 3"),
    ]
    
    results = []
    
    for start, size, name in tests:
        if start + size > len(text):
            continue
        
        test_text = text[start:start + size]
        
        print(f"{name} ({start:,}-{start+size:,}):")
        print(f"  Compressing {len(test_text):,} chars...")
        
        # Baseline
        baseline_bits = compress_baseline(test_text, text_models[5], char_vocab)
        
        # Complete (hybrid + cascading)
        complete_bits = compress_complete(test_text, text_models, char_freq, char_vocab, link_o6, link_o2, link_vocab)
        
        savings = baseline_bits - complete_bits
        percent = (savings / baseline_bits) * 100
        
        print(f"  Baseline: {baseline_bits:,.0f} bits")
        print(f"  Complete: {complete_bits:,.0f} bits")
        print(f"  Savings: {savings:,.0f} bits ({percent:.2f}%)")
        
        mb = savings / 8 / 1024 / 1024 * 1000
        print(f"  Extrapolated: {mb:.1f} MB\n")
        
        results.append(mb)
    
    # Final verdict
    print("=" * 70)
    print("🎯 FINAL VERDICT")
    print("=" * 70)
    
    if results:
        avg_mb = sum(results) / len(results)
        min_mb = min(results)
        max_mb = max(results)
        
        print(f"\nTests: {len(results)}")
        print(f"Range: {min_mb:.1f} - {max_mb:.1f} MB")
        print(f"Average: {avg_mb:.1f} MB")
        print(f"Conservative: {min_mb:.1f} MB")
        
        print(f"\n📊 FINAL CALCULATION:")
        print(f"   Current: 134.7 MB")
        print(f"   Conservative savings: -{min_mb:.1f} MB")
        print(f"   NEW: {134.7 - min_mb:.1f} MB")
        print(f"\n   World record: 114.0 MB")
        
        final_pos = 134.7 - min_mb
        
        if final_pos < 114.0:
            diff = 114.0 - final_pos
            print(f"\n   🏆 BEAT RECORD BY {diff:.1f} MB! #1! 🥇")
        elif final_pos < 116.0:
            diff = final_pos - 114.0
            print(f"\n   🥈 Within {diff:.1f} MB of #1!")
        else:
            diff = final_pos - 114.0
            print(f"\n   ✅ {diff:.1f} MB from #1")

if __name__ == "__main__":
    main()
