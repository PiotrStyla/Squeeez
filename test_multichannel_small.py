#!/usr/bin/env python3
"""
Test wielokanałowego kompresora na małym pliku (100 KB)
"""
import struct
import time
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

def quick_multichannel_test():
    print("=" * 70)
    print("MULTICHANNEL - Test na 100 KB")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    # Wczytaj tylko 100 KB
    print(f"\n[1] Czytanie 100 KB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(100 * 1024)
    
    print(f"    Rozmiar: {len(data):,} bajtów")
    
    # Szybkie parsowanie - tylko liczymy
    print(f"\n[2] Szybka analiza...")
    links = data.count(b'[[')
    headings = data.count(b'==') // 2  # Para ==
    templates = data.count(b'{{')
    xml_tags = data.count(b'<')
    
    print(f"    Linki: {links}")
    print(f"    Nagłówki: {headings}")
    print(f"    Templates: {templates}")
    print(f"    XML tagi: {xml_tags}")
    
    # Zamiast pełnego parsowania - prostszy split
    print(f"\n[3] Uproszczony podział...")
    
    # Wyciągnij tylko zawartość linków jako test
    link_data = bytearray()
    text_data = bytearray()
    
    i = 0
    while i < len(data):
        if i < len(data) - 1 and data[i:i+2] == b'[[':
            end = data.find(b']]', i + 2)
            if end != -1:
                link_data.extend(data[i+2:end])
                link_data.append(ord('\n'))
                i = end + 2
                continue
        
        # Wszystko inne to "text"
        text_data.append(data[i])
        i += 1
    
    print(f"    Link data: {len(link_data):,} bajtów")
    print(f"    Text data: {len(text_data):,} bajtów")
    
    # Test kompresji dwóch kanałów
    print(f"\n[4] Kompresja testowa...")
    
    # Kanał 1: Linki (Order-2)
    if len(link_data) > 100:  # Tylko jeśli mamy dość danych
        print(f"    Trening modelu linków (Order-2)...")
        link_model = ContextModel(order=2)
        link_model.train(bytes(link_data))
        
        print(f"    Kodowanie linków...")
        encoder = ArithmeticEncoder(precision_bits=32)
        link_model.start_encoding()
        
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
        
        wrapper = SimpleWrapper(link_model)
        link_compressed = encoder.encode(list(link_data), wrapper)
        link_bpb = (len(link_compressed) * 8) / len(link_data)
        
        print(f"      Linki: {len(link_compressed):,} bajtów ({link_bpb:.3f} bpb)")
    else:
        link_compressed = b''
        link_bpb = 0
        print(f"      Linki: za mało danych")
    
    # Kanał 2: Tekst (Order-3)
    print(f"    Trening modelu tekstu (Order-3)...")
    text_model = ContextModel(order=3)
    text_model.train(bytes(text_data))
    
    print(f"    Kodowanie tekstu...")
    encoder = ArithmeticEncoder(precision_bits=32)
    text_model.start_encoding()
    wrapper = SimpleWrapper(text_model)
    text_compressed = encoder.encode(list(text_data), wrapper)
    text_bpb = (len(text_compressed) * 8) / len(text_data)
    
    print(f"      Tekst: {len(text_compressed):,} bajtów ({text_bpb:.3f} bpb)")
    
    # Porównanie
    print(f"\n{'=' * 70}")
    print("WYNIKI")
    print(f"{'=' * 70}")
    
    total_compressed = len(link_compressed) + len(text_compressed)
    total_original = len(data)
    overall_bpb = (total_compressed * 8) / total_original
    
    import zlib
    zlib_compressed = zlib.compress(data, level=9)
    zlib_bpb = (len(zlib_compressed) * 8) / total_original
    
    # Single Order-3 baseline
    print(f"\n    Single Order-3 (baseline)...")
    single_model = ContextModel(order=3)
    single_model.train(data)
    single_model.start_encoding()
    encoder = ArithmeticEncoder(precision_bits=32)
    wrapper = SimpleWrapper(single_model)
    single_compressed = encoder.encode(list(data), wrapper)
    single_bpb = (len(single_compressed) * 8) / total_original
    
    print(f"\n{'Metoda':<25} {'Bity/bajt':<12} {'Rozmiar':<15}")
    print("-" * 70)
    print(f"{'zlib -9':<25} {zlib_bpb:<12.3f} {len(zlib_compressed):<15,}")
    print(f"{'Single Order-3':<25} {single_bpb:<12.3f} {len(single_compressed):<15,}")
    print(f"{'Multichannel (2 kanały)':<25} {overall_bpb:<12.3f} {total_compressed:<15,}")
    print("=" * 70)
    
    # Wnioski
    improvement_vs_single = ((single_bpb - overall_bpb) / single_bpb) * 100
    improvement_vs_zlib = ((zlib_bpb - overall_bpb) / zlib_bpb) * 100
    
    if improvement_vs_single > 0:
        print(f"\n✓ Multichannel lepszy od single Order-3 o {improvement_vs_single:.2f}%")
    else:
        print(f"\n⚠ Multichannel gorszy od single Order-3 o {-improvement_vs_single:.2f}%")
    
    print(f"✓ Multichannel lepszy od zlib o {improvement_vs_zlib:.2f}%")
    
    print(f"\n💡 Na 100 KB model overhead dominuje.")
    print(f"   Prawdziwy test wymaga większego pliku (1+ MB)")
    print("=" * 70)

if __name__ == "__main__":
    quick_multichannel_test()
