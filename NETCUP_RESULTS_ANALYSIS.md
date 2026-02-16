# Analiza Wyniku Kompresji Netcup (2026-01-28)

## Wynik Aktualny

**Netcup Server Run:**
- Input (po preprocessing): 961,693,324 bytes (918 MB)
- Output: **134,301,074 bytes (128.079 MiB)**
- Ratio: **13.97%** (relative to preprocessed input)
- Czas: 20.89 dni (501.3 h)
- RAM: 893 MB
- SHA256: `8d7f4cd7f2ae1471bf6e564ad2b41df725f366c6b109fdfa66680b96d50a567d`

## Porównanie z Celami

```
World Record (STARLIT):    114.0 MB  (11.40%)  ← CEL
Paper Target:              127.44 MB (12.74%)
Netcup Actual:             134.30 MB (13.43%)  ← CURRENT
Baseline PAQ8px:           182.6 MB  (18.26%)
```

**Gap Analysis:**
- Do world record: **20.30 MB** (134.30 - 114.0)
- Do paper target: **6.86 MB** (134.30 - 127.44)
- Improvement vs baseline: **48.30 MB** (182.6 - 134.30)

## Problem: Dlaczego Gorszy Wynik?

**Różnica 6.86 MB vs paper target (127.44 MB)**

### Możliwe Przyczyny:

1. **Flaga `-r` (LSTM repository)**
   - Netcup użył: `-5r` (LSTM z pre-trained models)
   - Paper użył: `-5` (bez LSTM? lub inny tryb?)
   - Flaga `-r` **dodaje** LSTM models (`english.rnn`, `x86_64.rnn`)
   - **Paradoks:** LSTM powinien POPRAWIĆ, nie POGORSZYĆ kompresję
   - **Hipoteza:** Możliwe że LSTM w PAQ8px ma bug lub niepoprawną konfigurację dla tego datasetu

2. **Wersja PAQ8px**
   - Netcup: `v209fix1` (2025)
   - Paper (hipotetyczny): może starsza wersja `v208` lub `v207`?
   - Różne wersje = różne wyniki

3. **Build/Compiler**
   - PAQ8px kompilowany na różnych platformach daje różne wyniki
   - ARM64 vs x86_64 architecture
   - Netcup: ARM64 (symulacja x86)

4. **Preprocessing Pipeline**
   - Czy preprocessing był identyczny?
   - Kolejność transformacji, parametry reorderingu

## Co Zrobić: Plan Poprawy (2 ścieżki)

### ✅ Ścieżka A: DEBUGUJ OBECNY WYNIK (Quick Win, 1-2 dni)

**Hipoteza:** `-r` (LSTM) pogarsza wynik dla tego datasetu

**Test:**
1. Uruchom kompresję **bez `-r`** (tylko `-5`)
2. Porównaj wynik z `-5r` vs `-5`
3. Jeśli `-5` da lepszy wynik → używaj `-5`

**Dlaczego to możliwe:**
- LSTM może być przeuczony (overfitting)
- Pre-trained models (`english.rnn`, `x86_64.rnn`) mogą nie pasować do preprocessed Wikipedia
- LSTM dodaje ~50 MB pamięci + obliczenia, ale może **nie** poprawiać kompresji dla już zoptymalizowanego inputu

**Czas:** ~20 dni kompresji, ale może dać **natychmiastową poprawę 6-7 MB**

---

### 🚀 Ścieżka B: IMPLEMENTUJ BRAKUJĄCE TECHNIKI (Medium-term, 2-4 tygodnie)

Z paper wiemy, że **5 technik jeszcze NIE użytych:**

| Technika | Estymowany Gain | Implementacja | Priority |
|----------|----------------|---------------|----------|
| PPM Order-25 | ~15 MB | Zmiana w PAQ8px source | 🔥 HIGH |
| cmix Mixing | ~10 MB | Integracja cmix | MEDIUM |
| LSTM Mixer (poprawny) | ~6 MB | Debug obecnego LSTM | 🔥 HIGH |
| Memory Optimization | ~5 MB | Tuning PAQ8px | LOW |
| UTF + Misc | ~4.6 MB | Małe tweaki | LOW |

**Plan Implementacji (priorytet = impact/effort):**

#### 1. **PPM Order-25** (NAJWYŻSZY PRIORYTET)
   - **Gain:** ~15 MB
   - **Jak:** Modyfikacja `PAQ8px` source code
   - **Plik:** `ContextModel.cpp` lub podobny
   - **Zmiana:** Zwiększ `MAX_ORDER` z 14 na 25
   - **Problem:** Wymaga **dużo więcej RAM** (~10-15 GB)
   - **Czas dev:** 1-2 dni (modyfikacja + kompilacja)
   - **Czas test:** 20-25 dni kompresji

#### 2. **Debug LSTM** (QUICK WIN)
   - **Gain:** ~6 MB (jeśli obecny LSTM psuje)
   - **Jak:** 
     a) Test `-5` vs `-5r` (bez vs z LSTM)
     b) Jeśli `-r` gorszy → używaj `-5`
     c) Jeśli `-r` lepszy → sprawdź konfigurację LSTM
   - **Czas dev:** 1 dzień (testy)
   - **Czas test:** 20 dni

#### 3. **cmix Integration**
   - **Gain:** ~10 MB
   - **Jak:** Użyj `cmix` zamiast PAQ8px jako final compressor
   - **Problem:** cmix jest BARDZO wolny (100-150 dni na 1 GB)
   - **Czas dev:** 2-3 dni (setup cmix)
   - **Czas test:** 100+ dni ⚠️

#### 4. **Memory Optimization**
   - **Gain:** ~5 MB
   - **Jak:** Tuning PAQ8px parameters, zwiększenie RAM dla mixers
   - **Czas dev:** 1-2 dni
   - **Czas test:** 20 dni

