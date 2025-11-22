#!/usr/bin/env python3
"""
Test wyższych orderów: Order-4 i Order-5
Sprawdzamy czy warto zwiększać kontekst
"""
import time
from context_model import ContextModel
from arithmetic_coder import ArithmeticEncoder

def test_order(data, order):
    """Test pojedynczego ordera"""
    print(f"\n{'=' * 70}")
    print(f"ORDER-{order} TEST")
    print(f"{'=' * 70}")
    
    start = time.time()
    
    # Trenuj model
    print(f"\nTrening Order-{order}...")
    model = ContextModel(order=order)
    model.train(data)
    
    train_time = time.time() - start
    print(f"Czas treningu: {train_time:.1f} s")
    print(f"Konteksty: {len(model.contexts):,}")
    
    # Koduj
    print(f"\nKodowanie...")
    start = time.time()
    
    encoder = ArithmeticEncoder(precision_bits=32)
    model.start_encoding()
    
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
    
    wrapper = SimpleWrapper(model)
    compressed = encoder.encode(list(data), wrapper)
    
    encode_time = time.time() - start
    
    bpb = (len(compressed) * 8) / len(data)
    
    print(f"Czas kodowania: {encode_time:.1f} s")
    print(f"Rozmiar: {len(compressed):,} bajtów")
    print(f"Bits per byte: {bpb:.3f}")
    
    total_time = train_time + encode_time
    speed = len(data) / (1024 * 1024 * total_time)
    
    print(f"\nCzas total: {total_time:.1f} s")
    print(f"Prędkość: {speed:.3f} MB/s")
    
    return {
        'order': order,
        'bpb': bpb,
        'compressed_size': len(compressed),
        'contexts': len(model.contexts),
        'train_time': train_time,
        'encode_time': encode_time,
        'total_time': total_time,
        'speed': speed
    }

def main():
    print("=" * 70)
    print("HIGHER ORDER CONTEXT MODELS TEST")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    # Test na mniejszym fragmencie (100 KB) żeby szybko zobaczyć trend
    print(f"\nCzytanie 100 KB z: {input_file}")
    print("(Mały test żeby szybko zobaczyć czy warto)")
    
    with open(input_file, 'rb') as f:
        data = f.read(100 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    
    # Test różnych orderów
    results = []
    
    for order in [3, 4, 5, 6]:
        try:
            result = test_order(data, order)
            results.append(result)
        except MemoryError:
            print(f"\n⚠️ Order-{order}: Out of memory!")
            break
        except Exception as e:
            print(f"\n⚠️ Order-{order}: Error: {e}")
            break
    
    # Podsumowanie
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    
    if results:
        print(f"\n{'Order':<8} {'BPB':<10} {'Konteksty':<12} {'Czas':<10} {'vs Order-3'}")
        print("-" * 70)
        
        baseline_bpb = next((r['bpb'] for r in results if r['order'] == 3), None)
        
        for r in results:
            improvement = ""
            if baseline_bpb and r['order'] > 3:
                imp = ((baseline_bpb - r['bpb']) / baseline_bpb) * 100
                improvement = f"{'+' if imp > 0 else ''}{imp:.2f}%"
            
            print(f"{r['order']:<8} {r['bpb']:<10.3f} {r['contexts']:<12,} {r['total_time']:<10.1f}s {improvement}")
    
    # Analiza trade-off
    print(f"\n{'=' * 70}")
    print("ANALIZA")
    print(f"{'=' * 70}")
    
    if len(results) >= 2:
        for i in range(1, len(results)):
            prev = results[i-1]
            curr = results[i]
            
            bpb_gain = ((prev['bpb'] - curr['bpb']) / prev['bpb']) * 100
            time_cost = curr['total_time'] / prev['total_time']
            memory_cost = curr['contexts'] / prev['contexts']
            
            print(f"\nOrder-{prev['order']} → Order-{curr['order']}:")
            print(f"  BPB improvement: {bpb_gain:+.2f}%")
            print(f"  Time cost: {time_cost:.2f}x slower")
            print(f"  Memory cost: {memory_cost:.2f}x more contexts")
            
            # Czy warto?
            if bpb_gain > 2 and time_cost < 5:
                print(f"  ✓ WARTO! Dobry trade-off")
            elif bpb_gain > 1:
                print(f"  ~ Marginalny benefit")
            else:
                print(f"  ✗ Za mały gain")
    
    # Rekomendacja
    print(f"\n{'=' * 70}")
    print("REKOMENDACJA")
    print(f"{'=' * 70}")
    
    if len(results) >= 3:
        best_tradeoff = max(results[1:], key=lambda r: r['bpb'])  # Najlepszy BPB > Order-3
        
        if best_tradeoff:
            improvement = ((results[0]['bpb'] - best_tradeoff['bpb']) / results[0]['bpb']) * 100
            
            if improvement > 3:
                print(f"\n✓ Order-{best_tradeoff['order']} daje {improvement:.1f}% improvement!")
                print(f"  Warto użyć zamiast Order-3")
                
                # Projekcja na full system
                current_text_bpb = 2.268  # Z ostatniego testu 10 MB
                new_text_bpb = current_text_bpb * (1 - improvement/100)
                
                # Tekst to ~96.7% total compressed size
                total_improvement = improvement * 0.967
                
                print(f"\n  Projekcja na pełny system:")
                print(f"    Obecny tekst: {current_text_bpb:.3f} bpb")
                print(f"    Nowy tekst: {new_text_bpb:.3f} bpb")
                print(f"    Total improvement: ~{total_improvement:.1f}%")
                
                current_total_bpb = 1.821  # Z ultimate 10 MB
                new_total_bpb = current_total_bpb * (1 - total_improvement/100)
                
                enwik9_proj = int(new_total_bpb * 1_000_000_000 / 8)
                print(f"    Nowy total: ~{new_total_bpb:.3f} bpb")
                print(f"    Projekcja enwik9: ~{enwik9_proj/(1024*1024):.0f} MB")
            else:
                print(f"\n~ Order-{best_tradeoff['order']} daje tylko {improvement:.1f}%")
                print(f"  Marginalny benefit, może nie warto")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
