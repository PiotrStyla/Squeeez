# Analiza wielokanałowego podejścia - 22.11.2024

## 🔬 Wyniki eksperymentu

### Test na 1 MB enwik8

**Multichannel (3 kanały):** 2.145 bpb  
**Single Order-3:** 2.068 bpb  
**Różnica:** -3.72% (multichannel GORSZY)

---

## 📊 Szczegółowe dane

### Podział danych:
- **Linki:** 181 KB (17.3%) → 66.9 KB skompresowane → **2.954 bpb**
- **Tekst:** 765 KB (73.0%) → 199.7 KB skompresowane → **2.086 bpb**
- **Inne:** 69 KB (6.6%) → 14.5 KB skompresowane → **1.675 bpb**

### Baseline:
- **Single Order-3:** 1,048 KB → 271 KB → **2.068 bpb**

---

## 💡 Dlaczego multichannel jest GORSZY?

### 1. Linki kompresują się GORZEJ niż w mixie

**Problem:** Linki (Order-2) dają 2.954 bpb  
**Baseline:** Całość (Order-3) daje 2.068 bpb

**Dlaczego?**
- Linki w kontekście otaczającego tekstu są bardziej przewidywalne
- Przykład: `"In [[computer science]], the [[Turing test]]..."`
  - W baseline: Order-3 widzi "In " przed "[[computer"
  - W multichannel: Widzimy tylko poprzednie linki

**Wniosek:** Kontekst międzykanałowy jest KLUCZOWY!

### 2. Utrata kontekstu na granicach

Gdy przechodzimy: `tekst` → `[[link]]` → `tekst`:
- **Baseline:** Zachowuje 3 znaki kontekstu przez granicę
- **Multichannel:** Resetuje kontekst przy każdej zmianie kanału

### 3. Tekst kompresuje się PODOBNIE

- Multichannel tekst: 2.086 bpb
- Baseline całość: 2.068 bpb
- Różnica: tylko 0.9%

**To znaczy:** Izolowanie tekstu nie daje dużej przewagi.

---

## 🎯 Co działa, co nie

### ✅ Co działa:

1. **"Inne" (struktura) kompresują się świetnie:** 1.675 bpb
   - Nagłówki, XML, entities są bardzo przewidywalne
   - Izolacja tutaj MA SENS

2. **Czysty tekst podobny do baseline:** 2.086 vs 2.068
   - Oznacza, że Order-3 na tekście jest już optymalny
   - Trudno poprawić bez NN

### ❌ Co nie działa:

1. **Linki w izolacji:** 2.954 bpb (o 43% gorsze niż baseline!)
   - Utrata kontekstu otaczającego tekstu
   - Order-2 za słaby dla linków

2. **Brak cross-channel context:**
   - Każdy kanał żyje w próżni
   - Nie wykorzystujemy zależności między kanałami

---

## 🔧 Jak to naprawić?

### Strategia 1: Cross-channel context (najbardziej obiecująca)

**Idea:** Zamiast resetować kontekst na granicy, przekazuj go między kanałami.

**Implementacja:**
```python
# Przy zmianie z text → link:
link_model.current_context = last_3_chars_from_text

# Przy zmianie z link → text:
text_model.current_context = last_3_chars_from_link
```

**Oczekiwany gain:** 5-10% na linkach → ~1-2% overall

### Strategia 2: Hierarchiczny model

**Idea:** Główny model Order-3 na wszystko + specjalizowane "eksperci" dla struktur

**Implementacja:**
```python
for symbol in data:
    if in_special_structure (link/heading/template):
        probability = mix(
            0.7 * main_model.predict(symbol),
            0.3 * specialist_model.predict(symbol)
        )
    else:
        probability = main_model.predict(symbol)
```

**Oczekiwany gain:** 2-5% overall

### Strategia 3: Lepsze modele dla linków

**Order-2 → Order-3 dla linków:**
- Więcej kontekstu dla przewidywania tytułów
- Koszt: większy model

**Dictionary-based dla popularnych linków:**
- Top 1000 linków jako single tokens
- Huffman coding dla nazw artykułów

**Oczekiwany gain:** 10-20% na linkach → 2-3% overall

---

## 📈 Projekcja z optymalizacjami

### Obecny stan (1 MB):
- Multichannel: 2.145 bpb
- Baseline: 2.068 bpb

### Z cross-channel context:
- Linki: 2.954 → ~2.6 bpb (-12%)
- Overall: 2.145 → ~2.09 bpb (-2.5%)
- **vs baseline:** -1% (prawie identyczne)

