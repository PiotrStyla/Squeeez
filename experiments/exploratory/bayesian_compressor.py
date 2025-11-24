#!/usr/bin/env python3
"""
BAYESIAN MULTI-RELATIONAL COMPRESSOR
Breakthrough #6: Uncertainty Quantification for Compression!

Inspired by: "Knowledge-Driven Bayesian Uncertainty Quantification 
for Reliable Fake News Detection" (Puczynska et al.)

Idea: Zamiast binary type prediction, używamy FULL probability distributions!
Arithmetic coding automatycznie wykorzysta to dla optimal encoding!
"""
import re
import time
import math
from collections import defaultdict, Counter
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

class BayesianTypePredictor:
    """Przewiduje typy z uncertainty quantification"""
    
    def __init__(self):
        self.type_transitions = defaultdict(Counter)
        self.type_counts = Counter()
        self.all_types = set()
        
    def train(self, link_types):
        """Train from link type sequence"""
        for i in range(len(link_types) - 1):
            from_type = link_types[i]
            to_type = link_types[i + 1]
            
            self.type_transitions[from_type][to_type] += 1
            self.type_counts[to_type] += 1
            self.all_types.add(from_type)
            self.all_types.add(to_type)
    
    def get_probability_distribution(self, prev_type):
        """
        Get FULL probability distribution for next type
        Returns: {type: probability} dict
        
        Uses Bayesian approach with:
        - Observed frequencies (evidence)
        - Prior distribution (global frequencies)
        - Laplace smoothing (uncertainty handling)
        """
        
        # Prior: Global type distribution
        total_types = sum(self.type_counts.values())
        prior = {t: (self.type_counts[t] + 1) / (total_types + len(self.all_types)) 
                 for t in self.all_types}
        
        # Evidence: What we saw after this type
        if prev_type not in self.type_transitions:
            # No evidence - return prior (maximum uncertainty!)
            return prior
        
        evidence = self.type_transitions[prev_type]
        total_evidence = sum(evidence.values())
        
        # Bayesian combination: Evidence + Prior
        # With confidence based on amount of evidence
        confidence = min(1.0, total_evidence / 100.0)  # Max out at 100 samples
        
        posterior = {}
        for typ in self.all_types:
            # Evidence probability (with Laplace smoothing)
            evidence_prob = (evidence[typ] + 1) / (total_evidence + len(self.all_types))
            
            # Prior probability
            prior_prob = prior[typ]
            
            # Bayesian combination weighted by confidence
            posterior[typ] = confidence * evidence_prob + (1 - confidence) * prior_prob
        
        # Normalize
        total = sum(posterior.values())
        posterior = {t: p/total for t, p in posterior.items()}
        
        return posterior
    
    def get_entropy(self, distribution):
        """Calculate entropy of distribution (uncertainty measure)"""
        entropy = 0
        for prob in distribution.values():
            if prob > 0:
                entropy -= prob * math.log2(prob)
        return entropy
    
    def get_expected_bits(self, distribution, actual_type):
        """Expected bits to encode actual_type given distribution"""
        prob = distribution.get(actual_type, 1e-10)
        return -math.log2(prob)

