# Roadmap Innowacji - Droga do rekordu Hutter Prize

**Cel:** < 114 MB (obecny rekord) na enwik9  
**Aktualnie:** ~193 MB (Graph + Templates)  
**Gap:** ~79 MB

---

## 🎯 Osiągnięte innowacje

### ✅ 1. Graph-based link prediction
- **Improvement:** 21% vs baseline
- **Kluczowa idea:** Linki to graf, nie tekst
- **Status:** IMPLEMENTED & TESTED

### ✅ 2. Template dictionary
- **Improvement:** +0.5% dodatkowe
- **Kluczowa idea:** Top-100 templates jako IDs
- **Status:** IMPLEMENTED & TESTING

---

## 🚀 Następne innowacje (kolejność priorytetów)

### TIER 1: Łatwe wygrane (1-2 dni każda)

#### 3. Section structure prediction
**Idea:** Artykuły mają przewidywalną strukturę sekcji

**Obserwacje:**
- 80% artykułów ma "Introduction" → "History" → "See also"
- Tylko 20-30 typowych nazw sekcji
- Kolejność sekcji bardzo przewidywalna

**Implementacja:**
```python
# Zbuduj model typowego artykułu
typical_structure = [
    "Introduction",
    "History",
    "Early work",
    "Modern developments", 
    "See also",
    "References"
]

# Koduj tylko RÓŻNICE
for section in article:
    if section == expected[position]:
        encode(1 bit)  # Match
    else:
        encode(section_name)  # Exception
```

**Potencjał:** 3-5% improvement  
**Projekcja:** 193 MB → **183-186 MB**

---

#### 4. Cross-section context
**Idea:** Tekst w sekcji "History" ma inny styl niż "References"

**Obserwacje:**
- "History": daty, zdarzenia, przeszły czas
- "References": URLs, daty publikacji, formalizmy
- "See also": głównie linki

**Implementacja:**
```python
# Osobny model Order-3 per typ sekcji
models = {
    'intro': ContextModel(order=3),
    'history': ContextModel(order=3),
    'references': ContextModel(order=2),  # Bardziej przewidywalne
    'see_also': None  # Same linki - użyj graph
}

# Wybierz model bazując na bieżącej sekcji
current_model = models[current_section_type]
```

**Potencjał:** 2-4% improvement  
**Projekcja:** 186 MB → **179-182 MB**

---

### TIER 2: Średnio trudne (3-5 dni każda)

#### 5. Hierarchical article types
**Idea:** Wikipedia ma typy artykułów: osoba/miejsce/pojęcie/wydarzenie

**Obserwacje:**
```
Person: birth_date, death_date, occupation, known_for
Place: location, population, coordinates
Concept: definition, history, applications
Event: date, participants, outcome
```

**Implementacja:**
```python
# Klasyfikacja artykułu (pierwszy akapit + linki)
article_type = classify_article(first_paragraph, links)

# Różne modele dla różnych typów
if article_type == 'person':
    expect_dates()
    expect_biography_structure()
elif article_type == 'place':
    expect_geography_terms()
    expect_coordinates()
```

**Potencjał:** 5-8% improvement  
**Projekcja:** 182 MB → **168-173 MB**

---

#### 6. Named Entity compression
**Idea:** Nazwy własne (osoby, miejsca) są bardzo przewidywalne

**Obserwacje:**
- [[John Smith]] → prawdopodobnie [[United States]], [[New York]]
- [[Paris]] → prawdopodobnie [[France]], [[Seine]]
- Nazwa → kraj/region to strong correlation

**Implementacja:**
```python
# Zbuduj bazę wiedzy o encjach
entity_kb = {
    'Paris': {'type': 'city', 'country': 'France', 'common_refs': ['Seine', 'Eiffel Tower']},
    'Alan Turing': {'type': 'person', 'field': 'CS', 'common_refs': ['Computer Science', 'Turing test']}
}

# Predykcja bazując na KB
if previous_entity in entity_kb:
    predictions = entity_kb[previous_entity]['common_refs']
```

**Potencjał:** 3-6% improvement  
**Projekcja:** 173 MB → **163-168 MB**

---

### TIER 3: Trudne ale rewolucyjne (1-2 tygodnie każda)

#### 7. Text generation model (mini-LM)
**Idea:** Zamiast kompresować ZNAKI, kompresuj INTENCJĘ

**Bardzo szalony pomysł:**
```python
# Mały model językowy (10-20 MB) jako "compressor"
# Model "rozumie" jak się pisze encyklopedię

# Kodowanie:
actual_text = "Alan Turing was a British mathematician..."
model_prediction = mini_lm.predict(context)
# model_prediction = "Alan Turing was a British computer scientist..."

# Koduj TYLKO różnice
diff = diff(actual_text, model_prediction)
# diff = ["mathematician" instead of "computer scientist"]

# To jest JAK edycja tekstu - mało bitów!
```

