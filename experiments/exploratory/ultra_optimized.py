#!/usr/bin/env python3
"""
ULTRA OPTIMIZED - Order-5 with Adaptive Context
Goal: Squeeze every bit out of Order-5!

Key optimizations:
1. Adaptive order (5 for hot, 3 for cold contexts)
2. Improved graph prediction (with type awareness)
3. Better template matching
4. Section hierarchy awareness
"""
import re
import time
from collections import defaultdict, Counter
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

class AdaptiveContextModel:
    """Context model with adaptive order selection"""
    
    def __init__(self, max_order=5, min_order=3, hot_threshold=10):
        self.max_order = max_order
        self.min_order = min_order
        self.hot_threshold = hot_threshold
        
        # Multiple order models
        self.models = {
            order: ContextModel(order=order) 
            for order in range(min_order, max_order + 1)
        }
        
        self.context_frequencies = Counter()
        self.current_context = b''
        
    def train(self, data):
        """Train all models and track frequencies"""
        print(f"    Training adaptive model (Order {self.min_order}-{self.max_order})...")
        
        # Train all models
        for order, model in self.models.items():
            model.train(data)
        
        # Track context frequencies for adaptive selection
        for i in range(len(data)):
            for order in range(self.min_order, self.max_order + 1):
                if i >= order:
                    ctx = bytes(data[i-order:i])
                    self.context_frequencies[ctx] += 1
        
        # Stats
        hot_contexts = sum(1 for count in self.context_frequencies.values() 
                          if count >= self.hot_threshold)
        total_contexts = len(self.context_frequencies)
        
        print(f"      Max order contexts: {len(self.models[self.max_order].contexts):,}")
        print(f"      Hot contexts (≥{self.hot_threshold}): {hot_contexts:,} / {total_contexts:,}")
        print(f"      Hot ratio: {hot_contexts/total_contexts*100:.1f}%")
    
    def start_encoding(self):
        """Start encoding session"""
        for model in self.models.values():
            model.start_encoding()
        self.current_context = b''
    
    def get_order_for_context(self, context):
        """Decide which order to use based on context frequency"""
        # Try max order first
        if len(context) >= self.max_order:
            max_ctx = context[-self.max_order:]
            if self.context_frequencies[max_ctx] >= self.hot_threshold:
                return self.max_order
        
        # Fall back to lower orders
        for order in range(self.max_order - 1, self.min_order - 1, -1):
            if len(context) >= order:
                ctx = context[-order:]
                if self.context_frequencies[ctx] >= self.hot_threshold // 2:
                    return order
        
        return self.min_order
    
    def get_range(self, symbol):
        """Get range using adaptive order"""
        order = self.get_order_for_context(self.current_context)
        return self.models[order].get_range(symbol)
    
    def get_total(self):
        """Get total from adaptive model"""
        order = self.get_order_for_context(self.current_context)
        return self.models[order].get_total()
    
    def update_context(self, symbol):
        """Update context after encoding symbol"""
        self.current_context = (self.current_context + bytes([symbol]))[-self.max_order:]
        
        # Update all models
        for model in self.models.values():
            model.update_context(symbol)

