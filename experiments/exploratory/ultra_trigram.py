#!/usr/bin/env python3
"""
TRI-GRAM LINK PREDICTION
Bi-gram = 97.8%... can we get 99%+ with TRI-GRAM?

3 previous links → next link prediction!
"""
import re
import time
from collections import defaultdict, Counter
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

class TrigramLinkGraph:
    """TRI-GRAM link prediction (3 previous!)"""
    
    def __init__(self):
        self.unigram = defaultdict(Counter)
        self.bigram = defaultdict(lambda: defaultdict(Counter))
        self.trigram = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))
        self.link_frequencies = Counter()
        self.link_to_id = {}
        
    def train(self, links):
        """Train with tri-gram awareness"""
        # Frequencies
        for link in links:
            self.link_frequencies[link] += 1
        
        sorted_links = [l for l, _ in self.link_frequencies.most_common()]
        self.link_to_id = {l: i for i, l in enumerate(sorted_links)}
        
        # Unigram
        for i in range(len(links) - 1):
            self.unigram[links[i]][links[i+1]] += 1
        
        # Bigram
        for i in range(len(links) - 2):
            self.bigram[links[i]][links[i+1]][links[i+2]] += 1
        
        # TRIGRAM! (3 previous)
        for i in range(len(links) - 3):
            prev3 = links[i]
            prev2 = links[i+1]
            prev1 = links[i+2]
            next_link = links[i+3]
            self.trigram[prev3][prev2][prev1][next_link] += 1
        
        print(f"    Linki: {len(self.link_to_id):,}")
        print(f"    Unigram contexts: {len(self.unigram):,}")
        print(f"    Bigram contexts: {sum(len(d) for d in self.bigram.values()):,}")
        print(f"    Trigram contexts: {sum(sum(len(dd) for dd in d.values()) for d in self.trigram.values()):,}")
        
        # Test accuracy
        correct_uni = 0
        correct_bi = 0
        correct_tri = 0
        total_tri = 0
        
        for i in range(len(links) - 3):
            prev3 = links[i]
            prev2 = links[i+1]
            prev1 = links[i+2]
            actual = links[i+3]
            
            # Unigram
            if prev1 in self.unigram:
                uni_preds = self.unigram[prev1].most_common(1)
                if uni_preds and uni_preds[0][0] == actual:
                    correct_uni += 1
            
            # Bigram
            if prev2 in self.bigram and prev1 in self.bigram[prev2]:
                bi_preds = self.bigram[prev2][prev1].most_common(1)
                if bi_preds and bi_preds[0][0] == actual:
                    correct_bi += 1
            
            # Trigram
            if prev3 in self.trigram:
                if prev2 in self.trigram[prev3]:
                    if prev1 in self.trigram[prev3][prev2]:
                        tri_preds = self.trigram[prev3][prev2][prev1].most_common(1)
                        if tri_preds and tri_preds[0][0] == actual:
                            correct_tri += 1
            
            total_tri += 1
        
        if total_tri > 0:
            print(f"    Unigram Top-1: {correct_uni/total_tri*100:.1f}%")
            print(f"    Bigram Top-1:  {correct_bi/total_tri*100:.1f}%")
            print(f"    Trigram Top-1: {correct_tri/total_tri*100:.1f}% 🚀")
            
            if correct_tri > correct_bi:
                print(f"    → Trigram +{(correct_tri-correct_bi)/total_tri*100:.1f}% better! 🎯")
    
    def compress_link(self, link, prev_link, prev_prev_link, prev_prev_prev_link):
        """Compress with tri-gram!"""
        predictions = []
        
        # Try TRIGRAM first!
        if prev_prev_prev_link and prev_prev_link and prev_link:
            if prev_prev_prev_link in self.trigram:
                if prev_prev_link in self.trigram[prev_prev_prev_link]:
                    if prev_link in self.trigram[prev_prev_prev_link][prev_prev_link]:
                        predictions = self.trigram[prev_prev_prev_link][prev_prev_link][prev_link].most_common(50)
        
        # Fallback to bigram
        if not predictions and prev_prev_link and prev_link:
            if prev_prev_link in self.bigram:
                if prev_link in self.bigram[prev_prev_link]:
                    predictions = self.bigram[prev_prev_link][prev_link].most_common(50)
        
        # Fallback to unigram
        if not predictions and prev_link:
            if prev_link in self.unigram:
                predictions = self.unigram[prev_link].most_common(50)
        
        if predictions:
            pred_links = [l for l, _ in predictions]
            
            if link == pred_links[0]:
                return (0, None)  # Top-1: 1 bit
            elif link in pred_links[:5]:
                return (1, pred_links.index(link))  # Top-5: 5 bits
            elif link in pred_links[:50]:
                return (2, pred_links.index(link))  # Top-50: 9 bits
        
        # Dictionary
        if link in self.link_to_id:
            return (3, self.link_to_id[link])
        
        return (4, link)

