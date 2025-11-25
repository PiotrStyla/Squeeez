#!/usr/bin/env python3
"""
FIX CALCULATION ERROR - Numbers don't make sense!

Problem: Enwik8 showed 229 MB savings, but that would give negative size!

The issue: We're measuring percentage improvement in BITS,
but need to convert to actual MB compressed size properly!

Let's recalculate correctly!
"""

def analyze_calculation_error():
    """Find where the calculation went wrong"""
    print("=" * 70)
    print("🔍 ANALYZING CALCULATION ERROR")
    print("=" * 70)
    
    print("\n❌ WRONG CALCULATION (from enwik8 test):")
    print("   Measured: 22.97% to 28.42% improvement in bits")
    print("   Extrapolated: 229.7 MB savings")
    print("   Result: -94.7 MB (IMPOSSIBLE!)")
    
    print("\n💡 THE PROBLEM:")
    print("   We measured percentage improvement in BIT ESTIMATES")
    print("   But extrapolated against RAW FILE SIZE (1 GB)")
    print("   This is WRONG!")
    
    print("\n✅ CORRECT APPROACH:")
    print("   1. Measure bits per character (BPC) for both methods")
    print("   2. Calculate actual compressed sizes")
    print("   3. Find the difference")
    
    print("\n" + "=" * 70)
    print("📊 RECALCULATING FROM ENWIK8 DATA")
    print("=" * 70)
    
    # Data from enwik8 test
    test_size_chars = 1048576  # 1 MB of text
    
    tests = [
        {"pos": "20 MB", "baseline_bits": 2700963, "combined_bits": 1933433},
        {"pos": "40 MB", "baseline_bits": 2582773, "combined_bits": 1929368},
        {"pos": "60 MB", "baseline_bits": 2515037, "combined_bits": 1937362},
        {"pos": "80 MB", "baseline_bits": 2537719, "combined_bits": 1911727},
    ]
    
    print("\n📊 Per-test analysis:")
    for t in tests:
        baseline_bpc = t["baseline_bits"] / test_size_chars
        combined_bpc = t["combined_bits"] / test_size_chars
        
        print(f"\n  {t['pos']}:")
        print(f"    Baseline: {baseline_bpc:.4f} bits/char")
        print(f"    Combined: {combined_bpc:.4f} bits/char")
        print(f"    Improvement: {baseline_bpc - combined_bpc:.4f} bits/char")
    
    # Average bits per character
    avg_baseline_bpc = sum(t["baseline_bits"] for t in tests) / (len(tests) * test_size_chars)
    avg_combined_bpc = sum(t["combined_bits"] for t in tests) / (len(tests) * test_size_chars)
    
    print(f"\n📈 AVERAGE:")
    print(f"  Baseline: {avg_baseline_bpc:.4f} bits/char")
    print(f"  Combined: {avg_combined_bpc:.4f} bits/char")
    print(f"  Improvement: {avg_baseline_bpc - avg_combined_bpc:.4f} bits/char")
    
    # Conservative (worst case)
    max_combined_bpc = max(t["combined_bits"] for t in tests) / test_size_chars
    min_baseline_bpc = min(t["baseline_bits"] for t in tests) / test_size_chars
    
    conservative_improvement = min_baseline_bpc - max_combined_bpc
    
    print(f"\n🎯 CONSERVATIVE:")
    print(f"  Worst baseline: {min_baseline_bpc:.4f} bits/char")
    print(f"  Worst combined: {max_combined_bpc:.4f} bits/char")
    print(f"  Conservative improvement: {conservative_improvement:.4f} bits/char")
    
    # Extrapolate to enwik9
    print("\n" + "=" * 70)
    print("🌍 EXTRAPOLATION TO ENWIK9 (1 BILLION CHARS)")
    print("=" * 70)
    
    enwik9_chars = 1_000_000_000
    
    # Baseline compressed size
    baseline_bits = avg_baseline_bpc * enwik9_chars
    baseline_mb = baseline_bits / 8 / 1024 / 1024
    
    # Combined compressed size
    combined_bits = avg_combined_bpc * enwik9_chars
    combined_mb = combined_bits / 8 / 1024 / 1024
    
    # Savings
    savings_bits = baseline_bits - combined_bits
    savings_mb = savings_bits / 8 / 1024 / 1024
    
    print(f"\n📊 AVERAGE CASE:")
    print(f"  Baseline Order-5: {baseline_mb:.1f} MB")
    print(f"  Our Combined: {combined_mb:.1f} MB")
    print(f"  SAVINGS: {savings_mb:.1f} MB")
    
    # Conservative case
    conservative_baseline_bits = min_baseline_bpc * enwik9_chars
    conservative_combined_bits = max_combined_bpc * enwik9_chars
    
    conservative_baseline_mb = conservative_baseline_bits / 8 / 1024 / 1024
    conservative_combined_mb = conservative_combined_bits / 8 / 1024 / 1024
    conservative_savings_mb = (conservative_baseline_bits - conservative_combined_bits) / 8 / 1024 / 1024
    
    print(f"\n🎯 CONSERVATIVE CASE:")
    print(f"  Baseline Order-5: {conservative_baseline_mb:.1f} MB")
    print(f"  Our Combined: {conservative_combined_mb:.1f} MB")
    print(f"  SAVINGS: {conservative_savings_mb:.1f} MB")
    
    # World record
    print("\n" + "=" * 70)
    print("🏆 WORLD RECORD CALCULATION")
    print("=" * 70)
    
    # Assume our Order-5 baseline is similar to other Order-5 compressors (~135 MB)
    estimated_baseline = 135.0
    
    # Our improvement
    percent_improvement = (savings_mb / baseline_mb) * 100
    our_savings = estimated_baseline * (percent_improvement / 100)
    our_result = estimated_baseline - our_savings
    
    print(f"\n📊 Based on {percent_improvement:.2f}% improvement:")
    print(f"  Typical Order-5 baseline: {estimated_baseline:.1f} MB")
    print(f"  Our improvement: -{our_savings:.1f} MB")
    print(f"  OUR RESULT: {our_result:.1f} MB")
    
    record = 114.0
    print(f"  World record: {record:.1f} MB")
    
    if our_result < record:
        diff = record - our_result
        print(f"\n  🏆 BEAT RECORD BY {diff:.1f} MB! #1! 🥇")
    else:
        diff = our_result - record
        print(f"\n  ✅ {diff:.1f} MB from #1")
    
    # Compare with enwik_10mb results
    print("\n" + "=" * 70)
    print("🔍 COMPARISON WITH ENWIK_10MB TESTS")
    print("=" * 70)
    
    print(f"\nEnwik_10mb tests: 60 MB savings (conservative)")
    print(f"Enwik8 calculation: {savings_mb:.1f} MB savings (average)")
    print(f"Enwik8 conservative: {conservative_savings_mb:.1f} MB savings")
    
    if abs(savings_mb - 60) < 10:
        print(f"\n✅ CONSISTENT! Results align!")
    else:
        print(f"\n⚠️ DIFFERENT! Need to understand why!")
        print(f"\nPossible reasons:")
        print(f"  1. Training data size (10 MB vs 10 MB)")
        print(f"  2. Test section size (500 KB vs 1 MB)")
        print(f"  3. Content distribution differences")
        print(f"  4. Measurement methodology")

if __name__ == "__main__":
    analyze_calculation_error()
