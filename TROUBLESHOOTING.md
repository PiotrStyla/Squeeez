# Troubleshooting - Jak reagować gdy coś nie działa

## 🔴 Problem: Proces się zawiesił / wisi bez zmian

### Objawy:
- Komenda pokazuje "Thought for Xs" bez zmian przez > 2 minuty
- Brak progress bara lub stuck na jednym kroku
- Brak aktywności na dysku/CPU

### Co robić:

1. **Natychmiast zatrzymaj proces:**
   - Kliknij czerwony kwadrat ⏹️ obok komendy w terminalu
   - Lub napisz do mnie: "zatrzymaj to" / "zabij proces" / "anuluj"

2. **NIE CZEKAJ godzinami** - jeśli coś trwa > 5 minut bez progress bara, to błąd

3. **Normalne czasy wykonania:**
   - Kompresja 10 MB: 3-5 minut
   - Analiza 1 MB: < 10 sekund
   - Tokenizacja: < 1 sekunda/MB
   
   Jeśli zajmuje 10x dłużej → coś jest nie tak

### Typowe przyczyny:

- **Regex catastrophic backtracking** (jak w `analyze_enwik.py`)
- Nieskończona pętla w kodzie
- Brak pamięci (Windows zaczyna swapować)
- Deadlock w wielowątkowym kodzie

### Rozwiązanie:

Zawsze możesz:
1. Przerwać proces (bezpieczne)
2. Napisać "coś się zepsuło" - naprawię i uruchomię lepszą wersję
3. Sprawdzić Task Manager czy `python.exe` rzeczywiście pracuje (CPU/Memory)

---

## ⚠️ Problem: Brak progress bara

Jeśli widzisz komunikat typu:
```
[2] Kodowanie...
```

Bez żadnych aktualizacji (%) przez > 30 sekund → napisz "dodaj progress bar"

---

## 💾 Problem: Brak miejsca na dysku

### Objawy:
```
OSError: [Errno 28] No space left on device
```

### Rozwiązanie:
1. Usuń niepotrzebne pliki z `C:\HutterLab\data\`
2. Możesz usunąć:
   - `enwik8.zip` (po rozpakowaniu)
   - `*.ctx` (archiwum testowe)
   - `*_restored.txt` (zweryfikowane kopie)

---

## 🐌 Problem: Bardzo wolne wykonanie

### Order-3 na 10 MB trwa > 10 minut?

**Normalne czasy:**
- Trening: 20-30 sekund
- Kodowanie: 3-5 minut
- **Całość: 4-6 minut**

Jeśli > 10 minut:
- Sprawdź Task Manager → czy inne programy nie zjadają CPU
- Zamknij przeglądarkę / inne ciężkie aplikacje
- Restart IDE może pomóc

---

## 🔧 Szybkie komendy ratunkowe

### Zabij wszystkie python procesy:
```powershell
taskkill /F /IM python.exe
```

### Sprawdź ile zajmuje katalog:
```powershell
Get-ChildItem C:\HutterLab -Recurse | Measure-Object -Property Length -Sum
```

### Wyczyść archiwum testowe:
```powershell
Remove-Item C:\HutterLab\data\*.ctx
Remove-Item C:\HutterLab\data\*_restored.txt
```

---

## ✅ Zasada ogólna:

**Jeśli cokolwiek nie działa jak oczekiwano - przerwij i zapytaj.**

Lepiej 30 sekund straty czasu na restart niż kilka godzin czekania na zawieszone zadanie.

---

**Ostatnia aktualizacja:** 2024-11-22  
**Pytania?** Po prostu napisz co się dzieje, naprawię to.
