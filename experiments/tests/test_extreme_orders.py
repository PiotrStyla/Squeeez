#!/usr/bin/env python3
"""
EXTREME ORDER TEST
Jak daleko możemy iść? Order-6? 7? 8?
Gdzie jest sweet spot jakość/memory/czas?
"""
import time
from context_model import ContextModel
from arithmetic_coder import ArithmeticEncoder

def test_order(data, order):
    """Test single order"""
    print(f"\n{'─' * 70}")
    print(f"ORDER-{order} TEST")
    print(f"{'─' * 70}")
    
    start = time.time()
    
    # Train
    print(f"Training...")
    model = ContextModel(order=order)
    model.train(data)
    
    train_time = time.time() - start
    contexts = len(model.contexts)
    
    print(f"  Contexts: {contexts:,}")
    print(f"  Train time: {train_time:.1f} s")
    
    # Compress
    print(f"Compressing...")
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
    
    compress_time = time.time() - start
    total_time = train_time + compress_time
    
    bpb = (len(compressed) * 8) / len(data)
    
    print(f"  Compress time: {compress_time:.1f} s")
    print(f"  Total: {total_time:.1f} s")
    print(f"  Compressed: {len(compressed):,} bytes ({bpb:.3f} bpb)")
    
    return {
        'order': order,
        'contexts': contexts,
        'bpb': bpb,
        'train_time': train_time,
        'compress_time': compress_time,
        'total_time': total_time,
        'compressed_bytes': len(compressed)
    }

def main():
    print("=" * 70)
    print("🔥 EXTREME ORDER EXPLORATION 🔥")
    print("=" * 70)
    
    print("\nPytanie: Jak wysoko możemy iść?")
    print("Order-6 dało +69% na 100KB. Co z Order-7? Order-8?")
    
    input_file = "data/enwik_10mb"
    
    # Test na 100 KB (szybko)
    print(f"\n📊 Test na 100 KB z: {input_file}")
    with open(input_file, 'rb') as f:
        data = f.read(100 * 1024)
    
    print(f"Rozmiar: {len(data):,} bajtów")
    
    # Test orders: 3, 4, 5, 6, 7, 8
    orders_to_test = [3, 4, 5, 6, 7, 8]
    results = []
    
    print(f"\n{'=' * 70}")
    print("TESTING MULTIPLE ORDERS")
    print(f"{'=' * 70}")
    
    for order in orders_to_test:
        try:
            result = test_order(data, order)
            results.append(result)
        except MemoryError:
            print(f"\n⚠️  Order-{order}: OUT OF MEMORY!")
            break
        except Exception as e:
            print(f"\n❌ Order-{order}: ERROR - {e}")
            break
    
    # Summary
    if results:
        print(f"\n{'=' * 70}")
        print("📊 SUMMARY")
        print(f"{'=' * 70}")
        
        print(f"\n{'Order':<8} {'BPB':<10} {'Contexts':<12} {'Time (s)':<10} {'vs Order-3'}")
        print("─" * 70)
        
        baseline_bpb = next((r['bpb'] for r in results if r['order'] == 3), None)
        
        for result in results:
            order = result['order']
            bpb = result['bpb']
            contexts = result['contexts']
            time_total = result['total_time']
            
            if baseline_bpb:
                improvement = ((baseline_bpb - bpb) / baseline_bpb) * 100
                vs_baseline = f"+{improvement:.1f}%"
            else:
                vs_baseline = "baseline"
            
            print(f"{order:<8} {bpb:<10.3f} {contexts:<12,} {time_total:<10.1f} {vs_baseline}")
        
        # Best order analysis
        print(f"\n{'=' * 70}")
        print("💡 ANALYSIS")
        print(f"{'=' * 70}")
        
        best_quality = min(results, key=lambda x: x['bpb'])
        best_speed = min(results, key=lambda x: x['total_time'])
        
        print(f"\nBest quality: Order-{best_quality['order']}")
        print(f"  BPB: {best_quality['bpb']:.3f}")
        print(f"  Improvement: +{((baseline_bpb - best_quality['bpb']) / baseline_bpb * 100):.1f}% vs Order-3")
        print(f"  Cost: {best_quality['contexts']:,} contexts, {best_quality['total_time']:.1f} s")
        
        print(f"\nFastest: Order-{best_speed['order']}")
        print(f"  Time: {best_speed['total_time']:.1f} s")
        print(f"  Quality: {best_speed['bpb']:.3f} bpb")
        
        # Sweet spot
        print(f"\n{'=' * 70}")
        print("🎯 SWEET SPOT")
        print(f"{'=' * 70}")
        
        # Find diminishing returns point
        improvements = []
        for i in range(1, len(results)):
            prev_bpb = results[i-1]['bpb']
            curr_bpb = results[i]['bpb']
            improvement = ((prev_bpb - curr_bpb) / prev_bpb) * 100
            improvements.append((results[i]['order'], improvement))
        
        print(f"\n{'Step':<15} {'Improvement'}")
        print("─" * 30)
        for order, improvement in improvements:
            print(f"Order-{order-1}→{order:<8} +{improvement:.1f}%")
        
        # Diminishing returns analysis
        if len(improvements) >= 2:
            print(f"\n💭 Observations:")
            
            for i, (order, improvement) in enumerate(improvements):
                if i > 0:
                    prev_improvement = improvements[i-1][1]
                    diminish = prev_improvement - improvement
                    print(f"  Order-{order}: +{improvement:.1f}% (diminish: {diminish:.1f}%)")
                else:
                    print(f"  Order-{order}: +{improvement:.1f}%")
            
            # Find sweet spot (where improvement drops below threshold)
            threshold = 5.0  # 5% improvement
            sweet_spot_order = None
            
            for order, improvement in improvements:
                if improvement < threshold:
                    sweet_spot_order = order - 1
                    break
            
            if sweet_spot_order:
                print(f"\n🎯 Sweet spot appears to be Order-{sweet_spot_order}")
                print(f"   (Next order improves by < {threshold}%)")
            else:
                print(f"\n🚀 Still improving! Higher orders may help!")
        
        # Projekcja na enwik9
        print(f"\n{'=' * 70}")
        print("📈 PROJECTION ON ENWIK9")
        print(f"{'=' * 70}")
        
        enwik9_size = 1_000_000_000
        record = 114 * 1024 * 1024
        
        print(f"\n{'Order':<8} {'Enwik9 Proj':<15} {'vs Record'}")
        print("─" * 40)
        
        for result in results:
            # Conservative scaling (assume more degradation on larger data)
            # 100KB → 1GB = 10,000x size
            # Assume bpb increases by ~20% at each 10x scale
            # 100KB → 1MB → 10MB → 100MB → 1GB = 4 steps
            degradation_per_10x = 1.15  # 15% increase per 10x
            estimated_bpb = result['bpb'] * (degradation_per_10x ** 4)
            
            projection = int(estimated_bpb * enwik9_size / 8)
            gap = projection - record
            
            print(f"{result['order']:<8} {projection/(1024*1024):>6.1f} MB      ", end='')
            if gap < 0:
                print(f"{-gap/(1024*1024):>5.1f} MB better! 🏆")
            else:
                print(f"+{gap/(1024*1024):>5.1f} MB")
        
        print(f"\nNote: Projection uses conservative 15% degradation per 10x scale")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
