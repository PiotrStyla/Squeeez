#!/usr/bin/env python3
"""
ORDER-6 LINK PREDICTION TEST

After bi-gram success (97.8% accuracy), test Order-6!

Could this be the next improvement? 🎯
"""
import re
from collections import defaultdict, Counter

def extract_links(text):
    """Extract Wikipedia links from XML"""
    pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
    return pattern.findall(text)

def build_order6_model(links):
    """
    Build Order-6 transition model
    
    Context: Previous 6 links → Next link
    """
    model = defaultdict(lambda: defaultdict(int))
    
    for i in range(6, len(links)):
        # Context = last 6 links
        context = tuple(links[i-6:i])
        next_link = links[i]
        model[context][next_link] += 1
    
    return model

def build_order2_model(links):
    """Build bi-gram (Order-2) for comparison"""
    model = defaultdict(lambda: defaultdict(int))
    
    for i in range(2, len(links)):
        context = (links[i-2], links[i-1])
        next_link = links[i]
        model[context][next_link] += 1
    
    return model

def test_prediction_accuracy(model, links, order):
    """Test how well model predicts"""
    
    correct_top1 = 0
    correct_top5 = 0
    total = 0
    
    for i in range(order, len(links)):
        context = tuple(links[i-order:i])
        actual = links[i]
        
        if context not in model:
            continue
        
        # Get predictions
        counter = Counter(model[context])
        predictions = counter.most_common(5)
        if not predictions:
            continue
        
        total += 1
        pred_links = [link for link, _ in predictions]
        
        if pred_links[0] == actual:
            correct_top1 += 1
            correct_top5 += 1
        elif actual in pred_links:
            correct_top5 += 1
    
    top1_acc = (correct_top1 / total * 100) if total > 0 else 0
    top5_acc = (correct_top5 / total * 100) if total > 0 else 0
    
    return top1_acc, top5_acc, total

def estimate_compression_bits(model, links, order):
    """
    Estimate bits needed for encoding links
    
    Uses arithmetic coding approximation: -log2(probability)
    """
    import math
    
    total_bits = 0
    encoded_count = 0
    
    for i in range(order, len(links)):
        context = tuple(links[i-order:i])
        actual = links[i]
        
        if context not in model:
            # Fallback: assume uniform over 1000 common links
            total_bits += math.log2(1000)
            encoded_count += 1
            continue
        
        predictions = model[context]
        total_count = sum(predictions.values())
        
        if actual in predictions:
            # Probability of this link in context
            prob = predictions[actual] / total_count
            bits = -math.log2(prob)
        else:
            # Not in predictions, fallback
            bits = math.log2(1000)
        
        total_bits += bits
        encoded_count += 1
    
    avg_bits = total_bits / encoded_count if encoded_count > 0 else 0
    return total_bits, avg_bits, encoded_count

