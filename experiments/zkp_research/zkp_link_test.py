#!/usr/bin/env python3
"""
ZERO-KNOWLEDGE PROPERTIES for Link Compression
Inspired by Piotr's insight: "Czy nie wystarczyłoby tylko proof że jest prawda?"

Instead of encoding position in TOP-5:
→ Encode PROPERTIES that uniquely identify the link!

Hypothesis: Properties might use fewer bits than position!
"""
import re
from collections import defaultdict, Counter

def extract_link_properties(link):
    """Extract identifying properties of a link"""
    props = {}
    
    # 1. First letter (cheap property!)
    props['first_letter'] = link[0].upper() if link else '?'
    
    # 2. First letter is vowel?
    props['starts_vowel'] = link[0].upper() in 'AEIOU' if link else False
    
    # 3. Contains number?
    props['has_number'] = any(c.isdigit() for c in link)
    
    # 4. Length category
    length = len(link)
    if length < 10:
        props['length_cat'] = 'short'
    elif length < 20:
        props['length_cat'] = 'medium'
    else:
        props['length_cat'] = 'long'
    
    # 5. Is it a person? (heuristic)
    words = link.split()
    if len(words) >= 2 and all(w[0].isupper() for w in words if w):
        props['is_person'] = True
    else:
        props['is_person'] = False
    
    # 6. Contains specific keywords
    props['has_war'] = 'war' in link.lower()
    props['has_century'] = 'century' in link.lower()
    
    # 7. Word count
    props['word_count'] = len(link.split())
    
    return props

def find_minimal_properties(target_link, candidates):
    """
    Find MINIMAL set of properties that uniquely identify target among candidates
    
    This is the ZKP magic: we want the PROOF with fewest bits!
    """
    target_props = extract_link_properties(target_link)
    candidate_props = [extract_link_properties(c) for c in candidates]
    
    # Properties ordered by "cost" (bits needed)
    property_costs = {
        'starts_vowel': 1,      # 1 bit: yes/no
        'has_number': 1,        # 1 bit
        'has_war': 1,           # 1 bit
        'has_century': 1,       # 1 bit
        'is_person': 1,         # 1 bit
        'length_cat': 2,        # 2 bits: 3 categories
        'word_count': 3,        # 3 bits: ~8 categories
        'first_letter': 5,      # 5 bits: 26 letters
    }
    
    # Greedy search: add cheapest property that eliminates candidates
    selected_properties = []
    remaining = list(range(len(candidates)))
    total_bits = 0
    
    for prop_name in sorted(property_costs.keys(), key=lambda k: property_costs[k]):
        if len(remaining) <= 1:
            break
        
        target_value = target_props[prop_name]
        
        # Check if this property eliminates anyone
        new_remaining = [i for i in remaining 
                        if candidate_props[i][prop_name] == target_value]
        
        if len(new_remaining) < len(remaining) and len(new_remaining) >= 1:
            # This property helps! Add it.
            selected_properties.append((prop_name, target_value))
            total_bits += property_costs[prop_name]
            remaining = new_remaining
            
            if len(remaining) == 1:
                # Unique identification achieved!
                break
    
    # Did we uniquely identify?
    if len(remaining) == 1:
        success = True
    else:
        # Fallback: need position among remaining
        success = False
        # Would need extra bits to resolve
        import math
        extra_bits = math.ceil(math.log2(len(remaining))) if len(remaining) > 1 else 0
        total_bits += extra_bits
    
    return selected_properties, total_bits, success