class UltraTrigram:
    """ULTRA with TRI-GRAM!"""
    
    def __init__(self):
        from ultra_compressor import TemplateDictionary, SectionGraph
        
        self.text_model = ContextModel(order=5)
        self.link_graph = TrigramLinkGraph()
        self.template_dict = TemplateDictionary()  # Back to 100 for speed
        self.section_graph = SectionGraph()
    
    def extract_everything(self, data):
        """Extract"""
        all_links = []
        all_templates = []
        all_sections = []
        
        section_pattern = re.compile(rb'(={2,6})\s*([^=]+?)\s*\1')
        link_pattern = re.compile(rb'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        template_pattern = re.compile(rb'\{\{([^}|]+)')
        
        for match in section_pattern.finditer(data):
            level = len(match.group(1))
            title = match.group(2).decode('utf-8', errors='ignore').strip()
            if 0 < len(title) < 100:
                all_sections.append((level, title))
        
        for match in link_pattern.finditer(data):
            link = match.group(1).decode('utf-8', errors='ignore').strip()
            if 0 < len(link) < 100:
                all_links.append(link)
        
        for match in template_pattern.finditer(data):
            name = match.group(1).decode('utf-8', errors='ignore').strip()
            if 0 < len(name) < 100:
                all_templates.append((name, name))
        
        text_data = data
        for pattern in [section_pattern, link_pattern, template_pattern]:
            text_data = pattern.sub(b' ', text_data)
        
        return all_sections, all_links, all_templates, text_data
    
    def train(self, data):
        """Train"""
        print(f"\n[1] Trening (TRI-GRAM)...")
        
        sections, links, templates, text_data = self.extract_everything(data)
        
        if sections:
            print(f"  Sections:")
            self.section_graph.train(sections)
        
        if links:
            print(f"  TRI-GRAM Link Graph:")
            self.link_graph.train(links)
        
        if templates:
            print(f"  Templates:")
            self.template_dict.train(templates)
        
        if len(text_data) > 100:
            print(f"  Text Order-5:")
            self.text_model.train(text_data)
            print(f"    Konteksty: {len(self.text_model.contexts):,}")
        
        return sections, links, templates, text_data
    
    def compress(self, data):
        """Compress with TRI-GRAM"""
        start = time.time()
        
        sections, links, templates, text_data = self.train(data)
        
        print(f"\n[2] Kompresja (TRI-GRAM)...")
        
        # Sections
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
        
        # Links (TRI-GRAM!)
        link_bits = 0
        prev_link = None
        prev_prev_link = None
        prev_prev_prev_link = None
        
        for link in links:
            mode, _ = self.link_graph.compress_link(link, prev_link, prev_prev_link, prev_prev_prev_link)
            
            if mode == 0:
                link_bits += 1  # Top-1
            elif mode == 1:
                link_bits += 5  # Top-5
            elif mode == 2:
                link_bits += 9  # Top-50
            elif mode == 3:
                link_bits += 17  # Dict
            else:
                link_bits += 2 + len(link) * 8
            
            prev_prev_prev_link = prev_prev_link
            prev_prev_link = prev_link
            prev_link = link
        
        link_bytes = link_bits // 8 + (1 if link_bits % 8 else 0)
        
        # Templates
        template_bits = 0
        for name, _ in templates:
            mode, _ = self.template_dict.compress_template(name)
            template_bits += 7 if mode == 0 else (2 + len(name) * 8)
        template_bytes = template_bits // 8 + (1 if template_bits % 8 else 0)
        
        # Text
        print(f"  Tekst Order-5...")
        if len(text_data) > 100:
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
            text_compressed = encoder.encode(list(text_data), wrapper)
            text_bpb = (len(text_compressed) * 8) / len(text_data)
        else:
            text_compressed = b''
            text_bpb = 0
        
        total_compressed = section_bytes + link_bytes + template_bytes + len(text_compressed)
        total_time = time.time() - start
        
        print(f"\n  Sekcje:    {section_bytes:>10,} bajtów")
        print(f"  Linki:     {link_bytes:>10,} bajtów (TRI-GRAM!)")
        print(f"  Templates: {template_bytes:>10,} bajtów")
        print(f"  Tekst:     {len(text_compressed):>10,} bajtów ({text_bpb:.3f} bpb)")
        
        return {
            'total_bytes': total_compressed,
            'time': total_time
        }

def main():
    print("=" * 70)
    print("🚀 TRI-GRAM LINK PREDICTION! 🚀")
    print("=" * 70)
    print("\nBi-gram = 97.8%")
    print("Tri-gram = ???")
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 10 MB...")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    compressor = UltraTrigram()
    result = compressor.compress(data)
    
    # Results
    print(f"\n{'=' * 70}")
    print("🎯 TRI-GRAM RESULTS")
    print(f"{'=' * 70}")
    
    bpb = (result['total_bytes'] * 8) / len(data)
    proj = bpb * 1_000_000_000 / 8 / (1024 * 1024)
    
    print(f"\nTotal: {result['total_bytes']:,} bajtów")
    print(f"BPB: {bpb:.3f}")
    print(f"Projection: {proj:.1f} MB")
    
    print(f"\n{'=' * 70}")
    print("📊 N-GRAM EVOLUTION")
    print(f"{'=' * 70}")
    
    print(f"\nULTRA original:     1.167 bpb = 139.0 MB")
    print(f"BI-GRAM:            1.130 bpb = 134.7 MB (-4.3 MB)")
    print(f"TRI-GRAM:           {bpb:.3f} bpb = {proj:.1f} MB", end='')
    
    improvement = 134.7 - proj
    if improvement > 0:
        print(f" (-{improvement:.1f} MB!) 🚀")
    elif improvement > -0.5:
        print(f" (≈same, no gain)")
    else:
        print(f" (+{-improvement:.1f} MB worse)")
    
    record = 114
    print(f"\nRecord: {record} MB")
    print(f"Gap: {proj - record:+.1f} MB")
    
    print(f"\nTime: {result['time']:.1f} s")
    print("=" * 70)

if __name__ == "__main__":
    main()