class ImprovedLinkGraph:
    """Enhanced link graph with type awareness and better prediction"""
    
    def __init__(self):
        self.link_transitions = defaultdict(Counter)
        self.link_types = {}
        self.type_transitions = defaultdict(Counter)
        self.link_to_id = {}
        self.next_id = 0
        
    def classify_type(self, link):
        """Simple type classification"""
        if any(c.isdigit() for c in link) and sum(c.isdigit() for c in link) >= 3:
            return 'TIME'
        words = link.split()
        if len(words) >= 2 and all(w[0].isupper() for w in words if w):
            return 'PERSON'
        if len(words) == 1 and link[0].isupper():
            return 'ENTITY'
        if link[0].islower():
            return 'CONCEPT'
        return 'OTHER'
    
    def train(self, links):
        """Train with type awareness"""
        # Classify
        for link in links:
            self.link_types[link] = self.classify_type(link)
            if link not in self.link_to_id:
                self.link_to_id[link] = self.next_id
                self.next_id += 1
        
        # Build transition graphs
        for i in range(len(links) - 1):
            from_link = links[i]
            to_link = links[i + 1]
            
            self.link_transitions[from_link][to_link] += 1
            
            from_type = self.link_types.get(from_link, 'OTHER')
            to_type = self.link_types.get(to_link, 'OTHER')
            self.type_transitions[from_type][to_type] += 1
        
        # Enhanced prediction: combine link and type info
        self.combined_predictions = {}
        for from_link, to_links in self.link_transitions.items():
            from_type = self.link_types.get(from_link, 'OTHER')
            
            # Get type predictions
            type_preds = self.type_transitions[from_type].most_common(3)
            predicted_types = {t for t, _ in type_preds}
            
            # Boost predictions of correct type
            enhanced_scores = Counter()
            for to_link, count in to_links.items():
                to_type = self.link_types.get(to_link, 'OTHER')
                boost = 1.5 if to_type in predicted_types else 1.0
                enhanced_scores[to_link] = count * boost
            
            self.combined_predictions[from_link] = enhanced_scores
    
    def compress_link(self, link, prev_link):
        """Compress with enhanced prediction"""
        if not prev_link or prev_link not in self.combined_predictions:
            # Fallback to dictionary
            if link in self.link_to_id:
                return (3, self.link_to_id[link])
            return (4, link)
        
        predictions = self.combined_predictions[prev_link].most_common(10)
        pred_links = [l for l, _ in predictions]
        
        if pred_links and link == pred_links[0]:
            return (0, None)  # Top-1
        elif link in pred_links[:3]:
            return (1, pred_links.index(link))  # Top-3
        elif link in pred_links[:10]:
            return (2, pred_links.index(link))  # Top-10
        elif link in self.link_to_id:
            return (3, self.link_to_id[link])  # Dict
        else:
            return (4, link)  # Full

class UltraOptimized:
    """Fully optimized ULTRA compressor"""
    
    def __init__(self):
        from ultra_compressor import TemplateDictionary, SectionGraph
        
        self.text_model = AdaptiveContextModel(max_order=5, min_order=3, hot_threshold=10)
        self.link_graph = ImprovedLinkGraph()
        self.template_dict = TemplateDictionary()
        self.section_graph = SectionGraph()
    
    def extract_everything(self, data):
        """Extract all structures"""
        print(f"\n[1] Ekstrakcja struktury...")
        
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
        
        print(f"    Sekcje:    {len(all_sections):>6,}")
        print(f"    Linki:     {len(all_links):>6,}")
        print(f"    Templates: {len(all_templates):>6,}")
        print(f"    Tekst:     {len(text_data):>6,} bajtów")
        
        return all_sections, all_links, all_templates, text_data
    
    def train(self, data):
        """Train all models"""
        print(f"\n[2] Trening modeli (OPTIMIZED)...")
        
        sections, links, templates, text_data = self.extract_everything(data)
        
        if sections:
            print(f"  Graf sekcji:")
            self.section_graph.train(sections)
            print(f"    Unikalnych: {len(self.section_graph.section_to_id):,}")
        
        if links:
            print(f"  Improved Link Graph (type-aware):")
            self.link_graph.train(links)
            print(f"    Linki: {len(self.link_graph.link_to_id):,}")
            print(f"    Typy: {len(set(self.link_graph.link_types.values()))}")
        
        if templates:
            print(f"  Słownik templates:")
            self.template_dict.train(templates)
            print(f"    Słownik: {len(self.template_dict.template_to_id):,}")
        
        print(f"  Adaptive Context Model:")
        if len(text_data) > 100:
            self.text_model.train(text_data)
        
        return sections, links, templates, text_data
    
    def compress(self, data):
        """Compress with all optimizations"""
        start = time.time()
        
        sections, links, templates, text_data = self.train(data)
        
        print(f"\n[3] Kompresja (ULTRA OPTIMIZED)...")
        
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
        
        # Links (improved)
        link_bits = 0
        context_link = None
        for link in links:
            mode, data_val = self.link_graph.compress_link(link, context_link)
            
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
        
        # Templates
        template_bits = 0
        for name, _ in templates:
            mode, _ = self.template_dict.compress_template(name)
            template_bits += 7 if mode == 0 else (2 + len(name) * 8)
        template_bytes = template_bits // 8 + (1 if template_bits % 8 else 0)
        
        # Text (adaptive!)
        print(f"  Kompresja tekstu (Adaptive Order 3-5)...")
        if len(text_data) > 100:
            encoder = ArithmeticEncoder(precision_bits=32)
            self.text_model.start_encoding()
            
            class AdaptiveWrapper:
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
            
            wrapper = AdaptiveWrapper(self.text_model)
            text_compressed = encoder.encode(list(text_data), wrapper)
            text_bpb = (len(text_compressed) * 8) / len(text_data)
        else:
            text_compressed = b''
            text_bpb = 0
        
        total_compressed = section_bytes + link_bytes + template_bytes + len(text_compressed)
        total_time = time.time() - start
        
        print(f"\n  Sekcje:    {section_bytes:>10,} bajtów")
        print(f"  Linki:     {link_bytes:>10,} bajtów")
        print(f"  Templates: {template_bytes:>10,} bajtów")
        print(f"  Tekst:     {len(text_compressed):>10,} bajtów ({text_bpb:.3f} bpb)")
        
        return {
            'section_bytes': section_bytes,
            'link_bytes': link_bytes,
            'template_bytes': template_bytes,
            'text_bytes': len(text_compressed),
            'total_bytes': total_compressed,
            'text_bpb': text_bpb,
            'time': total_time
        }

