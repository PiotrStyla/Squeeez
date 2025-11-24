#!/usr/bin/env python3
"""
ULTIMATE COMPRESSOR: Graph links + Templates + Section structure
Wszystkie innowacje w jednym systemie!
"""
import re
import time
from collections import defaultdict, Counter
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

class SectionGraph:
    """Graf sekcji z predykcją następnej sekcji"""
    
    def __init__(self):
        self.edges = defaultdict(Counter)
        self.section_to_id = {}
        self.id_to_section = {}
        self.next_id = 0
        self.section_freq = Counter()
    
    def train(self, sections):
        """
        Trenuj graf na sekwencji sekcji
        sections: List[(level, title)]
        """
        if not sections:
            return
            
        # Zbuduj słownik
        for level, title in sections:
            self.section_freq[title] += 1
            if title not in self.section_to_id:
                self.section_to_id[title] = self.next_id
                self.id_to_section[self.next_id] = title
                self.next_id += 1
        
        # Zbuduj graf (same tytuły, bez level)
        for i in range(len(sections) - 1):
            _, current = sections[i]
            _, next_section = sections[i + 1]
            self.edges[current][next_section] += 1
    
    def compress_section(self, title, level, context_section):
        """
        Kompresuje sekcję używając kontekstu poprzedniej
        
        Returns:
            (mode, data)
            mode 0: top-1 match (1 bit + level)
            mode 1: top-3 match (2 bits + which + level)
            mode 2: known ID (ID + level)
            mode 3: new section (full text + level)
        """
        if not context_section or context_section not in self.edges:
            # Brak kontekstu, użyj dictionary
            if title in self.section_to_id:
                return (2, (self.section_to_id[title], level))
            else:
                return (3, (title, level))
        
        # Predykcja bazując na poprzedniej sekcji
        predictions = self.edges[context_section].most_common(10)
        pred_titles = [t for t, _ in predictions]
        
        if title == pred_titles[0]:
            return (0, level)  # Top-1 + level
        elif title in pred_titles[:3]:
            idx = pred_titles.index(title)
            return (1, (idx, level))  # Top-3 + level
        elif title in self.section_to_id:
            return (2, (self.section_to_id[title], level))
        else:
            return (3, (title, level))

class LinkGraph:
    """Graf linków (jak wcześniej)"""
    
    def __init__(self):
        self.edges = defaultdict(Counter)
        self.link_to_id = {}
        self.next_id = 0
    
    def train(self, links):
        for link in links:
            if link not in self.link_to_id:
                self.link_to_id[link] = self.next_id
                self.next_id += 1
        
        for i in range(len(links) - 1):
            self.edges[links[i]][links[i + 1]] += 1
    
    def compress_link(self, link, context_link):
        if not context_link or context_link not in self.edges:
            return (3, self.link_to_id.get(link)) if link in self.link_to_id else (4, link)
        
        predictions = [l for l, _ in self.edges[context_link].most_common(10)]
        
        if link == predictions[0] if predictions else None:
            return (0, None)
        elif link in predictions[:3]:
            return (1, predictions.index(link))
        elif link in predictions[:10]:
            return (2, predictions.index(link))
        elif link in self.link_to_id:
            return (3, self.link_to_id[link])
        else:
            return (4, link)

class TemplateDictionary:
    """Słownik templates (jak wcześniej - uproszczony)"""
    
    def __init__(self):
        self.template_to_id = {}
        self.next_id = 0
    
    def train(self, templates):
        freq = Counter(name for name, _ in templates)
        for name, _ in freq.most_common(100):
            self.template_to_id[name] = self.next_id
            self.next_id += 1
    
    def compress_template(self, name):
        if name in self.template_to_id:
            return (0, self.template_to_id[name])
        else:
            return (1, name)

