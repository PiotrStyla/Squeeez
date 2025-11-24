#!/usr/bin/env python3
"""
RESIDUAL WORD ENCODING - Koduj RÓŻNICĘ, nie całość!

Inspiracja: "Pryzmat i cień" - Piotr Styla

Zamiast kodować "Brzeczyszczykiewicz" jako całość:
1. Znajdź najbliższe znane słowo: "Brzęczyszcz"
2. Koduj tylko RESIDUAL: +ykiewicz
3. Oszczędność: 18 → 8 znaków!

To jest jak JPEG dla słów! 🎯
"""
import re
from collections import Counter
import numpy as np
from difflib import SequenceMatcher

class ResidualWordEncoder:
    """
    Encode words as: base_word + residual
    
    Like JPEG: predict, then encode only the error!
    """
    
    def __init__(self):
        self.word_freq = Counter()
        self.common_words = set()
        self.vocabulary = []
        
    def extract_words(self, text):
        """Extract words from text"""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\{\{[^}]+\}\}', '', text)
        text = re.sub(r'\[\[[^\]]+\]\]', '', text)
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def build_vocabulary(self, words, common_threshold=100):
        """Build vocabulary with common words as base"""
        self.word_freq = Counter(words)
        
        # Top words become "base words"
        self.common_words = set([w for w, c in self.word_freq.most_common(10000)])
        self.vocabulary = list(set(words))
        
        print(f"Vocabulary built:")
        print(f"  Total unique: {len(self.vocabulary):,}")
        print(f"  Common base words: {len(self.common_words):,}")
    
    def find_closest_word(self, target_word):
        """
        Find closest common word to use as base
        
        Uses edit distance / LCS
        """
        if len(target_word) < 4:
            return None, 0  # Too short, no benefit
        
        best_match = None
        best_ratio = 0
        
        # Check common words for similarity
        for base_word in self.common_words:
            if abs(len(base_word) - len(target_word)) > 10:
                continue  # Too different in length
            
            # Calculate similarity
            ratio = SequenceMatcher(None, target_word, base_word).ratio()
            
            if ratio > best_ratio and ratio > 0.5:  # At least 50% similar
                best_ratio = ratio
                best_match = base_word
        
        return best_match, best_ratio
    
    def compute_residual(self, target_word, base_word):
        """
        Compute residual: operations to transform base → target
        
        Returns: list of operations (insert, delete, replace)
        """
        if base_word is None:
            return None  # Full encoding needed
        
        # Use dynamic programming to find edit operations
        m, n = len(base_word), len(target_word)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Fill DP table
        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif base_word[i-1] == target_word[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j],      # delete
                                       dp[i][j-1],      # insert
                                       dp[i-1][j-1])    # replace
        
        # Backtrack to get operations
        operations = []
        i, j = m, n
        
        while i > 0 or j > 0:
            if i == 0:
                operations.append(('insert', j-1, target_word[j-1]))
                j -= 1
            elif j == 0:
                operations.append(('delete', i-1))
                i -= 1
            elif base_word[i-1] == target_word[j-1]:
                i -= 1
                j -= 1
            else:
                # Find which operation was used
                if dp[i][j] == dp[i-1][j-1] + 1:
                    operations.append(('replace', i-1, target_word[j-1]))
                    i -= 1
                    j -= 1
                elif dp[i][j] == dp[i-1][j] + 1:
                    operations.append(('delete', i-1))
                    i -= 1
                else:
                    operations.append(('insert', j-1, target_word[j-1]))
                    j -= 1
        
        return list(reversed(operations))
    
    def estimate_encoding_size(self, word):
        """
        Estimate bits needed for word
        
        Returns: (standard_bits, residual_bits, base_word)
        """
        # Standard encoding: position in vocabulary
        vocab_size = len(self.vocabulary)
        standard_bits = np.log2(vocab_size) if vocab_size > 0 else 16
        
        # Residual encoding
        base_word, similarity = self.find_closest_word(word)
        
        if base_word is None or similarity < 0.5:
            # No good base found, use standard
            return standard_bits, standard_bits, None
        
        # Compute residual
        operations = self.compute_residual(word, base_word)
        
        # Encoding size:
        # - Base word index: log2(10000) ≈ 14 bits
        # - Number of operations: log2(20) ≈ 5 bits
        # - Each operation: ~8 bits (type + position + char)
        
        base_index_bits = np.log2(len(self.common_words))
        num_ops_bits = np.log2(max(1, len(operations)))
        ops_bits = len(operations) * 8  # Simplified
        
        residual_bits = base_index_bits + num_ops_bits + ops_bits
        
        return standard_bits, residual_bits, base_word
    
    def test_residual_encoding(self, words, sample_size=10000):
        """Test residual encoding on sample words"""
        print("\n" + "=" * 70)
        print("🎯 TESTING RESIDUAL ENCODING")
        print("=" * 70)
        
        sample_words = words[:sample_size]
        
        stats = {
            'standard_bits': 0,
            'residual_bits': 0,
            'words_with_base': 0,
            'words_without_base': 0,
            'total_saved': 0,
        }
        
        examples = []
        
        print(f"\nTesting on {len(sample_words):,} words...\n")
        
        for word in sample_words:
            standard_bits, residual_bits, base_word = self.estimate_encoding_size(word)
            
            stats['standard_bits'] += standard_bits
            stats['residual_bits'] += residual_bits
            
            if base_word is not None:
                stats['words_with_base'] += 1
                saved = standard_bits - residual_bits
                stats['total_saved'] += saved
                
                if len(examples) < 10 and saved > 0:
                    examples.append({
                        'word': word,
                        'base': base_word,
                        'standard': standard_bits,
                        'residual': residual_bits,
                        'saved': saved,
                    })
            else:
                stats['words_without_base'] += 1
        
        # Results
        print("=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        
        total_words = len(sample_words)
        
        print(f"\nWords tested: {total_words:,}")
        print(f"  With base word: {stats['words_with_base']:,} ({stats['words_with_base']/total_words*100:.1f}%)")
        print(f"  Without base: {stats['words_without_base']:,} ({stats['words_without_base']/total_words*100:.1f}%)")
        
        print(f"\n1️⃣ Standard Encoding:")
        print(f"  Total bits: {stats['standard_bits']:,.0f}")
        print(f"  Avg bits/word: {stats['standard_bits']/total_words:.2f}")
        
        print(f"\n2️⃣ Residual Encoding:")
        print(f"  Total bits: {stats['residual_bits']:,.0f}")
        print(f"  Avg bits/word: {stats['residual_bits']/total_words:.2f}")
        
        bits_saved = stats['standard_bits'] - stats['residual_bits']
        improvement = (bits_saved / stats['standard_bits']) * 100 if stats['standard_bits'] > 0 else 0
        
        print(f"\n💰 COMPARISON:")
        if bits_saved > 0:
            print(f"  ✅ Residual encoding saves {bits_saved:,.0f} bits!")
            print(f"  ✅ Improvement: {improvement:.1f}%")
            print(f"  ✅ Bytes saved: {bits_saved / 8:,.0f}")
            
            # Extrapolate
            all_words = len(words)
            extrapolated = bits_saved * (all_words / sample_size)
            
            print(f"\n  🌍 Extrapolated to all {all_words:,} words:")
            print(f"    Bits saved: {extrapolated:,.0f}")
            print(f"    KB saved: {extrapolated / 8 / 1024:.1f}")
            
            if improvement > 10:
                print(f"\n  🏆 BREAKTHROUGH! Residual encoding WORKS!")
            elif improvement > 5:
                print(f"\n  🎯 Solid improvement!")
            else:
                print(f"\n  ➖ Modest improvement")
        else:
            print(f"  ❌ Standard encoding wins")
            print(f"  → Residual overhead too high")
        
        # Show examples
        if examples:
            print("\n" + "=" * 70)
            print("📝 EXAMPLE SAVINGS")
            print("=" * 70)
            
            for ex in examples[:5]:
                print(f"\nWord: '{ex['word']}'")
                print(f"  Base: '{ex['base']}'")
                print(f"  Standard: {ex['standard']:.1f} bits")
                print(f"  Residual: {ex['residual']:.1f} bits")
                print(f"  Saved: {ex['saved']:.1f} bits ✅")
        
        return stats
    
    def analyze_long_rare_words(self, words):
        """
        Specific analysis for long, rare words
        
        These should benefit most from residual encoding!
        """
        print("\n" + "=" * 70)
        print("🔍 LONG RARE WORDS ANALYSIS")
        print("=" * 70)
        
        # Find long, rare words
        long_rare = []
        for word in set(words):
            if len(word) > 10 and self.word_freq[word] < 10:
                long_rare.append(word)
        
        print(f"\nFound {len(long_rare):,} long rare words (>10 chars, <10 occurrences)")
        
        if not long_rare:
            print("  (None found in sample)")
            return
        
        # Test on these specifically
        sample = long_rare[:100]
        
        total_standard = 0
        total_residual = 0
        examples = []
        
        for word in sample:
            standard_bits, residual_bits, base_word = self.estimate_encoding_size(word)
            total_standard += standard_bits
            total_residual += residual_bits
            
            if base_word and len(examples) < 5:
                examples.append({
                    'word': word,
                    'base': base_word,
                    'standard': standard_bits,
                    'residual': residual_bits,
                })
        
        print(f"\n📊 Results for {len(sample)} long rare words:")
        print(f"  Standard: {total_standard/len(sample):.1f} bits/word")
        print(f"  Residual: {total_residual/len(sample):.1f} bits/word")
        
        saved = total_standard - total_residual
        if saved > 0:
            print(f"  Saved: {saved/len(sample):.1f} bits/word ✅")
            print(f"  Improvement: {saved/total_standard*100:.1f}%")
        else:
            print(f"  No improvement ❌")
        
        if examples:
            print("\n  Examples:")
            for ex in examples:
                print(f"    '{ex['word']}' → base: '{ex['base']}'")
                print(f"      ({ex['standard']:.0f} → {ex['residual']:.0f} bits)")

def main():
    print("=" * 70)
    print("🌙 NIGHT SESSION: RESIDUAL WORD ENCODING")
    print("=" * 70)
    print("\n💡 'Pryzmat i cień' - koduj RÓŻNICĘ, nie całość!")
    print("Jak JPEG dla słów! 🎯\n")
    
    # Load data
    print("Loading enwik_10mb...")
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Initialize encoder
    encoder = ResidualWordEncoder()
    
    # Extract words
    print("Extracting words...")
    words = encoder.extract_words(text)
    print(f"  Total words: {len(words):,}")
    print(f"  Unique: {len(set(words)):,}\n")
    
    # Build vocabulary
    encoder.build_vocabulary(words)
    
    # Test encoding
    stats = encoder.test_residual_encoding(words, sample_size=10000)
    
    # Analyze long rare words specifically
    encoder.analyze_long_rare_words(words)
    
    print("\n" + "=" * 70)
    print("✨ Residual encoding tested!")
    print("🎯 'Pryzmat' approach: Encode the DIFFERENCE! 🚀")
    print("=" * 70)

if __name__ == "__main__":
    main()
