#!/usr/bin/env python3
"""
HYBRID: Neural Properties for Tie-Breaking

Neural alone didn't beat position, BUT what if we combine them?

Use case: When multiple candidates have SAME frequency,
use neural properties to break ties!

This could be the sweet spot! 🎯
"""
import re
import numpy as np
from collections import defaultdict, Counter

class HybridNeuralPosition:
    """
    Hybrid approach: Position first, Neural for ties
    """
    
    def __init__(self):
        self.weights = None
        
    def extract_links(self, text):
        """Extract Wikipedia links"""
        pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        links = []
        for match in pattern.finditer(text):
            link = match.group(1)
            position = match.start()
            links.append((link, position))
        return links
    
    def compute_features(self, link, position, total_length, link_freq):
        """Compute 16-dim feature vector"""
        features = []
        
        features.append(len(link) / 100.0)
        
        if len(link) > 0:
            capitals = sum(1 for c in link if c.isupper())
            features.append(capitals / len(link))
        else:
            features.append(0.0)
        
        features.append(1.0 if any(c.isdigit() for c in link) else 0.0)
        features.append(1.0 if link.isupper() else 0.0)
        features.append(1.0 if link and link[0].isupper() else 0.0)
        features.append(1.0 if '_' in link else 0.0)
        features.append(1.0 if ',' in link else 0.0)
        features.append(position / total_length if total_length > 0 else 0.0)
        features.append(np.log1p(link_freq.get(link, 1)) / 10.0)
        
        # Simplified category features
        year_pattern = re.compile(r'^\d{4}$')
        features.append(1.0 if year_pattern.match(link) else 0.0)
        features.extend([0.0, 0.0, 0.0])  # Other categories
        
        words = link.split('_')
        features.append(len(words))
        avg_word_len = np.mean([len(w) for w in words]) if words else 0
        features.append(avg_word_len / 10.0)
        features.append(1.0)  # Bias
        
        return np.array(features, dtype=np.float32)
    
    def train_simple_model(self, X, y, epochs=10, lr=0.01):
        """Train simple neural network"""
        np.random.seed(42)
        
        n_features = X.shape[1]
        n_hidden = 8
        
        W1 = np.random.randn(n_features, n_hidden) * np.sqrt(2.0 / n_features)
        b1 = np.zeros(n_hidden)
        W2 = np.random.randn(n_hidden, 1) * np.sqrt(2.0 / n_hidden)
        b2 = np.zeros(1)
        
        n_samples = len(X)
        batch_size = 256
        
        for epoch in range(epochs):
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            for i in range(0, n_samples, batch_size):
                X_batch = X_shuffled[i:i+batch_size]
                y_batch = y_shuffled[i:i+batch_size]
                
                # Forward
                z1 = X_batch @ W1 + b1
                a1 = np.maximum(0, z1)
                z2 = a1 @ W2 + b2
                a2 = 1 / (1 + np.exp(-z2))
                
                # Backward
                dz2 = a2 - y_batch.reshape(-1, 1)
                dW2 = a1.T @ dz2 / len(X_batch)
                db2 = np.sum(dz2, axis=0) / len(X_batch)
                
                da1 = dz2 @ W2.T
                dz1 = da1 * (z1 > 0)
                dW1 = X_batch.T @ dz1 / len(X_batch)
                db1 = np.sum(dz1, axis=0) / len(X_batch)
                
                # Update
                W2 -= lr * dW2
                b2 -= lr * db2
                W1 -= lr * dW1
                b1 -= lr * db1
        
        self.weights = {'W1': W1, 'b1': b1, 'W2': W2, 'b2': b2}
    
    def predict_score(self, features):
        """Predict neural score"""
        z1 = features @ self.weights['W1'] + self.weights['b1']
        a1 = np.maximum(0, z1)
        z2 = a1 @ self.weights['W2'] + self.weights['b2']
        score = 1 / (1 + np.exp(-z2))
        return score[0] if score.shape == (1,) else score
    
    def hybrid_ranking(self, candidates, frequencies, features_dict):
        """
        Hybrid ranking strategy:
        1. Group by frequency (primary)
        2. Within same frequency, sort by neural score (tie-breaker)
        """
        # Create groups by frequency
        freq_groups = defaultdict(list)
        for cand in candidates:
            freq = frequencies.get(cand, 0)
            neural_score = self.predict_score(features_dict[cand])
            freq_groups[freq].append((cand, neural_score))
        
        # Sort each group by neural score
        sorted_candidates = []
        for freq in sorted(freq_groups.keys(), reverse=True):
            group = freq_groups[freq]
            group.sort(key=lambda x: x[1], reverse=True)  # Sort by neural score
            sorted_candidates.extend([cand for cand, _ in group])
        
        return sorted_candidates
    
    def test_hybrid(self, text, bigram_model, link_freq):
        """Test hybrid approach"""
        print("\n" + "=" * 70)
        print("🔥 TESTING HYBRID APPROACH")
        print("=" * 70)
        
        links_with_pos = self.extract_links(text)
        links = [l for l, p in links_with_pos]
        
        stats_position = {'total_bits': 0, 'top1': 0, 'ties_broken': 0}
        stats_hybrid = {'total_bits': 0, 'top1': 0, 'ties_broken': 0}
        
        total_length = len(text)
        
        print("\nProcessing links...")
        
        for i in range(2, len(links)):
            context = tuple(links[i-2:i])
            correct_link = links[i]
            position = links_with_pos[i][1]
            
            if context not in bigram_model:
                continue
            
            candidates_counter = bigram_model[context]
            candidates = list(candidates_counter.keys())
            
            # Method 1: Pure position (frequency-based)
            candidates_by_freq = sorted(candidates, 
                                       key=lambda x: candidates_counter[x], 
                                       reverse=True)
            
            try:
                pos_idx = candidates_by_freq.index(correct_link)
            except ValueError:
                pos_idx = len(candidates_by_freq)
            
            if pos_idx == 0:
                stats_position['top1'] += 1
                stats_position['total_bits'] += 1
            elif pos_idx < 5:
                stats_position['total_bits'] += 3
            elif pos_idx < 50:
                stats_position['total_bits'] += 6
            else:
                stats_position['total_bits'] += 17
            
            # Method 2: Hybrid (frequency + neural for ties)
            # Precompute features for all candidates
            features_dict = {}
            for cand in candidates:
                features_dict[cand] = self.compute_features(cand, position, 
                                                            total_length, link_freq)
            
            hybrid_candidates = self.hybrid_ranking(candidates, 
                                                    candidates_counter, 
                                                    features_dict)
            
            try:
                hybrid_idx = hybrid_candidates.index(correct_link)
            except ValueError:
                hybrid_idx = len(hybrid_candidates)
            
            # Check if this was a tie-breaking situation
            if pos_idx > 0:  # Not already top-1
                correct_freq = candidates_counter[correct_link]
                tied_candidates = [c for c in candidates 
                                  if candidates_counter[c] == correct_freq]
                if len(tied_candidates) > 1:
                    stats_hybrid['ties_broken'] += 1
            
            if hybrid_idx == 0:
                stats_hybrid['top1'] += 1
                stats_hybrid['total_bits'] += 1
            elif hybrid_idx < 5:
                stats_hybrid['total_bits'] += 3
            elif hybrid_idx < 50:
                stats_hybrid['total_bits'] += 6
            else:
                stats_hybrid['total_bits'] += 17
            
            if (i + 1) % 10000 == 0:
                print(f"  Processed {i+1:,} / {len(links):,} links...")
        
        # Results
        print("\n" + "=" * 70)
        print("📊 HYBRID RESULTS")
        print("=" * 70)
        
        total_links = len(links) - 2
        
        print(f"\nTotal links tested: {total_links:,}")
        
        print(f"\n1️⃣ Pure Position (baseline):")
        print(f"  TOP-1 accuracy: {stats_position['top1']/total_links*100:.1f}%")
        print(f"  Total bits: {stats_position['total_bits']:,}")
        print(f"  Bits per link: {stats_position['total_bits']/total_links:.2f}")
        
        print(f"\n2️⃣ Hybrid (Position + Neural ties):")
        print(f"  TOP-1 accuracy: {stats_hybrid['top1']/total_links*100:.1f}%")
        print(f"  Total bits: {stats_hybrid['total_bits']:,}")
        print(f"  Bits per link: {stats_hybrid['total_bits']/total_links:.2f}")
        print(f"  Tie-breaking opportunities: {stats_hybrid['ties_broken']:,}")
        
        bits_saved = stats_position['total_bits'] - stats_hybrid['total_bits']
        
        print(f"\n💰 COMPARISON:")
        if bits_saved > 0:
            improvement = (bits_saved / stats_position['total_bits']) * 100
            print(f"  ✅ Hybrid wins by {bits_saved:,} bits!")
            print(f"  ✅ Improvement: {improvement:.2f}%")
            print(f"  ✅ Extrapolated to enwik9: {bits_saved * 100 / 8 / 1024:.1f} KB")
            
            if improvement > 1:
                print(f"\n  🎯 SUCCESS! Hybrid approach helps!")
            else:
                print(f"\n  ➖ Tiny gain. Ties are rare.")
        else:
            print(f"  ➖ No improvement from tie-breaking")
            print(f"  → Frequency ordering already optimal")
        
        return stats_position, stats_hybrid

