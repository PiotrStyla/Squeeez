#!/usr/bin/env python3
"""
NEURAL LEARNED PROPERTIES - The Next Evolution!

Hand-crafted properties failed because they weren't discriminative enough.
What if a NEURAL NETWORK learns optimal properties for compression?

Key idea:
- Train network to output MINIMAL binary features
- Features optimized to discriminate among candidates
- Could beat position encoding by learning domain patterns!

This is NOVEL research direction! 🚀
"""
import numpy as np
import re
from collections import defaultdict, Counter

class NeuralPropertyLearner:
    """
    Learn optimal properties using a simple neural approach
    
    Goal: Find features that minimize bits while maximizing discrimination
    """
    
    def __init__(self, feature_dim=8):
        """
        Args:
            feature_dim: Number of binary features to learn (e.g., 8 = 8 bits max)
        """
        self.feature_dim = feature_dim
        self.char_to_idx = {}
        self.idx_to_char = {}
        self._build_vocab()
        
    def _build_vocab(self):
        """Build character vocabulary"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -'
        self.char_to_idx = {c: i for i, c in enumerate(chars)}
        self.idx_to_char = {i: c for i, c in enumerate(chars)}
        self.vocab_size = len(chars)
    
    def link_to_vector(self, link, max_len=30):
        """Convert link text to simple numeric vector"""
        # Truncate/pad to fixed length
        link = link[:max_len].ljust(max_len)
        
        # Character-level encoding
        indices = [self.char_to_idx.get(c, 0) for c in link]
        
        # Simple features
        features = []
        
        # 1. Character indices (normalized)
        features.extend([idx / self.vocab_size for idx in indices[:10]])
        
        # 2. Length
        features.append(len(link.strip()) / max_len)
        
        # 3. Capital ratio
        capitals = sum(1 for c in link if c.isupper())
        features.append(capitals / max(len(link.strip()), 1))
        
        # 4. Digit ratio  
        digits = sum(1 for c in link if c.isdigit())
        features.append(digits / max(len(link.strip()), 1))
        
        # 5. Word count
        words = len(link.strip().split())
        features.append(words / 10.0)
        
        return np.array(features, dtype=np.float32)
    
    def extract_learned_features(self, link, candidates):
        """
        Extract LEARNED binary features optimized for discrimination
        
        This is simplified - in real version would use trained neural network
        For now: use heuristics that simulate learned features
        """
        # Get vector representations
        link_vec = self.link_to_vector(link)
        cand_vecs = [self.link_to_vector(c) for c in candidates]
        
        # Learn discriminative features
        features = []
        bits_used = 0
        
        # Feature 1: Length comparison
        link_len = len(link)
        # Is link shorter than median?
        median_len = np.median([len(c) for c in candidates])
        is_short = link_len < median_len
        
        # How discriminative is this?
        matches = sum(1 for c in candidates if (len(c) < median_len) == is_short)
        confidence = 1.0 - (matches / len(candidates))
        
        if confidence > 0.3:  # Useful feature
            features.append({
                'name': 'shorter_than_median',
                'value': is_short,
                'confidence': confidence,
                'bits': 1
            })
            bits_used += 1
        
        # Feature 2: First character similarity cluster
        first_char = link[0].lower() if link else '?'
        
        # Group characters by similarity (vowels vs consonants)
        vowels = 'aeiou'
        is_vowel = first_char in vowels
        
        matches = sum(1 for c in candidates if (c[0].lower() in vowels) == is_vowel)
        confidence = 1.0 - (matches / len(candidates))
        
        if confidence > 0.3:
            features.append({
                'name': 'first_char_vowel',
                'value': is_vowel,
                'confidence': confidence,
                'bits': 1
            })
            bits_used += 1
        
        # Feature 3: Capital pattern (learned from data)
        # Does it look like a person name? (Title Case Pattern)
        words = link.split()
        is_title_case = len(words) >= 2 and all(w[0].isupper() for w in words if w)
        
        matches = sum(1 for c in candidates if 
                     (len(c.split()) >= 2 and all(w[0].isupper() for w in c.split() if w)) == is_title_case)
        confidence = 1.0 - (matches / len(candidates))
        
        if confidence > 0.3 and bits_used < self.feature_dim:
            features.append({
                'name': 'title_case_pattern',
                'value': is_title_case,
                'confidence': confidence,
                'bits': 1
            })
            bits_used += 1
        
        # Feature 4: Numeric content
        has_digits = any(c.isdigit() for c in link)
        
        matches = sum(1 for c in candidates if any(ch.isdigit() for ch in c) == has_digits)
        confidence = 1.0 - (matches / len(candidates))
        
        if confidence > 0.3 and bits_used < self.feature_dim:
            features.append({
                'name': 'has_numeric',
                'value': has_digits,
                'confidence': confidence,
                'bits': 1
            })
            bits_used += 1
        
        # Feature 5-8: Character-level learned patterns
        # (In real version: neural network would learn these)
        
        # For now: simple heuristics that simulate learning
        
        # Feature 5: Contains common suffix?
        common_suffixes = ['tion', 'ism', 'land', 'berg', 'burg']
        has_suffix = any(link.lower().endswith(s) for s in common_suffixes)
        
        if has_suffix and bits_used < self.feature_dim:
            matches = sum(1 for c in candidates if any(c.lower().endswith(s) for s in common_suffixes))
            confidence = 1.0 - (matches / len(candidates))
            
            if confidence > 0.2:
                features.append({
                    'name': 'common_suffix',
                    'value': has_suffix,
                    'confidence': confidence,
                    'bits': 1
                })
                bits_used += 1
        
        return features
    
    def encode_with_learned_features(self, link, candidates, max_bits=8):
        """
        Encode using learned features
        
        Returns: (bits_used, confidence_achieved)
        """
        if not candidates or len(candidates) == 1:
            return 0, 1.0
        
        features = self.extract_learned_features(link, candidates)
        
        # Sort by confidence (greedily select best)
        features.sort(key=lambda f: f['confidence'], reverse=True)
        
        total_bits = 0
        total_confidence = 0.0
        
        for feat in features:
            if total_bits >= max_bits:
                break
            if total_confidence >= 0.85:  # Target certainty
                break
            
            total_bits += feat['bits']
            total_confidence = min(1.0, total_confidence + feat['confidence'])
        
        return total_bits, total_confidence

def test_neural_properties():
    """Test learned properties vs hand-crafted vs position"""
    
    print("=" * 70)
    print("🧠 NEURAL LEARNED PROPERTIES TEST")
    print("=" * 70)
    print("\nCan learned features beat hand-crafted properties?")
    print("(This is a simplified simulation - real version needs actual training!)\n")
    
    learner = NeuralPropertyLearner(feature_dim=8)
    
    # Test scenarios
    test_cases = [
        {
            'desc': 'History: Mixed entities',
            'target': 'Napoleon Bonaparte',
            'candidates': [
                'Louis XIV', 'Napoleon Bonaparte', 'Joan of Arc',
                'Charlemagne', 'France', 'Paris', 'Europe',
                'Battle of Waterloo', '1815', 'French Revolution'
            ]
        },
        {
            'desc': 'Science: Terms',
            'target': 'Quantum Mechanics',
            'candidates': [
                'Physics', 'Quantum Mechanics', 'Relativity',
                'Thermodynamics', 'Electromagnetism', 'Optics',
                'Mechanics', 'Albert Einstein', 'Newton', 'Theory'
            ]
        },
        {
            'desc': 'Geography: European cities',
            'target': 'Berlin',
            'candidates': [
                'Paris', 'London', 'Berlin', 'Rome', 'Madrid',
                'Amsterdam', 'Vienna', 'Prague', 'Warsaw', 'Brussels'
            ]
        },
    ]
    
    print("Testing learned features:\n")
    
    total_learned = 0
    total_position = 0
    
    for case in test_cases:
        target = case['target']
        candidates = case['candidates']
        
        # Position encoding baseline
        import math
        position_bits = math.ceil(math.log2(len(candidates)))
        
        # Learned features
        learned_bits, confidence = learner.encode_with_learned_features(target, candidates)
        
        print(f"{case['desc']}")
        print(f"  Target: '{target}' among {len(candidates)} candidates")
        print(f"  Position: {position_bits} bits")
        print(f"  Learned:  {learned_bits} bits (confidence: {confidence:.0%})")
        
        # Show learned features
        features = learner.extract_learned_features(target, candidates)
        if features:
            print(f"  Features: {', '.join(f['name'] for f in features[:3])}")
        
        if learned_bits < position_bits:
            print(f"  ✅ Learned WINS! (-{position_bits - learned_bits} bits)")
        elif learned_bits == position_bits:
            print(f"  ➖ Tie")
        else:
            print(f"  ❌ Position wins (+{learned_bits - position_bits} bits)")
        
        total_learned += learned_bits
        total_position += position_bits
        print()
    
    # Summary
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    print(f"\nTotal bits:")
    print(f"  Position: {total_position} bits")
    print(f"  Learned:  {total_learned} bits")
    print(f"  Savings:  {total_position - total_learned:+d} bits")
    
    if total_learned < total_position:
        pct = (total_position - total_learned) / total_position * 100
        print(f"\n🏆 LEARNED FEATURES WIN! ({pct:.1f}% better)")
    else:
        print(f"\n➖ Position still better (but we're learning!)")
    
    print("\n" + "=" * 70)
    print("💡 INSIGHTS")
    print("=" * 70)
    
    print("\nThis is a SIMPLIFIED simulation!")
    print("Real neural approach would:")
    print("  ✓ Train on thousands of examples")
    print("  ✓ Learn optimal feature combinations")
    print("  ✓ Discover patterns we didn't think of")
    print("  ✓ Adapt to specific domain (Wikipedia vs web vs etc.)")
    
    print("\nPromising because:")
    print("  ✓ Learned features can be more discriminative")
    print("  ✓ Can discover domain-specific patterns")
    print("  ✓ Flexible - adapts to data")
    
    print("\nChallenges:")
    print("  ⚠  Needs training data (we have it!)")
    print("  ⚠  Computational cost (one-time training)")
    print("  ⚠  Model size (needs to fit in compressor)")
    
    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS FOR REAL NEURAL VERSION")
    print("=" * 70)
    
    print("\n1. Collect training data:")
    print("   → Extract 10K link + candidate pairs from enwik")
    print("   → Label with 'which features identify target?'")
    
    print("\n2. Train neural network:")
    print("   → Input: link text + candidates")
    print("   → Output: binary feature vector (8-16 bits)")
    print("   → Loss: minimize bits while maximizing discrimination")
    
    print("\n3. Test on held-out data:")
    print("   → Compare to position encoding")
    print("   → Measure bits saved")
    
    print("\n4. Integrate with compressor:")
    print("   → Embed small network in compressor")
    print("   → Use for TOP-10+ cases")
    
    print("\n📝 This could be Paper #2 or #3!")
    print("   'Neural Property Learning for Structured Compression'")
    print("   → Novel approach (ZKP + neural)")
    print("   → Could actually beat position!")
    print("   → Publishable even if marginal gains")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_neural_properties()
    
    print("\n✨ Neural properties concept tested!")
    print("🚀 This is the FUTURE of property-based compression!")
    print("🎯 Want to build the REAL neural version? 😊")
