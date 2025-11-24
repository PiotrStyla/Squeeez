#!/usr/bin/env python3
"""
ORDER-6 TEST on 1 MB - SWEET SPOT?
Może być perfect balance: lepszy niż Order-5, mniej RAM niż Order-7
"""
import time
from context_model import ContextModel
from arithmetic_coder import ArithmeticEncoder

def main():
    print("=" * 70)
    print("🎯 ORDER-6 SWEET SPOT TEST - 1 MB 🎯")
    print("=" * 70)
    
    print("\nOrder-5: 1.088 bpb, 139 MB proj, DOABLE")
    print("Order-7: 0.611 bpb, 102 MB proj, 51 GB RAM!")
    print("\nOrder-6: Sweet spot? 🤔")
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 1 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(1024 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów\n")
    
    # Order-6 test
    print("=" * 70)
    print("TRENING ORDER-6")
    print("=" * 70)
    
    start_train = time.time()
    model = ContextModel(order=6)
    model.train(data)
    train_time = time.time() - start_train
    
    contexts = len(model.contexts)
    
    print(f"Konteksty: {contexts:,}")
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
    print(f"Rozmiar: {len(compressed):,} bajtów")
    print(f"BPB: {bpb:.3f}")
    print(f"\nTotal: {total_time:.1f} s")
    
    # Porównanie
    print(f"\n{'=' * 70}")
    print("ULTIMATE COMPARISON")
    print(f"{'=' * 70}")
    
    print(f"\n{'Order':<8} {'BPB (1MB)':<12} {'Contexts':<12} {'Time':<10} {'Improvement'}")
    print("─" * 70)
    print(f"{'3':<8} {'2.018':<12} {'~30K':<12} {'~2s':<10} {'baseline'}")
    print(f"{'5':<8} {'1.088':<12} {'334K':<12} {'~10s':<10} {'+46.1%'}")
    print(f"{'6':<8} {f'{bpb:.3f}':<12} {f'{contexts:,}':<12} {f'{total_time:.1f}s':<10}", end='')
    
    improvement_vs_3 = ((2.018 - bpb) / 2.018) * 100
    improvement_vs_5 = ((1.088 - bpb) / 1.088) * 100
    print(f" +{improvement_vs_3:.1f}% vs O3, +{improvement_vs_5:.1f}% vs O5")
    
    print(f"{'7':<8} {'0.611':<12} {'1.07M':<12} {'~19s':<10} {'+69.7%'}")
    
    # Memory estimate
    print(f"\n{'=' * 70}")
    print("PRAKTYCZNOŚĆ ORDER-6")
    print(f"{'=' * 70}")
    
    ram_per_context = 50  # bytes estimate
    ram_1gb_estimate = contexts * 1000 * ram_per_context / (1024**2)
    time_1gb_estimate = 1000 * total_time / 3600
    
    print(f"\nMemory na 1 GB: ~{ram_1gb_estimate:.0f} MB ({ram_1gb_estimate/1024:.1f} GB)")
    print(f"Time na 1 GB: ~{time_1gb_estimate:.1f} hours")
    
    if ram_1gb_estimate / 1024 < 32:
        print(f"\n✓✓ EXCELLENT! Memory feasible (< 32 GB)")
        print(f"✓✓ Time OK ({time_1gb_estimate:.1f}h reasonable)")
        feasible = True
    elif ram_1gb_estimate / 1024 < 64:
        print(f"\n✓ Good! Memory doable with server/cloud (< 64 GB)")
        feasible = True
    else:
        print(f"\n⚠ Memory high but possible with proper setup")
        feasible = False
    
    # Projekcja enwik9
    print(f"\n{'=' * 70}")
    print("FINAL PROJECTION ENWIK9")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    record = 114 * 1024 * 1024
    
    # Conservative scaling (based on observed degradation)
    # 100KB → 1MB: saw ~50-70% degradation for higher orders
    # 1MB → 1GB: assume another 20-30% degradation
    
    linear = int(bpb * enwik9_size / 8)
    conservative = int(bpb * 1.25 * enwik9_size / 8)
    very_conservative = int(bpb * 1.5 * enwik9_size / 8)
    
    print(f"\n{'Scenario':<25} {'BPB':<10} {'Size':<15} {'vs Record'}")
    print("─" * 70)
    
    scenarios = [
        ("Linear", bpb, linear),
        ("Conservative (+25%)", bpb * 1.25, conservative),
        ("V.Conservative (+50%)", bpb * 1.5, very_conservative),
    ]
    
    for name, scenario_bpb, projection in scenarios:
        gap = projection - record
        print(f"{name:<25} {scenario_bpb:<10.3f} {projection/(1024*1024):>6.1f} MB    ", end='')
        if gap < 0:
            print(f"{-gap/(1024*1024):>5.1f} MB better! RECORD!")
        else:
            print(f"+{gap/(1024*1024):>5.1f} MB")
    
    # FINAL VERDICT
    print(f"\n{'=' * 70}")
    print("ULTIMATE VERDICT")
    print(f"{'=' * 70}")
    
    if linear < record:
        print(f"\nPROJECTED WORLD RECORD!")
        print(f"  Order-6 = {bpb:.3f} bpb")
        print(f"  Projection: {linear/(1024*1024):.1f} MB")
        print(f"  vs Record: {-((linear - record)/(1024*1024)):.1f} MB better")
        
        if feasible:
            print(f"\n  AND IT'S FEASIBLE!")
            print(f"  Memory: {ram_1gb_estimate/1024:.1f} GB (doable!)")
            print(f"  Time: {time_1gb_estimate:.1f} hours (reasonable!)")
            print(f"\n  THIS IS THE SWEET SPOT!")
        else:
            print(f"\n  But needs {ram_1gb_estimate/1024:.0f} GB RAM")
    
    elif conservative < record:
        print(f"\nCONSERVATIVE: Still potential record!")
        print(f"  With 25% degradation: {conservative/(1024*1024):.1f} MB")
        print(f"  vs Record: {-((conservative - record)/(1024*1024)):.1f} MB better")
    
    elif very_conservative < record * 1.1:  # Within 10%
        print(f"\nVery close to record!")
        print(f"  Gap: {(very_conservative - record)/(1024*1024):.1f} MB")
        print(f"  Solid TOP-5 result")
    
    else:
        print(f"\nSolid improvement but not record-breaking")
        print(f"  Still excellent TOP-10 result!")
    
    # Comparison with other approaches
    print(f"\n{'=' * 70}")
    print("COMPARISON WITH ALL APPROACHES")
    print(f"{'=' * 70}")
    
    print(f"\n{'Method':<30} {'Proj (MB)':<12} {'Feasible?':<12} {'Status'}")
    print("─" * 70)
    print(f"{'ULTRA Order-5 (verified)':<30} {'139':<12} {'Yes':<12} {'TOP-10'}")
    print(f"{'Order-6 (projected)':<30} {f'{linear/(1024*1024):.0f}':<12} {('Yes' if feasible else 'Maybe'):<12}", end='')
    if linear < record:
        print(" RECORD POSSIBLE!")
    else:
        print(" TOP-5")
    print(f"{'Order-7 (projected)':<30} {'102':<12} {'Difficult':<12} {'RECORD but 51GB RAM'}")
    
    print(f"\n{'=' * 70}")
    print("RECOMMENDATION")
    print(f"{'=' * 70}")
    
    if feasible and linear < record * 1.2:
        print(f"\nOrder-6 is THE SWEET SPOT!")
        print(f"  - Better compression than Order-5")
        print(f"  - Feasible memory/time")
        print(f"  - Potential world record")
        print(f"\nNext step: Test on 10 MB to verify!")
    else:
        print(f"\nOrder-5 remains most practical:")
        print(f"  - Verified on 10 MB: 139 MB")
        print(f"  - Solid TOP-10")
        print(f"  - Fully feasible")
        print(f"\nOrder-6/7 theoretical but challenging")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
