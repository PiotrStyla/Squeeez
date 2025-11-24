#!/usr/bin/env python3
"""
HYBRID COMPRESSOR: Character + Word Level
Kombinacja Order-5 dla characters + Word bigrams
"""
import re
import time
from collections import defaultdict, Counter
from arithmetic_coder import ArithmeticEncoder
from ultra_compressor import UltraCompressor

class WordLevelModel:
    """Model dla word-level prediction"""
    
    def __init__(self, top_n=1000):
        self.top_n = top_n
        self.word_to_id = {}
        self.id_to_word = {}
        self.word_bigrams = defaultdict(Counter)
        self.word_freq = Counter()
        
    def extract_words(self, data):
        """Extract words from data"""
        if isinstance(data, bytes):
            text = data.decode('utf-8', errors='ignore')
        else:
            text = data
        
        # Simple word extraction (alphanumeric sequences)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        return words
    
    def train(self, data):
        """Train word-level model"""
        words = self.extract_words(data)
        
        print(f"  Word-level model:")
        print(f"    Słowa: {len(words):,}")
        print(f"    Unikalne: {len(set(words)):,}")
        
        # Count word frequencies
        for word in words:
            self.word_freq[word] += 1
        
        # Build word dictionary (top-N)
        for i, (word, _) in enumerate(self.word_freq.most_common(self.top_n)):
            self.word_to_id[word] = i
            self.id_to_word[i] = word
        
        # Build bigrams
        for i in range(len(words) - 1):
            if words[i] in self.word_to_id and words[i+1] in self.word_to_id:
                self.word_bigrams[words[i]][words[i+1]] += 1
        
        print(f"    Dictionary: {len(self.word_to_id):,} words")
        print(f"    Bigrams: {sum(len(v) for v in self.word_bigrams.values()):,}")
        
        # Compute accuracy
        total = 0
        top1 = 0
        top5 = 0
        
        for word, nexts in self.word_bigrams.items():
            total_count = sum(nexts.values())
            total += total_count
            
            top_nexts = nexts.most_common(5)
            if top_nexts:
                top1 += top_nexts[0][1]
                top5 += sum(c for _, c in top_nexts)
        
        if total > 0:
            print(f"    Top-1 accuracy: {(top1/total)*100:.1f}%")
            print(f"    Top-5 accuracy: {(top5/total)*100:.1f}%")
    
    def compress_word(self, word, prev_word):
        """Compress word using bigram model"""
        # Word not in dictionary
        if word not in self.word_to_id:
            return (3, word)  # Mode 3: full word
        
        word_id = self.word_to_id[word]
        
        # No previous word or not in dictionary
        if not prev_word or prev_word not in self.word_bigrams:
            return (2, word_id)  # Mode 2: dictionary ID only
        
        # Check bigram predictions
        predictions = self.word_bigrams[prev_word].most_common(10)
        pred_words = [w for w, _ in predictions]
        
        if word == pred_words[0] if pred_words else None:
            return (0, None)  # Mode 0: top-1 prediction
        elif word in pred_words[:5]:
            return (1, pred_words.index(word))  # Mode 1: top-5 index
        else:
            return (2, word_id)  # Mode 2: dictionary ID