def main():
    print("=" * 70)
    print("🌙 NIGHT SESSION: HYBRID NEURAL+POSITION")
    print("=" * 70)
    print("\nCan neural properties help break ties?\n")
    
    # Load data
    print("Loading enwik_10mb...")
    with open("data/enwik_10mb", 'rb') as f:
        data = f.read()
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Initialize hybrid system
    hybrid = HybridNeuralPosition()
    
    # Extract links and build model
    print("Building bi-gram model...")
    links_with_pos = hybrid.extract_links(text)
    links = [l for l, p in links_with_pos]
    
    link_freq = Counter(links)
    
    bigram_model = defaultdict(lambda: Counter())
    for i in range(2, len(links)):
        context = tuple(links[i-2:i])
        next_link = links[i]
        bigram_model[context][next_link] += 1
    
    print(f"  Links: {len(links):,}")
    print(f"  Contexts: {len(bigram_model):,}")
    
    # Quick training (simplified)
    print("\nTraining neural tie-breaker...")
    X_train = []
    y_train = []
    
    total_length = len(text)
    
    for i in range(2, min(30000, len(links))):  # Sample for speed
        context = tuple(links[i-2:i])
        correct_link = links[i]
        position = links_with_pos[i][1]
        
        if context not in bigram_model:
            continue
        
        # Positive
        features = hybrid.compute_features(correct_link, position, total_length, link_freq)
        X_train.append(features)
        y_train.append(1.0)
        
        # Negatives
        candidates = list(bigram_model[context].keys())
        neg_candidates = [l for l in candidates if l != correct_link]
        
        for neg in neg_candidates[:3]:  # Sample 3 negatives
            features = hybrid.compute_features(neg, position, total_length, link_freq)
            X_train.append(features)
            y_train.append(0.0)
    
    X_train = np.array(X_train, dtype=np.float32)
    y_train = np.array(y_train, dtype=np.float32)
    
    print(f"  Training samples: {len(X_train):,}")
    
    hybrid.train_simple_model(X_train, y_train, epochs=5, lr=0.01)
    
    print("  ✅ Training complete!")
    
    # Test hybrid approach
    hybrid.test_hybrid(text, bigram_model, link_freq)
    
    print("\n" + "=" * 70)
    print("✨ Hybrid experiment complete!")
    print("🎯 Now we know if tie-breaking helps! 😊")
    print("=" * 70)

if __name__ == "__main__":
    main()