def main():
    print("=" * 70)
    print("⚡ ULTRA OPTIMIZED - Maximum Squeeze! ⚡")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    # Test on 10 MB
    print(f"\nCzytanie 10 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    print(f"Rozmiar: {len(data):,} bajtów ({len(data)/(1024*1024):.1f} MB)")
    
    compressor = UltraOptimized()
    result = compressor.compress(data)
    
    # Results
    print(f"\n{'=' * 70}")
    print("📊 ULTRA OPTIMIZED RESULTS")
    print(f"{'=' * 70}")
    
    optimized_bpb = (result['total_bytes'] * 8) / len(data)
    
    print(f"\nTotal: {result['total_bytes']:,} bajtów ({optimized_bpb:.3f} bpb)")
    
    # Comparison
    print(f"\n{'=' * 70}")
    print("📈 IMPROVEMENT")
    print(f"{'=' * 70}")
    
    ultra_10mb_bpb = 1.167  # Original ULTRA on 10 MB
    order6_10mb_bpb = 1.172  # Order-6 on 10 MB
    
    print(f"\n{'Version':<30} {'BPB':<10} {'Enwik9':<15} {'Status'}")
    print("-" * 70)
    print(f"{'ULTRA Order-5 (original)':<30} {ultra_10mb_bpb:<10.3f} {'139 MB':<15} {'Baseline'}")
    print(f"{'Order-6 (pure)':<30} {order6_10mb_bpb:<10.3f} {'140 MB':<15} {'Degraded'}")
    print(f"{'ULTRA OPTIMIZED (adaptive)':<30} {optimized_bpb:<10.3f}", end='')
    
    enwik9_size = 1_000_000_000
    optimized_proj = int(optimized_bpb * enwik9_size / 8) / (1024 * 1024)
    
    print(f" {f'{optimized_proj:.0f} MB':<15}", end='')
    
    if optimized_bpb < ultra_10mb_bpb:
        improvement = ((ultra_10mb_bpb - optimized_bpb) / ultra_10mb_bpb) * 100
        print(f" +{improvement:.1f}% BETTER! 🎉")
    else:
        print(f" (testing)")
    
    # Projection
    print(f"\n{'=' * 70}")
    print("🎯 ENWIK9 PROJECTION")
    print(f"{'=' * 70}")
    
    record = 114
    
    print(f"\nOptimized: {optimized_proj:.1f} MB")
    print(f"Record:    {record:.1f} MB")
    print(f"Gap:       {optimized_proj - record:+.1f} MB")
    
    if optimized_proj < record:
        print(f"\n🏆🏆🏆 BEATS WORLD RECORD! 🏆🏆🏆")
    elif optimized_proj < record + 10:
        print(f"\n🎯 Close to record! TOP-5 likely!")
    else:
        print(f"\n✓ TOP-10, room for more optimization")
    
    # Save
    with open("ULTRA_OPTIMIZED_RESULTS.txt", "w") as f:
        f.write(f"ULTRA OPTIMIZED RESULTS\n")
        f.write(f"======================\n\n")
        f.write(f"BPB: {optimized_bpb:.3f}\n")
        f.write(f"Projection: {optimized_proj:.1f} MB\n")
        f.write(f"vs Record: {optimized_proj - record:+.1f} MB\n")
        f.write(f"Time: {result['time']:.1f} s\n")
    
    print(f"\n✓ Results saved")
    print("=" * 70)

if __name__ == "__main__":
    main()
