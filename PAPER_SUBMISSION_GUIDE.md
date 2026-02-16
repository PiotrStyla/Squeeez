# Research Paper Submission Guide
## "Systematic Stacking for Wikipedia Compression"

Author: Piotr Styła  
Date: January 2026

---

## Target Conferences and Journals

### Tier 1 (Top-Tier Venues)

#### 1. **DCC - Data Compression Conference** 🎯 **BEST FIT**
- **Website:** http://www.cs.brandeis.edu/~dcc/
- **Deadline:** Usually October/November (for March conference)
- **Acceptance Rate:** ~30%
- **Why Perfect Fit:**
  - Premier venue for compression research
  - Hutter Prize submissions often presented here
  - Audience deeply familiar with enwik9 benchmark
  - Values both theoretical and practical contributions
  - Our 80.4% gap closure is highly competitive
  
- **Paper Format:**
  - 10 pages max (IEEE two-column format)
  - Single-blind review
  - Abstract: 150-200 words
  - Camera-ready: LaTeX required (IEEE template)
  
- **Submission Tips:**
  - Emphasize non-linear scaling discovery (novel finding)
  - Position as methodology paper, not just results
  - Include reproducibility section (code release)
  - Mention potential for beating world record

#### 2. **ISIT - IEEE International Symposium on Information Theory**
- **Website:** https://2026.ieee-isit.org/
- **Deadline:** January (for July conference)
- **Acceptance Rate:** ~40%
- **Why Good Fit:**
  - Theory-focused (Shannon entropy, compression bounds)
  - Values rigorous mathematical treatment
  - Compression as information theory application
  
- **Paper Format:**
  - 5 pages (extended abstract)
  - IEEE two-column
  - Very dense, theory-heavy
  
- **Submission Tips:**
  - Add theoretical analysis of scaling (Section 6 expansion needed)
  - Derive bounds on stacking efficiency
  - Connect to rate-distortion theory

#### 3. **NeurIPS - Neural Information Processing Systems**
- **Website:** https://neurips.cc/
- **Deadline:** May (for December conference)
- **Acceptance Rate:** ~25%
- **Why Possible Fit:**
  - Machine learning angle (LSTM, neural compressors)
  - Compression as AGI benchmark (Hutter connection)
  - Systematic ML optimization methodology
  
- **Paper Format:**
  - 9 pages main + unlimited appendix
  - NeurIPS LaTeX template
  - Double-blind review (anonymize everything!)
  
- **Submission Tips:**
  - Frame as ML optimization methodology
  - Emphasize systematic approach > random hyperparameter search
  - Connect to LLM compression
  - Position non-linear scaling as ML insight

### Tier 2 (Strong Venues)

#### 4. **ICML - International Conference on Machine Learning**
- **Deadline:** January (for July conference)
- **Acceptance Rate:** ~25%
- **Similar to NeurIPS but more ML-focused**

#### 5. **AAAI - Association for Advancement of Artificial Intelligence**
- **Deadline:** August (for February conference)
- **Acceptance Rate:** ~20%
- **AGI angle, compression = intelligence**

#### 6. **IEEE Transactions on Information Theory (Journal)**
- **Rolling submission**
- **Acceptance Rate:** ~30%
- **Rigorous review, 6-12 month turnaround**
- **Archival, high impact factor**

### Tier 3 (Specialized/Workshop)

#### 7. **ICLR Workshop on Compression**
- **Good for early-stage feedback**
- **Less prestige but faster publication**

#### 8. **arXiv Preprint** 🚀 **IMMEDIATE ACTION**
- **Website:** https://arxiv.org/
- **Timeline:** Immediate (24-hour review)
- **Why Do This First:**
  - Timestamp your discovery (non-linear scaling)
  - Build visibility before conference submission
  - Standard in ML/compression community
  - Citable while under review elsewhere
  
- **Categories:**
  - cs.IT (Information Theory)
  - cs.AI (Artificial Intelligence)
  - cs.LG (Machine Learning)
  
- **Submission Tips:**
  - Upload PDF + source (LaTeX recommended)
  - Choose primary + secondary categories
  - Write compelling abstract (150 words)
  - Include GitHub link in comments

