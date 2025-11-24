#!/usr/bin/env python3
"""
ENHANCED: Graph-based links + Template dictionary compression
Łączy dwie innowacje w jeden system
"""
import re
import struct
import time
from collections import defaultdict, Counter
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

class TemplateDictionary:
    """Słownik templates z predykcją parametrów"""
    
    def __init__(self):
        self.template_freq = Counter()
        self.template_to_id = {}
        self.id_to_template = {}
        self.next_id = 0
        
        # Analiza parametrów dla popularnych templates
        self.param_patterns = defaultdict(Counter)  # template_name -> Counter(param_patterns)
    
    def train(self, templates):
        """
        Trenuj słownik na templates
        templates: List[(name, full_content)]
        """
        print(f"    Budowanie słownika z {len(templates):,} templates...")
        
        # Zlicz częstości
        names = [name for name, _ in templates]
        self.template_freq = Counter(names)
        
        # Zbuduj słownik dla top-N
        for name, count in self.template_freq.most_common(100):
            self.template_to_id[name] = self.next_id
            self.id_to_template[self.next_id] = name
            self.next_id += 1
        
        # Analizuj wzorce parametrów
        for name, full_content in templates:
            if name in self.template_to_id:
                # Wyodrębnij wzorzec parametrów (uproszczony)
                params = full_content[len(name):].strip()
                if len(params) < 200:  # Limit
                    self.param_patterns[name][params] += 1
        
        print(f"    Słownik: {len(self.template_to_id):,} templates")
        top_10_cov = sum(count for _, count in self.template_freq.most_common(10))
        coverage = (top_10_cov / len(templates) * 100) if templates else 0
        print(f"    Top-10 pokrywa: {coverage:.1f}% wystąpień")
    
    def compress_template(self, name, full_content):
        """
        Kompresuje template
        
        Returns:
            (mode, data)
            mode 0: Known template, common params (ID + param_id)
            mode 1: Known template, custom params (ID + params)
            mode 2: Unknown template (full content)
        """
        if name in self.template_to_id:
            template_id = self.template_to_id[name]
            params = full_content[len(name):].strip()
            
            # Sprawdź czy params są w top-K dla tego template
            if name in self.param_patterns:
                top_params = [p for p, _ in self.param_patterns[name].most_common(10)]
                if params in top_params:
                    param_idx = top_params.index(params)
                    return (0, (template_id, param_idx))  # ID + param_id
            
            # Known template, custom params
            return (1, (template_id, params))
        else:
            # Unknown template
            return (2, full_content)

class LinkGraph:
    """Graf linków (jak wcześniej)"""
    
    def __init__(self):
        self.edges = defaultdict(Counter)
        self.link_to_id = {}
        self.id_to_link = {}
        self.next_id = 0
    
    def train(self, links):
        for link in links:
            if link not in self.link_to_id:
                self.link_to_id[link] = self.next_id
                self.id_to_link[self.next_id] = link
                self.next_id += 1
        
        for i in range(len(links) - 1):
            current = links[i]
            next_link = links[i + 1]
            self.edges[current][next_link] += 1
    
    def predict_next(self, current_link, top_k=10):
        if current_link not in self.edges or len(self.edges[current_link]) == 0:
            return []
        
        total = sum(self.edges[current_link].values())
        predictions = []
        
        for link, count in self.edges[current_link].most_common(top_k):
            prob = count / total
            predictions.append((link, prob))
        
        return predictions
    
    def compress_link(self, link, context_link):
        predictions = self.predict_next(context_link, top_k=10)
        
        if not predictions:
            if link in self.link_to_id:
                return (3, self.link_to_id[link])
            else:
                return (4, link)
        
        pred_links = [l for l, p in predictions]
        
        if link == pred_links[0]:
            return (0, None)
        elif link in pred_links[:3]:
            idx = pred_links.index(link)
            return (1, idx)
        elif link in pred_links[:10]:
            idx = pred_links.index(link)
            return (2, idx)
        elif link in self.link_to_id:
            return (3, self.link_to_id[link])
        else:
            return (4, link)

