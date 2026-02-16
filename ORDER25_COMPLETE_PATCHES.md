# PAQ8px Order-25 Complete Modification Patches

## Files to Modify (5 critical files)

### 1. Shared.hpp (Line 120)
**Purpose:** Increase context array size

```cpp
// BEFORE:
uint64_t cxt[15]; // context hashes used by NormalModel and MatchModel

// AFTER:
uint64_t cxt[26]; // context hashes used by NormalModel and MatchModel (Order 0-25)
```

### 2. Hash.hpp (Line 24-28)
**Purpose:** Add hash constants for orders 14-24

```cpp
// BEFORE:
static constexpr uint64_t hashes[14] = {UINT64_C(0x9E3779B97F4A7C15), ..., UINT64_C(0xE3E4E8AA829AB9B5)};

// AFTER:
static constexpr uint64_t hashes[25] = {
  // Original 14:
  UINT64_C(0x9E3779B97F4A7C15), UINT64_C(0x993DDEFFB1462949), UINT64_C(0xE9C91DC159AB0D2D),
  UINT64_C(0x83D6A14F1B0CED75), UINT64_C(0xA14F1B0CED5A841D), UINT64_C(0xC0E51314A614F4E1),
  UINT64_C(0xDA9CC2600AE45A25), UINT64_C(0x826797AA04A65735), UINT64_C(0x2375BE54C41A08ED),
  UINT64_C(0xD39104E950564B39), UINT64_C(0x3091697D5E685621), UINT64_C(0x20EB84EE04A3C7E1),
  UINT64_C(0xF501F1D0944B2385), UINT64_C(0xE3E4E8AA829AB9B5),
  // New 11 (14-24):
  UINT64_C(0xD2C9B3A58F7E6D41), UINT64_C(0xC1B8A29F7E6D5C31),
  UINT64_C(0xB0A7918E6D5C4B21), UINT64_C(0xA096807D5C4B3A11),
  UINT64_C(0x9F856F6C4B3A2901), UINT64_C(0x8E745E5B3A291808),
  UINT64_C(0x7D634D4A29180717), UINT64_C(0x6C523C3918071626),
  UINT64_C(0x5B412B2807162535), UINT64_C(0x4A301A1716253444),
  UINT64_C(0x391F0916253443F3)
};
```

### 3. NormalModel.hpp (Lines 7-9, 32)
**Purpose:** Update comments and documentation

```cpp
// BEFORE (Line 7-9):
/**
 * Model for order 0-14 contexts
 * Contexts are hashes of previous 0..14 bytes.
 * Order 0..6, 8 and 14 are used for prediction.
 * Note: order 7+ contexts are modeled by matchModel as well.
 */

// AFTER:
/**
 * Model for order 0-25 contexts
 * Contexts are hashes of previous 0..25 bytes.
 * Order 0..6, 8, 14, 18, 22, and 25 are used for prediction.
 * Note: order 7+ contexts are modeled by matchModel as well.
 */

// BEFORE (Line 32):
  /**
    * update order 1..14 context hashes.
    * Note: order 0 context does not need an update so its hash never changes.
    */

// AFTER:
  /**
    * update order 1..25 context hashes.
    * Note: order 0 context does not need an update so its hash never changes.
    */
```

### 4. NormalModel.cpp (Lines 29-31, 40-45)
**Purpose:** Update loop bounds and prediction orders

```cpp
// BEFORE (Line 29):
for( uint64_t i = 14; i > 0; --i ) {

// AFTER:
for( uint64_t i = 25; i > 0; --i ) {

// BEFORE (Lines 40-45):
for(uint64_t i = 1; i <= 6; ++i ) {
  cm.set(RH, cxtHashes[i]);
}
cm.set(RH, cxtHashes[8]); 
cm.set(RH, cxtHashes[11]);
cm.set(RH, cxtHashes[14]);

// AFTER (add more prediction orders):
for(uint64_t i = 1; i <= 6; ++i ) {
  cm.set(RH, cxtHashes[i]);
}
cm.set(RH, cxtHashes[8]); 
cm.set(RH, cxtHashes[11]);
cm.set(RH, cxtHashes[14]);
cm.set(RH, cxtHashes[18]);  // NEW
cm.set(RH, cxtHashes[22]);  // NEW
cm.set(RH, cxtHashes[25]);  // NEW
```

### 5. NormalModel.hpp (Line 14)
**Purpose:** Update number of context maps

```cpp
// BEFORE:
static constexpr int nCM = 9;

// AFTER:
static constexpr int nCM = 12;  // 9 original + 3 new orders (18, 22, 25)
```

### 6. ContextMap2.cpp/hpp (if needed)
**Purpose:** May need to increase hash table size

Check current size, if < 256M entries, increase to:
```cpp
// Suggested size for Order-25:
static constexpr size_t HASH_TABLE_SIZE = 1ULL << 28; // 256M entries
```

## Compilation

After modifications:

```bash
cd /root/hutter/paq8px_order25
# Copy modified source from main paq8px
cp -r ../paq8px paq8px_order25_modified
cd paq8px_order25_modified

# Apply patches above manually or via script

# Compile
g++ -O3 -march=native -std=c++17 -pthread -o paq8px_o25 paq8px.cpp -lm

# Or with cmake:
mkdir build_o25
cd build_o25
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
```

## Testing Sequence

```bash
# 1. Smoke test (1 MB, ~30 sec)
head -c 1000000 enwik9_reordered_transformed > test_1m.dat
./paq8px_o25 -5 test_1m.dat test_1m_o25.paq8

# 2. Small test (10 MB, ~45 min)
head -c 10485760 enwik9_reordered_transformed > test_10m.dat
time ./paq8px_o25 -5 test_10m.dat test_10m_o25.paq8
# Compare with Order-14 baseline

# 3. Medium test (100 MB, ~8-10 hours)
head -c 100000000 enwik9_reordered_transformed > test_100m.dat
time ./paq8px_o25 -5 test_100m.dat test_100m_o25.paq8

# 4. Full run (1 GB, ~25-30 days)
time ./paq8px_o25 -5 enwik9_reordered_transformed final_o25.paq8
```

## Expected Results

| Test | Order-14 | Order-25 | Gain |
|------|----------|----------|------|
| 10 MB | 1.87 MB | ~1.73 MB | ~7.5% |
| 100 MB | ~18 MB | ~16.2 MB | ~10% |
| 1 GB | 134.3 MB | ~117-119 MB | ~11-13% |

**Target:** ~117-119 MB (vs world record 114 MB)

## Risk Mitigation

1. **Memory:** May need 12-15 GB RAM (test on server first)
2. **Speed:** Will be slower (~25% more time)
3. **Bugs:** Test thoroughly on small files first

## Next Actions

1. ✅ Wait for -5 vs -5r test results
2. ⏳ Apply patches to source
3. ⏳ Compile and test on 1 MB
4. ⏳ Test on 10 MB
5. ⏳ If OK → full 1 GB run
