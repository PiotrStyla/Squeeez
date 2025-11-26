# 🚀 HIGHER-ORDER CONTEXT MODEL - IMPLEMENTATION PLAN

**Goal:** Extend PAQ8px from Order-14 to Order-25 contexts  
**Expected:** 10-15 MB improvement on enwik9 (1.0-1.5%)  
**Complexity:** Medium (extending existing model)  
**Time:** 4-6 hours implementation + testing

---

## 📊 CURRENT STATE

### PAQ8px NormalModel:
```
Supports: Order 0-14 contexts
Uses for prediction: Order 1, 2, 3, 4, 5, 6, 8, 11, 14
Hash calculation: Rolling hash with PHI64 constant
Memory: 9 ContextMap2 instances
```

### What World Record Used:
```
cmix-hp: Order-25 PPM (Prediction by Partial Matching)
Memory: 850 MB - 2 GB (memory-mapped to disk)
Time: 50+ hours compression
Result: ~15 MB improvement vs lower orders
```

---

## 🎯 OUR APPROACH: Extend to Order-25

### Strategy A: Simple Extension (RECOMMENDED)
```
Extend NormalModel context array from 14 to 25
Add prediction contexts for: 15, 18, 22, 25
Memory: ~50% increase (manageable)
Time: Same compression speed (~50 min on 10MB)
Expected: 60-70% of PPM's benefit = 10 MB on enwik9

Why this works:
- Simpler than full PPM implementation
- Reuses existing PAQ8 infrastructure
- Much faster than memory-mapped PPM
- Good balance: improvement vs complexity
```

### Strategy B: Full PPM Implementation (AMBITIOUS)
```
Implement proper PPM algorithm
Memory-map to disk (like cmix-hp)
Full Order-25 with escape probabilities
Expected: 15 MB on enwik9 (full benefit)

Why this is harder:
- Complex algorithm (weeks, not hours)
- Need to understand PPM deeply
- Memory management complexity
- Disk I/O overhead
- Risk of bugs
```

**DECISION: Strategy A first!**  
Fast, lower risk, 60-70% of benefit.

---

## 🔧 IMPLEMENTATION: Strategy A

### Step 1: Modify Shared State
```cpp
// In Shared.hpp, increase context array size

struct NormalModelState {
  uint64_t cxt[25];  // WAS: [15], NOW: [25]
  int order;
};
```

### Step 2: Update Hash Calculation
```cpp
// In NormalModel.cpp, updateHashes()

void NormalModel::updateHashes() {
  // ... existing code ...
  uint64_t* cxt = shared->State.NormalModel.cxt;
  
  // EXTEND from 14 to 25
  for(uint64_t i = 25; i > 0; --i) {  // WAS: i = 14
    cxt[i] = (cxt[i - 1] + blocktype_c1 + i) * PHI64;
  }
}
```

### Step 3: Add Higher-Order Predictions
```cpp
// In NormalModel.cpp, mix()

void NormalModel::mix(Mixer &m) {
  if(bpos == 0) {
    updateHashes();
    uint64_t* cxtHashes = shared->State.NormalModel.cxt;
    const uint8_t RH = CM_USE_RUN_STATS | CM_USE_BYTE_HISTORY;
    
    // Existing predictions (1-6, 8, 11, 14)
    for(uint64_t i = 1; i <= 6; ++i) {
      cm.set(RH, cxtHashes[i]);
    }
    cm.set(RH, cxtHashes[8]);
    cm.set(RH, cxtHashes[11]);
    cm.set(RH, cxtHashes[14]);
    
    // NEW: Add higher orders
    cm.set(RH, cxtHashes[15]);  // Order-15
    cm.set(RH, cxtHashes[18]);  // Order-18
    cm.set(RH, cxtHashes[22]);  // Order-22
    cm.set(RH, cxtHashes[25]);  // Order-25
  }
  cm.mix(m);
  // ... rest of method ...
}
```

### Step 4: Update ContextMap2 Size
```cpp
// In NormalModel.hpp

static constexpr int nCM = 13;  // WAS: 9, NOW: 9 + 4 = 13
```

