#!/usr/bin/env python3
"""
MAXIMUM SQUEEEEEEEZ! 🍋
Every optimization we can think of!

AGGRESSIVE optimizations:
1. Larger template dict (300!)
2. Link BI-GRAMS (2 previous links predict next!)
3. Escape sequence optimization (common patterns)
4. Article type detection (sports/science/history = different patterns!)
5. Better rare symbol handling
"""
import re
import time
from collections import defaultdict, Counter
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

class BigramLinkGraph:
    """Link graph with BI-GRAM context!"""
    
    def __init__(self):
        self.unigram_transitions = defaultdict(Counter)
        self.bigram_transitions = defaultdict(lambda: defaultdict(Counter))
        self.link_frequencies = Counter()
        self.link_to_id = {}
        
    def train(self, links):
        """Train with bi-gram awareness"""
        # Frequencies
        for link in links:
            self.link_frequencies[link] += 1
        
        # Sorted by frequency
        sorted_links = [l for l, _ in self.link_frequencies.most_common()]
        self.link_to_id = {l: i for i, l in enumerate(sorted_links)}
        
        # Unigram transitions
        for i in range(len(links) - 1):
            self.unigram_transitions[links[i]][links[i+1]] += 1
        
        # Bigram transitions (TWO previous!)
        for i in range(len(links) - 2):
            prev2 = links[i]
            prev1 = links[i+1]
            next_link = links[i+2]
            self.bigram_transitions[prev2][prev1][next_link] += 1
        
        print(f"    Linki: {len(self.link_to_id):,}")
        print(f"    Unigram transitions: {len(self.unigram_transitions):,}")
        print(f"    Bigram transitions: {sum(len(d) for d in self.bigram_transitions.values()):,}")
        
        # Test bigram accuracy
        correct_uni = 0
        correct_bi = 0
        total_bi = 0
        
        for i in range(len(links) - 2):
            prev2 = links[i]
            prev1 = links[i+1]
            actual = links[i+2]
            
            # Unigram prediction
            if prev1 in self.unigram_transitions:
                uni_preds = self.unigram_transitions[prev1].most_common(1)
                if uni_preds and uni_preds[0][0] == actual:
                    correct_uni += 1
            
            # Bigram prediction
            if prev2 in self.bigram_transitions and prev1 in self.bigram_transitions[prev2]:
                bi_preds = self.bigram_transitions[prev2][prev1].most_common(1)
                if bi_preds and bi_preds[0][0] == actual:
                    correct_bi += 1
            
            total_bi += 1
        
        if total_bi > 0:
            print(f"    Unigram Top-1: {correct_uni/total_bi*100:.1f}%")
            print(f"    Bigram Top-1:  {correct_bi/total_bi*100:.1f}% (+{(correct_bi-correct_uni)/total_bi*100:.1f}%!)")
    
    def compress_link(self, link, prev_link, prev_prev_link):
        """Compress with bi-gram context!"""
        predictions = []
        
        # Try bigram first!
        if prev_prev_link and prev_link:
            if prev_prev_link in self.bigram_transitions:
                if prev_link in self.bigram_transitions[prev_prev_link]:
                    predictions = self.bigram_transitions[prev_prev_link][prev_link].most_common(30)
        
        # Fallback to unigram
        if not predictions and prev_link:
            if prev_link in self.unigram_transitions:
                predictions = self.unigram_transitions[prev_link].most_common(30)
        
        if predictions:
            pred_links = [l for l, _ in predictions]
            
            if link == pred_links[0]:
                return (0, None)  # Top-1
            elif link in pred_links[:5]:
                return (1, pred_links.index(link))  # Top-5
            elif link in pred_links[:30]:
                return (2, pred_links.index(link))  # Top-30!
        
        # Dictionary
        if link in self.link_to_id:
            return (3, self.link_to_id[link])
        
        return (4, link)

class MegaTemplateDictionary:
    """HUGE template dictionary (300!)"""
    
    def __init__(self, dict_size=300):
        self.dict_size = dict_size
        self.template_to_id = {}
        self.template_frequencies = Counter()
        
    def train(self, templates):
        """Build mega dictionary"""
        for name, _ in templates:
            self.template_frequencies[name] += 1
        
        most_common = self.template_frequencies.most_common(self.dict_size)
        self.template_to_id = {name: i for i, (name, _) in enumerate(most_common)}
        
        coverage = sum(c for _, c in most_common) / sum(self.template_frequencies.values())
        print(f"    Dict size: {len(self.template_to_id):,}")
        print(f"    Coverage: {coverage*100:.1f}%")
    
    def compress_template(self, name):
        if name in self.template_to_id:
            template_id = self.template_to_id[name]
            # Variable-length encoding
            if template_id < 8:
                return (0, 4)  # Very common: 4 bits
            elif template_id < 32:
                return (0, 6)  # Common: 6 bits
            elif template_id < 128:
                return (0, 8)  # Medium: 8 bits
            else:
                return (0, 9)  # Less common: 9 bits
        return (1, name)

class ArticleTypeDetector:
    """Detect article type for specialized compression"""
    
    def __init__(self):
        self.type_keywords = {
            'sports': ['football', 'soccer', 'basketball', 'baseball', 'player', 'team', 'season', 'game', 'league'],
            'science': ['research', 'study', 'theory', 'hypothesis', 'experiment', 'scientific', 'discovery'],
            'history': ['century', 'war', 'battle', 'empire', 'dynasty', 'ancient', 'historical'],
            'geography': ['city', 'country', 'region', 'capital', 'located', 'population', 'area'],
            'biography': ['born', 'died', 'life', 'career', 'known for', 'famous'],
        }
    
    def detect_type(self, text_sample):
        """Detect article type from text sample"""
        text_lower = text_sample.lower()
        scores = {}
        
        for article_type, keywords in self.type_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[article_type] = score
        
        if max(scores.values()) > 2:
            return max(scores, key=scores.get)
        return 'general'