class GraphTemplateCompressor:
    """Enhanced kompresor: Graph + Templates + Order-3 text"""
    
    def __init__(self):
        self.link_graph = LinkGraph()
        self.template_dict = TemplateDictionary()
        self.text_model = ContextModel(order=3)
    
    def extract_structure(self, data):
        """Wyodrębnia linki, templates i tekst"""
        print(f"\n[1] Ekstrakcja struktury...")
        
        tokens = []
        all_links = []
        all_templates = []
        
        # Regex patterns
        link_pattern = re.compile(rb'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        template_pattern = re.compile(rb'\{\{([^}]+)\}\}')
        
        # Znajduj wszystkie
        link_matches = [(m.start(), m.end(), 'link', m.group(1)) for m in link_pattern.finditer(data)]
        template_matches = [(m.start(), m.end(), 'template', m.group(1)) for m in template_pattern.finditer(data)]
        
        # Sortuj wszystkie matches po pozycji
        all_matches = sorted(link_matches + template_matches, key=lambda x: x[0])
        
        last_pos = 0
        
        for start, end, match_type, content in all_matches:
            # Tekst przed matchem
            if start > last_pos:
                text_chunk = data[last_pos:start]
                if len(text_chunk) > 0:
                    tokens.append(('text', text_chunk))
            
            # Match
            content_str = content.decode('utf-8', errors='ignore').strip()
            
            if match_type == 'link':
                if len(content_str) > 0 and len(content_str) < 100:
                    tokens.append(('link', content_str))
                    all_links.append(content_str)
            
            elif match_type == 'template':
                if len(content_str) > 0 and len(content_str) < 200:
                    # Wyodrębnij nazwę template (przed |)
                    template_name = content_str.split('|')[0].strip()
                    tokens.append(('template', (template_name, content_str)))
                    all_templates.append((template_name, content_str))
            
            last_pos = end
        
        # Reszta tekstu
        if last_pos < len(data):
            tokens.append(('text', data[last_pos:]))
        
        print(f"    Tokenów: {len(tokens):,}")
        print(f"    Linków: {len(all_links):,}")
        print(f"    Templates: {len(all_templates):,}")
        print(f"    Tekstu: {len([t for t in tokens if t[0] == 'text']):,} chunków")
        
        return tokens, all_links, all_templates
    
    def train(self, data):
        """Trenuj wszystkie modele"""
        print(f"\n[2] Trening modeli...")
        
        tokens, all_links, all_templates = self.extract_structure(data)
        
        # Graf linków
        print(f"  Graf linków:")
        if all_links:
            self.link_graph.train(all_links)
            print(f"    Unikalnych: {len(self.link_graph.link_to_id):,}")
        
        # Słownik templates
        print(f"  Słownik templates:")
        if all_templates:
            self.template_dict.train(all_templates)
        
        # Model tekstu
        print(f"  Model tekstu (Order-3):")
        text_data = b''.join(content for typ, content in tokens if typ == 'text')
        if len(text_data) > 0:
            self.text_model.train(text_data)
            print(f"    Trenowano na {len(text_data):,} bajtach")
        
        return tokens, all_links, all_templates
    
    def compress(self, data):
        """Kompresja z wszystkimi technikami"""
        start = time.time()
        
        tokens, all_links, all_templates = self.train(data)
        
        print(f"\n[3] Kompresja...")
        
        # Linki (graph-based)
        print(f"  Linki (graph-based)...")
        link_stats = {'top1': 0, 'top3': 0, 'top10': 0, 'id': 0, 'new': 0}
        link_bits = 0
        
        context_link = None
        for link in all_links:
            mode, data_val = self.link_graph.compress_link(link, context_link)
            
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
        print(f"    → {link_bytes:,} bajtów ({link_bits / len(all_links) if all_links else 0:.2f} bity/link)")
        
        # Templates (dictionary-based)
        print(f"  Templates (dictionary-based)...")
        template_stats = {'dict_common': 0, 'dict_custom': 0, 'unknown': 0}
        template_bits = 0
        
        for name, full_content in all_templates:
            mode, data_val = self.template_dict.compress_template(name, full_content)
            
            if mode == 0:  # Dict + common params
                template_bits += 7 + 4  # template_id + param_id
                template_stats['dict_common'] += 1
            elif mode == 1:  # Dict + custom params
                _, params = data_val
                template_bits += 7 + len(params) * 8
                template_stats['dict_custom'] += 1
            else:  # Unknown
                template_bits += 2 + len(full_content) * 8
                template_stats['unknown'] += 1
        
        template_bytes = template_bits // 8 + (1 if template_bits % 8 else 0)
        print(f"    → {template_bytes:,} bajtów ({template_bits / len(all_templates) if all_templates else 0:.2f} bity/template)")
        
        # Tekst (Order-3)
        print(f"  Tekst (Order-3)...")
        text_data = b''.join(content for typ, content in tokens if typ == 'text')
        
        if len(text_data) > 0:
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
            print(f"    → {len(text_compressed):,} bajtów ({text_bpb:.3f} bpb)")
        else:
            text_compressed = b''
            text_bpb = 0
        
        total_compressed = link_bytes + template_bytes + len(text_compressed)
        total_time = time.time() - start
        
        return {
            'link_bytes': link_bytes,
            'template_bytes': template_bytes,
            'text_bytes': len(text_compressed),
            'total_bytes': total_compressed,
            'link_stats': link_stats,
            'template_stats': template_stats,
            'text_bpb': text_bpb,
            'time': total_time
        }