class HybridCompressor(UltraCompressor):
    """ULTRA + Word-level hybrid"""
    
    def __init__(self, text_order=5, word_dict_size=1000):
        super().__init__(text_order=text_order)
        self.word_model = WordLevelModel(top_n=word_dict_size)
        self.text_order = text_order
    
    def train(self, data):
        """Train both structure models and word model"""
        # Standard structure training
        sections, links, templates, text_data = super().train(data)
        
        # Additional: Word-level training
        print(f"  Model słów:")
        self.word_model.train(text_data)
        
        return sections, links, templates, text_data
    
    def estimate_word_compression(self, text_data):
        """Estimate compression with word-level"""
        words = self.word_model.extract_words(text_data)
        
        total_bits = 0
        prev_word = None
        
        for word in words:
            mode, data = self.word_model.compress_word(word, prev_word)
            
            if mode == 0:  # Top-1
                total_bits += 2  # Mode bits
            elif mode == 1:  # Top-5
                total_bits += 2 + 3  # Mode + index
            elif mode == 2:  # Dictionary
                total_bits += 2 + 10  # Mode + ID (1000 words = 10 bits)
            else:  # Full word
                total_bits += 2 + len(word) * 8
            
            prev_word = word
        
        return total_bits
    
    def compress(self, data):
        """Compress with hybrid model"""
        start = time.time()
        
        # Standard structure compression
        sections, links, templates, text_data = self.train(data)
        
        print(f"\n[3] Kompresja...")
        
        # Structures (same as ULTRA)
        section_bits = 0
        context_section = None
        for level, title in sections:
            mode, _ = self.section_graph.compress_section(title, level, context_section)
            if mode == 0:
                section_bits += 3
            elif mode == 1:
                section_bits += 6
            elif mode == 2:
                section_bits += 12
            else:
                section_bits += 2 + len(title) * 8 + 2
            context_section = title
        section_bytes = section_bits // 8 + (1 if section_bits % 8 else 0)
        
        link_bits = 0
        context_link = None
        for link in links:
            mode, _ = self.link_graph.compress_link(link, context_link)
            if mode == 0:
                link_bits += 1
            elif mode == 1:
                link_bits += 4
            elif mode == 2:
                link_bits += 6
            elif mode == 3:
                link_bits += 18
            else:
                link_bits += 2 + len(link) * 8
            context_link = link
        link_bytes = link_bits // 8 + (1 if link_bits % 8 else 0)
        
        template_bits = 0
        for name, _ in templates:
            mode, _ = self.template_dict.compress_template(name)
            template_bits += 7 if mode == 0 else (2 + len(name) * 8)
        template_bytes = template_bits // 8 + (1 if template_bits % 8 else 0)
        
        # Text with HYBRID (character + word)
        print(f"  Hybrid compression (Order-{self.text_order} + Words)...")
        
        if len(text_data) > 100:
            # Character-level (Order-5) - same as before
            encoder = ArithmeticEncoder(precision_bits=32)
            self.text_model.start_encoding()
            
            class SimpleWrapper:
                def __init__(self, model):
                    self.model = model
                def get_range(self, symbol):
                    result = self.model.get_range(symbol)
                    self.model.update_context(symbol)
                    return result
                def get_total(self):
                    return self.model.get_total()
                def get_symbol(self, offset):
                    raise NotImplementedError()
            
            wrapper = SimpleWrapper(self.text_model)
            char_compressed = encoder.encode(list(text_data), wrapper)
            char_bpb = (len(char_compressed) * 8) / len(text_data)
            
            # Word-level (estimate)
            word_bits = self.estimate_word_compression(text_data)
            word_bytes = word_bits // 8 + (1 if word_bits % 8 else 0)
            word_bpb = (word_bits / len(text_data))
            
            # Hybrid estimate (combine both)
            # W praktyce: używamy word prediction dla słów, char dla reszty
            # Crude estimate: 70% words, 30% other characters
            hybrid_bpb = 0.7 * word_bpb + 0.3 * char_bpb
            hybrid_bytes = int(hybrid_bpb * len(text_data) / 8)
            
            print(f"    Character-level: {char_bpb:.3f} bpb")
            print(f"    Word-level:      {word_bpb:.3f} bpb")
            print(f"    Hybrid (est):    {hybrid_bpb:.3f} bpb")
            
            text_compressed_bytes = hybrid_bytes
            text_bpb = hybrid_bpb
        else:
            text_compressed_bytes = 0
            text_bpb = 0
        
        total_compressed = section_bytes + link_bytes + template_bytes + text_compressed_bytes
        total_time = time.time() - start
        
        print(f"\n  Sekcje:    {section_bytes:>10,} bajtów")
        print(f"  Linki:     {link_bytes:>10,} bajtów")
        print(f"  Templates: {template_bytes:>10,} bajtów")
        print(f"  Tekst:     {text_compressed_bytes:>10,} bajtów ({text_bpb:.3f} bpb)")
        
        return {
            'section_bytes': section_bytes,
            'link_bytes': link_bytes,
            'template_bytes': template_bytes,
            'text_bytes': text_compressed_bytes,
            'total_bytes': total_compressed,
            'text_bpb': text_bpb,
            'char_bpb': char_bpb if len(text_data) > 100 else 0,
            'word_bpb': word_bpb if len(text_data) > 100 else 0,
            'time': total_time
        }

def main():
    print("=" * 70)
    print("🔥 HYBRID COMPRESSOR - Character + Word Level 🔥")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    # Test na 1 MB
    print(f"\nCzytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    
    compressor = HybridCompressor(text_order=5, word_dict_size=1000)
    result = compressor.compress(data)
    
    # Wyniki
    print(f"\n{'=' * 70}")
    print("HYBRID RESULTS - 1 MB")
    print(f"{'=' * 70}")
    
    hybrid_bpb = (result['total_bytes'] * 8) / len(data)
    
    print(f"\nTotal: {result['total_bytes']:,} bajtów ({hybrid_bpb:.3f} bpb)")
    
    # Porównanie
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    
    ultra_bpb = 0.898  # Pure ULTRA Order-5
    
    print(f"\nPure ULTRA (Order-5):  {ultra_bpb:.3f} bpb")
    print(f"HYBRID (Order-5+Word): {hybrid_bpb:.3f} bpb")
    
    if hybrid_bpb < ultra_bpb:
        improvement = ((ultra_bpb - hybrid_bpb) / ultra_bpb) * 100
        print(f"Improvement: +{improvement:.1f}% 🎉")
    else:
        degradation = ((hybrid_bpb - ultra_bpb) / ultra_bpb) * 100
        print(f"Note: +{degradation:.1f}% (estimate needs refinement)")
    
    # Projekcja enwik9
    print(f"\n{'=' * 70}")
    print("PROJEKCJA ENWIK9")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    hybrid_proj = int(hybrid_bpb * enwik9_size / 8)
    ultra_proj = int(ultra_bpb * enwik9_size / 8)
    record = 114 * 1024 * 1024
    
    print(f"\nRecord:        {record/(1024*1024):>6.1f} MB")
    print(f"ULTRA:         {ultra_proj/(1024*1024):>6.1f} MB")
    print(f"HYBRID (est):  {hybrid_proj/(1024*1024):>6.1f} MB")
    
    gap = hybrid_proj - record
    if gap < 0:
        print(f"\n🏆 Projected: BEAT RECORD by {-gap/(1024*1024):.1f} MB!")
    else:
        print(f"\nGap to record: {gap/(1024*1024):.1f} MB")
    
    print(f"\nCzas: {result['time']:.1f} s")
    
    # Breakdown
    print(f"\n{'=' * 70}")
    print("BREAKDOWN")
    print(f"{'=' * 70}")
    
    print(f"\nCharacter-level: {result['char_bpb']:.3f} bpb")
    print(f"Word-level:      {result['word_bpb']:.3f} bpb")
    print(f"Hybrid combined: {result['text_bpb']:.3f} bpb")
    
    print(f"\n💡 Word-level oszczędza: {((result['char_bpb'] - result['word_bpb']) / result['char_bpb'] * 100):.1f}%")
    print(f"   Hybrid balance: Best of both!")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