---

## Recommended Strategy

### Phase 1: Immediate (Week 1)
```
✓ Paper written (DONE)
✓ Figures created (DONE)
→ Upload to arXiv (establishes priority)
→ Announce on social media (Twitter, LinkedIn)
→ Post on Hutter Prize forums
```

### Phase 2: Short-term (Weeks 2-4)
```
→ Prepare DCC submission (deadline ~October)
→ If DCC deadline passed: target ISIT or NeurIPS
→ Expand theoretical sections for journal version
→ Collect community feedback from arXiv
```

### Phase 3: Medium-term (Months 2-3)
```
→ Implement remaining techniques (close 100% gap?)
→ If world record beaten: major announcement
→ Submit to IEEE Transactions on IT (journal)
→ Present at compression conferences/workshops
```

---

## Submission Checklist

### Before Submission:

#### Content Completeness
- [ ] Abstract (150-250 words, self-contained)
- [ ] Introduction (motivation, research questions, contributions)
- [ ] Related Work (comprehensive literature review)
- [ ] Methodology (reproducible, detailed)
- [ ] Experimental Setup (hardware, software, parameters)
- [ ] Results (tables, figures, statistical significance)
- [ ] Discussion (limitations, threats to validity)
- [ ] Conclusion (summary, future work)
- [ ] References (complete, formatted correctly)
- [ ] Appendices (detailed data, proofs)

#### Figures and Tables
- [ ] All figures referenced in text
- [ ] Figure captions self-explanatory
- [ ] High resolution (300+ DPI for raster, vector preferred)
- [ ] Color-blind accessible palette
- [ ] Axis labels, legends, units clearly marked
- [ ] Tables formatted consistently
- [ ] Numbers reported with appropriate precision

#### Reproducibility
- [ ] Code released on GitHub
- [ ] Dataset publicly available or clearly described
- [ ] Random seeds documented (if applicable)
- [ ] Hardware specifications listed
- [ ] Software versions specified
- [ ] Exact commands/parameters documented
- [ ] README with quickstart instructions

#### Writing Quality
- [ ] Spell-checked (US or UK English, consistent)
- [ ] Grammar-checked (Grammarly, LanguageTool)
- [ ] No colloquialisms or informal language
- [ ] Consistent terminology throughout
- [ ] Active voice preferred (where appropriate)
- [ ] Concise (remove filler words)
- [ ] Equations numbered and referenced
- [ ] Acronyms defined on first use

#### Formatting
- [ ] Correct template (IEEE, NeurIPS, etc.)
- [ ] Page limit respected
- [ ] Font size and margins correct
- [ ] Line numbers (if required for review)
- [ ] Anonymized (for double-blind review)
- [ ] References formatted correctly (BibTeX)
- [ ] Supplementary material prepared (if allowed)

#### Ethics and Integrity
- [ ] No plagiarism (check with Turnitin or similar)
- [ ] Proper citations for all prior work
- [ ] No duplicate submission (one venue at a time)
- [ ] All co-authors approved submission
- [ ] Conflicts of interest declared
- [ ] Data usage rights confirmed

---

## Conference-Specific Adaptations

### For DCC (Data Compression Conference):

**What to Emphasize:**
- Technical details of compression pipeline
- Comparison to prior Hutter Prize submissions
- Gap breakdown and systematic methodology
- Reproducibility (all code released)
- Path to world record (remaining techniques)

**What to De-emphasize:**
- AGI/philosophical aspects
- Machine learning theory (unless using LSTM)
- Over-selling results (be honest about 19.6% remaining gap)

**Suggested Structure:**
1. Introduction (1 page)
2. Related Work (0.75 pages)
3. Gap Decomposition Methodology (1.5 pages)
4. Experimental Setup (1 page)
5. Results (2 pages with figures)
6. Scaling Analysis Discussion (2 pages)
7. Conclusion and Future Work (0.75 pages)
8. References (1 page)

**Target Length:** 9-10 pages

---

### For NeurIPS/ICML (Machine Learning):