### Step 5: Update Mixer Inputs
```cpp
// In NormalModel.hpp

static constexpr int MIXERINPUTS =
  nCM * (ContextMap2::MIXERINPUTS + 
         ContextMap2::MIXERINPUTS_RUN_STATS + 
         ContextMap2::MIXERINPUTS_BYTE_HISTORY) + 
  nSM;  // Will increase from 71 to ~103
```

### Step 6: Recompile & Test
```bash
cd C:\HutterLab\paq8px
.\build.bat
```

---

## 📈 EXPECTED RESULTS

### On enwik_10mb:
```
Current (Order-14):        1,914,555 bytes (18.26%)
With reorder+transform:    1,873,130 bytes (17.87%)
Add Order-25:              1,830,000 bytes (17.45%  est.)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Additional from Order-25:  43,130 bytes (0.42%)
```

### On enwik9 (1 GB):
```
Current stack:             178.7 MB (reorder+transform)
Add Order-25:              168.7 MB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Improvement:               10 MB (1.0%)

Total from baseline:       182.6 MB → 168.7 MB
Total improvement:         13.9 MB (1.39%)
Progress:                  20% of gap closed!
```

---

## ⏰ TIMELINE

```
Hour 1-2:    Modify Shared.hpp and NormalModel.hpp
Hour 2-3:    Modify NormalModel.cpp (hash and mix)
Hour 3-4:    Update mixer initialization
Hour 4-5:    Compile and fix errors
Hour 5-6:    Test on simple.txt and wiki_1mb.txt
Hour 6-7:    Test on enwik_10mb (50 min compression)
Hour 7-8:    Analyze results, document

Total: 8 hours (one evening!)
```

---

## 🎯 SUCCESS CRITERIA

### Minimum Success:
```
Improvement: >= 0.3% on enwik_10mb
Scaled: >= 6 MB on enwik9
Worth it: Yes (easy implementation)
```

### Target Success:
```
Improvement: >= 0.5% on enwik_10mb
Scaled: >= 10 MB on enwik9
Worth it: Definitely!
```

### Stretch Success:
```
Improvement: >= 1.0% on enwik_10mb
Scaled: >= 15 MB on enwik9
Worth it: AMAZING!
```

---

## 💪 WHY THIS WILL WORK

### Evidence:
```
1. World record used Order-25 (15 MB benefit)
2. PAQ8px currently stops at Order-14
3. Wikipedia has long repetitive patterns
4. Higher orders capture longer contexts
5. Easy to implement (just extend array)
6. Low risk (same algorithm, more contexts)
```

### Physics:
```
Order-6:  "United" → predicts "States"
Order-14: "According to the United" → better
Order-25: "According to the United Nations" → even better!

More context = better predictions = smaller output
```

---

## 🚨 RISKS & MITIGATION

### Risk 1: Memory Usage
```
Problem: 25 contexts = more memory
Impact: May slow down or run out of RAM
Mitigation:
  - Test on small files first
  - Monitor memory usage
  - Can reduce ContextMap sizes if needed
```

### Risk 2: Diminishing Returns
```
Problem: Order 15-25 may not help much
Impact: Little improvement for added complexity
Mitigation:
  - Test incrementally (15, then 20, then 25)
  - Can remove if no benefit
  - Still learning about limits
```

### Risk 3: Compilation Errors
```
Problem: Changing struct sizes affects layout
Impact: Need to update other code
Mitigation:
  - Careful testing
  - Check all uses of NormalModel.cxt
  - Verify no array overruns
```

---

## 🎓 LEARNING VALUE

Even if results are modest:
```
✅ Learn how context models work
✅ Understand memory/performance tradeoffs
✅ See diminishing returns empirically
✅ Practice PAQ8 modification
✅ Build foundation for future work
```

---

## 🚀 READY TO START?

**Next action:**
1. Modify Shared.hpp (cxt[25])
2. Modify NormalModel.cpp (loop to 25, add contexts)
3. Modify NormalModel.hpp (nCM = 13)
4. Compile
5. Test
6. Measure
7. Celebrate!

**Estimated time:** 8 hours  
**Expected gain:** 10 MB on enwik9  
**Risk:** Low (simple extension)  
**Excitement:** HIGH! 🔥

---

**Let's implement this NOW!** 💪