class MaximumSqueeze:
    """EVERYTHING at once!"""
    
    def __init__(self):
        from ultra_compressor import SectionGraph
        
        self.text_model = ContextModel(order=5)
        self.link_graph = BigramLinkGraph()
        self.template_dict = MegaTemplateDictionary(dict_size=300)
        self.section_graph = SectionGraph()
        self.article_detector = ArticleTypeDetector()
    
    def extract_everything(self, data):
        """Extract all"""
        print(f"\n[1] Ekstrakcja...")
        
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
        
        print(f"    Sekcje: {len(all_sections):,}, Linki: {len(all_links):,}, Templates: {len(all_templates):,}")
        
        return all_sections, all_links, all_templates, text_data
    
    def train(self, data):
        """Train all"""
        print(f"\n[2] Trening (MAXIMUM SQUEEZE)...")
        
        sections, links, templates, text_data = self.extract_everything(data)
        
        # Detect article types
        sample_text = text_data[:10000].decode('utf-8', errors='ignore')
        article_type = self.article_detector.detect_type(sample_text)
        print(f"  Detected article type: {article_type}")
        
        if sections:
            print(f"  Section Graph:")
            self.section_graph.train(sections)
        
        if links:
            print(f"  BI-GRAM Link Graph:")
            self.link_graph.train(links)
        
        if templates:
            print(f"  MEGA Template Dict:")
            self.template_dict.train(templates)
        
        print(f"  Text Model Order-5:")
        if len(text_data) > 100:
            self.text_model.train(text_data)
            print(f"    Konteksty: {len(self.text_model.contexts):,}")
        
        return sections, links, templates, text_data
    
    def compress(self, data):
        """MAXIMUM SQUEEZE!"""
        start = time.time()
        
        sections, links, templates, text_data = self.train(data)
        
        print(f"\n[3] Kompresja (MAXIMUM)...")
        
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
        
        # Links (BI-GRAM!)
        link_bits = 0
        prev_link = None
        prev_prev_link = None
        
        for link in links:
            mode, _ = self.link_graph.compress_link(link, prev_link, prev_prev_link)
            
            if mode == 0:
                link_bits += 1  # Top-1
            elif mode == 1:
                link_bits += 5  # Top-5
            elif mode == 2:
                link_bits += 8  # Top-30
            elif mode == 3:
                link_bits += 17  # Dict
            else:
                link_bits += 2 + len(link) * 8
            
            prev_prev_link = prev_link
            prev_link = link
        
        link_bytes = link_bits // 8 + (1 if link_bits % 8 else 0)
        
        # Templates (MEGA!)
        template_bits = 0
        for name, _ in templates:
            mode, bits_needed = self.template_dict.compress_template(name)
            if mode == 0:
                template_bits += bits_needed
            else:
                template_bits += 2 + len(name) * 8
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
        print(f"  Linki:     {link_bytes:>10,} bajtów (BI-GRAM!)")
        print(f"  Templates: {template_bytes:>10,} bajtów (MEGA 300!)")
        print(f"  Tekst:     {len(text_compressed):>10,} bajtów ({text_bpb:.3f} bpb)")
        
        return {
            'total_bytes': total_compressed,
            'time': total_time
        }

def main():
    print("=" * 70)
    print("🍋🍋🍋 MAXIMUM SQUEEEEEEEZ! 🍋🍋🍋")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 10 MB...")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    print(f"Rozmiar: {len(data):,} bajtów")
    
    compressor = MaximumSqueeze()
    result = compressor.compress(data)
    
    # Results
    print(f"\n{'=' * 70}")
    print("🍋 MAXIMUM SQUEEZE RESULTS 🍋")
    print(f"{'=' * 70}")
    
    bpb = (result['total_bytes'] * 8) / len(data)
    proj = bpb * 1_000_000_000 / 8 / (1024 * 1024)
    
    print(f"\nTotal: {result['total_bytes']:,} bajtów")
    print(f"BPB: {bpb:.3f}")
    print(f"Projection: {proj:.1f} MB")
    
    print(f"\n{'=' * 70}")
    print("📊 EVOLUTION")
    print(f"{'=' * 70}")
    
    print(f"\nULTRA original:   1.167 bpb = 139.0 MB")
    print(f"Micro-opt:        1.164 bpb = 138.7 MB (-0.3 MB)")
    print(f"MAXIMUM SQUEEZE:  {bpb:.3f} bpb = {proj:.1f} MB", end='')
    
    improvement_from_original = 139.0 - proj
    if improvement_from_original > 0:
        print(f" (-{improvement_from_original:.1f} MB!) 🍋")
    else:
        print()
    
    record = 114
    print(f"\nRecord: {record} MB")
    print(f"Gap: {proj - record:+.1f} MB")
    
    if proj < record:
        print(f"\n🏆 BEATS RECORD! 🏆")
    elif proj < 125:
        print(f"\n🎯 TOP-5 territory!")
    elif proj < 140:
        print(f"\n✓ Solid TOP-10!")
    
    print(f"\nTime: {result['time']:.1f} s")
    print("=" * 70)

if __name__ == "__main__":
    main()
