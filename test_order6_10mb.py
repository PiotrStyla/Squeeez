#!/usr/bin/env python3
"""
ORDER-6 ON 10 MB - THE DECISIVE TEST
This determines if 98 MB world record projection is real!

If < 1.0 bpb → Record is REAL, go for it!
If ~1.1 bpb → Still TOP-5, good
If > 1.2 bpb → Order-5 safer bet
"""
import time
from context_model import ContextModel
from arithmetic_coder import ArithmeticEncoder

def test_order6_10mb():
    print("=" * 70)
    print("🎯 ORDER-6 ON 10 MB - THE DECISIVE TEST!")
    print("=" * 70)
    
    input_file = "data/enwik_10mb"
    
    print(f"\nCzytanie 10 MB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    print(f"Rozmiar: {len(data):,} bajtów ({len(data)/(1024*1024):.1f} MB)")
    
    # Przygotowanie
    print(f"\n[1] Przygotowanie Order-6 model...")
    model = ContextModel(order=6)
    
    print(f"    Trening modelu...")
    train_start = time.time()
    model.train(data)
    train_time = time.time() - train_start
    
    print(f"    Czas treningu: {train_time:.1f} s ({train_time/60:.1f} min)")
    print(f"    Konteksty: {len(model.contexts):,}")
    
    if len(model.contexts) > 0:
        avg_symbols = sum(sum(c.values()) for c in model.contexts.values()) / len(model.contexts)
        print(f"    Średnio symboli/kontekst: {avg_symbols:.1f}")
    
    # Estimate memory
    import sys
    mem_contexts = sys.getsizeof(model.contexts)
    for ctx_dict in list(model.contexts.values())[:100]:  # Sample
        mem_contexts += sys.getsizeof(ctx_dict)
        for k, v in list(ctx_dict.items())[:10]:
            mem_contexts += sys.getsizeof(k) + sys.getsizeof(v)
    
    # Extrapolate
    mem_total_mb = (mem_contexts * len(model.contexts) / 100) / (1024 * 1024)
    print(f"    Szacowana pamięć: ~{mem_total_mb:.0f} MB")
    
    # Compress
    print(f"\n[2] Kompresja Order-6...")
    print(f"    To może zająć 5-15 minut...")
    
    compress_start = time.time()
    
    encoder = ArithmeticEncoder(precision_bits=32)
    model.start_encoding()
    
    # Progress tracking
    last_progress = 0
    progress_interval = len(data) // 20  # 5% chunks
    
    class ModelWrapper:
        def __init__(self, model, data_len):
            self.model = model
            self.data_len = data_len
            self.processed = 0
            self.last_time = time.time()
            
        def get_range(self, symbol):
            result = self.model.get_range(symbol)
            self.model.update_context(symbol)
            
            # Progress
            self.processed += 1
            if self.processed % progress_interval == 0:
                pct = (self.processed / self.data_len) * 100
                elapsed = time.time() - self.last_time
                speed = progress_interval / elapsed / 1024  # KB/s
                eta = (self.data_len - self.processed) / (progress_interval / elapsed) / 60
                print(f"    {pct:>5.1f}% | Speed: {speed:>6.1f} KB/s | ETA: {eta:>5.1f} min")
                self.last_time = time.time()
            
            return result
        
        def get_total(self):
            return self.model.get_total()
        
        def get_symbol(self, offset):
            raise NotImplementedError()
    
    wrapper = ModelWrapper(model, len(data))
    compressed = encoder.encode(list(data), wrapper)
    
    compress_time = time.time() - compress_start
    
    # Results
    print(f"\n{'=' * 70}")
    print("📊 ORDER-6 RESULTS - 10 MB")
    print(f"{'=' * 70}")
    
    bpb = (len(compressed) * 8) / len(data)
    compression_ratio = len(data) / len(compressed)
    
    print(f"\nOriginal:    {len(data):>12,} bajtów ({len(data)/(1024*1024):>6.1f} MB)")
    print(f"Compressed:  {len(compressed):>12,} bajtów ({len(compressed)/(1024*1024):>6.1f} MB)")
    print(f"Ratio:       {compression_ratio:>12.2f}x")
    print(f"BPB:         {bpb:>12.3f}")
    
    print(f"\nCzas kompresji: {compress_time:.1f} s ({compress_time/60:.1f} min)")
    print(f"Szybkość: {len(data)/compress_time/1024:.1f} KB/s")
    
    # Projection to enwik9
    print(f"\n{'=' * 70}")
    print("🎯 PROJEKCJA NA ENWIK9")
    print(f"{'=' * 70}")
    
    enwik9_size = 1_000_000_000
    projected_size = int(bpb * enwik9_size / 8)
    projected_mb = projected_size / (1024 * 1024)
    
    record = 114 * 1024 * 1024
    record_mb = 114
    
    print(f"\nOrder-6 projection: {projected_mb:.1f} MB")
    print(f"Current record:     {record_mb:.1f} MB")
    print(f"Difference:         {projected_mb - record_mb:+.1f} MB")
    
    # Verdict
    print(f"\n{'=' * 70}")
    print("🎯 VERDICT")
    print(f"{'=' * 70}")
    
    if bpb < 1.0:
        print(f"\n🏆🏆🏆 WORLD RECORD PATH CONFIRMED! 🏆🏆🏆")
        print(f"    BPB < 1.0 on 10 MB = Excellent scaling!")
        print(f"    {projected_mb:.0f} MB beats record by {record_mb - projected_mb:.0f} MB!")
        print(f"\n    RECOMMENDATION: GO FOR IT!")
        print(f"    - C++ port for speed")
        print(f"    - Test on 100 MB")
        print(f"    - Full enwik9 run")
        print(f"    - WORLD RECORD ATTEMPT! 🚀")
        
    elif bpb < 1.1:
        print(f"\n✓✓ Order-6 VIABLE for record attempt!")
        print(f"    BPB ~1.0-1.1 = Good scaling")
        print(f"    {projected_mb:.0f} MB {'beats' if projected_mb < record_mb else 'close to'} record!")
        print(f"\n    RECOMMENDATION: SERIOUSLY CONSIDER")
        print(f"    - C++ port recommended")
        print(f"    - Test on 100 MB to confirm")
        print(f"    - Could beat record with optimization")
        
    elif bpb < 1.2:
        print(f"\n✓ Order-6 possible but challenging")
        print(f"    BPB ~1.1-1.2 = Some degradation")
        print(f"    {projected_mb:.0f} MB = {'Still beats' if projected_mb < record_mb else 'Close to'} record")
        print(f"\n    RECOMMENDATION: EVALUATE")
        print(f"    - Compare with Order-5 optimization")
        print(f"    - Consider hybrid approach")
        print(f"    - Need C++ for practicality")
        
    else:
        print(f"\n⚠️  Order-6 shows degradation")
        print(f"    BPB > 1.2 = Significant degradation on scale")
        print(f"    {projected_mb:.0f} MB = May not beat record")
        print(f"\n    RECOMMENDATION: Order-5 safer")
        print(f"    - Optimize Order-5 instead")
        print(f"    - Or try adaptive Order-5/6")
        print(f"    - Still TOP-10 with Order-5!")
    
    # Comparison
    print(f"\n{'=' * 70}")
    print("📊 COMPARISON")
    print(f"{'=' * 70}")
    
    order5_bpb = 1.088  # From 1 MB test
    ultra5_bpb = 0.898  # ULTRA Order-5 on 1 MB
    order6_bpb_1mb = 0.820  # Order-6 on 1 MB
    
    print(f"\n{'Test':<30} {'BPB':<10} {'Enwik9 Proj':<15} {'Status'}")
    print("-" * 70)
    print(f"{'Order-5 (1 MB pure)':<30} {order5_bpb:<10.3f} {'130 MB':<15} {'Baseline'}")
    print(f"{'ULTRA Order-5 (1 MB)':<30} {ultra5_bpb:<10.3f} {'107 MB':<15} {'Best verified'}")
    print(f"{'Order-6 (1 MB pure)':<30} {order6_bpb_1mb:<10.3f} {'98 MB':<15} {'Initial test'}")
    print(f"{'Order-6 (10 MB pure)':<30} {bpb:<10.3f} {f'{projected_mb:.0f} MB':<15} {'THIS TEST'}")
    
    # Time projection
    print(f"\n{'=' * 70}")
    print("⏱️  TIME PROJECTION FOR ENWIK9")
    print(f"{'=' * 70}")
    
    speed_bps = len(data) / compress_time  # bytes per second
    enwik9_time_sec = enwik9_size / speed_bps
    enwik9_time_hours = enwik9_time_sec / 3600
    
    print(f"\nCurrent speed: {speed_bps/1024:.1f} KB/s")
    print(f"Enwik9 time (Python): {enwik9_time_hours:.1f} hours")
    print(f"Enwik9 time (C++ 10x): {enwik9_time_hours/10:.1f} hours")
    print(f"Enwik9 time (C++ 50x): {enwik9_time_hours/50:.1f} hours")
    
    # Save results
    print(f"\n{'=' * 70}")
    print("💾 SAVING RESULTS")
    print(f"{'=' * 70}")
    
    with open("ORDER6_10MB_RESULTS.txt", "w", encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("ORDER-6 ON 10 MB - DECISIVE TEST RESULTS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Input: {input_file}\n")
        f.write(f"Size: {len(data):,} bytes ({len(data)/(1024*1024):.1f} MB)\n\n")
        f.write(f"Results:\n")
        f.write(f"  Compressed: {len(compressed):,} bytes\n")
        f.write(f"  BPB: {bpb:.3f}\n")
        f.write(f"  Ratio: {compression_ratio:.2f}x\n\n")
        f.write(f"Performance:\n")
        f.write(f"  Train time: {train_time:.1f} s\n")
        f.write(f"  Compress time: {compress_time:.1f} s ({compress_time/60:.1f} min)\n")
        f.write(f"  Speed: {len(data)/compress_time/1024:.1f} KB/s\n")
        f.write(f"  Contexts: {len(model.contexts):,}\n")
        f.write(f"  Memory: ~{mem_total_mb:.0f} MB\n\n")
        f.write(f"Enwik9 Projection:\n")
        f.write(f"  Size: {projected_mb:.1f} MB\n")
        f.write(f"  vs Record (114 MB): {projected_mb - record_mb:+.1f} MB\n")
        f.write(f"  Time (Python): {enwik9_time_hours:.1f} hours\n")
        f.write(f"  Time (C++ 10x): {enwik9_time_hours/10:.1f} hours\n\n")
        
        if bpb < 1.0:
            f.write("VERDICT: WORLD RECORD PATH CONFIRMED! 🏆\n")
            f.write("Action: GO FOR IT!\n")
        elif bpb < 1.1:
            f.write("VERDICT: Order-6 VIABLE for record!\n")
            f.write("Action: Seriously consider\n")
        elif bpb < 1.2:
            f.write("VERDICT: Order-6 possible but challenging\n")
            f.write("Action: Evaluate vs Order-5\n")
        else:
            f.write("VERDICT: Order-6 shows degradation\n")
            f.write("Action: Order-5 safer bet\n")
    
    print(f"\n✓ Results saved to: ORDER6_10MB_RESULTS.txt")
    print("=" * 70)
    
    return bpb, projected_mb

if __name__ == "__main__":
    bpb, proj_mb = test_order6_10mb()
    
    print(f"\n{'=' * 70}")
    print("🎊 TEST COMPLETE!")
    print(f"{'=' * 70}")
    print(f"\nOrder-6 on 10 MB: {bpb:.3f} bpb")
    print(f"Enwik9 projection: {proj_mb:.1f} MB")
    
    if proj_mb < 114:
        print(f"\n🏆 WE CAN BEAT THE WORLD RECORD! 🏆")
    else:
        print(f"\n💡 Still TOP-10, consider optimization!")
    
    print("=" * 70)
