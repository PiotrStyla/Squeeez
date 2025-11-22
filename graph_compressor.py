#!/usr/bin/env python3
"""
INNOWACYJNY KOMPRESOR: Graph-based link prediction + Order-3 text
Wykorzystuje strukturę graph'u Wikipedia do kompresji linków
"""
import re
import struct
import time
import pickle
from collections import defaultdict, Counter
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

class LinkGraph:
    """Graf linków z predykcją następnego linka"""
    
    def __init__(self):
        self.edges = defaultdict(Counter)  # link -> Counter(next_links)
        self.link_to_id = {}  # Słownik link -> ID
        self.id_to_link = {}  # ID -> link
        self.next_id = 0
    
    def train(self, links):
        """Trenuj graf na sekwencji linków"""
        print(f"    Budowanie graph'u z {len(links):,} linków...")
        
        # Buduj słownik
        for link in links:
            if link not in self.link_to_id:
                self.link_to_id[link] = self.next_id
                self.id_to_link[self.next_id] = link
                self.next_id += 1
        
        # Buduj krawędzie
        for i in range(len(links) - 1):
            current = links[i]
            next_link = links[i + 1]
            self.edges[current][next_link] += 1
        
        print(f"    Unikalnych linków: {len(self.link_to_id):,}")
        print(f"    Krawędzi: {sum(len(v) for v in self.edges.values()):,}")
    
    def predict_next(self, current_link, top_k=10):
        """
        Przewiduje top-K następnych linków
        
        Returns:
            List[(link, probability)]
        """
        if current_link not in self.edges or len(self.edges[current_link]) == 0:
            return []
        
        total = sum(self.edges[current_link].values())
        predictions = []
        
        for link, count in self.edges[current_link].most_common(top_k):
            prob = count / total
            predictions.append((link, prob))
        
        return predictions
    
    def compress_link(self, link, context_link):
        """
        Kompresuje link używając kontekstu poprzedniego linka
        
        Returns:
            (mode, data)
            mode 0: top-1 match (1 bit)
            mode 1: top-3 match (2 bits + which)
            mode 2: top-10 match (4 bits + which)
            mode 3: new link (full encoding)
        """
        predictions = self.predict_next(context_link, top_k=10)
        
        if not predictions:
            # Brak predykcji, zwróć ID jeśli znany
            if link in self.link_to_id:
                return (3, self.link_to_id[link])
            else:
                # Nowy link - zwróć jako string
                return (4, link)
        
        # Sprawdź czy link jest w top-K
        pred_links = [l for l, p in predictions]
        
        if link == pred_links[0]:
            return (0, None)  # Top-1 match
        elif link in pred_links[:3]:
            idx = pred_links.index(link)
            return (1, idx)  # Top-3, zwróć index (0-2)
        elif link in pred_links[:10]:
            idx = pred_links.index(link)
            return (2, idx)  # Top-10, zwróć index (0-9)
        elif link in self.link_to_id:
            return (3, self.link_to_id[link])  # Known link by ID
        else:
            return (4, link)  # New link, full string