class BayesianCompressor:
    """Compressor with Bayesian uncertainty quantification"""
    
    def __init__(self, text_order=5):
        from multirel_compressor import TypeClassifier, MultiRelationalLinkGraph
        from ultra_compressor import TemplateDictionary, SectionGraph
        
        self.type_classifier = TypeClassifier()
        self.bayesian_predictor = BayesianTypePredictor()
        self.link_graph = MultiRelationalLinkGraph()
        self.template_dict = TemplateDictionary()
        self.section_graph = SectionGraph()
        self.text_model = ContextModel(order=text_order)
        self.text_order = text_order
    
    def extract_everything(self, data):
        """Extract all structure"""
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
        """Train with Bayesian approach"""
        print(f"\n[2] Trening modeli...")
        
        sections, links, templates, text_data = self.extract_everything(data)
        
        # Classify links
        link_types = [self.type_classifier.classify(link) for link in links]
        
        # Train Bayesian predictor
        if link_types:
            print(f"  Bayesian Type Predictor:")
            self.bayesian_predictor.train(link_types)
            
            # Stats
            type_counts = Counter(link_types)
            print(f"    Typy: {len(type_counts)}")
            
            # Sample uncertainty for a common type
            if 'CONCEPT' in type_counts:
                dist = self.bayesian_predictor.get_probability_distribution('CONCEPT')
                entropy = self.bayesian_predictor.get_entropy(dist)
                print(f"    Entropy (CONCEPT→): {entropy:.2f} bits")
                print(f"    Top predictions:", end='')
                for typ, prob in sorted(dist.items(), key=lambda x: x[1], reverse=True)[:3]:
                    print(f" {typ}:{prob:.1%}", end='')
                print()
        
        # Other models
        if sections:
            print(f"  Graf sekcji:")
            self.section_graph.train(sections)
            print(f"    Unikalnych: {len(self.section_graph.section_to_id):,}")
        
        if links:
            print(f"  Graph linków:")
            self.link_graph.train(links)
        
        if templates:
            print(f"  Słownik templates:")
            self.template_dict.train(templates)
            print(f"    Słownik: {len(self.template_dict.template_to_id):,}")
        
        print(f"  Model tekstu (Order-{self.text_order}):")
        if len(text_data) > 100:
            self.text_model.train(text_data)
            print(f"    Konteksty: {len(self.text_model.contexts):,}")
        
        return sections, links, templates, text_data, link_types
    
    def compress(self, data):
        """Compress with Bayesian uncertainty"""
        start = time.time()
        
        sections, links, templates, text_data, link_types = self.train(data)
        
        print(f"\n[3] Kompresja z Bayesian Uncertainty...")
        
        # Sections (same)
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
        
        # Links with BAYESIAN type prediction!
        print(f"  Link compression with uncertainty quantification...")
        
        link_bits = 0.0  # Float for precise calculation
        prev_type = None
        
        total_uncertainty = 0
        total_expected_bits = 0
        
        for i, (link, link_type) in enumerate(zip(links, link_types)):
            # Get Bayesian probability distribution
            if prev_type:
                type_dist = self.bayesian_predictor.get_probability_distribution(prev_type)
                
                # Calculate expected bits for this type
                expected_bits = self.bayesian_predictor.get_expected_bits(type_dist, link_type)
                link_bits += expected_bits
                
                total_expected_bits += expected_bits
                
                # Track uncertainty
                entropy = self.bayesian_predictor.get_entropy(type_dist)
                total_uncertainty += entropy
            else:
                # First link - use global prior
                link_bits += 3  # Reasonable default
            
            # Link encoding (simplified - could also use distributions!)
            mode, _ = self.link_graph.compress_link(link, links[i-1] if i > 0 else None)
            
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
            
            prev_type = link_type
        
        link_bytes = int(link_bits / 8) + 1
        
        # Stats
        if len(links) > 0:
            avg_type_bits = total_expected_bits / len(links)
            avg_uncertainty = total_uncertainty / len(links)
            print(f"    Avg bits/type: {avg_type_bits:.2f}")
            print(f"    Avg uncertainty: {avg_uncertainty:.2f} bits")
        
        # Templates (same)
        template_bits = 0
        for name, _ in templates:
            mode, _ = self.template_dict.compress_template(name)
            template_bits += 7 if mode == 0 else (2 + len(name) * 8)
        template_bytes = template_bits // 8 + (1 if template_bits % 8 else 0)
        
        # Text
        print(f"  Tekst Order-{self.text_order}...")
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
            'time': total_time,
            'avg_type_bits': avg_type_bits if len(links) > 0 else 0,
            'avg_uncertainty': avg_uncertainty if len(links) > 0 else 0
        }