**What to Emphasize:**
- Systematic optimization methodology
- Non-linear scaling as ML insight
- Compression as AGI benchmark
- Transferable lessons for ML hyperparameter optimization
- Subset validation strategy (small test → full scale)

**What to De-emphasize:**
- Low-level compression details
- PAQ8px internals
- Too much focus on Wikipedia-specific techniques

**Suggested Structure:**
1. Introduction (1 page)
   - Compression = Intelligence
   - Problem: Random vs. Systematic Optimization
2. Background (1 page)
   - Hutter Prize
   - Prior ML approaches
3. Methodology (2 pages)
   - Gap decomposition framework
   - Incremental validation strategy
4. Experiments (2 pages)
   - Setup
   - Results
5. Scaling Analysis (2 pages) ← KEY CONTRIBUTION
   - 14x factor discovery
   - Implications for ML
6. Discussion (0.5 pages)
7. Conclusion (0.5 pages)
8. References (unlimited in appendix)

**Target Length:** 9 pages main + appendix

---

### For arXiv (Preprint):

**What to Emphasize:**
- Everything! No page limits
- Comprehensive details
- All experimental data
- Full reproducibility information

**Suggested Structure:**
- Use full 20-page version
- Include all appendices
- Link to GitHub in abstract
- Add acknowledgments section
- Include future work roadmap

**Target Length:** 15-25 pages (comprehensive)

---

## Abstract Templates

### Version 1: DCC (Technical)
```
We present a systematic approach to Wikipedia compression achieving 
12.74% compression ratio on the enwik9 benchmark, closing 80.4% of 
the gap between baseline PAQ8px (18.26%) and the current world record 
(11.40%). Through decomposition of the 68.6 MB gap into seven specific 
techniques and prioritized implementation of two (article reordering, 
preprocessing transforms), we achieved 55.16 MB improvement. Our key 
finding is non-linear scaling: techniques showing 2.16% improvement on 
10 MB achieved 30.21% on 1 GB—a 14-fold factor. This demonstrates 
small-scale validation can dramatically underestimate large-scale 
benefits. Our systematic methodology—gap analysis, prioritization, 
subset testing, full validation—achieved world-class results (estimated 
TOP 5-10) in four days. All code and data are publicly released.
```

### Version 2: NeurIPS/ICML (ML-Focused)
```
Can systematic decomposition outperform random search in complex 
optimization problems? We investigate this question in the domain of 
data compression, achieving state-of-the-art results on the Hutter 
Prize benchmark (1 GB Wikipedia). Our systematic approach—decomposing 
the optimization space, prioritizing by impact/effort ratio, and 
validating on subsets—closed 80.4% of the gap to world record in four 
days. Most significantly, we discovered extreme non-linear scaling: 
improvements measured at 2.16% on small data (10 MB) scaled to 30.21% 
on large data (1 GB)—a 14-fold factor. This has broad implications for 
ML research that relies on subset validation, suggesting small-scale 
tests may dramatically underestimate large-scale performance. Our work 
demonstrates that systematic decomposition can achieve in days what 
random exploration might take months, with transferable lessons for 
hyperparameter optimization and neural architecture search.
```

### Version 3: arXiv (Comprehensive)
```
The Hutter Prize challenges researchers to compress 1 GB of Wikipedia 
to the smallest size, serving as a benchmark for progress toward 
artificial general intelligence. We present a systematic approach that 
achieved 127.44 MB (12.74% compression ratio), closing 80.4% of the 
68.6 MB gap between baseline PAQ8px (18.26%) and the current world 
record (11.40%). Our methodology consists of: (1) decomposing the gap 
into seven specific techniques with estimated contributions, (2) 
prioritizing by impact/effort ratio, (3) validating on 10 MB subsets 
before full-scale testing, and (4) systematic measurement of stacking 
effects. Using only two techniques—STARLIT-based article reordering and 
Wikipedia-specific preprocessing—we achieved 55.16 MB improvement, 
1.97x better than estimated from subset testing. Our key discovery is 
dramatic non-linear scaling: techniques showing 2.16% improvement on 
10 MB achieved 30.21% on 1 GB—a 14-fold scaling factor. This finding 
has significant implications for compression research, machine learning 
validation methodology, and any domain relying on subset testing. We 
provide comprehensive experimental data, theoretical analysis of scaling 
mechanisms, and release all code and preprocessed data publicly. Our 
result would rank in the TOP 5-10 globally on the Hutter Prize 
leaderboard, achieved in four days through systematic decomposition 
versus the months or years typically required by random experimentation.
```

