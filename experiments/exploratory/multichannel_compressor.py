#!/usr/bin/env python3
"""
Wielokanałowy kompresor dla Wikipedia
Rozbija dane na kanały (linki, nagłówki, tekst) i kompresuje każdy osobno
"""
import struct
import pickle
import time
from typing import List, Tuple
from arithmetic_coder import ArithmeticEncoder
from context_model import ContextModel

class WikiChannel:
    """Pojedynczy kanał z własnym modelem"""
    
    def __init__(self, name: str, order: int = 3):
        self.name = name
        self.order = order
        self.model = ContextModel(order=order)
        self.data = bytearray()
        self.compressed = None
        self.stats = {}
    
    def add(self, data: bytes):
        """Dodaj dane do kanału"""
        self.data.extend(data)
    
    def train(self):
        """Wytrenuj model na danych kanału"""
        if len(self.data) > 0:
            print(f"  Trening {self.name}: {len(self.data):,} bajtów, Order-{self.order}")
            self.model.train(bytes(self.data))
    
    def compress(self):
        """Skompresuj dane kanału"""
        if len(self.data) == 0:
            self.compressed = b''
            self.stats = {'original': 0, 'compressed': 0, 'bpb': 0}
            return
        
        print(f"  Kodowanie {self.name}...", end=' ')
        start = time.time()
        
        encoder = ArithmeticEncoder(precision_bits=32)
        self.model.start_encoding()
        
        # Prosty wrapper
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
        
        wrapper = SimpleWrapper(self.model)
        self.compressed = encoder.encode(list(self.data), wrapper)
        
        elapsed = time.time() - start
        bpb = (len(self.compressed) * 8) / len(self.data) if len(self.data) > 0 else 0
        
        print(f"{len(self.compressed):,} bajtów ({bpb:.3f} bpb) w {elapsed:.1f}s")
        
        self.stats = {
            'original': len(self.data),
            'compressed': len(self.compressed),
            'bpb': bpb,
            'time': elapsed
        }

