# PPM Order-25 Implementation Plan
## Największy Potencjalny Gain: ~15 MB (134.3 MB → ~119 MB)

## Aktualny Status

**Problem:** PAQ8px używa Order-14 PPM, co ogranicza context window do 14 bajtów.
**Cel:** Zwiększyć do Order-25 dla lepszego modelowania long-range dependencies.
**Gain:** ~15 MB (z gap analysis)

## Techniczne Wymagania

### 1. Pamięć RAM
- Order-14: ~750 MB RAM
- Order-25: ~10-15 GB RAM (szacunek)
- **Rozwiązanie:** Netcup server ma wystarczająco RAM

### 2. Modyfikacje Source Code

**Główne pliki do modyfikacji:**

#### A. `Shared.hpp` lub `ContextModel.hpp`
```cpp
// PRZED:
#define MAX_ORDER 14
static constexpr int maxOrder = 14;

// PO:
#define MAX_ORDER 25
static constexpr int maxOrder = 25;
```

#### B. Context Map Size (w `ContextMap.cpp` lub podobnym)
```cpp
// Zwiększyć rozmiar hash table
// PRZED:
static constexpr uint32_t contextMapSize = 1 << 24; // 16M entries

// PO (dla Order-25):
static constexpr uint32_t contextMapSize = 1 << 28; // 256M entries
```

#### C. Memory Allocation (w `paq8px.cpp` main function)
```cpp
// Zwiększyć limity pamięci
// Znaleźć linie z:
if (level >= 5) mem = 747 << 20; // 747 MB

// Dodać nowy level lub zwiększyć:
if (level == 5 && orderOverride == 25) mem = 12000 << 20; // 12 GB
```

### 3. Compilation Flags

```bash
# Dla większej pamięci, kompiluj z:
g++ -O3 -march=native -DMAX_ORDER=25 -o paq8px_order25 paq8px.cpp
```

Lub w CMakeLists.txt:
```cmake
add_definitions(-DMAX_ORDER=25)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native")
```

## Implementation Steps

### Phase 1: Source Analysis (1-2 dni)

1. **Download PAQ8px source do lokalnego:**
```bash
git clone https://github.com/hxim/paq8px
cd paq8px
```

2. **Znajdź wszystkie wystąpienia Order-14:**
```bash
grep -rn "14" *.cpp *.hpp | grep -i "order\|max"
grep -rn "MAX_ORDER\|maxOrder" *.cpp *.hpp
```

3. **Zidentyfikuj kluczowe struktury:**
- Context hash tables
- PPM model state
- Memory allocation
- Context encoding/decoding

### Phase 2: Modification (2-3 dni)

**Plik 1: `Shared.hpp` (lub gdzie jest MAX_ORDER)**
```cpp
// Line ~50-100 (szukać):
#ifndef MAX_ORDER
#define MAX_ORDER 14  // ← ZMIENIĆ NA 25
#endif
```

**Plik 2: `ContextMap.cpp` lub `HashTable.cpp`**
```cpp
// Zwiększyć rozmiar hash table
// Szukać: hashTableSize, contextMapSize, tableSize
// Obecna wartość: prawdopodobnie 1<<24 (16M)
// Nowa wartość: 1<<28 (256M) lub 1<<29 (512M)
```

**Plik 3: `paq8px.cpp` (main memory allocation)**
```cpp
// W funkcji parseArgs lub podobnej:
// Znaleźć gdzie ustawia się `mem` based on `level`
// Dodać special case dla Order-25:

if (order25Mode) {
    mem = 12000 << 20; // 12 GB for Order-25
}
```

**Plik 4: `ContextModel.cpp` (jeśli istnieje)**
```cpp
// Sprawdzić czy są hardcoded loops do Order-14
// Zmienić na MAX_ORDER lub 25
```

### Phase 3: Compilation Test (1 dzień)

```bash
# Na serwerze Netcup:
cd /root/hutter/paq8px
git clone https://github.com/hxim/paq8px paq8px_order25
cd paq8px_order25

# Edytuj pliki (vim/nano)
vim Shared.hpp  # MAX_ORDER 14 → 25

# Kompiluj
g++ -O3 -march=native -o paq8px_order25 paq8px.cpp \
    -std=c++17 -pthread -lm

# Albo cmake:
cmake -B build_order25 -DMAX_ORDER=25
cmake --build build_order25
```

### Phase 4: Testing (2-3 dni)

**Test 1: Smoke test (1 MB)**
```bash
head -c 1000000 enwik9_reordered_transformed > test_1mb.dat
./paq8px_order25 -5 test_1mb.dat test_1mb_order25.paq8
# Sprawdzić czy nie crashuje
```

**Test 2: Small test (10 MB, ~1h)**
```bash
head -c 10485760 enwik9_reordered_transformed > test_10mb.dat
./paq8px_order25 -5 test_10mb.dat test_10mb_order25.paq8
# Porównać rozmiar z Order-14 version
```