def main():
    print("=" * 70)
    print("ENHANCED COMPRESSOR: Graph + Templates + Order-3")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    
    # Kompresja
    compressor = GraphTemplateCompressor()
    result = compressor.compress(data)
    
    # Wyniki
    print(f"\n{'=' * 70}")
    print("WYNIKI - GRAPH + TEMPLATES")
    print(f"{'=' * 70}")
    
    enhanced_bpb = (result['total_bytes'] * 8) / len(data)
    
    print(f"\nLinki:      {result['link_bytes']:>10,} bajtów")
    print(f"Templates:  {result['template_bytes']:>10,} bajtów")
    print(f"Tekst:      {result['text_bytes']:>10,} bajtów ({result['text_bpb']:.3f} bpb)")
    print(f"─" * 50)
    print(f"RAZEM:      {result['total_bytes']:>10,} bajtów ({enhanced_bpb:.3f} bpb)")
    
    # Porównania
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    
    import zlib
    zlib_comp = zlib.compress(data, level=9)
    zlib_bpb = (len(zlib_comp) * 8) / len(data)
    
    baseline_bpb = 2.068
    graph_only_bpb = 1.630
    
    print(f"\n{'Metoda':<30} {'Rozmiar':<15} {'Bity/bajt':<12} {'vs Baseline'}")
    print("-" * 75)
    print(f"{'zlib -9':<30} {len(zlib_comp):<15,} {zlib_bpb:<12.3f} {'-'}")
    print(f"{'Baseline Order-3':<30} {'~271,000':<15} {baseline_bpb:<12.3f} {'baseline'}")
    print(f"{'Graph-only':<30} {'~214,000':<15} {graph_only_bpb:<12.3f} {'+21.2%'}")
    print(f"{'Graph + Templates':<30} {result['total_bytes']:<15,} {enhanced_bpb:<12.3f}", end='')
    
    improvement = ((baseline_bpb - enhanced_bpb) / baseline_bpb) * 100
    improvement_vs_graph = ((graph_only_bpb - enhanced_bpb) / graph_only_bpb) * 100
    
    print(f" {'+' if improvement > 0 else ''}{improvement:.1f}%")
    
    print(f"\n{'=' * 70}")
    if improvement_vs_graph > 0:
        print(f"✓ Templates dodały {improvement_vs_graph:.2f}% dodatkowej poprawy!")
    print(f"✓ RAZEM {improvement:.2f}% lepiej niż baseline Order-3")
    
    # Projekcja
    print(f"\n{'=' * 70}")
    print("PROJEKCJA NA ENWIK9 (1 GB)")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    baseline_proj = int(baseline_bpb * enwik9_size / 8)
    enhanced_proj = int(enhanced_bpb * enwik9_size / 8)
    
    print(f"\nBaseline Order-3:    {baseline_proj:>15,} B  ({baseline_proj/(1024*1024):>6.1f} MB)")
    print(f"Graph + Templates:   {enhanced_proj:>15,} B  ({enhanced_proj/(1024*1024):>6.1f} MB)")
    
    savings = baseline_proj - enhanced_proj
    print(f"\nOszczędność:         {savings:>15,} B  ({savings/(1024*1024):>6.1f} MB)")
    
    print(f"\n🎯 Gap do rekordu (114 MB): {(enhanced_proj/(1024*1024)) - 114:.1f} MB")
    
    print(f"\nCzas: {result['time']:.1f} s")
    print("=" * 70)

if __name__ == "__main__":
    main()