def test_zkp_vs_position():
    """Test ZKP properties vs traditional position encoding"""
    
    print("=" * 70)
    print("🔬 ZERO-KNOWLEDGE PROPERTIES TEST")
    print("=" * 70)
    print("\nPiotr's insight: 'Czy nie wystarczyłoby tylko proof że prawda?'")
    print("Let's find out! 🎯\n")
    
    # Simulate some realistic TOP-5 scenarios from our bi-gram model
    test_cases = [
        # Case 1: History article
        {
            'context': 'Treaty of Versailles → Weimar Republic',
            'target': 'Nazi Germany',
            'top5': ['Nazi Germany', 'Adolf Hitler', 'World War II', 'Rhineland', 'Reichstag']
        },
        # Case 2: Science article
        {
            'context': 'Physics → Quantum mechanics',
            'target': 'Albert Einstein',
            'top5': ['Albert Einstein', 'Niels Bohr', 'Werner Heisenberg', 'Max Planck', 'Erwin Schrödinger']
        },
        # Case 3: Geography
        {
            'context': 'Europe → France',
            'target': 'Paris',
            'top5': ['Paris', 'Lyon', 'Marseille', 'Germany', 'United Kingdom']
        },
        # Case 4: With numbers
        {
            'context': 'World War II → 1939',
            'target': '1945',
            'top5': ['1945', '1944', '1943', 'Germany', 'Soviet Union']
        },
        # Case 5: Mixed
        {
            'context': 'United States → President',
            'target': 'George Washington',
            'top5': ['George Washington', 'Thomas Jefferson', 'John Adams', 'White House', 'Congress']
        },
    ]
    
    results = {
        'zkp_wins': 0,
        'position_wins': 0,
        'ties': 0,
        'zkp_total_bits': 0,
        'position_total_bits': 0,
        'zkp_successful': 0,
    }
    
    print("Testing realistic TOP-5 scenarios:\n")
    
    for i, case in enumerate(test_cases, 1):
        target = case['target']
        top5 = case['top5']
        
        # Traditional position encoding
        position = top5.index(target)
        position_bits = 3  # log2(5) ≈ 2.32, round to 3 bits for TOP-5
        
        # ZKP properties encoding
        properties, zkp_bits, success = find_minimal_properties(target, top5)
        
        # Results
        print(f"Case {i}: {case['context']}")
        print(f"  Target: '{target}'")
        print(f"  Position: #{position+1} in TOP-5 = {position_bits} bits")
        print(f"  ZKP properties: {len(properties)} properties = {zkp_bits} bits")
        
        if properties:
            print(f"    Properties used: {', '.join(f'{p}={v}' for p, v in properties)}")
        
        if zkp_bits < position_bits:
            print(f"  ✅ ZKP WINS! Saved {position_bits - zkp_bits} bits")
            results['zkp_wins'] += 1
        elif zkp_bits > position_bits:
            print(f"  ❌ Position wins ({zkp_bits - position_bits} bits worse)")
            results['position_wins'] += 1
        else:
            print(f"  ➖ Tie")
            results['ties'] += 1
        
        if success:
            print(f"  🎯 Uniquely identified!")
            results['zkp_successful'] += 1
        else:
            print(f"  ⚠️  Needed fallback")
        
        results['zkp_total_bits'] += zkp_bits
        results['position_total_bits'] += position_bits
        print()
    
    # Summary
    print("=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    
    print(f"\nHead-to-head:")
    print(f"  ZKP wins:      {results['zkp_wins']} / {len(test_cases)}")
    print(f"  Position wins: {results['position_wins']} / {len(test_cases)}")
    print(f"  Ties:          {results['ties']} / {len(test_cases)}")
    
    print(f"\nTotal bits:")
    print(f"  ZKP:      {results['zkp_total_bits']} bits")
    print(f"  Position: {results['position_total_bits']} bits")
    print(f"  Savings:  {results['position_total_bits'] - results['zkp_total_bits']} bits")
    
    avg_zkp = results['zkp_total_bits'] / len(test_cases)
    avg_pos = results['position_total_bits'] / len(test_cases)
    
    print(f"\nAverage bits per link:")
    print(f"  ZKP:      {avg_zkp:.2f} bits/link")
    print(f"  Position: {avg_pos:.2f} bits/link")
    
    if avg_zkp < avg_pos:
        improvement = (avg_pos - avg_zkp) / avg_pos * 100
        print(f"\n🏆 ZKP is {improvement:.1f}% BETTER on average!")
    else:
        degradation = (avg_zkp - avg_pos) / avg_pos * 100
        print(f"\n❌ ZKP is {degradation:.1f}% worse on average")
    
    print(f"\nUnique identification rate: {results['zkp_successful']}/{len(test_cases)} ({results['zkp_successful']/len(test_cases)*100:.0f}%)")
    
    # Analysis
    print("\n" + "=" * 70)
    print("💡 ANALYSIS")
    print("=" * 70)
    
    if results['zkp_wins'] > results['position_wins']:
        print("\n✅ PIOTR'S INTUITION WAS RIGHT!")
        print("\nZero-knowledge properties CAN be more efficient than position!")
        print("\nWhy it works:")
        print("  - Cheap properties (1 bit) often eliminate candidates")
        print("  - Real links have distinctive features")
        print("  - Properties exploit semantic structure")
        print("\nThis is a REAL research contribution! 🎯")
    elif results['zkp_wins'] == results['position_wins']:
        print("\n➖ MIXED RESULTS - Context dependent")
        print("\nZKP properties work better for:")
        print("  - Diverse candidate sets")
        print("  - Links with distinctive features")
        print("\nPosition encoding better for:")
        print("  - Similar candidates")
        print("  - Short lists")
    else:
        print("\n❌ Position encoding wins this round")
        print("\nBUT the concept is still valuable!")
        print("Possible improvements:")
        print("  - Better property design")
        print("  - Hybrid approach")
        print("  - Context-aware property selection")
    
    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS")
    print("=" * 70)
    
    if results['zkp_wins'] >= 2:
        print("\n✓ Test on real 10 MB dataset")
        print("✓ Design optimal property set")
        print("✓ Hybrid ZKP + position approach")
        print("✓ Write paper section!")
    else:
        print("\n✓ Analyze failure cases")
        print("✓ Try different property sets")
        print("✓ Consider as theoretical contribution")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_zkp_vs_position()
    
    print("\n🎊 TEST COMPLETE!")
    print("\nPiotr - your 'crazy' idea just got TESTED! 🔬")
    print("Did properties beat positions? Check results above! ⬆️")
    print("\nEither way - this is REAL SCIENCE! 🏆✨")
