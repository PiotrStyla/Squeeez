# Hutter Lab - Compression Research

Projekt badawczy nad kompresją dla **Hutter Prize** (500,000€ za najlepszą kompresję enwik9).

## 🎯 Cel

Zbudować kompresor, który:
- Osiąga lepszą kompresję niż obecne rekordy na enwik9 (1 GB Wikipedii)
- Używa **out-of-the-box** podejścia: wielokanałowe modelowanie struktury Wiki
- Spełnia wymagania Hutter Prize (samodzielne exe, bez zewnętrznych danych, < 70k/T godzin)

## 📊 Dotychczasowe wyniki

### Test na sample.txt (2,372 bajty):

| Model | Rozmiar danych | Bity/bajt | Poprawa vs zlib |
|-------|----------------|-----------|-----------------|
| zlib poziom 9 | 1,136 B | 3.831 | baseline |
| Order-0 | 1,315 B | 4.435 | -16% |
| Order-1 | 943 B | 3.180 | +17% |
| Order-2 | 528 B | 1.781 | +53% |
| **Order-3** | **226 B** | **0.762** | **+80%** 🎯 |

## 🛠 Komponenty

### 1. `arithmetic_coder.py`
- Implementacja arithmetic coding z precyzją całkowitoliczbową
- Enkoder i dekoder z normalizacją zakresów
- Wsparcie dla dowolnych modeli probabilistycznych

### 2. `context_model.py`
- Model Order-N (n-gram) z backoff mechanism
- Trenowanie na danych (statyczny model)
- Wersja adaptacyjna (model aktualizuje się podczas kodowania)
- Serializacja/deserializacja modelu

### 3. `compress_context.py`
- Pełny pipeline kompresji z modelem kontekstowym
- Test różnych wartości Order (0, 1, 2, 3)
- Weryfikacja poprawności dekompresji
- Porównanie z zlib

## 🚀 Jak używać

### Podstawowy test:
```bash
python compress_context.py
```

To uruchomi testy Order-0 do Order-3 na `data/sample.txt`.

### Pobierz prawdziwe dane enwik:
```bash
python download_enwik.py
```

Opcje:
- enwik8 (100 MB) - szybsze testy
- enwik9 (1 GB) - pełny konkurs
- Fragment 10 MB - do szybkich eksperymentów

### Test na większym pliku:
```python
python compress_context.py  # edytuj input_file w test_multiple_orders()
```

## 📈 Plan rozwoju

### ✅ Ukończone:
1. Środowisko Python + baseline (zlib)
2. Arithmetic coder od podstaw
3. Model Order-0 (statystyka globalna)
4. Model Order-1 do Order-3 (konteksty n-gram)

### 🔄 W toku:
5. Test na większym fragmencie enwik9

### 📝 Planowane:
6. **Parser struktury Wikipedia:**
   - Wykrywanie nagłówków `== Sekcja ==`
   - Wydzielanie linków `[[Artykuł]]`
   - Parsowanie szablonów `{{Template|param=value}}`
   - Osobne kanały dla różnych typów treści

7. **Wielokanałowe modelowanie:**
   - Osobne modele Order-N dla każdego kanału
   - Model hierarchiczny (tytuł → sekcja → treść)
   - Cross-attention między kanałami

8. **Neural language model:**
   - Mały Transformer/RNN dla każdego kanału
   - Kwantyzacja wag (4-bit, 8-bit)
   - Destylacja z większego modelu

9. **Port do C++:**
   - Przepisanie do C++ (bez zależności)
   - Optymalizacja pod single-core CPU
   - Minimalizacja rozmiaru exe (zip compression)

10. **Hutter Prize submission:**
    - Spełnienie wszystkich wymagań
    - Dokumentacja
    - Submission package

## 🧠 Kluczowe insight'y

### Dlaczego Order-3 jest taki dobry?
- Przewiduje znak na podstawie 3 poprzednich znaków
- W tekście naturalnym (Wikipedia) kontekst 3-4 znaków daje ogromną informację
- Przykład: po "the" najczęściej jest spacja, po "qu" prawie zawsze "e"

### Dlaczego model jest duży na małym pliku?
- Model Order-3 potrzebuje przechować statystyki dla ~1400 kontekstów
- Na małym pliku (2 KB) to dominuje rozmiar
- Na enwik9 (1 GB) model będzie ~50 KB = 0.005% całości
- W finalnym exe model jest zip-owany, więc powtarzalne struktury się dobrze pakują

### Co dalej?
- Dla Wikipedii możemy wykorzystać jej **strukturę**:
  - Nagłówki są przewidywalne (`== Introduction ==`, `== History ==`)
  - Linki mają regularny format `[[Article|text]]`
  - Szablony `{{cite|...}}` też
- Zamiast jednego modelu na wszystko, zbudujemy **ekspertów** dla różnych części
- To jest "out of the box" approach, który może dać przewagę nad PAQ/cmix

## 📚 Zasoby

- [Hutter Prize oficjalna strona](http://prize.hutter1.net/)
- [Arithmetic coding - Wikipedia](https://en.wikipedia.org/wiki/Arithmetic_coding)
- [PPM compression](https://en.wikipedia.org/wiki/Prediction_by_partial_matching)
- [Current records](http://prize.hutter1.net/hfaq.htm#current)

## 📝 Notatki

### 2024-11-21
- Utworzono projekt
- Zaimplementowano arithmetic coder
- Osiągnięto 0.762 bity/bajt na Order-3 (80% lepsze niż zlib na małym pliku)

### 2024-11-22
- Przetestowano na 10 MB enwik8: **2.36 bity/bajt** (19.9% lepsze niż zlib)
- Projekcja na enwik9 (1 GB): ~281 MB vs 351 MB (zlib) = **70 MB oszczędności**
- Zbudowano parser struktury Wiki
- Analiza: 74% czysty tekst, 25.6% markup, ~9,300 linków/MB
- Strategia wielokanałowa potwierdzona jako obiecująca

---

**Status:** 🟢 Faza 1 ukończona - baseline działa lepiej niż zlib
**Następny milestone:** Implementacja wielokanałowego kompresora (osobne modele dla linków/nagłówków/tekstu)