### Z cross-channel + lepsze modele linków:
- Linki: 2.954 → ~2.3 bpb (-22%)
- Overall: 2.145 → ~2.02 bpb (-6%)
- **vs baseline:** +2.3% LEPSZY

### Z hierarchicznym mixing:
- Overall: 2.02 → ~1.95 bpb
- **vs baseline:** +5.7% LEPSZY

---

## 🎓 Kluczowe lekcje

### 1. Kontekst > Specjalizacja

**Utrata 3 znaków kontekstu na granicy = większy problem niż brak specjalizacji**

Dla kompresji Order-N, kontekst jest WSZYSTKIM.

### 2. Wikipedia to nie kanały, to kontinuum

Struktura `text [[link]] text [[link]]` jest mocno spleciona.  
Sztuczny podział niszczy informację.

### 3. Prosty split ≠ wielokanałowy model

Prawdziwy multichannel to:
- Cross-channel context
- Hierarchiczne mixing
- Adaptive weighting

Nie tylko: "podziel i kompresuj osobno"

---

## 🚀 Zalecany plan działania

### Opcja A: Napraw multichannel (2-3 dni pracy)

1. Implementuj cross-channel context
2. Testuj na 1 MB
3. Jeśli > +2% vs baseline → kontynuuj
4. Jeśli nie → abandoned, fokus na NN

**Prawdopodobieństwo sukcesu:** 60%  
**Potencjalny gain:** +3-7% vs baseline

### Opcja B: Abandoned multichannel, fokus na NN (zalecane)

1. Single Order-3 działa rewelacyjnie (2.068 bpb)
2. Multichannel to marginalne ulepszenie w najlepszym wypadku
3. **Neural model ma DUŻO większy potencjał:**
   - Transformer znakowy: potencjalnie < 1.5 bpb
   - Hybrid Order-3 + NN: potencjalnie < 1.3 bpb

**Prawdopodobieństwo sukcesu:** 40% (ale większy gain)  
**Potencjalny gain:** 30-50% vs baseline

### Opcja C: Port do C++, optymalizacja baseline (pragmatyczne)

1. Obecny baseline (2.068 bpb) jest solidny
2. Główny problem: SZYBKOŚĆ (0.02 MB/s)
3. C++ może dać 100-200x przyspieszenie
4. Szybszy development → lepsze iteracje

**Prawdopodobieństwo sukcesu:** 95%  
**Potencjalny gain:** 0% kompresji, ale dużo szybszy workflow

---

## 💰 ROI Analysis

### Multichannel (Opcja A):
- **Czas:** 2-3 dni
- **Gain:** +3-7% (optymistycznie)
- **ROI:** Niski - dużo pracy, mały efekt

### Neural (Opcja B):
- **Czas:** 2-3 tygodnie
- **Gain:** +30-50% (jeśli zadziała)
- **ROI:** Wysoki - ryzykowne, ale duży potencjał

### C++ Port (Opcja C):
- **Czas:** 1 tydzień
- **Gain:** 0% kompresji, 100x szybciej
- **ROI:** Średni - quality of life, lepszy development

---

## 🎯 Rekomendacja

### Dla Hutter Prize:

**Fokus na Neural model (Opcja B)**

Powody:
1. Single Order-3 @ 2.068 bpb to już ~246 MB na enwik9
2. Rekord to ~114 MB
3. Gap: 132 MB = wymaga > 50% poprawy
4. Multichannel da max 7% → wciąż 230 MB (nie wygra)
5. **Tylko NN ma szansę zbliżyć się do rekordu**

### Dla nauki / portfolio:

**Port do C++ (Opcja C) + publikacja**

Powody:
1. Solid implementation Order-3 lepszy od zlib to wartość sama w sobie
2. C++ kod to dobry materiał edukacyjny
3. Można publikować jako open-source
4. Realnie użyteczne (szybkie testy)

---

## 📝 Wnioski końcowe

**Multichannel podejście (w prostej formie) NIE działa.**

Utrata kontekstu > gain ze specjalizacji.

**Ale eksperyment był wartościowy:**
- Potwierdziliśmy że Order-3 baseline jest bardzo dobry
- Zrozumieliśmy dlaczego kontekst jest kluczowy
- Nauczyliśmy się że "podział" ≠ "lepsza kompresja"

**Następny krok:** Decyzja strategiczna - NN, C++, czy hybrid?

---

**Data:** 2024-11-22 07:30  
**Eksperyment:** Multichannel compression  
**Wynik:** Negatywny, ale pouczający  
**Status:** Gotowi do Fazy 3
