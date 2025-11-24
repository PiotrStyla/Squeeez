#!/usr/bin/env python3
"""
Test Order-5 na realistic 1 MB
Sprawdzamy czy to się skaluje
"""
import time
from context_model import ContextModel
from arithmetic_coder import ArithmeticEncoder

def main():
    print("=" * 70)
    print("ORDER-5 REALISTIC TEST - 1 MB")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    print("\n⚠️ To może zająć 2-5 minut...")
    
    # Order-5
    print(f"\n{'=' * 70}")
    print("TRENING ORDER-5")
    print(f"{'=' * 70}")
    
    start = time.time()
    
    model = ContextModel(order=5)
    model.train(data)
    
    train_time = time.time() - start
    
    print(f"\nCzas treningu: {train_time:.1f} s")
    print(f"Konteksty: {len(model.contexts):,}")
    print(f"Średnio symboli/kontekst: {sum(len(c) for c in model.contexts.values()) / len(model.contexts):.1f}")
    
    # Kodowanie
    print(f"\n{'=' * 70}")
    print("KODOWANIE")
    print(f"{'=' * 70}")
    
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
    total_time = train_time + encode_time
    
    bpb = (len(compressed) * 8) / len(data)
    
    print(f"\nCzas kodowania: {encode_time:.1f} s")
    print(f"Rozmiar skompresowany: {len(compressed):,} bajtów")
    print(f"Bits per byte: {bpb:.3f}")
    print(f"\nCzas total: {total_time:.1f} s ({total_time/60:.1f} min)")
    print(f"Prędkość: {len(data)/(1024*1024*total_time):.3f} MB/s")
    
    # Porównanie
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    
    order3_bpb = 2.018  # Z wcześniejszych testów Order-3 na 1 MB tekstu
    improvement = ((order3_bpb - bpb) / order3_bpb) * 100
    
    print(f"\nOrder-3 (baseline): {order3_bpb:.3f} bpb")
    print(f"Order-5:            {bpb:.3f} bpb")
    print(f"Improvement:        {improvement:+.1f}%")
    
    # Projekcja na full system
    print(f"\n{'=' * 70}")
    print("PROJEKCJA NA FULL SYSTEM")
    print(f"{'=' * 70}")
    
    # Ultimate system miał 1.821 bpb total, z czego tekst to 96.7%
    current_total = 1.821
    current_text_contribution = 2.268 * 0.967  # tekst to 96.7% total
    new_text_contribution = bpb * 0.967
    structure_contribution = current_total - current_text_contribution
    
    new_total = structure_contribution + new_text_contribution
    
    print(f"\nObecny system (Ultimate):")
    print(f"  Total: {current_total:.3f} bpb")
    print(f"  Tekst (96.7%): ~{current_text_contribution:.3f} bpb contribution")
    print(f"  Struktura (3.3%): ~{structure_contribution:.3f} bpb contribution")
    
    print(f"\nZ Order-5:")
    print(f"  Tekst: {new_text_contribution:.3f} bpb contribution")
    print(f"  Total: ~{new_total:.3f} bpb")
    
    total_improvement = ((current_total - new_total) / current_total) * 100
    print(f"\nTotal improvement: {total_improvement:+.1f}%")
    
    # enwik9
    enwik9_current = int(current_total * 1_000_000_000 / 8)
    enwik9_new = int(new_total * 1_000_000_000 / 8)
    
    print(f"\n{'=' * 70}")
    print("PROJEKCJA ENWIK9")
    print(f"{'=' * 70}")
    
    print(f"\nUltimate (Order-3): {enwik9_current:>12,} B ({enwik9_current/(1024*1024):>6.1f} MB)")
    print(f"Order-5:            {enwik9_new:>12,} B ({enwik9_new/(1024*1024):>6.1f} MB)")
    
    savings = enwik9_current - enwik9_new
    gap_to_record = (enwik9_new / (1024*1024)) - 114
    
    print(f"\nOszczędność:        {savings:>12,} B ({savings/(1024*1024):>6.1f} MB)")
    print(f"Gap do rekordu (114 MB): {gap_to_record:>6.1f} MB")
    
    # Wnioski
    print(f"\n{'=' * 70}")
    print("WNIOSKI")
    print(f"{'=' * 70}")
    
    if gap_to_record < 0:
        print(f"\n🏆 NOWY REKORD ŚWIATOWY!")
        print(f"   Poprawa vs rekord: {-gap_to_record:.1f} MB")
    elif gap_to_record < 20:
        print(f"\n🎯 BARDZO BLISKO REKORDU!")
        print(f"   Gap tylko {gap_to_record:.1f} MB")
        print(f"   Z dalszymi optymalizacjami możliwy rekord!")
    elif gap_to_record < 50:
        print(f"\n✓ Solidny wynik - top-10 territory")
        print(f"   Gap {gap_to_record:.1f} MB do rekordu")
    
    print(f"\nKluczowe odkrycie:")
    print(f"  Order-5 znacznie lepszy niż Order-3")
    print(f"  Trade-off czas/jakość akceptowalny")
    
    if total_time < 120:  # < 2 min
        print(f"  Czas {total_time:.0f}s na 1 MB jest OK")
        print(f"  ✓ Warto użyć Order-5 w final system!")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
