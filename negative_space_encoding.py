#!/usr/bin/env python3
"""
NEGATIVE SPACE ENCODING - Czym słowo NIE JEST

Inspiracja: Piotr Styla - Night Session Nov 24, 2025

Zamiast opisywać "Brzeczyszczykiewicz" jako B-r-z-e-c-h...
Opiszmy jako: NIE krótkie, NIE powszechne, NIE cyfry...

Każde wykluczenie zawęża przestrzeń poszukiwań!
Process of elimination = compression! 🎯
"""
import re
from collections import Counter
import numpy as np
import math

class NegativeSpaceEncoder:
    """
    Encode words by what they are NOT
    
    Hierarchy of exclusions:
    1. Frequency (NOT common)
    2. Length (NOT short)
    3. Character type (NOT digits)
    4. Pattern (NOT all-vowels)
    5. Language (NOT English)
    
    Each exclusion reduces search space!
    """
    
    def __init__(self):
        self.word_freq = Counter()
        self.vocabulary = set()
        
    def extract_words(self, text):
        """Extract words from text"""
        # Remove XML, templates, links
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\{\{[^}]+\}\}', '', text)
        text = re.sub(r'\[\[[^\]]+\]\]', '', text)
        
        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def build_frequency_tiers(self, words):
        """Build frequency tiers for exclusion"""
        self.word_freq = Counter(words)
        self.vocabulary = set(words)
        
        # Create tiers
        sorted_words = [w for w, c in self.word_freq.most_common()]
        
        tiers = {
            'top_10': set(sorted_words[:10]),
            'top_100': set(sorted_words[:100]),
            'top_1000': set(sorted_words[:1000]),
            'top_10000': set(sorted_words[:10000]) if len(sorted_words) > 10000 else set(sorted_words),
            'rare': set(sorted_words[10000:]) if len(sorted_words) > 10000 else set(),
        }
        
        print("Frequency tiers built:")
        for tier, words in tiers.items():
            print(f"  {tier}: {len(words):,} words")
        
        return tiers
    
    def classify_word(self, word):
        """
        Classify word by what it is NOT
        
        Returns hierarchy of exclusions
        """
        properties = {}
        
        # 1. FREQUENCY EXCLUSIONS
        if word in self.word_freq:
            freq_rank = sorted(self.word_freq.items(), 
                             key=lambda x: x[1], 
                             reverse=True).index((word, self.word_freq[word])) + 1
            
            properties['NOT_top10'] = freq_rank > 10
            properties['NOT_top100'] = freq_rank > 100
            properties['NOT_top1000'] = freq_rank > 1000
            properties['NOT_top10000'] = freq_rank > 10000
        else:
            properties['NOT_top10'] = True
            properties['NOT_top100'] = True
            properties['NOT_top1000'] = True
            properties['NOT_top10000'] = True
        
        # 2. LENGTH EXCLUSIONS
        length = len(word)
        properties['NOT_short'] = length > 4  # NOT 1-4 chars
        properties['NOT_medium'] = length < 5 or length > 8  # NOT 5-8 chars
        properties['NOT_long'] = length <= 12  # NOT 12+ chars
        
        # 3. CHARACTER TYPE EXCLUSIONS
        properties['NOT_digits_only'] = not word.isdigit()
        properties['NOT_alpha_only'] = not word.isalpha()
        properties['NOT_has_digits'] = not any(c.isdigit() for c in word)
        
        # 4. PATTERN EXCLUSIONS
        vowels = set('aeiou')
        consonants = set('bcdfghjklmnpqrstvwxyz')
        
        word_lower = word.lower()
        word_chars = set(word_lower)
        
        properties['NOT_all_vowels'] = not (word_chars.issubset(vowels) and len(word_chars) > 0)
        properties['NOT_all_consonants'] = not (word_chars.issubset(consonants) and len(word_chars) > 0)
        properties['NOT_starts_vowel'] = word_lower[0] not in vowels if word_lower else True
        properties['NOT_ends_vowel'] = word_lower[-1] not in vowels if word_lower else True
        
        # 5. SPECIAL PATTERNS
        properties['NOT_year'] = not (word.isdigit() and len(word) == 4)
        properties['NOT_single_char'] = len(word) > 1
        properties['NOT_capitalized'] = not (word[0].isupper() and word[1:].islower()) if len(word) > 1 else True
        
        return properties
    
    def encode_by_exclusion(self, word, properties):
        """
        Encode word using exclusion properties
        
        Returns: bit sequence
        """
        encoding = []
        
        # Use exclusions to narrow down
        # Each TRUE exclusion = 1 bit, saves more bits later!
        
        # Frequency hierarchy (most important!)
        if properties['NOT_top10']:
            encoding.append(1)  # Exclude top-10
            
            if properties['NOT_top100']:
                encoding.append(1)  # Exclude top-100
                
                if properties['NOT_top1000']:
                    encoding.append(1)  # Exclude top-1000
                    
                    if properties['NOT_top10000']:
                        encoding.append(1)  # Very rare!
                        # Now space is TINY! Can encode with fewer bits
                    else:
                        encoding.append(0)  # In top-10K
                else:
                    encoding.append(0)  # In top-1K
            else:
                encoding.append(0)  # In top-100
        else:
            encoding.append(0)  # In top-10 (encode directly, 4 bits!)
            return encoding  # Stop early for common words
        
        # Length exclusions (if rare)
        if properties['NOT_short']:
            encoding.append(1)
            
            if properties['NOT_medium']:
                encoding.append(1)  # Long word!
            else:
                encoding.append(0)  # Medium
        else:
            encoding.append(0)  # Short
        
        # Pattern exclusions
        encoding.append(1 if properties['NOT_all_vowels'] else 0)
        encoding.append(1 if properties['NOT_all_consonants'] else 0)
        encoding.append(1 if properties['NOT_has_digits'] else 0)
        
        return encoding
    
    def estimate_bits_saved(self, words):
        """
        Estimate how many bits saved vs standard encoding
        """
        print("\n" + "=" * 70)
        print("🎯 TESTING NEGATIVE SPACE ENCODING")
        print("=" * 70)
        
        # Sample words for testing
        sample_size = min(10000, len(words))
        sample_words = words[:sample_size]
        
        stats = {
            'standard_bits': 0,
            'negative_bits': 0,
            'words_tested': 0,
        }
        
        print(f"\nTesting on {sample_size:,} words...")
        
        for word in sample_words:
            # Standard encoding: position in vocabulary
            vocab_size = len(self.vocabulary)
            standard_bits = math.ceil(math.log2(vocab_size))
            
            # Negative encoding: exclusions + reduced space
            properties = self.classify_word(word)
            encoding = self.encode_by_exclusion(word, properties)
            
            # Calculate remaining space after exclusions
            space_reduction = 1.0
            
            if properties['NOT_top10']:
                space_reduction *= 0.9  # Exclude 10%
            if properties['NOT_top100']:
                space_reduction *= 0.85  # Exclude more
            if properties['NOT_top1000']:
                space_reduction *= 0.8
            if properties['NOT_top10000']:
                space_reduction *= 0.5  # Rare words
            
            if properties['NOT_short']:
                space_reduction *= 0.7
            if properties['NOT_medium']:
                space_reduction *= 0.8
            
            # Final encoding space
            remaining_space = max(1, int(vocab_size * space_reduction))
            encoding_bits = len(encoding) + math.ceil(math.log2(remaining_space))
            
            stats['standard_bits'] += standard_bits
            stats['negative_bits'] += encoding_bits
            stats['words_tested'] += 1
        
        # Results
        print("\n" + "=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        
        print(f"\nWords tested: {stats['words_tested']:,}")
        
        print(f"\n1️⃣ Standard Encoding:")
        print(f"  Total bits: {stats['standard_bits']:,}")
        print(f"  Avg bits/word: {stats['standard_bits']/stats['words_tested']:.2f}")
        
        print(f"\n2️⃣ Negative Space Encoding:")
        print(f"  Total bits: {stats['negative_bits']:,}")
        print(f"  Avg bits/word: {stats['negative_bits']/stats['words_tested']:.2f}")
        
        bits_saved = stats['standard_bits'] - stats['negative_bits']
        improvement = (bits_saved / stats['standard_bits']) * 100 if stats['standard_bits'] > 0 else 0
        
        print(f"\n💰 COMPARISON:")
        if bits_saved > 0:
            print(f"  ✅ Negative encoding saves {bits_saved:,} bits!")
            print(f"  ✅ Improvement: {improvement:.1f}%")
            print(f"  ✅ Bytes saved: {bits_saved // 8:,}")
            
            # Extrapolate to full dataset
            total_words = len(words)
            extrapolated = bits_saved * (total_words / sample_size)
            
            print(f"\n  🌍 Extrapolated to all {total_words:,} words:")
            print(f"    Bits saved: {extrapolated:,.0f}")
            print(f"    Bytes saved: {extrapolated // 8:,.0f}")
            print(f"    KB saved: {extrapolated // 8 / 1024:.1f}")
            
            if improvement > 10:
                print(f"\n  🏆 SIGNIFICANT IMPROVEMENT!")
                print(f"  → Negative space encoding WORKS!")
            elif improvement > 5:
                print(f"\n  🎯 Solid improvement!")
                print(f"  → Worth exploring further")
            else:
                print(f"\n  ➖ Modest improvement")
                print(f"  → Interesting concept, limited practical gain")
        else:
            print(f"  ❌ Standard encoding wins")
            print(f"  → Negative encoding overhead too high")
        
        return stats
    
    def show_examples(self, words):
        """Show example encodings"""
        print("\n" + "=" * 70)
        print("📝 EXAMPLE ENCODINGS")
        print("=" * 70)
        
        # Select diverse examples
        examples = []
        
        # Common word
        if 'the' in self.word_freq:
            examples.append('the')
        
        # Medium word
        if 'wikipedia' in self.word_freq:
            examples.append('wikipedia')
        
        # Rare long word
        rare_words = [w for w in words if len(w) > 12]
        if rare_words:
            examples.append(rare_words[0])
        
        # Number
        numbers = [w for w in words if w.isdigit()]
        if numbers:
            examples.append(numbers[0])
        
        print("\nShowing encoding for different word types:\n")
        
        for word in examples[:5]:
            properties = self.classify_word(word)
            encoding = self.encode_by_exclusion(word, properties)
            
            print(f"Word: '{word}'")
            print(f"  Properties (exclusions):")
            for prop, value in properties.items():
                if value:  # Show only TRUE exclusions
                    print(f"    ✓ {prop}")
            print(f"  Encoding bits: {len(encoding)}")
            print(f"  Encoding: {''.join(map(str, encoding))}")
            print()

def main():
    print("=" * 70)
    print("🌙 NIGHT SESSION: NEGATIVE SPACE ENCODING")
    print("=" * 70)
    print("\n💡 Inspired by: 'Opiszmy czym słowo NIE JEST'")
    print("Process of elimination = Compression! 🎯\n")
    
    # Load data
    print("Loading enwik_10mb...")
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Initialize encoder
    encoder = NegativeSpaceEncoder()
    
    # Extract words
    print("Extracting words...")
    words = encoder.extract_words(text)
    print(f"  Total words: {len(words):,}")
    print(f"  Unique words: {len(set(words)):,}\n")
    
    # Build frequency tiers
    tiers = encoder.build_frequency_tiers(words)
    
    # Test encoding
    stats = encoder.estimate_bits_saved(words)
    
    # Show examples
    encoder.show_examples(words)
    
    print("=" * 70)
    print("✨ Negative space encoding tested!")
    print("🎯 'Czym NIE jest' approach evaluated! 🚀")
    print("=" * 70)

if __name__ == "__main__":
    main()
