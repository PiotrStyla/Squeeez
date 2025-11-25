# 🔨 PAQ8 COMPILATION GUIDE

**Status:** Code integration complete! Ready for compilation.

---

## ✅ WHAT WE'VE DONE

### Files Modified:
```
✅ paq8px/Models.hpp
   - Added includes for WikipediaLinkModel and CascadingContextModel
   - Added accessor method declarations

✅ paq8px/Models.cpp
   - Added accessor implementations
   - Allocated memory (shared->mem * 4 and * 8)

✅ paq8px/model/ContextModelText.cpp
   - Added MIXERINPUTS counts
   - Added MIXERCONTEXTS counts
   - Added MIXERCONTEXTSETS counts
   - Added model calls in p() function

✅ paq8px/model/WikipediaLinkModel.hpp
   - Complete implementation (150 lines)
   - Detects [[Wikipedia links]]
   - Order-6 prediction

✅ paq8px/model/CascadingContextModel.hpp
   - Complete implementation (180 lines)
   - Cascading fallback Order-5→4→3→2→1
   - 5 context maps
```

---

## 🔨 COMPILATION OPTIONS

### Option 1: Visual Studio (Recommended on Windows)

**Step 1: Open Visual Studio Developer Command Prompt**
```
Start Menu → Visual Studio 2022 → Developer Command Prompt
```

**Step 2: Navigate to project**
```cmd
cd C:\HutterLab\paq8px
```

**Step 3: Build with MSBuild**
```cmd
msbuild paq8px.sln /p:Configuration=Release /p:Platform=x64
```

Or open `paq8px.sln` in Visual Studio IDE and build from there.

---

### Option 2: MinGW-w64 (If installed)

**Step 1: Install MinGW-w64**
```
Download from: https://www.mingw-w64.org/
Or use MSYS2: pacman -S mingw-w64-x86_64-gcc
```

**Step 2: Add to PATH**
```
Add C:\msys64\mingw64\bin to system PATH
```

**Step 3: Compile**
```bash
cd C:\HutterLab\paq8px
g++ -O3 -march=native -std=c++17 paq8px.cpp -o paq8px-wiki.exe
```

---

### Option 3: CMake (Cross-platform)

**Step 1: Install CMake**
```
Download from: https://cmake.org/download/
Or: winget install Kitware.CMake
```

**Step 2: Build**
```cmd
cd C:\HutterLab\paq8px
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

---

## 🐛 EXPECTED COMPILATION ISSUES

### Issue 1: Missing ModelStats Parameter

**Error:**
```
error: no matching constructor for WikipediaLinkModel
```

**Fix:**
Check if ModelStats* is needed. If yes, modify Models.cpp:
```cpp
auto Models::wikipediaLinkModel() -> WikipediaLinkModel & {
  static ModelStats stats;
  static WikipediaLinkModel instance {shared, &stats, shared->mem * 4};
  return instance;
}
```

---

### Issue 2: INJECT_SHARED Macros

**Error:**
```
error: 'INJECT_SHARED_buf' was not declared
```

**Fix:**
These are PAQ8 macros. Should be defined in Shared.hpp.
Check that our models include correct headers.

---

### Issue 3: ContextMap2 Interface

**Error:**
```
error: no matching function for 'ContextMap2::set'
```

**Fix:**
Check ContextMap2 interface in ContextMap2.hpp.
Adjust our model's usage to match.

---

## ✅ TESTING PLAN AFTER SUCCESSFUL COMPILATION

### Test 1: Sanity Check
```cmd
paq8px-wiki.exe -h
# Should show help without crashing
```

### Test 2: Small File
```cmd
echo "Test [[Wikipedia]] links" > test.txt
paq8px-wiki.exe -5 test.paq8 test.txt
# Should compress without errors
```

### Test 3: Decompress
```cmd
paq8px-wiki.exe -d test.txt.decompressed test.paq8
fc test.txt test.txt.decompressed
# Should be identical
```

### Test 4: Enwik8 Test (100 MB)
```cmd
paq8px-wiki.exe -8 enwik8.paq8 ..\data\enwik8
# Compare size with baseline PAQ8px
# Should see improvement!
```

---

## 📊 EXPECTED RESULTS

### Baseline PAQ8px on enwik8:
```
~11-12 MB compressed
```

### Our integrated version:
```
Target: 8-9 MB (25% improvement)
Minimum: 10-11 MB (15% improvement)
```

---

## 🚀 NEXT STEPS

1. **Tomorrow Morning:**
   - Set up Visual Studio environment
   - Attempt compilation
   - Debug any compilation errors

2. **Tomorrow Afternoon:**
   - Get successful build
   - Test on small files
   - Test on enwik8

3. **This Week:**
   - Measure improvement
   - Tune parameters if needed
   - Test on enwik9 (1 GB)

4. **Next Week:**
   - Final optimization
   - Prepare submission
   - Submit to Hutter Prize! 🏆

---

## 💡 DEBUGGING TIPS

### If compilation fails:
1. Read error messages carefully
2. Check if headers are included correctly
3. Verify constructor parameters match
4. Look at similar models for examples
5. Check PAQ8px documentation

### If it crashes at runtime:
1. Run under debugger
2. Check memory allocation sizes
3. Verify array bounds
4. Add debug prints
5. Test models separately

### If no improvement:
1. Verify models are being called
2. Check mixer weights
3. Add statistics to see model usage
4. Compare with baseline on same data
5. Profile to find bottlenecks

---

## 📚 RESOURCES

### PAQ8px Documentation:
- README.md: Overview
- DOC: Technical details
- CHANGELOG: Version history

### Online Resources:
- PAQ8 Wikipedia page
- Hutter Prize website
- Matt Mahoney's data compression page
- PAQ8 source code comments

### Our Documentation:
- paq8_integration_guide.md: Strategy
- OUR_INTEGRATION.md: Step-by-step
- This file: Compilation guide

---

## 🎯 SUCCESS CRITERIA

### Minimum Success:
- ✅ Compiles without errors
- ✅ Runs without crashes
- ✅ Compresses/decompresses correctly
- ✅ Shows any improvement on enwik8

### Target Success:
- ✅ 15-20% improvement on enwik8
- ✅ Scales to enwik9
- ✅ Beats world record! 🏆

---

**Status: Code ready, compilation next! 🚀**
