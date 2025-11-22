#!/usr/bin/env python3
"""
Test wielokanałowego kompresora na 1 MB - sweet spot do oceny potencjału
"""
import struct
import time
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

def multichannel_1mb_test():
    print("=" * 70)
    print("MULTICHANNEL - Test na 1 MB")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    # Wczytaj 1 MB
    print(f"\n[1] Czytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"    Rozmiar: {len(data):,} bajtów")
    start_total = time.time()
    
    # Szybkie parsowanie z progress
    print(f"\n[2] Parsowanie i podział na kanały...")
    
    link_data = bytearray()
    text_data = bytearray()
    other_data = bytearray()  # Nagłówki, templates, struktura
    
    i = 0
    total = len(data)
    last_report = 0
    parse_start = time.time()
    
    while i < total:
        if i - last_report > 50000:
            pct = (i / total) * 100
            print(f"    Postęp parsowania: {pct:.1f}%", end='\r')
            last_report = i
        
        # Linki [[...]]
        if i < total - 1 and data[i:i+2] == b'[[':
            end = data.find(b']]', i + 2)
            if end != -1 and end - i < 200:  # Limit długości linka
                link_data.extend(data[i+2:end])
                link_data.append(ord('\n'))
                i = end + 2
                continue
        
        # Templates {{...}}
        if i < total - 1 and data[i:i+2] == b'{{':
            end = data.find(b'}}', i + 2)
            if end != -1 and end - i < 200:
                other_data.extend(data[i+2:end])
                other_data.append(ord('|'))
                i = end + 2
                continue
        
        # Nagłówki ==...==
        if i < total - 1 and data[i:i+2] == b'==':
            j = i
            while j < total and data[j:j+1] == b'=':
                j += 1
            level = j - i
            end = data.find(b'=' * level, j)
            if end != -1 and end > j and end - j < 100:
                other_data.extend(data[j:end].strip())
                other_data.append(ord('\n'))
                i = end + level
                continue
        
        # XML/specjalne znaki
        if data[i:i+1] in b'<>&\n*#:;\'"':
            other_data.append(data[i])
            i += 1
            continue
        
        # Plain text
        text_data.append(data[i])
        i += 1
    
    parse_time = time.time() - parse_start
    print(f"\n    Parsowanie: {parse_time:.2f} s")
    print(f"\n    Rozkład:")
    print(f"      Linki:      {len(link_data):>8,} bajtów ({len(link_data)/total*100:>5.1f}%)")
    print(f"      Tekst:      {len(text_data):>8,} bajtów ({len(text_data)/total*100:>5.1f}%)")
    print(f"      Inne:       {len(other_data):>8,} bajtów ({len(other_data)/total*100:>5.1f}%)")
    
    # Kompresja - 3 kanały
    print(f"\n[3] Kompresja kanałów...")
    results = {}
    
    # Kanał 1: Linki (Order-2)
    if len(link_data) > 100:
        print(f"\n    Kanał LINKI (Order-2):")
        print(f"      Trening...", end=' ')
        t = time.time()
        link_model = ContextModel(order=2)
        link_model.train(bytes(link_data))
        print(f"{time.time()-t:.1f}s")
        
        print(f"      Kodowanie...", end=' ')
        t = time.time()
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
        print(f"{time.time()-t:.1f}s → {len(link_compressed):,} B ({link_bpb:.3f} bpb)")
        results['link'] = (len(link_data), len(link_compressed), link_bpb)
    else:
        link_compressed = b''
        results['link'] = (0, 0, 0)
    
    # Kanał 2: Tekst główny (Order-3)
    print(f"\n    Kanał TEKST (Order-3):")
    print(f"      Trening...", end=' ')
    t = time.time()
    text_model = ContextModel(order=3)
    text_model.train(bytes(text_data))
    print(f"{time.time()-t:.1f}s")
    
    print(f"      Kodowanie...", end=' ')
    t = time.time()
    encoder = ArithmeticEncoder(precision_bits=32)
    text_model.start_encoding()
    wrapper = SimpleWrapper(text_model)
    text_compressed = encoder.encode(list(text_data), wrapper)
    text_bpb = (len(text_compressed) * 8) / len(text_data)
    print(f"{time.time()-t:.1f}s → {len(text_compressed):,} B ({text_bpb:.3f} bpb)")
    results['text'] = (len(text_data), len(text_compressed), text_bpb)
    
    # Kanał 3: Inne (Order-2)
    if len(other_data) > 100:
        print(f"\n    Kanał INNE (Order-2):")
        print(f"      Trening...", end=' ')
        t = time.time()
        other_model = ContextModel(order=2)
        other_model.train(bytes(other_data))
        print(f"{time.time()-t:.1f}s")
        
        print(f"      Kodowanie...", end=' ')
        t = time.time()
        encoder = ArithmeticEncoder(precision_bits=32)
        other_model.start_encoding()
        wrapper = SimpleWrapper(other_model)
        other_compressed = encoder.encode(list(other_data), wrapper)
        other_bpb = (len(other_compressed) * 8) / len(other_data)
        print(f"{time.time()-t:.1f}s → {len(other_compressed):,} B ({other_bpb:.3f} bpb)")
        results['other'] = (len(other_data), len(other_compressed), other_bpb)
    else:
        other_compressed = b''
        results['other'] = (0, 0, 0)
    
    # Baseline dla porównania
    print(f"\n[4] Baseline Single Order-3...")
    print(f"    Trening...", end=' ')
    t = time.time()
    single_model = ContextModel(order=3)
    single_model.train(data)
    print(f"{time.time()-t:.1f}s")
    
    print(f"    Kodowanie...", end=' ')
    t = time.time()
    single_model.start_encoding()
    encoder = ArithmeticEncoder(precision_bits=32)
    wrapper = SimpleWrapper(single_model)
    single_compressed = encoder.encode(list(data), wrapper)
    single_bpb = (len(single_compressed) * 8) / len(data)
    print(f"{time.time()-t:.1f}s → {len(single_compressed):,} B ({single_bpb:.3f} bpb)")
    
    total_time = time.time() - start_total
    
    # Wyniki
    print(f"\n{'=' * 70}")
    print("WYNIKI")
    print(f"{'=' * 70}")
    
    total_multi_compressed = len(link_compressed) + len(text_compressed) + len(other_compressed)
    multi_bpb = (total_multi_compressed * 8) / len(data)
    
    import zlib
    zlib_compressed = zlib.compress(data, level=9)
    zlib_bpb = (len(zlib_compressed) * 8) / len(data)
    
    print(f"\n{'Metoda':<30} {'Rozmiar':<15} {'Bity/bajt':<12}")
    print("-" * 70)
    print(f"{'Oryginalny':<30} {len(data):<15,} {8.000:<12.3f}")
    print(f"{'zlib -9':<30} {len(zlib_compressed):<15,} {zlib_bpb:<12.3f}")
    print(f"{'Single Order-3':<30} {len(single_compressed):<15,} {single_bpb:<12.3f}")
    print(f"{'Multichannel (3 kanały)':<30} {total_multi_compressed:<15,} {multi_bpb:<12.3f}")
    
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    
    improvement_vs_zlib = ((zlib_bpb - multi_bpb) / zlib_bpb) * 100
    improvement_vs_single = ((single_bpb - multi_bpb) / single_bpb) * 100
    
    print(f"\nMultichannel vs zlib:         {improvement_vs_zlib:>+7.2f}%")
    print(f"Multichannel vs single:       {improvement_vs_single:>+7.2f}%")
    
    if improvement_vs_single > 0:
        print(f"\n✓ Multichannel LEPSZY od baseline o {improvement_vs_single:.2f}%!")
    elif improvement_vs_single > -1:
        print(f"\n≈ Multichannel prawie identyczny jak baseline ({improvement_vs_single:.2f}%)")
    else:
        print(f"\n⚠ Multichannel gorszy od baseline o {-improvement_vs_single:.2f}%")
    
    # Projekcja
    print(f"\n{'=' * 70}")
    print("PROJEKCJA NA ENWIK9 (1 GB)")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    
    zlib_proj = int(zlib_bpb * enwik9_size / 8)
    single_proj = int(single_bpb * enwik9_size / 8)
    multi_proj = int(multi_bpb * enwik9_size / 8)
    
    print(f"\n{'Metoda':<30} {'Rozmiar':<20}")
    print("-" * 70)
    print(f"{'zlib':<30} {zlib_proj:>15,} B  ({zlib_proj/(1024*1024):>6.1f} MB)")
    print(f"{'Single Order-3':<30} {single_proj:>15,} B  ({single_proj/(1024*1024):>6.1f} MB)")
    print(f"{'Multichannel':<30} {multi_proj:>15,} B  ({multi_proj/(1024*1024):>6.1f} MB)")
    
    savings = single_proj - multi_proj
    if savings > 0:
        print(f"\nOszczędność vs baseline: {savings:,} B ({savings/(1024*1024):.1f} MB)")
    
    print(f"\nCałkowity czas: {total_time:.1f} s ({len(data)/(1024*1024*total_time):.2f} MB/s)")
    print("=" * 70)

if __name__ == "__main__":
    multichannel_1mb_test()
