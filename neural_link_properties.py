#!/usr/bin/env python3
"""
NEURAL LEARNED PROPERTIES - Real Wikipedia Implementation

Night session breakthrough attempt! 🌙🚀

After Order-6 achieved 100% accuracy but modest savings (~65 KB),
let's try a completely different approach: LEARNED PROPERTIES.

Instead of: position_in_candidate_list
Use: neural_network(link_features) → discriminative_score

Simulation showed 66% improvement. Can we achieve this on real data?
"""
import re
import numpy as np
from collections import defaultdict, Counter
import pickle
from pathlib import Path

class NeuralLinkPropertyLearner:
    """
    Learn discriminative properties of links using neural network
    
    Features per link:
    - Text length
    - Capital letter patterns
    - Numeric content
    - Special characters
    - Position in article (normalized)
    - Frequency rank
    - Category indicators (Person, Place, Year, Concept)
    """
    
    def __init__(self):
        self.link_features = {}
        self.category_patterns = {
            'year': re.compile(r'^\d{4}$'),
            'person': re.compile(r'\b(born|died|president|king|queen|emperor)\b', re.I),
            'place': re.compile(r'\b(city|country|river|mountain|state|province)\b', re.I),
            'concept': re.compile(r'\b(theory|principle|law|effect|system)\b', re.I),
        }
        self.weights = None
        self.link_to_idx = {}
        
    def extract_links(self, text):
        """Extract Wikipedia links with context"""
        pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
        links = []
        for match in pattern.finditer(text):
            link = match.group(1)
            position = match.start()
            links.append((link, position))
        return links
    
    def compute_features(self, link, position, total_length, link_freq):
        """
        Compute discriminative features for a link
        
        Returns: 16-dimensional feature vector
        """
        features = []
        
        # 1. Text length (normalized)
        features.append(len(link) / 100.0)
        
        # 2. Capital letter ratio
        if len(link) > 0:
            capitals = sum(1 for c in link if c.isupper())
            features.append(capitals / len(link))
        else:
            features.append(0.0)
        
        # 3. Has numbers
        features.append(1.0 if any(c.isdigit() for c in link) else 0.0)
        
        # 4. All caps
        features.append(1.0 if link.isupper() else 0.0)
        
        # 5. Starts with capital
        features.append(1.0 if link and link[0].isupper() else 0.0)
        
        # 6. Contains underscore
        features.append(1.0 if '_' in link else 0.0)
        
        # 7. Contains comma
        features.append(1.0 if ',' in link else 0.0)
        
        # 8. Position in article (normalized)
        features.append(position / total_length if total_length > 0 else 0.0)
        
        # 9. Frequency rank (log scale)
        features.append(np.log1p(link_freq.get(link, 1)) / 10.0)
        
        # 10-13. Category indicators (Year, Person, Place, Concept)
        for category in ['year', 'person', 'place', 'concept']:
            if category == 'year':
                features.append(1.0 if self.category_patterns[category].match(link) else 0.0)
            else:
                # These would need article context, simplify for now
                features.append(0.0)
        
        # 14. Word count
        features.append(len(link.split('_')))
        
        # 15. Average word length
        words = link.split('_')
        avg_word_len = np.mean([len(w) for w in words]) if words else 0
        features.append(avg_word_len / 10.0)
        
        # 16. Bias term
        features.append(1.0)
        
        return np.array(features, dtype=np.float32)
    
    def build_training_data(self, text):
        """
        Build training dataset from Wikipedia text
        
        For each context, we have:
        - Correct link (label = 1)
        - Candidate links (label = 0)
        """
        print("Building training data...")
        
        # Extract links
        links_with_pos = self.extract_links(text)
        links = [l for l, p in links_with_pos]
        
        print(f"  Found {len(links):,} links")
        
        # Compute frequency
        link_freq = Counter(links)
        
        # Build bi-gram model for candidate generation
        bigram_model = defaultdict(lambda: Counter())
        for i in range(2, len(links)):
            context = tuple(links[i-2:i])
            next_link = links[i]
            bigram_model[context][next_link] += 1
        
        print(f"  Built bi-gram model: {len(bigram_model):,} contexts")
        
        # Generate training examples
        X_train = []
        y_train = []
        
        total_length = len(text)
        
        for i in range(2, len(links)):
            context = tuple(links[i-2:i])
            correct_link = links[i]
            position = links_with_pos[i][1]
            
            if context not in bigram_model:
                continue
            
            candidates = bigram_model[context]
            
            # Positive example (correct link)
            features = self.compute_features(correct_link, position, total_length, link_freq)
            X_train.append(features)
            y_train.append(1.0)
            
            # Negative examples (other candidates)
            neg_candidates = [l for l in candidates.keys() if l != correct_link]
            
            # Sample up to 5 negative examples
            neg_sample = np.random.choice(neg_candidates, 
                                         size=min(5, len(neg_candidates)), 
                                         replace=False) if neg_candidates else []
            
            for neg_link in neg_sample:
                features = self.compute_features(neg_link, position, total_length, link_freq)
                X_train.append(features)
                y_train.append(0.0)
            
            if (i + 1) % 10000 == 0:
                print(f"  Processed {i+1:,} / {len(links):,} links...")
        
        X_train = np.array(X_train, dtype=np.float32)
        y_train = np.array(y_train, dtype=np.float32)
        
        print(f"\n  Training examples: {len(X_train):,}")
        print(f"  Positive: {np.sum(y_train):,.0f}")
        print(f"  Negative: {np.sum(1-y_train):,.0f}")
        
        return X_train, y_train, links, link_freq, bigram_model
    
    def train_neural_network(self, X, y, epochs=10, learning_rate=0.01):
        """
        Train simple neural network using gradient descent
        
        Architecture: 16 → 8 → 1 (binary classifier)
        """
        print("\n" + "=" * 70)
        print("🧠 TRAINING NEURAL NETWORK")
        print("=" * 70)
        
        np.random.seed(42)
        
        # Initialize weights
        n_features = X.shape[1]
        n_hidden = 8
        
        # He initialization
        W1 = np.random.randn(n_features, n_hidden) * np.sqrt(2.0 / n_features)
        b1 = np.zeros(n_hidden)
        W2 = np.random.randn(n_hidden, 1) * np.sqrt(2.0 / n_hidden)
        b2 = np.zeros(1)
        
        n_samples = len(X)
        batch_size = 256
        
        print(f"\nArchitecture: {n_features} → {n_hidden} → 1")
        print(f"Training samples: {n_samples:,}")
        print(f"Batch size: {batch_size}")
        print(f"Epochs: {epochs}")
        print(f"Learning rate: {learning_rate}")
        
        for epoch in range(epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            total_loss = 0
            n_batches = 0
            
            for i in range(0, n_samples, batch_size):
                X_batch = X_shuffled[i:i+batch_size]
                y_batch = y_shuffled[i:i+batch_size]
                
                # Forward pass
                z1 = X_batch @ W1 + b1
                a1 = np.maximum(0, z1)  # ReLU
                z2 = a1 @ W2 + b2
                a2 = 1 / (1 + np.exp(-z2))  # Sigmoid
                
                # Loss (binary cross-entropy)
                loss = -np.mean(y_batch * np.log(a2 + 1e-8) + 
                               (1 - y_batch) * np.log(1 - a2 + 1e-8))
                total_loss += loss
                n_batches += 1
                
                # Backward pass
                dz2 = a2 - y_batch.reshape(-1, 1)
                dW2 = a1.T @ dz2 / len(X_batch)
                db2 = np.sum(dz2, axis=0) / len(X_batch)
                
                da1 = dz2 @ W2.T
                dz1 = da1 * (z1 > 0)  # ReLU derivative
                dW1 = X_batch.T @ dz1 / len(X_batch)
                db1 = np.sum(dz1, axis=0) / len(X_batch)
                
                # Update weights
                W2 -= learning_rate * dW2
                b2 -= learning_rate * db2
                W1 -= learning_rate * dW1
                b1 -= learning_rate * db1
            
            avg_loss = total_loss / n_batches
            
            # Compute accuracy
            z1 = X @ W1 + b1
            a1 = np.maximum(0, z1)
            z2 = a1 @ W2 + b2
            a2 = 1 / (1 + np.exp(-z2))
            predictions = (a2 > 0.5).astype(float)
            accuracy = np.mean(predictions.flatten() == y)
            
            print(f"  Epoch {epoch+1}/{epochs}: Loss = {avg_loss:.4f}, Accuracy = {accuracy*100:.1f}%")
        
        # Store weights
        self.weights = {
            'W1': W1, 'b1': b1,
            'W2': W2, 'b2': b2
        }
        
        print("\n✅ Training complete!")
        return self.weights
    
    def predict_score(self, features):
        """Predict discriminative score for link features"""
        if self.weights is None:
            raise ValueError("Model not trained yet!")
        
        # Forward pass
        z1 = features @ self.weights['W1'] + self.weights['b1']
        a1 = np.maximum(0, z1)
        z2 = a1 @ self.weights['W2'] + self.weights['b2']
        score = 1 / (1 + np.exp(-z2))
        
        return score[0] if score.shape == (1,) else score
    
    def test_on_real_data(self, text, bigram_model, link_freq):
        """
        Test neural property-based compression vs position-based
        """
        print("\n" + "=" * 70)
        print("🎯 TESTING: Neural Properties vs Position Encoding")
        print("=" * 70)
        
        links_with_pos = self.extract_links(text)
        links = [l for l, p in links_with_pos]
        
        stats_position = {'total_bits': 0, 'top1': 0}
        stats_neural = {'total_bits': 0, 'top1': 0}
        
        total_length = len(text)
        
        print("\nProcessing links...")
        
        for i in range(2, len(links)):
            context = tuple(links[i-2:i])
            correct_link = links[i]
            position = links_with_pos[i][1]
            
            if context not in bigram_model:
                continue
            
            candidates = list(bigram_model[context].keys())
            
            # Method 1: Position encoding (baseline)
            try:
                pos_idx = candidates.index(correct_link)
            except ValueError:
                pos_idx = len(candidates)
            
            if pos_idx == 0:
                stats_position['top1'] += 1
                stats_position['total_bits'] += 1
            elif pos_idx < 5:
                stats_position['total_bits'] += 3
            elif pos_idx < 50:
                stats_position['total_bits'] += 6
            else:
                stats_position['total_bits'] += 17
            
            # Method 2: Neural property ranking
            candidate_scores = []
            for cand in candidates:
                features = self.compute_features(cand, position, total_length, link_freq)
                score = self.predict_score(features)
                candidate_scores.append((cand, score))
            
            # Sort by neural score (descending)
            candidate_scores.sort(key=lambda x: x[1], reverse=True)
            neural_candidates = [c for c, s in candidate_scores]
            
            try:
                neural_idx = neural_candidates.index(correct_link)
            except ValueError:
                neural_idx = len(neural_candidates)
            
            if neural_idx == 0:
                stats_neural['top1'] += 1
                stats_neural['total_bits'] += 1
            elif neural_idx < 5:
                stats_neural['total_bits'] += 3
            elif neural_idx < 50:
                stats_neural['total_bits'] += 6
            else:
                stats_neural['total_bits'] += 17
            
            if (i + 1) % 10000 == 0:
                print(f"  Processed {i+1:,} / {len(links):,} links...")
        
        # Results
        print("\n" + "=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        
        total_links = len(links) - 2
        
        print(f"\nTotal links tested: {total_links:,}")
        
        print(f"\n1️⃣ Position Encoding (baseline):")
        print(f"  TOP-1 accuracy: {stats_position['top1']/total_links*100:.1f}%")
        print(f"  Total bits: {stats_position['total_bits']:,}")
        print(f"  Bits per link: {stats_position['total_bits']/total_links:.2f}")
        
        print(f"\n2️⃣ Neural Properties:")
        print(f"  TOP-1 accuracy: {stats_neural['top1']/total_links*100:.1f}%")
        print(f"  Total bits: {stats_neural['total_bits']:,}")
        print(f"  Bits per link: {stats_neural['total_bits']/total_links:.2f}")
        
        bits_saved = stats_position['total_bits'] - stats_neural['total_bits']
        improvement = (bits_saved / stats_position['total_bits']) * 100 if stats_position['total_bits'] > 0 else 0
        
        print(f"\n💰 SAVINGS:")
        if bits_saved > 0:
            print(f"  ✅ Neural wins by {bits_saved:,} bits!")
            print(f"  ✅ Improvement: {improvement:.1f}%")
            print(f"  ✅ Extrapolated to enwik9: {bits_saved * 100 / 8 / 1024:.1f} KB")
            
            if improvement > 20:
                print(f"\n  🏆 BREAKTHROUGH! Major improvement!")
            elif improvement > 5:
                print(f"\n  🎯 Solid gain! Worth implementing!")
            else:
                print(f"\n  ➖ Modest gain. Position encoding competitive.")
        else:
            print(f"  ❌ Position encoding wins")
            print(f"  → Neural properties need more work")
        
        return stats_position, stats_neural

def main():
    print("=" * 70)
    print("🌙 NIGHT SESSION: NEURAL LEARNED PROPERTIES")
    print("=" * 70)
    print("\nCan learned features beat position encoding?")
    print("Simulation showed 66% improvement - let's test on real data!\n")
    
    # Load data
    print("Loading enwik_10mb...")
    try:
        with open("data/enwik_10mb", 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print("❌ File not found!")
        return
    
    text = data.decode('utf-8', errors='ignore')
    print(f"Loaded: {len(data):,} bytes\n")
    
    # Initialize learner
    learner = NeuralLinkPropertyLearner()
    
    # Build training data
    X_train, y_train, links, link_freq, bigram_model = learner.build_training_data(text)
    
    # Train neural network
    learner.train_neural_network(X_train, y_train, epochs=10, learning_rate=0.01)
    
    # Test on real compression task
    learner.test_on_real_data(text, bigram_model, link_freq)
    
    print("\n" + "=" * 70)
    print("✨ Night session experiment complete!")
    print("🧠 Neural properties tested on real Wikipedia data! 🎯")
    print("=" * 70)

if __name__ == "__main__":
    main()