**Test 3: Medium test (100 MB, ~10h)**
```bash
head -c 100000000 enwik9_reordered_transformed > test_100mb.dat
./paq8px_order25 -5 test_100mb.dat test_100mb_order25.paq8
```

**Test 4: Full run (1 GB, ~25-30 dni)**
```bash
./paq8px_order25 -5 enwik9_reordered_transformed final_order25.paq8
```

## Expected Results

### Compression Ratio Improvements

| Dataset | Order-14 | Order-25 (Expected) | Gain |
|---------|----------|---------------------|------|
| 10 MB | 1.87 MB | ~1.75 MB | ~6.4% |
| 100 MB | ~18 MB | ~16.5 MB | ~8.3% |
| 1 GB | 134.3 MB | ~119 MB | **~11.4%** |

**Final target:** ~119 MB (vs world record 114 MB = 5 MB gap)

### Memory & Time

| Metric | Order-14 | Order-25 |
|--------|----------|----------|
| RAM | 750 MB | ~12 GB |
| Time (1 GB) | 20 days | 25-30 days |
| Compression ratio | 13.43% | ~11.9% |

## Risk Analysis

### HIGH RISK ⚠️

1. **Memory Overflow:**
   - Order-25 może potrzebować >15 GB RAM
   - Netcup server: sprawdzić limit pamięci
   - **Mitigation:** Test na małych plikach najpierw

2. **Hash Collisions:**
   - Większy order = więcej unique contexts
   - Hash table może być za mały
   - **Mitigation:** Zwiększyć rozmiar hash table (1<<28 lub więcej)

3. **Integer Overflow:**
   - Context hashing może overflow przy Order-25
   - **Mitigation:** Użyć uint64_t zamiast uint32_t

### MEDIUM RISK ⚡

1. **Compilation Errors:**
   - Hardcoded assumptions o Order-14
   - **Mitigation:** Przejrzeć cały kod, użyć MAX_ORDER wszędzie

2. **Performance Degradation:**
   - Order-25 może być dużo wolniejszy (CPU cache misses)
   - **Mitigation:** Akceptowalne (25-30 dni vs 20 dni)

3. **Diminishing Returns:**
   - Order-25 może nie dać full 15 MB gain
   - Możliwe: tylko 10-12 MB gain
   - **Mitigation:** Wciąż worth it

### LOW RISK ✅

1. **Bug w Code:**
   - PAQ8px jest dojrzały, modyfikacja jest prosta
   - **Mitigation:** Extensive testing na małych plikach

## Alternative Approach: Hybrid Order

Jeśli Order-25 daje memory problems, spróbuj **Adaptive Order:**

```cpp
// Użyj Order-25 dla text blocks
// Użyj Order-14 dla innych blocks
if (blockType == TEXT) {
    order = 25;
} else {
    order = 14;
}
```

To da większość gain przy mniejszym zużyciu RAM.

## Timeline

```
Week 1:
  Day 1-2: Download source, analiza kodu
  Day 3-4: Modyfikacja source (MAX_ORDER, hash tables)
  Day 5-7: Compilation, smoke tests (1 MB, 10 MB)

Week 2:
  Day 8-10: Medium test (100 MB, ~10h compression)
  Day 11-14: Debug issues, optimize, finalize

Week 3-5:
  Day 15-44: Full run (1 GB, ~25-30 days)

Week 6:
  Day 45-47: Analyze results, celebrate! 🎉
```

## Success Criteria

✅ **Minimum Success:** 125 MB (9 MB gain)
✅ **Expected Success:** 119 MB (15 MB gain)
✅ **Stretch Goal:** 115 MB (19 MB gain, close to world record!)

## Next Steps (ACTION ITEMS)

**Immediate (Dzisiaj):**
1. ⏳ Czekaj na wyniki `-5` vs `-5r` test (50 MB, ~2-3h)
2. 📥 Download PAQ8px source lokalnie
3. 🔍 Znajdź wszystkie wystąpienia MAX_ORDER w kodzie

**Tomorrow:**
1. ✏️ Zmodyfikuj source code (MAX_ORDER, hash tables, memory)
2. 🔨 Kompiluj na serwerze
3. 🧪 Test na 1 MB (smoke test)

**This Week:**
1. 🧪 Test na 10 MB (~1h)
2. 🧪 Test na 100 MB (~10h)
3. 🚀 Jeśli OK → launch full 1 GB run (~25-30 dni)

**Month 2:**
1. 🏆 Analyze final result (~119 MB expected)
2. 📝 Update paper with new result
3. 🎯 Decide: Submit to Hutter Prize? Or push for cmix (world record)?

---

**CONCLUSION:** Order-25 jest najlepszą inwestycją czasu/effort dla maksymalnego gain. Start implementation teraz, równolegle z testami `-5` vs `-5r`.