class FullStructureCompressor:
    """Ultimate kompresor z wszystkimi innowacjami"""
    
    def __init__(self):
        self.link_graph = LinkGraph()
        self.template_dict = TemplateDictionary()
        self.section_graph = SectionGraph()
        self.text_model = ContextModel(order=3)
    
    def extract_everything(self, data):
        """Wyodrębnia WSZYSTKO: sekcje, linki, templates, tekst"""
        
        print(f"\n[1] Ekstrakcja pełnej struktury...")
        
        tokens = []
        all_links = []
        all_templates = []
        all_sections = []
        
        # Patterns
        section_pattern = re.compile(rb'(={2,6})\s*([^=]+?)\s*\1')
        link_pattern = re.compile(rb'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        template_pattern = re.compile(rb'\{\{([^}|]+)')
        
        # Sekcje
        for match in section_pattern.finditer(data):
            level = len(match.group(1))
            title = match.group(2).decode('utf-8', errors='ignore').strip()
            if 0 < len(title) < 100:
                all_sections.append((level, title))
        
        # Linki
        for match in link_pattern.finditer(data):
            link = match.group(1).decode('utf-8', errors='ignore').strip()
            if 0 < len(link) < 100:
                all_links.append(link)
        
        # Templates
        for match in template_pattern.finditer(data):
            name = match.group(1).decode('utf-8', errors='ignore').strip()
            if 0 < len(name) < 100:
                all_templates.append((name, name))
        
        # Tekst (uproszczony - wszystko co nie jest strukturą)
        text_data = data
        for pattern in [section_pattern, link_pattern, template_pattern]:
            text_data = pattern.sub(b' ', text_data)
        
        print(f"    Sekcje:    {len(all_sections):>6,}")
        print(f"    Linki:     {len(all_links):>6,}")
        print(f"    Templates: {len(all_templates):>6,}")
        print(f"    Tekst:     {len(text_data):>6,} bajtów")
        
        return all_sections, all_links, all_templates, text_data
    
    def train(self, data):
        """Trenuj wszystkie modele"""
        print(f"\n[2] Trening modeli...")
        
        sections, links, templates, text_data = self.extract_everything(data)
        
        # Graf sekcji
        if sections:
            print(f"  Graf sekcji:")
            self.section_graph.train(sections)
            print(f"    Unikalnych: {len(self.section_graph.section_to_id):,}")
        
        # Graf linków
        if links:
            print(f"  Graf linków:")
            self.link_graph.train(links)
            print(f"    Unikalnych: {len(self.link_graph.link_to_id):,}")
        
        # Templates
        if templates:
            print(f"  Słownik templates:")
            self.template_dict.train(templates)
            print(f"    Słownik: {len(self.template_dict.template_to_id):,}")
        
        # Tekst
        print(f"  Model tekstu (Order-3):")
        if len(text_data) > 100:
            self.text_model.train(text_data)
            print(f"    Trenowano na {len(text_data):,} bajtach")
        
        return sections, links, templates, text_data
    
    def compress(self, data):
        """Kompresja z wszystkimi technikami"""
        start = time.time()
        
        sections, links, templates, text_data = self.train(data)
        
        print(f"\n[3] Kompresja...")
        
        # Sekcje
        section_bits = 0
        section_stats = {'top1': 0, 'top3': 0, 'id': 0, 'new': 0}
        context_section = None
        
        for level, title in sections:
            mode, data_val = self.section_graph.compress_section(title, level, context_section)
            
            if mode == 0:  # Top-1
                section_bits += 1 + 2  # flag + level
                section_stats['top1'] += 1
            elif mode == 1:  # Top-3
                section_bits += 2 + 2 + 2  # flag + which + level
                section_stats['top3'] += 1
            elif mode == 2:  # ID
                section_bits += 2 + 8 + 2  # flag + ID + level
                section_stats['id'] += 1
            else:  # New
                section_bits += 2 + len(title) * 8 + 2
                section_stats['new'] += 1
            
            context_section = title
        
        section_bytes = section_bits // 8 + (1 if section_bits % 8 else 0)
        
        # Linki
        link_bits = 0
        link_stats = {'top1': 0, 'top3': 0, 'top10': 0, 'id': 0, 'new': 0}
        context_link = None
        
        for link in links:
            mode, _ = self.link_graph.compress_link(link, context_link)
            
            if mode == 0:
                link_bits += 1
                link_stats['top1'] += 1
            elif mode == 1:
                link_bits += 4
                link_stats['top3'] += 1
            elif mode == 2:
                link_bits += 6
                link_stats['top10'] += 1
            elif mode == 3:
                link_bits += 18
                link_stats['id'] += 1
            else:
                link_bits += 2 + len(link) * 8
                link_stats['new'] += 1
            
            context_link = link
        
        link_bytes = link_bits // 8 + (1 if link_bits % 8 else 0)
        
        # Templates
        template_bits = 0
        for name, _ in templates:
            mode, _ = self.template_dict.compress_template(name)
            template_bits += 7 if mode == 0 else (2 + len(name) * 8)
        
        template_bytes = template_bits // 8 + (1 if template_bits % 8 else 0)
        
        # Tekst
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
        
        print(f"  Sekcje:    {section_bytes:>10,} bajtów")
        print(f"  Linki:     {link_bytes:>10,} bajtów")
        print(f"  Templates: {template_bytes:>10,} bajtów")
        print(f"  Tekst:     {len(text_compressed):>10,} bajtów ({text_bpb:.3f} bpb)")
        
        return {
            'section_bytes': section_bytes,
            'link_bytes': link_bytes,
            'template_bytes': template_bytes,
            'text_bytes': len(text_compressed),
            'total_bytes': total_compressed,
            'section_stats': section_stats,
            'link_stats': link_stats,
            'text_bpb': text_bpb,
            'time': total_time
        }

def main():
    print("=" * 70)
    print("ULTIMATE STRUCTURE COMPRESSOR")
    print("Sections + Links + Templates + Order-3 Text")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    
    # Kompresja
    compressor = FullStructureCompressor()
    result = compressor.compress(data)
    
    # Wyniki
    print(f"\n{'=' * 70}")
    print("FINALNE WYNIKI")
    print(f"{'=' * 70}")
    
    ultimate_bpb = (result['total_bytes'] * 8) / len(data)
    
    print(f"\nSekcje:     {result['section_bytes']:>10,} bajtów")
    print(f"Linki:      {result['link_bytes']:>10,} bajtów")
    print(f"Templates:  {result['template_bytes']:>10,} bajtów")
    print(f"Tekst:      {result['text_bytes']:>10,} bajtów")
    print(f"─" * 50)
    print(f"TOTAL:      {result['total_bytes']:>10,} bajtów ({ultimate_bpb:.3f} bpb)")
    
    # Porównania
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE Z POPRZEDNIMI WERSJAMI")
    print(f"{'=' * 70}")
    
    baseline_bpb = 2.068
    graph_only_bpb = 1.630
    graph_template_bpb = 1.621
    
    print(f"\n{'Wersja':<30} {'Bity/bajt':<12} {'Improvement'}")
    print("-" * 70)
    print(f"{'Baseline Order-3':<30} {baseline_bpb:<12.3f} {'baseline'}")
    print(f"{'+ Graph links':<30} {graph_only_bpb:<12.3f} {'+21.2%'}")
    print(f"{'+ Templates':<30} {graph_template_bpb:<12.3f} {'+21.6%'}")
    print(f"{'+ Sections (FULL)':<30} {ultimate_bpb:<12.3f}", end='')
    
    improvement = ((baseline_bpb - ultimate_bpb) / baseline_bpb) * 100
    print(f" {'+' if improvement > 0 else ''}{improvement:.1f}%")
    
    # Projekcja enwik9
    print(f"\n{'=' * 70}")
    print("PROJEKCJA NA ENWIK9 (1 GB)")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    ultimate_proj = int(ultimate_bpb * enwik9_size / 8)
    baseline_proj = int(baseline_bpb * enwik9_size / 8)
    
    print(f"\nBaseline Order-3:  {baseline_proj:>15,} B  ({baseline_proj/(1024*1024):>6.1f} MB)")
    print(f"ULTIMATE:          {ultimate_proj:>15,} B  ({ultimate_proj/(1024*1024):>6.1f} MB)")
    
    savings = baseline_proj - ultimate_proj
    gap_to_record = (ultimate_proj / (1024*1024)) - 114
    
    print(f"\nOszczędność:       {savings:>15,} B  ({savings/(1024*1024):>6.1f} MB)")
    print(f"Gap do rekordu:    {gap_to_record:>15.1f} MB")
    
    print(f"\nCzas: {result['time']:.1f} s")
    print("=" * 70)

if __name__ == "__main__":
    main()