class GraphBasedCompressor:
    """Główny kompresor z graph-based link prediction"""
    
    def __init__(self):
        self.link_graph = LinkGraph()
        self.text_model = ContextModel(order=3)
        self.other_model = ContextModel(order=2)
        
    def extract_structure(self, data):
        """
        Wyodrębnia linki i tekst z danych
        
        Returns:
            tokens: List[(type, content)] gdzie type = 'link' | 'text'
            all_links: List[str] - lista linków w kolejności
        """
        print(f"\n[1] Ekstrakcja struktury...")
        
        tokens = []
        all_links = []
        
        link_pattern = re.compile(rb'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        
        last_pos = 0
        
        for match in link_pattern.finditer(data):
            # Tekst przed linkiem
            if match.start() > last_pos:
                text_chunk = data[last_pos:match.start()]
                if len(text_chunk) > 0:
                    tokens.append(('text', text_chunk))
            
            # Link
            link_text = match.group(1).decode('utf-8', errors='ignore').strip()
            if len(link_text) > 0 and len(link_text) < 100:
                tokens.append(('link', link_text))
                all_links.append(link_text)
            
            last_pos = match.end()
        
        # Reszta tekstu
        if last_pos < len(data):
            tokens.append(('text', data[last_pos:]))
        
        print(f"    Tokenów: {len(tokens):,}")
        print(f"    Linków: {len(all_links):,}")
        print(f"    Tekstu: {len([t for t in tokens if t[0] == 'text']):,} chunków")
        
        return tokens, all_links
    
    def train(self, data):
        """Trenuj oba modele"""
        print(f"\n[2] Trening modeli...")
        
        tokens, all_links = self.extract_structure(data)
        
        # Trenuj graf linków
        print(f"  Graf linków:")
        self.link_graph.train(all_links)
        
        # Trenuj model tekstu
        print(f"  Model tekstu (Order-3):")
        text_data = b''.join(content for typ, content in tokens if typ == 'text')
        if len(text_data) > 0:
            self.text_model.train(text_data)
            print(f"    Trenowano na {len(text_data):,} bajtach")
        
        return tokens, all_links
    
    def compress(self, data):
        """Kompresuje dane"""
        start = time.time()
        
        tokens, all_links = self.train(data)
        
        print(f"\n[3] Kompresja...")
        
        # Kompresja linków z graph prediction
        print(f"  Kompresja linków (graph-based)...")
        link_stats = {'top1': 0, 'top3': 0, 'top10': 0, 'id': 0, 'new': 0}
        link_bits = 0
        
        context_link = None
        for i, link in enumerate(all_links):
            mode, data_val = self.link_graph.compress_link(link, context_link)
            
            if mode == 0:  # Top-1
                link_bits += 1
                link_stats['top1'] += 1
            elif mode == 1:  # Top-3
                link_bits += 2 + 2  # mode + which
                link_stats['top3'] += 1
            elif mode == 2:  # Top-10
                link_bits += 2 + 4  # mode + which
                link_stats['top10'] += 1
            elif mode == 3:  # Known ID
                link_bits += 2 + 16  # mode + ID (assume 16 bit for IDs)
                link_stats['id'] += 1
            else:  # New link
                link_bits += 2 + len(link) * 8  # mode + full string
                link_stats['new'] += 1
            
            context_link = link
        
        link_bytes = link_bits // 8 + (1 if link_bits % 8 else 0)
        print(f"    Linki: {link_bytes:,} bajtów ({link_bits / len(all_links) if all_links else 0:.2f} bity/link)")
        print(f"    Breakdown: top1={link_stats['top1']}, top3={link_stats['top3']}, "
              f"top10={link_stats['top10']}, id={link_stats['id']}, new={link_stats['new']}")
        
        # Kompresja tekstu Order-3
        print(f"  Kompresja tekstu (Order-3)...")
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
            print(f"    Tekst: {len(text_compressed):,} bajtów ({text_bpb:.3f} bpb)")
        else:
            text_compressed = b''
            text_bpb = 0
        
        total_compressed = link_bytes + len(text_compressed)
        total_time = time.time() - start
        
        return {
            'link_bytes': link_bytes,
            'text_bytes': len(text_compressed),
            'total_bytes': total_compressed,
            'link_stats': link_stats,
            'text_bpb': text_bpb,
            'time': total_time,
            'tokens': tokens,
            'all_links': all_links
        }

def main():
    print("=" * 70)
    print("GRAPH-BASED KOMPRESOR - Test na 1 MB")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    
    # Graph-based compression
    compressor = GraphBasedCompressor()
    result = compressor.compress(data)
    
    # Wyniki
    print(f"\n{'=' * 70}")
    print("WYNIKI - GRAPH-BASED")
    print(f"{'=' * 70}")
    
    graph_bpb = (result['total_bytes'] * 8) / len(data)
    
    print(f"\nLinki:  {result['link_bytes']:>10,} bajtów")
    print(f"Tekst:  {result['text_bytes']:>10,} bajtów ({result['text_bpb']:.3f} bpb)")
    print(f"RAZEM:  {result['total_bytes']:>10,} bajtów ({graph_bpb:.3f} bpb)")
    
    # Porównanie z baseline
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    
    import zlib
    zlib_comp = zlib.compress(data, level=9)
    zlib_bpb = (len(zlib_comp) * 8) / len(data)
    
    # Baseline Order-3 (z poprzednich testów)
    baseline_bpb = 2.068
    
    print(f"\n{'Metoda':<30} {'Rozmiar':<15} {'Bity/bajt':<12}")
    print("-" * 70)
    print(f"{'zlib -9':<30} {len(zlib_comp):<15,} {zlib_bpb:<12.3f}")
    print(f"{'Baseline Order-3':<30} {'~271,000':<15} {baseline_bpb:<12.3f}")
    print(f"{'Graph-based':<30} {result['total_bytes']:<15,} {graph_bpb:<12.3f}")
    
    improvement = ((baseline_bpb - graph_bpb) / baseline_bpb) * 100
    
    print(f"\n{'=' * 70}")
    if improvement > 0:
        print(f"✓ Graph-based LEPSZY o {improvement:.2f}%!")
        print(f"✓ To jest PRZEŁOM - graph prediction działa!")
    else:
        print(f"⚠ Graph-based gorszy o {-improvement:.2f}%")
        print(f"  (Overhead graph'u może dominować na 1 MB)")
    
    # Projekcja
    print(f"\n{'=' * 70}")
    print("PROJEKCJA NA ENWIK9 (1 GB)")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    baseline_proj = int(baseline_bpb * enwik9_size / 8)
    graph_proj = int(graph_bpb * enwik9_size / 8)
    
    print(f"\nBaseline Order-3:  {baseline_proj:>15,} B  ({baseline_proj/(1024*1024):>6.1f} MB)")
    print(f"Graph-based:       {graph_proj:>15,} B  ({graph_proj/(1024*1024):>6.1f} MB)")
    
    if graph_proj < baseline_proj:
        savings = baseline_proj - graph_proj
        print(f"\nOszczędność:       {savings:>15,} B  ({savings/(1024*1024):>6.1f} MB)")
    
    print(f"\nCzas: {result['time']:.1f} s")
    print("=" * 70)

if __name__ == "__main__":
    main()