class MultiChannelCompressor:
    """Główny kompresor wielokanałowy"""
    
    def __init__(self):
        # Definicje kanałów (name, order)
        self.channels = {
            'link': WikiChannel('link', order=2),       # Linki - Order-2 wystarczy
            'heading': WikiChannel('heading', order=2),  # Nagłówki - przewidywalne
            'template': WikiChannel('template', order=2), # Templates
            'text': WikiChannel('text', order=3),        # Główny tekst - Order-3
            'structure': WikiChannel('structure', order=1) # Markup - Order-1
        }
        
        # Metadata: pozycje i długości dla rekonstrukcji
        self.sequence = []  # Lista (channel_name, length) dla rekonstrukcji kolejności
    
    def parse_and_split(self, data: bytes):
        """
        Parsuje dane i dzieli na kanały
        Prostsza wersja bez regex - szybka i bezpieczna
        """
        print(f"\n[1] Parsowanie i podział na kanały...")
        print(f"    Rozmiar wejścia: {len(data):,} bajtów")
        
        i = 0
        total = len(data)
        last_report = 0
        
        while i < total:
            # Progress co 100 KB
            if i - last_report > 100000:
                pct = (i / total) * 100
                print(f"    Postęp: {pct:.1f}%", end='\r')
                last_report = i
            
            # Sprawdź linki [[...]]
            if i < total - 1 and data[i:i+2] == b'[[':
                end = data.find(b']]', i + 2)
                if end != -1:
                    # Zapisz link
                    link_content = data[i+2:end]
                    self.channels['link'].add(link_content)
                    self.channels['link'].add(b'\n')  # Separator
                    
                    # Zapisz strukturę (nawiasy)
                    self.channels['structure'].add(b'[[]]')
                    
                    self.sequence.append(('link', len(link_content) + 1))
                    
                    i = end + 2
                    continue
            
            # Sprawdź templates {{...}}
            if i < total - 1 and data[i:i+2] == b'{{':
                end = data.find(b'}}', i + 2)
                if end != -1:
                    template_content = data[i+2:end]
                    self.channels['template'].add(template_content)
                    self.channels['template'].add(b'\n')
                    
                    self.channels['structure'].add(b'{{}}')
                    
                    self.sequence.append(('template', len(template_content) + 1))
                    
                    i = end + 2
                    continue
            
            # Sprawdź nagłówki ==...==
            if i < total - 1 and data[i:i+2] == b'==':
                # Zlicz =
                j = i
                while j < total and data[j:j+1] == b'=':
                    j += 1
                
                level = j - i
                
                # Znajdź koniec nagłówka
                end = data.find(b'=' * level, j)
                if end != -1 and end > j:
                    heading_content = data[j:end].strip()
                    self.channels['heading'].add(heading_content)
                    self.channels['heading'].add(b'\n')
                    
                    self.channels['structure'].add(b'=' * level + b'=')
                    
                    self.sequence.append(('heading', len(heading_content) + 1))
                    
                    i = end + level
                    continue
            
            # XML tag <...>
            if data[i:i+1] == b'<':
                end = data.find(b'>', i + 1)
                if end != -1:
                    self.channels['structure'].add(data[i:end+1])
                    self.sequence.append(('structure', end - i + 1))
                    i = end + 1
                    continue
            
            # Entity &...;
            if data[i:i+1] == b'&':
                end = data.find(b';', i + 1)
                if end != -1 and end - i < 10:  # Rozsądna długość entity
                    self.channels['structure'].add(data[i:end+1])
                    self.sequence.append(('structure', end - i + 1))
                    i = end + 1
                    continue
            
            # Newline
            if data[i:i+1] == b'\n':
                self.channels['structure'].add(b'\n')
                self.sequence.append(('structure', 1))
                i += 1
                continue
            
            # Specjalne znaki markup
            if data[i:i+1] in b"*#:;'":
                self.channels['structure'].add(data[i:i+1])
                self.sequence.append(('structure', 1))
                i += 1
                continue
            
            # Plain text - zbieraj do następnego specjalnego
            start = i
            while i < total:
                ch = data[i:i+1]
                if ch in b'\n*#:;\'<&=' or (i < total - 1 and data[i:i+2] in [b'[[', b'{{', b'==']):
                    break
                i += 1
            
            if i > start:
                chunk = data[start:i]
                self.channels['text'].add(chunk)
                self.sequence.append(('text', len(chunk)))
        
        print(f"    Postęp: 100.0%")
        
        # Statystyki
        print(f"\n    Rozkład kanałów:")
        total_bytes = sum(len(ch.data) for ch in self.channels.values())
        for name, channel in self.channels.items():
            if len(channel.data) > 0:
                pct = (len(channel.data) / total_bytes) * 100
                print(f"      {name:<12}: {len(channel.data):>10,} bajtów ({pct:>5.1f}%)")
    
    def compress(self):
        """Kompresuje wszystkie kanały"""
        print(f"\n[2] Trening modeli...")
        for channel in self.channels.values():
            if len(channel.data) > 0:
                channel.train()
        
        print(f"\n[3] Kompresja kanałów...")
        for channel in self.channels.values():
            channel.compress()
    
    def save(self, output_path: str):
        """Zapisuje skompresowane archiwum"""
        print(f"\n[4] Zapis archiwum: {output_path}")
        
        with open(output_path, 'wb') as f:
            # Header: liczba kanałów
            f.write(struct.pack('<I', len(self.channels)))
            
            # Dla każdego kanału: name, order, model, compressed_data
            for name, channel in self.channels.items():
                # Nazwa kanału (max 20 bajtów)
                name_bytes = name.encode('utf-8')[:20].ljust(20, b'\x00')
                f.write(name_bytes)
                
                # Order
                f.write(struct.pack('<I', channel.order))
                
                # Model (serializowany)
                if len(channel.data) > 0:
                    model_data = channel.model.serialize()
                else:
                    model_data = b''
                
                f.write(struct.pack('<I', len(model_data)))
                f.write(model_data)
                
                # Skompresowane dane
                f.write(struct.pack('<I', len(channel.compressed)))
                f.write(channel.compressed)
                
                # Oryginalna długość (dla dekompresji)
                f.write(struct.pack('<I', len(channel.data)))
            
            # Sequence (dla rekonstrukcji)
            sequence_data = pickle.dumps(self.sequence)
            f.write(struct.pack('<I', len(sequence_data)))
            f.write(sequence_data)
    
    def print_stats(self):
        """Wyświetl statystyki kompresji"""
        print(f"\n{'=' * 70}")
        print("STATYSTYKI WIELOKANAŁOWE")
        print(f"{'=' * 70}")
        
        total_original = sum(ch.stats.get('original', 0) for ch in self.channels.values())
        total_compressed = sum(ch.stats.get('compressed', 0) for ch in self.channels.values())
        
        print(f"\n{'Kanał':<15} {'Oryginalny':<15} {'Skompresowany':<15} {'Bity/bajt':<10}")
        print("-" * 70)
        
        for name, channel in self.channels.items():
            if channel.stats.get('original', 0) > 0:
                print(f"{name:<15} {channel.stats['original']:<15,} "
                      f"{channel.stats['compressed']:<15,} "
                      f"{channel.stats['bpb']:<10.4f}")
        
        print("-" * 70)
        overall_bpb = (total_compressed * 8) / total_original if total_original > 0 else 0
        print(f"{'RAZEM':<15} {total_original:<15,} {total_compressed:<15,} {overall_bpb:<10.4f}")
        
        print(f"\nStopień kompresji: {(1 - total_compressed / total_original) * 100:.2f}%")
        
        return total_original, total_compressed, overall_bpb