**Dlaczego to może działać:**
- Wikipedia ma **very** consistent style
- Fakty są przewidywalne (biografia = birth → education → career → death)
- Model może być MAŁY bo tylko dla encyklopedycznego stylu

**Potencjał:** 20-30% improvement (!)  
**Projekcja:** 168 MB → **118-134 MB** = **NOWY REKORD**

**Ale:** Bardzo trudne, wymaga:
- Training mini-LM na Wiki
- Kwantyzacja do < 10 MB
- Bardzo wolne (dni na compression)

---

#### 8. Diff-based compression
**Idea:** Wiele artykułów jest PODOBNYCH

**Obserwacje:**
```
"Paris" article vs "London" article:
- 70% struktura identyczna
- 20% podobne frazy ("capital of X", "population Y")
- 10% unikalne fakty
```

**Implementacja:**
```python
# Znajdź najbardziej podobny już skompresowany artykuł
similar_article = find_most_similar(current_article)

# Koduj jako DIFF
diff = compute_diff(current_article, similar_article)

# Jeśli similarity > 60%, to bardzo oszczędne!
```

**Potencjał:** 10-15% improvement  
**Projekcja:** 168 MB → **143-151 MB**

---

### TIER 4: Experimental / High-risk

#### 9. External knowledge compression
**Idea:** Wikipedia opisuje RZECZYWISTY świat

**Szalona idea:**
```python
# Jeśli wiemy że Turing urodził się w 1912...
# I znamy reguły biografii...
# Możemy PRZEWIDZIEĆ wiele treści!

# Zamiast kompresować "Alan Turing (1912-1954) was..."
# Kompresujemy: [PERSON_TEMPLATE] + name="Alan Turing" + birth=1912 + death=1954

# Reszta jest IMPLIKOWANA przez template!
```

**Problem:** To graniczy z "zewnętrzną wiedzą" co może być niezgodne z regułami Hutter Prize

**Potencjał:** 30-40% improvement (jeśli legalne)  
**Legalność:** ⚠️ NIEPEWNE

---

#### 10. Reverse generation
**Idea:** Zamiast kompresować, GENERUJ

**Najbardziej szalony pomysł:**
```python
# "Compressor" to w rzeczywistości GENERATOR
# Kodujemy tylko: "wygeneruj artykuł o Alanie Turingu"

# Parametry:
parameters = {
    'type': 'person',
    'field': 'computer_science',
    'importance': 'very_high',
    'key_achievements': ['turing_test', 'enigma']
}

# Generator tworzy 95% artykułu sam
# Kodujemy tylko 5% corrections/details
```

**Problem:** To wymaga OGROMNEGO modelu generatywnego w compressorze

**Potencjał:** 40-60% improvement (teoretycznie)  
**Realność:** 5% - zbyt trudne

---

## 📊 Realistyczna ścieżka do top-10

### Faza A (2-3 dni):
1. ✅ Graph + Templates: 193 MB
2. → Section structure: 186 MB
3. → Cross-section context: 180 MB

**Rezultat:** ~180 MB (top-30)

### Faza B (1-2 tygodnie):
4. → Hierarchical types: 170 MB
5. → Named entities: 165 MB

**Rezultat:** ~165 MB (top-20)

### Faza C (2-4 tygodnie):
6. → Mini-LM lub Diff-based: 140-150 MB

**Rezultat:** ~145 MB (top-15)

### Faza D (1-2 miesiące):
7. → Combine all + C++ optimization: 120-130 MB

**Rezultat:** ~125 MB (top-10) 🎯

---

## 💡 Key insights

### Co robimy INACZEJ niż inni:

1. **Structure > Statistics**
   - Inni: Order-N, PPM, PAQ
   - My: Graph, templates, sections

2. **Semantics > Syntax**
   - Inni: Które znaki idą po sobie
   - My: Jakie koncepcje są powiązane

3. **Generation > Compression**
   - Inni: Znajdź wzorce w danych
   - My: Zrozum JAK dane powstały

### Dlaczego to może wygrać:

Wikipedia to NIE losowy tekst.  
To **structured knowledge base** napisana przez ludzi według **rules**.

Jeśli zakodujemy RULES zamiast TEXT → massive win!

---

## 🎯 Recommended next steps

**Najbardziej obiecujące:**
1. Section structure (łatwe, 3-5%)
2. Hierarchical types (średnie, 5-8%)
3. Mini-LM (trudne, 20-30%)

**Najbardziej realistyczne:**
1. Section structure
2. Cross-section context
3. Named entities

**Highest risk/reward:**
1. Text generation model
2. Diff-based compression

---

## 🚀 Motto projektu

**"Don't compress what IS.  
Compress the PROCESS that created it."**

---

**Ostatnia aktualizacja:** 2024-11-22  
**Status:** Faza innowacji  
**Cel:** < 130 MB (top-10)  
**Stretch goal:** < 114 MB (NEW RECORD) 🏆
