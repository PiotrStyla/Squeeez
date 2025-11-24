# Neural Learned Properties for Link Compression: Negative Results

**Date:** November 24, 2025 (Night Session)  
**Experiment:** Testing neural learned properties vs position encoding  
**Result:** Negative (position encoding wins)  
**Status:** Documented for future reference

---

## Abstract

We tested whether neural networks could learn discriminative properties of Wikipedia links to improve compression beyond simple position encoding. Despite promising simulation results (66% improvement), real Wikipedia data showed **no improvement**. Frequency-based position encoding remains optimal for bi-gram link prediction.

**Key Finding:** Simple frequency ordering is already near-optimal for this task.

---

## Motivation

### Previous Work

- **Bi-gram model:** Achieved 97.8% TOP-1 accuracy
- **Order-6 model:** Achieved 100% accuracy
- **Simulation:** Neural properties showed 66% improvement on synthetic data

### Research Question

Can a neural network learn discriminative features (length, capitals, categories, etc.) that outperform simple position encoding for link compression?

---

## Methodology

### Neural Architecture

```
Input: 16 features per link
Architecture: 16 → 8 → 1 (binary classifier)
Activation: ReLU → Sigmoid
Loss: Binary cross-entropy
Optimizer: SGD (learning rate 0.01)
```

### Features (16-dimensional)

1. **Text properties**
   - Link length (normalized)
   - Capital letter ratio
   - Has numbers (binary)
   - All caps (binary)
   - Starts with capital (binary)

2. **Structural properties**
   - Contains underscore
   - Contains comma
   - Position in article (normalized)

3. **Statistical properties**
   - Frequency rank (log scale)

4. **Category indicators**
   - Is year (regex match)
   - Is person (simplified)
   - Is place (simplified)
   - Is concept (simplified)

5. **Linguistic properties**
   - Word count
   - Average word length

6. **Bias term**

### Training

- Dataset: enwik_10mb (114,702 links)
- Training examples: 122,380 (positive + negative)
- Positive examples: 114,700 (correct links)
- Negative examples: 7,680 (incorrect candidates)
- Batch size: 256
- Epochs: 10

### Testing

Three approaches compared on real compression task:

1. **Position encoding:** Rank candidates by frequency, encode position
2. **Neural properties:** Rank candidates by neural score, encode position
3. **Hybrid:** Use frequency for ranking, neural for tie-breaking

---

## Results

### Training Performance

```
Final training accuracy: 93.7%
Final loss: 0.2376
Convergence: Stable after epoch 3
```

The neural network successfully learned to classify links with 93.7% accuracy.

### Compression Performance

| Method | Total Bits | Bits/Link | TOP-1 Accuracy | Result |
|--------|-----------|-----------|----------------|--------|
| Position (baseline) | 120,108 | 1.05 | 97.8% | ✅ WINS |
| Neural Properties | 120,362 | 1.05 | 97.7% | ❌ Worse by 254 bits |
| Hybrid (ties) | 120,113 | 1.05 | 97.8% | ❌ Worse by 5 bits |

**Conclusion:** Position encoding wins. Neural adds no value.

### Tie-Breaking Analysis

- Tie-breaking opportunities found: 2,447 (2.1% of links)
- Hybrid approach helped: None
- Improvement from neural tie-breaking: 0 bits

**Conclusion:** Even in tie situations, neural doesn't help.

---

## Analysis

### Why Neural Failed

1. **Frequency is sufficient**
   - In bi-gram contexts, frequency alone captures predictability
   - Most common candidates are genuinely most likely
   - No additional discriminative signal needed

2. **Features not discriminative enough**
   - 16 hand-crafted features don't capture semantic relationships
   - Length, capitals, etc. don't predict likelihood given context
   - Category features too simplistic (would need NLP)

3. **Task is already solved**
   - 97.8% accuracy with position encoding
   - Remaining 2.2% are genuinely ambiguous cases
   - No learnable pattern in failures

4. **Training data limitations**
   - Negative examples are random candidates
   - Doesn't reflect actual compression failures
   - Model learns classification, not compression optimization