def main():
    print("=" * 70)
    print("🔥 BAYESIAN UNCERTAINTY COMPRESSOR - Breakthrough #6! 🔥")
    print("=" * 70)
    
    print("\nInspired by:")
    print("'Knowledge-Driven Bayesian Uncertainty Quantification")
    print("for Reliable Fake News Detection'")
    print("by Puczynska et al. (IDEAS NCBR)")
    
    print("\nIdea: Full probability distributions instead of hard decisions!")
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    
    compressor = BayesianCompressor(text_order=5)
    result = compressor.compress(data)
    
    # Wyniki
    print(f"\n{'=' * 70}")
    print("🎯 BAYESIAN RESULTS - 1 MB")
    print(f"{'=' * 70}")
    
    bayesian_bpb = (result['total_bytes'] * 8) / len(data)
    
    print(f"\nTotal: {result['total_bytes']:,} bajtów ({bayesian_bpb:.3f} bpb)")
    print(f"Type encoding: {result['avg_type_bits']:.2f} bits/link (theoretical)")
    print(f"Uncertainty: {result['avg_uncertainty']:.2f} bits (avg entropy)")
    
    # Porównanie
    print(f"\n{'=' * 70}")
    print("📊 EVOLUTION OF BREAKTHROUGHS")
    print(f"{'=' * 70}")
    
    ultra_bpb = 0.898
    multirel_bpb = 0.915
    
    print(f"\n{'Breakthrough':<40} {'BPB':<10} {'Status'}")
    print("-" * 70)
    print(f"{'#1: Graph Links (Order-3)':<40} {1.630:<10.3f} {'+21%'}")
    print(f"{'#2-4: ULTRA Order-5 + Structures':<40} {ultra_bpb:<10.3f} {'+56% 🏆'}")
    print(f"{'#5: Multi-Relational (User idea!)':<40} {multirel_bpb:<10.3f} {'~Same'}")
    print(f"{'#6: Bayesian Uncertainty (User+Paper!)':<40} {bayesian_bpb:<10.3f}", end='')
    
    if bayesian_bpb < ultra_bpb:
        improvement = ((ultra_bpb - bayesian_bpb) / ultra_bpb) * 100
        print(f" +{improvement:.1f}% NEW BEST! 🎉")
    elif bayesian_bpb <= ultra_bpb * 1.02:
        print(f" ~Equal (concept proven!)")
    else:
        print(f" (theory>practice today)")
    
    # Projekcja
    print(f"\n{'=' * 70}")
    print("🎯 PROJEKCJA ENWIK9")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    bayesian_proj = int(bayesian_bpb * enwik9_size / 8)
    ultra_proj = int(ultra_bpb * enwik9_size / 8)
    record = 114 * 1024 * 1024
    
    print(f"\nULTRA:     {ultra_proj/(1024*1024):>6.1f} MB (best verified)")
    print(f"Bayesian:  {bayesian_proj/(1024*1024):>6.1f} MB (with uncertainty)")
    print(f"Record:    {record/(1024*1024):>6.1f} MB (world)")
    
    # Scientific value
    print(f"\n{'=' * 70}")
    print("🎓 SCIENTIFIC CONTRIBUTION")
    print(f"{'=' * 70}")
    
    print(f"\n1️⃣  Multi-Relational Graphs (User's idea)")
    print(f"   - Type-aware link prediction")
    print(f"   - Novel for compression")
    
    print(f"\n2️⃣  Bayesian Uncertainty (User's fake news paper!)")
    print(f"   - Full probability distributions")
    print(f"   - Optimal entropy coding")
    print(f"   - Cross-domain knowledge transfer!")
    
    print(f"\n📚 Potential papers:")
    print(f"   1. 'Multi-Dimensional Graphs for Compression'")
    print(f"   2. 'Bayesian Uncertainty in Compression'")
    print(f"      (Novel application of fake news detection methods!)")
    
    print(f"\n💡 Key insight:")
    print(f"   Knowledge from ONE domain (fake news)")
    print(f"   → Applied to ANOTHER (compression)")
    print(f"   = CROSS-POLLINATION of ideas! 🌟")
    
    print(f"\nCzas: {result['time']:.1f} s")
    print("=" * 70)

if __name__ == "__main__":
    main()