def main():
    print("=" * 70)
    print("WIELOKANAŁOWY KOMPRESOR - Test")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    output_file = "data/enwik_10mb_multichannel.mch"
    
    # Wczytaj dane
    print(f"\n[0] Czytanie: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    print(f"    Rozmiar: {len(data):,} bajtów ({len(data) / (1024*1024):.2f} MB)")
    
    # Kompresja
    start_time = time.time()
    
    compressor = MultiChannelCompressor()
    compressor.parse_and_split(data)
    compressor.compress()
    compressor.save(output_file)
    
    total_time = time.time() - start_time
    
    # Statystyki
    orig_size, comp_size, bpb = compressor.print_stats()
    
    # Porównanie
    import zlib
    zlib_size = len(zlib.compress(data, level=9))
    zlib_bpb = (zlib_size * 8) / orig_size
    
    # Baseline Order-3
    baseline_file = "data/enwik_10mb_order3.ctx"
    import os
    if os.path.exists(baseline_file):
        baseline_size = os.path.getsize(baseline_file) - 8  # Odejmij header
        # Odczytaj rozmiar modelu
        with open(baseline_file, 'rb') as f:
            f.read(4)  # skip orig_len
            model_len = struct.unpack('<I', f.read(4))[0]
        baseline_data_size = baseline_size - model_len
        baseline_bpb = (baseline_data_size * 8) / orig_size
    else:
        baseline_bpb = 2.361  # Z wcześniejszych testów
    
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    print(f"\n{'Metoda':<25} {'Bity/bajt':<12} {'vs zlib':<15}")
    print("-" * 70)
    print(f"{'zlib -9':<25} {zlib_bpb:<12.4f} {'baseline':<15}")
    print(f"{'Order-3 (single)':<25} {baseline_bpb:<12.4f} {((zlib_bpb - baseline_bpb) / zlib_bpb * 100):>+6.1f}%")
    print(f"{'Multichannel':<25} {bpb:<12.4f} {((zlib_bpb - bpb) / zlib_bpb * 100):>+6.1f}%")
    print("-" * 70)
    
    improvement = ((baseline_bpb - bpb) / baseline_bpb) * 100
    if improvement > 0:
        print(f"\n✓ Multichannel lepszy od baseline o {improvement:.2f}%!")
    else:
        print(f"\n⚠ Multichannel gorszy od baseline o {-improvement:.2f}%")
        print(f"  (To może się zdarzyć na małych plikach - model overhead)")
    
    print(f"\nCałkowity czas: {total_time:.1f} s")
    print(f"Prędkość: {len(data) / (1024*1024*total_time):.2f} MB/s")
    print("=" * 70)

if __name__ == "__main__":
    main()