def main():
    print("=" * 70)
    print("🎯 ORDER-6 vs BI-GRAM TEST")
    print("=" * 70)
    print("\nCan deeper context improve compression?\n")
    
    # Load data
    print("Loading enwik_10mb...")
    try:
        with open("data/enwik_10mb", 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print("File not found!")
        return
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Extract links
    print("Extracting links...")
    links = extract_links(text)
    print(f"Found: {len(links):,} links\n")
    
    if len(links) < 1000:
        print("Too few links!")
        return
    
    # Build models
    print("=" * 70)
    print("🔨 BUILDING MODELS...")
    print("=" * 70)
    
    print("\n1️⃣ Building Order-2 (bi-gram)...")
    model_order2 = build_order2_model(links)
    print(f"   Contexts: {len(model_order2):,}")
    
    print("\n2️⃣ Building Order-6...")
    model_order6 = build_order6_model(links)
    print(f"   Contexts: {len(model_order6):,}")
    
    # Test accuracy
    print("\n" + "=" * 70)
    print("📊 TESTING ACCURACY...")
    print("=" * 70)
    
    print("\n🔹 Order-2 (bi-gram):")
    top1_o2, top5_o2, total_o2 = test_prediction_accuracy(model_order2, links, 2)
    print(f"   TOP-1: {top1_o2:.1f}%")
    print(f"   TOP-5: {top5_o2:.1f}%")
    print(f"   Tested: {total_o2:,} predictions")
    
    print("\n🔹 Order-6:")
    top1_o6, top5_o6, total_o6 = test_prediction_accuracy(model_order6, links, 6)
    print(f"   TOP-1: {top1_o6:.1f}%")
    print(f"   TOP-5: {top5_o6:.1f}%")
    print(f"   Tested: {total_o6:,} predictions")
    
    # Comparison
    print("\n📈 IMPROVEMENT:")
    if top1_o6 > top1_o2:
        improvement = top1_o6 - top1_o2
        print(f"   ✅ Order-6 BETTER by {improvement:+.1f}%!")
    elif top1_o6 < top1_o2:
        decline = top1_o2 - top1_o6
        print(f"   ❌ Order-2 better by {decline:.1f}%")
    else:
        print(f"   ➖ Same accuracy")
    
    # Compression estimate
    print("\n" + "=" * 70)
    print("💾 COMPRESSION ESTIMATE...")
    print("=" * 70)
    
    print("\n🔹 Order-2 (bi-gram):")
    bits_o2, avg_o2, count_o2 = estimate_compression_bits(model_order2, links, 2)
    print(f"   Total bits: {bits_o2:,.0f}")
    print(f"   Avg per link: {avg_o2:.2f} bits")
    print(f"   Total bytes: {bits_o2/8:,.0f}")
    
    print("\n🔹 Order-6:")
    bits_o6, avg_o6, count_o6 = estimate_compression_bits(model_order6, links, 6)
    print(f"   Total bits: {bits_o6:,.0f}")
    print(f"   Avg per link: {avg_o6:.2f} bits")
    print(f"   Total bytes: {bits_o6/8:,.0f}")
    
    # Savings
    print("\n💰 SAVINGS:")
    if bits_o6 < bits_o2:
        saved_bits = bits_o2 - bits_o6
        saved_bytes = saved_bits / 8
        pct = (saved_bits / bits_o2) * 100
        print(f"   ✅ Order-6 saves {saved_bits:,.0f} bits = {saved_bytes:,.0f} bytes")
        print(f"   ✅ Improvement: {pct:.2f}%")
        
        # Extrapolate to full enwik9
        scale = 1000 / 10  # 1GB / 10MB
        full_saving = saved_bytes * scale
        print(f"\n   🌍 Extrapolated to enwik9: ~{full_saving/1024:.1f} KB saved")
        
        if full_saving > 100000:  # > 100 KB
            print(f"   🏆 SIGNIFICANT! Worth implementing!")
        else:
            print(f"   🤔 Small gain, may not be worth complexity")
    else:
        worse_bits = bits_o6 - bits_o2
        worse_bytes = worse_bits / 8
        print(f"   ❌ Order-6 worse by {worse_bytes:,.0f} bytes")
        print(f"   → Overfitting? Sparse contexts?")
    
    # Final verdict
    print("\n" + "=" * 70)
    print("🎯 VERDICT")
    print("=" * 70)
    
    if bits_o6 < bits_o2 and (bits_o2 - bits_o6) / bits_o2 > 0.01:
        print("\n✅ ORDER-6 WINS!")
        print("   → Deeper context helps!")
        print("   → Worth implementing in compressor!")
        print("   → Could be part of next improvement! 🚀")
    elif bits_o6 < bits_o2:
        print("\n🤔 ORDER-6 slightly better")
        print("   → Marginal gain")
        print("   → May not justify complexity")
    else:
        print("\n➖ ORDER-2 (bi-gram) is better")
        print("   → Order-6 too sparse")
        print("   → Bi-gram is sweet spot for this data")
        print("   → But we learned something! ✓")
    
    # Insights
    print("\n💡 INSIGHTS:")
    print(f"   Order-2 contexts: {len(model_order2):,}")
    print(f"   Order-6 contexts: {len(model_order6):,}")
    
    if len(model_order6) > len(model_order2) * 5:
        print(f"   → Order-6 much sparser!")
        print(f"   → Many contexts seen only once")
        print(f"   → Less reliable predictions")
    
    print("\n" + "=" * 70)
    print("✨ Test complete!")
    print("🎯 Now we know if Order-6 is worth it! 😊")
    print("=" * 70)

if __name__ == "__main__":
    main()
