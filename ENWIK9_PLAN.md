# 🎯 ENWIK9 FULL TEST PLAN - Phase 2 Validation

**Date:** November 26, 2025 - 10:00 PM  
**Goal:** Validate Phase 2 (2.16%) on full enwik9  
**Status:** 🚀 STARTING NOW

---

## ✅ COMPLETED

```
1. ✅ Order-25 reverted (back to proven Phase 2)
2. ✅ PAQ8px recompiled (stock Order-14)
3. ✅ enwik9 downloaded (1,000,000,000 bytes verified)
```

---

## 📋 PIPELINE

### Step 1: Baseline Compression (Optional)
```
Input: enwik9 (original, alphabetical)
Action: paq8px-wiki.exe -5 enwik9 baseline.paq8
Time: ~50 hours
Purpose: Verify 182.6 MB baseline
Status: ⏸️ SKIP (already know from PAQ8px benchmarks)
```

### Step 2: Article Reordering ⏳
```
Input: enwik9 (1 GB)
Script: starlit_reorder.py
Output: enwik9_reordered (1 GB)
Time: ~10-20 minutes (parsing + reordering)
Expected: Lossless transformation
Status: 🔄 NEXT
```

### Step 3: Wikipedia Transforms ⏳
```
Input: enwik9_reordered (1 GB)
Script: simplified_transforms.py (modified for enwik9)
Output: enwik9_reordered_transformed
Time: ~10-20 minutes
Expected: ~26.5 MB smaller (2.65% preprocessing)
Status: ⏳ PENDING
```

### Step 4: Compression Test ⏳
```
Input: enwik9_reordered_transformed (~973 MB)
Action: paq8px-wiki.exe -5 enwik9_reordered_transformed final.paq8
Time: ~50 hours (2+ days!)
Expected: ~178-179 MB (2.16% improvement)
Status: ⏳ PENDING
```

---

## 📊 PROJECTIONS

### Based on 10 MB Test:

```
10 MB Results:
  Baseline: 1,914,555 bytes (18.26%)
  Phase 2: 1,873,130 bytes (17.87% of preprocessed)
  Improvement: 41,425 bytes (2.16%)

Scaled to enwik9 (100x):
  Baseline: 182.6 MB (expected from PAQ8px)
  Phase 2: ~178.7 MB
  Improvement: ~3.9 MB

Conservative: 3.9 MB (exact scaling)
Realistic: 4.2 MB (slightly better on more data)
Optimistic: 5.5 MB (much better scaling)
```

### Why Scaling Might Be Better:

```
✅ More articles = better STARLIT reordering
✅ More patterns = better context learning  
✅ More data = statistical models train better
✅ Longer articles = higher-order contexts help more

But:
❌ More diversity = some articles don't reorder well
❌ Rare patterns = harder to compress
❌ Edge cases = preprocessing may miss some

Realistic expectation: 4-5 MB improvement on enwik9
```

---

## ⏰ TIMELINE

```
10:00 PM - Start preprocessing
10:10 PM - Reordering complete (estimated)
10:30 PM - Transforms complete (estimated)
10:35 PM - Start compression (estimated)

Compression: 50+ hours
Expected completion: Friday afternoon (Nov 29)

Then:
- Decompress and verify
- Measure final size
- Compare to baseline
- Document results
- Celebrate or analyze! 🎉
```

---

## 🎯 SUCCESS CRITERIA

### Minimum Success (3.5 MB):
```
✅ Proves preprocessing works on full dataset
✅ Validates 10 MB test methodology
✅ Closes 5% of gap to world record
✅ Ready to add more optimizations
```

### Target Success (4.2 MB):
```
✅ Exact scaling from 10 MB test
✅ Systematic approach validated
✅ Closes 6% of gap
✅ Strong foundation for Phase 4
```

### Stretch Success (5.5 MB):
```
🎉 Better than expected!
🎉 Proves scaling benefit
🎉 Closes 8% of gap
🎉 Very encouraging for future work
```

---

## 💾 DISK SPACE CHECK

```
Required space:
  enwik9 original: 1.0 GB
  enwik9 reordered: 1.0 GB
  enwik9 transformed: 0.97 GB
  Compressed: 0.18 GB
  Total: ~3.15 GB

Available: (checking...)
```

---

## 🚨 RISKS & MITIGATION

### Risk 1: Preprocessing Bugs
```
Problem: Reordering or transforms might fail on full dataset
Mitigation:
  - Test on enwik8 (100 MB) first if needed
  - Verify lossless transformation
  - Check file sizes match expectations
```

### Risk 2: Memory Issues
```
Problem: 1 GB files might cause OOM
Mitigation:
  - Process in chunks
  - Stream processing where possible
  - Monitor memory usage
```

### Risk 3: Disk I/O
```
Problem: HDD slowness, disk full
Mitigation:
  - Check free space first
  - Use SSD if available
  - Clean up old test files
```

### Risk 4: Compression Failure
```
Problem: PAQ8px crashes on large file
Mitigation:
  - Test on enwik8 first (100 MB)
  - Increase memory limits
  - Monitor for crashes
```

---

## 📈 WHAT WE'LL LEARN

### If Result is Good (4-5 MB):
```
✅ Preprocessing scales well
✅ 10 MB test is representative
✅ Systematic approach works
✅ Ready for Phase 4 (LSTM/cmix)
✅ Clear path forward
```

### If Result is Modest (3-4 MB):
```
✅ Some scaling benefit
✅ Baseline methodology sound
✅ Still 5-6% of gap closed
✅ Can add more techniques
```

### If Result Disappoints (< 3 MB):
```
✅ Learn about scaling limits
✅ 10 MB test overpredicted
✅ Need different approach
✅ Focus on model improvements
```

---

## 🎓 DOCUMENTATION PLAN

### During Processing:
```
- Track timing for each step
- Monitor resource usage
- Log any errors/issues
- Take screenshots if helpful
```

### After Completion:
```
- ENWIK9_RESULTS.md (detailed analysis)
- Update README with actual results
- Update GAP_BREAKDOWN with progress
- Commit all code and results
- Plan Phase 4 based on findings
```

---

## 💪 CONFIDENCE LEVEL

```
Very High (90%+) that we'll get 3.5-5.5 MB improvement

Why confident:
✅ 2.16% proven on 10 MB
✅ Preprocessing is lossless
✅ PAQ8px is stable
✅ Methodology is sound
✅ Conservative expectations

Risk factors:
⚠️ First time on full dataset
⚠️ 50 hour compression time (can't iterate)
⚠️ Scaling assumptions untested

But: Even if we get 3 MB, that's REAL progress!
```

---

**Status:** 🚀 READY TO START  
**Next:** Apply starlit_reorder.py to enwik9  
**Timeline:** 3 days total (preprocessing + compression)  
**Expected:** 4-5 MB improvement (2.16% → ~178 MB)

**Let's validate our systematic approach on the REAL target!** 🎯