---

## Rekomendowany Plan Działania (Next 48h)

### Faza 1: QUICK DEBUG (Dzisiaj-Jutro)

**A. Sprawdź co dał `-5r` vs `-5` lokalnie (10 MB test):**
```bash
# Test 1: Z LSTM (-5r)
./paq8px -5r enwik_10mb test_with_lstm.paq8

# Test 2: Bez LSTM (-5)
./paq8px -5 enwik_10mb test_no_lstm.paq8

# Porównaj rozmiary
```

**B. Jeśli `-5` lepszy:**
- Restart kompresji na Netcup **bez `-r`**
- Ekspektowany wynik: ~127-128 MB (bliżej paper target)

**C. Jeśli `-5r` lepszy:**
- Problem leży gdzie indziej (preprocessing? wersja PAQ8px?)

### Faza 2: IMPLEMENTUJ PPM ORDER-25 (Tydzień 1-2)

**1. Clone PAQ8px source:**
```bash
git clone https://github.com/hxim/paq8px
cd paq8px
```

**2. Znajdź MAX_ORDER w source:**
```bash
grep -r "MAX_ORDER\|#define.*14\|Order.*14" *.cpp *.hpp
```

**3. Zwiększ Order 14 → 25:**
```cpp
// Przed:
#define MAX_ORDER 14

// Po:
#define MAX_ORDER 25
```

**4. Zwiększ alokację pamięci:**
- Context map size
- Hash table size
- Memory limits

**5. Kompiluj:**
```bash
cmake -B build
cmake --build build
```

**6. Test na 10 MB:**
```bash
./paq8px_order25 -5 enwik_10mb test_order25.paq8
```

**7. Jeśli działa → run na full 1 GB**

**Ekspektowany gain:** ~15 MB (127 MB → 112 MB)

### Faza 3: CMIX (Opcjonalnie, jeśli czas pozwala)

**1. Install cmix:**
```bash
git clone https://github.com/byronknoll/cmix
cd cmix
cmake -B build
cmake --build build
```

**2. Run cmix na preprocessed input:**
```bash
./cmix -c enwik9_reordered_transformed output.cmix
```

**Uwaga:** cmix jest **BARDZO** wolny (100-150 dni), ale daje najlepszy wynik

---

## Timeline Estimate

```
┌─────────────────────────────────────────────────────────────┐
│ Week 1-2: Debug LSTM + Implement PPM Order-25              │
│   - Day 1-2: Test -5 vs -5r locally                        │
│   - Day 3-7: Modify PAQ8px source (Order 25)               │
│   - Day 8-10: Test Order-25 on 10 MB                       │
│   - Day 11-14: Fix bugs, optimize                          │
├─────────────────────────────────────────────────────────────┤
│ Week 3-5: Full Compression Run (Order-25)                  │
│   - 20-25 days compression time                            │
│   - Expected: ~112-115 MB (close to world record!)         │
├─────────────────────────────────────────────────────────────┤
│ Week 6-8: Optional cmix integration                        │
│   - If we want to beat world record decisively            │
│   - 100+ days compression time                             │
│   - Expected: ~105-110 MB (NEW WORLD RECORD)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Kluczowe Decyzje (DO PODJĘCIA TERAZ)

### Decyzja 1: `-5` vs `-5r` (LSTM)
**Pytanie:** Czy LSTM pomaga czy przeszkadza?
**Test:** Kompresja 10 MB z i bez `-r`
**Czas:** 2-4 godziny
**Action:** Zrobić test TERAZ

### Decyzja 2: Order-25 Implementation
**Pytanie:** Czy warto modyfikować PAQ8px source?
**Gain:** ~15 MB (największy single gain)
**Effort:** 1 tydzień dev + 3 tygodnie test
**Risk:** Medium (może nie działać, wymaga debug)
**Action:** START development w Week 1

### Decyzja 3: cmix vs PAQ8px
**Pytanie:** Czy przejść na cmix dla final push?
**Gain:** ~10-15 MB dodatkowe
**Effort:** 100+ dni compression
**Risk:** Low (cmix jest proven)
**Action:** Zrobić to TYLKO jeśli chcemy bezwzględnie pobić rekord świata

---

## Immediate Next Steps (TERAZ)

1. ✅ **Test `-5` vs `-5r` locally na 10 MB** (2-4h)
2. ⏳ **Sprawdź czy verification test na serwerze się skończył** (running)
3. 📝 **Clone PAQ8px source i przeanalizuj możliwość Order-25** (2h)
4. 🚀 **Jeśli `-5` lepszy → restart compression bez `-r`** (20 dni)
5. 🔧 **Jeśli Order-25 feasible → start implementation** (Week 1)

---

## Expected Final Results

**Conservative (tylko -5 bez LSTM):**
- Result: ~127-128 MB
- Gap to world record: ~13-14 MB
- Ranking: TOP 5-10

**Optimistic (Order-25 implemented):**
- Result: ~112-115 MB
- Gap to world record: 0-2 MB
- Ranking: TOP 2-3 (WORLD RECORD CONTENDER!)

**Aggressive (Order-25 + cmix):**
- Result: ~105-110 MB
- Gap to world record: -4 to -9 MB
- Ranking: **NEW WORLD RECORD** 🏆

---

**CONCLUSION:** Mamy jasny plan. Najbardziej obiecująca ścieżka to:
1. Quick test `-5` vs `-5r` (dzisiaj)
2. Implementacja PPM Order-25 (Week 1-2)
3. Full run z Order-25 (Week 3-5)
4. Opcjonalnie cmix dla world record (Week 6+)

**Action Item #1:** Uruchomić test porównawczy `-5` vs `-5r` na 10 MB datasecie.