### Comparison to Simulation

Simulation showed 66% improvement, but used synthetic data where:
- Position was deliberately weak
- Properties were designed to be discriminative
- Clear signal existed between correct and incorrect candidates

Real Wikipedia data:
- Position (frequency) already optimal
- No clear discriminative signal beyond frequency
- Properties don't add information

**Lesson:** Simulations can be misleading if assumptions don't match reality!

---

## Alternative Approaches Tried

### 1. Pure Neural Ranking

**Approach:** Replace frequency-based ranking entirely with neural scores

**Result:** Failed (120,362 bits vs 120,108 baseline)

**Why:** Neural network can't learn frequency patterns as well as simply counting

### 2. Hybrid Tie-Breaking

**Approach:** Use position for ranking, neural only for ties (same frequency)

**Result:** No improvement (120,113 bits vs 120,108 baseline)

**Why:** Ties are rare (2.1%) and genuinely ambiguous - no learnable signal

---

## Insights for Future Work

### What We Learned

1. **Simple approaches work**
   - Frequency-based ordering is near-optimal
   - Don't add complexity without clear benefit
   - "Premature optimization is the root of all evil"

2. **Feature engineering is hard**
   - Hand-crafted features rarely beat simple statistics
   - Would need deep semantic features (embeddings)
   - Cost/benefit ratio unfavorable

3. **Simulation vs Reality**
   - Always test on real data
   - Synthetic results can be misleading
   - Negative results are valuable!

### When Neural Might Help

Neural properties could work if:

1. **Task has learnable patterns**
   - Not just frequency-based
   - Clear discriminative signal
   - Failures have common causes

2. **Better features available**
   - Word embeddings (semantic similarity)
   - Graph features (co-occurrence patterns)
   - Contextual features (article topic, section type)

3. **Sufficient training data**
   - Large datasets
   - Balanced positive/negative examples
   - Representative of test distribution

4. **Cost-effective**
   - Inference overhead acceptable
   - Model size reasonable
   - Complexity justified by gains

---

## Recommendations

### For Link Compression

**Stick with position encoding!**

- Simple
- Fast
- Near-optimal
- No neural overhead

### For Future Research

If pursuing neural approaches:

1. **Focus on text compression** (98% of data, more room for improvement)
2. **Use pre-trained embeddings** (semantic features)
3. **Target specific failure modes** (not general ranking)
4. **Measure cost-benefit carefully** (neural overhead vs gains)

### For Paper

This negative result should be mentioned briefly:

> "We explored neural learned properties but found frequency-based position encoding to be already near-optimal (120,108 vs 120,362 bits). This validates the effectiveness of simple statistical approaches for this task."

---

## Experimental Details

### Code

- `neural_link_properties.py` - Pure neural approach
- `hybrid_neural_position.py` - Hybrid tie-breaking approach

### Hardware

- CPU: 12 cores
- RAM: ~2 GB used
- Runtime: ~5 minutes per experiment

### Reproducibility

```bash
python neural_link_properties.py
python hybrid_neural_position.py
```

Results are deterministic (seed=42).

---

## Conclusion

Neural learned properties **do not improve** link compression beyond simple position encoding on real Wikipedia data.

**Key Takeaway:** Simple frequency-based ranking is already near-optimal. Adding neural complexity provides no benefit.

**Positive Outcome:** This validates our existing approach and saves future effort!

**Status:** Negative result documented. Moving on to more promising directions.

---

## Related Work

- **Simulation:** `neural_properties.py` (66% improvement on synthetic data)
- **Real Implementation:** `neural_link_properties.py` (no improvement)
- **Hybrid:** `hybrid_neural_position.py` (no improvement)
- **Positive Results:** `test_order6_links.py` (100% accuracy with Order-6)
- **Lessons Learned:** `zkp_properties_lessons_learned.md` (probabilistic properties)

---

**Timestamp:** November 24, 2025 - 21:00  
**Session:** Night experiment  
**Duration:** ~1 hour  
**Result:** Negative (but valuable!)  
**Next:** Pivot to more promising areas 🎯