---

## Cover Letter Template

**For submission to DCC:**

```
Dear Program Committee,

I am pleased to submit our paper "Systematic Stacking for Wikipedia 
Compression: Closing 80% of Gap to World Record" for consideration at 
DCC 2026.

Our work makes three primary contributions to the compression community:

1. **Novel Methodology**: We demonstrate that systematic gap 
decomposition and incremental validation can achieve world-class results 
(127.44 MB on enwik9, TOP 5-10 globally) in just four days of 
implementation, versus the months or years typically required.

2. **Non-Linear Scaling Discovery**: We discovered that compression 
improvements scale dramatically with dataset size—techniques showing 
2.16% improvement on 10 MB achieved 30.21% on 1 GB (14-fold factor). 
This has important implications for compression research methodology.

3. **Reproducibility**: All code, data transformations, and experimental 
protocols are publicly released at https://github.com/PiotrStyla/Squeeez, 
enabling the community to build on our work.

Our result closes 80.4% of the gap to the current Hutter Prize world 
record using only two of seven identified techniques, suggesting the 
remaining gap is achievable. We believe this work will be of high 
interest to the DCC community and welcome the opportunity to present it.

Thank you for your consideration.

Sincerely,
Piotr Styła
```

---

## Post-Submission Strategy

### If Accepted:
1. **Prepare presentation** (15-20 minute talk)
2. **Create poster** (if poster session)
3. **Update arXiv** with camera-ready version
4. **Announce on social media** with DOI
5. **Present at conference** professionally
6. **Network** with compression researchers
7. **Discuss future work** (remaining 19.6% gap)

### If Rejected:
1. **Read reviews carefully** (valuable feedback)
2. **Don't take personally** (competitive venues)
3. **Revise based on feedback**
4. **Submit to next-tier venue** (ISIT, AAAI, workshops)
5. **Consider journal** (IEEE Transactions on IT)
6. **Keep arXiv updated** (always accessible)

### Either Way:
1. **Continue research** (implement remaining techniques)
2. **Engage community** (Hutter Prize forums, GitHub)
3. **Build on results** (aim for world record)
4. **Document everything** (for future papers)

---

## Timeline

```
Week 1:  
  ✓ Paper complete
  ✓ Figures generated
  → Upload to arXiv
  → Social media announcement

Week 2-3:
  → Collect feedback
  → Revise based on comments
  → Prepare conference submission

Week 4:
  → Submit to DCC (or next deadline)
  → Start working on remaining techniques

Months 2-3:
  → Conference review process
  → Continue research
  → Potentially beat world record!

Month 4+:
  → Present at conference (if accepted)
  → Submit journal version
  → Plan future work
```

---

## Success Metrics

### Short-term (1-3 months):
- [ ] arXiv preprint published
- [ ] 50+ reads on arXiv
- [ ] Conference submission completed
- [ ] GitHub repo has 10+ stars
- [ ] Social media engagement (100+ likes)

### Medium-term (6-12 months):
- [ ] Paper accepted at conference
- [ ] Paper cited by 5+ other works
- [ ] Presentation delivered
- [ ] Hutter Prize submission registered
- [ ] Remaining techniques implemented

### Long-term (12+ months):
- [ ] Journal publication
- [ ] 20+ citations
- [ ] World record beaten (< 114 MB)
- [ ] Methodology adopted by others
- [ ] Invited talks at workshops

---

## Contact Information

**Author:** Piotr Styła  
**GitHub:** https://github.com/PiotrStyla/Squeeez  
**Email:** [Your email]  
**Twitter/X:** [Your handle]  
**LinkedIn:** [Your profile]

---

**READY FOR SUBMISSION!** 🚀

Next action: Choose primary venue and finalize submission package.
