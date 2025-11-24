#!/usr/bin/env python3
"""
ORDER-7 TEST on 1 MB
Sprawdzamy czy ekstremalne ordery działają na większych danych
"""
import time
from context_model import ContextModel
from arithmetic_coder import ArithmeticEncoder

def main():
    print("=" * 70)
    print("🔥 ORDER-7 REALISTIC TEST - 1 MB 🔥")
    print("=" * 70)
    
    print("\n100 KB test pokazał: Order-7 = 0.361 bpb (+78% vs Order-3)")
    print("Czy to się utrzyma na 1 MB?")
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    print("\n⚠️ Order-7 może zająć 2-5 minut i użyć dużo pamięci...")
    print("   (To jest moment prawdy!)\n")
    
    # Order-7 test
    print("=" * 70)
    print("TRENING ORDER-7")
    print("=" * 70)
    
    start_train = time.time()
    model = ContextModel(order=7)
    model.train(data)
    train_time = time.time() - start_train
    
    contexts = len(model.contexts)
    avg_symbols = sum(len(symbols) for symbols in model.contexts.values()) / len(model.contexts)
    
    print(f"Konteksty: {contexts:,}")
    print(f"Średnio symboli/kontekst: {avg_symbols:.1f}")
    print(f"Czas treningu: {train_time:.1f} s")
    
    # Compression
    print(f"\n{'=' * 70}")
    print("KODOWANIE")
    print(f"{'=' * 70}\n")
    
    start_compress = time.time()
    
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
    
    compress_time = time.time() - start_compress
    total_time = train_time + compress_time
    
    bpb = (len(compressed) * 8) / len(data)
    
    print(f"Czas kodowania: {compress_time:.1f} s")
    print(f"Rozmiar skompresowany: {len(compressed):,} bajtów")
    print(f"Bits per byte: {bpb:.3f}")
    
    print(f"\nCzas total: {total_time:.1f} s ({total_time/60:.1f} min)")
    print(f"Prędkość: {len(data)/(1024*1024*total_time):.3f} MB/s")
    
    # Porównanie
    print(f"\n{'=' * 70}")
    print("PORÓWNANIE")
    print(f"{'=' * 70}")
    
    order3_bpb = 2.018  # Z wcześniejszych testów
    order5_bpb = 1.088
    order6_100kb = 0.508
    order7_100kb = 0.361
    
    print(f"\nOrder-3 (1 MB):      {order3_bpb:.3f} bpb")
    print(f"Order-5 (1 MB):      {order5_bpb:.3f} bpb (+{((order3_bpb-order5_bpb)/order3_bpb*100):.1f}%)")
    print(f"Order-7 (100 KB):    {order7_100kb:.3f} bpb (+78.1% vs Order-3)")
    print(f"Order-7 (1 MB):      {bpb:.3f} bpb", end='')
    
    if order3_bpb > 0:
        improvement = ((order3_bpb - bpb) / order3_bpb) * 100
        print(f" (+{improvement:.1f}%)")
    
    # Degradacja vs 100 KB
    degradation = ((bpb - order7_100kb) / order7_100kb) * 100
    print(f"\nDegradacja 100KB → 1MB: +{degradation:.1f}%")
    
    # PROJEKCJA ENWIK9
    print(f"\n{'=' * 70}")
    print("PROJEKCJA ENWIK9")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    record = 114 * 1024 * 1024
    
    # Conservative: assume continued degradation
    # 100KB → 1MB: measured degradation
    # 1MB → 10MB → 100MB → 1GB: assume similar per 10x
    
    # Linear extrapolation
    linear_proj = int(bpb * enwik9_size / 8)
    
    # Conservative (20% degradation)
    conservative_bpb = bpb * 1.2
    conservative_proj = int(conservative_bpb * enwik9_size / 8)
    
    # Very conservative (40% degradation)
    very_conservative_bpb = bpb * 1.4
    very_conservative_proj = int(very_conservative_bpb * enwik9_size / 8)
    
    print(f"\n{'Scenariusz':<25} {'BPB':<10} {'Rozmiar':<15} {'vs Record'}")
    print("─" * 70)
    print(f"{'Linear (optymistyczny)':<25} {bpb:<10.3f} {linear_proj/(1024*1024):>6.1f} MB    ", end='')
    gap = linear_proj - record
    if gap < 0:
        print(f"{-gap/(1024*1024):>5.1f} MB lepiej! 🏆")
    else:
        print(f"+{gap/(1024*1024):>5.1f} MB")
    
    print(f"{'Conservative (+20%)':<25} {conservative_bpb:<10.3f} {conservative_proj/(1024*1024):>6.1f} MB    ", end='')
    gap = conservative_proj - record
    if gap < 0:
        print(f"{-gap/(1024*1024):>5.1f} MB lepiej! 🏆")
    else:
        print(f"+{gap/(1024*1024):>5.1f} MB")
    
    print(f"{'Very conservative (+40%)':<25} {very_conservative_bpb:<10.3f} {very_conservative_proj/(1024*1024):>6.1f} MB    ", end='')
    gap = very_conservative_proj - record
    if gap < 0:
        print(f"{-gap/(1024*1024):>5.1f} MB lepiej! 🏆")
    else:
        print(f"+{gap/(1024*1024):>5.1f} MB")
    
    # VERDICT
    print(f"\n{'=' * 70}")
    print("VERDICT")
    print(f"{'=' * 70}")
    
    if bpb < 0.8:
        print(f"\n🏆🏆🏆 EKSTREMALNIE DOBRY WYNIK!")
        print(f"   Order-7 działa ŚWIETNIE na 1 MB")
        print(f"   {bpb:.3f} bpb = potencjał rekordu światowego!")
        
        if linear_proj < record:
            print(f"\n   🎯 Nawet z degradacją możliwy NOWY REKORD!")
        
    elif bpb < 1.0:
        print(f"\n✓✓ Bardzo dobry wynik")
        print(f"   Order-7 znacznie lepszy niż Order-5")
        print(f"   Potencjał top-5")
    
    # Praktyczność
    print(f"\n{'=' * 70}")
    print("PRAKTYCZNOŚĆ")
    print(f"{'=' * 70}")
    
    print(f"\nMemory: {contexts:,} kontekstów")
    print(f"  Na 1 GB: ~{contexts * 1000:,} kontekstów")
    print(f"  Estimate: ~{contexts * 1000 * 50 / (1024**2):.0f} MB RAM")
    
    print(f"\nSpeed: {len(data)/(1024*1024*total_time):.3f} MB/s")
    print(f"  Na 1 GB: ~{1000 * total_time / 60:.0f} min = {1000 * total_time / 3600:.1f} hours")
    
    if contexts * 1000 * 50 / (1024**2) < 32000:  # < 32 GB
        print(f"\n✓ FEASIBLE! Memory w granicach możliwości!")
        if 1000 * total_time / 3600 < 24:
            print(f"✓ Time OK! Możliwe w ciągu 24h!")
        else:
            print(f"⚠ Time długi, ale doable")
    else:
        print(f"\n⚠ Memory może być problem (potrzeba > 32 GB RAM)")
    
    # Save results
    with open('ORDER7_RESULTS.txt', 'w') as f:
        f.write(f"ORDER-7 TEST - 1 MB RESULTS\n")
        f.write(f"{'=' * 70}\n\n")
        f.write(f"Compression: {bpb:.3f} bpb\n")
        f.write(f"Contexts: {contexts:,}\n")
        f.write(f"Time: {total_time:.1f} s\n")
        f.write(f"Improvement vs Order-3: {improvement:.1f}%\n")
        f.write(f"\nProjection enwik9 (conservative): {conservative_proj/(1024*1024):.1f} MB\n")
        if conservative_proj < record:
            f.write(f"🏆 PROJECTED NEW RECORD!\n")
    
    print(f"\nWyniki zapisane do: ORDER7_RESULTS.txt")
    print("=" * 70)

if __name__ == "__main__":
    main()
