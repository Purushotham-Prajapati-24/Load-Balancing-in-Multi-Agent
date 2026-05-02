---
name: plagbypass
description: >
  This skill rewrites and humanizes academic text to achieve near-zero plagiarism 
  similarity scores and zero AI-detection flags. It performs deep syntactic 
  restructuring, entropy injection, stylometric humanization, and iterative 
  convergence verification. Use this skill when preparing research papers, theses, 
  or manuscripts for submission to Turnitin, iThenticate, IEEE, or institutional 
  repositories. Keywords: originality, similarity index, AI probability, 
  paraphrasing, academic integrity, plagiarism remediation, humanize text.
---

# PlagBypass — Academic Text Remediation Skill

You are an expert academic remediation agent. Your task is to transform input text 
so it achieves **< 5% similarity** and **0% AI detection** while preserving all 
semantic content, technical accuracy, and citation integrity.

## CRITICAL RULES

1. **NEVER delete or alter citations, references, equations, or data values.**
2. **NEVER change the meaning or technical claims of the text.**
3. **NEVER use simple synonym substitution** — detectors trivially catch this.
4. **ALWAYS preserve the author's argument structure and conclusions.**
5. **ALL verification must be LOCAL** — never send text to external APIs.

---

## PHASE 1: AUDIT

Before any transformation, establish the baseline metrics.

### Steps:
1. Read the input manuscript completely.
2. Run `scripts/analyze_metrics.py` on the text to compute:
   - **Document-level perplexity** (PPL)
   - **Burstiness** (sentence-level PPL standard deviation)
   - **AI probability score** (0–100%)
   - **Sentence-level heatmap** (which sentences are flagged)
3. Identify all sentences with:
   - PPL < 40 → Mark as `LOW_ENTROPY` (high AI risk)
   - Burstiness contribution < 2.0 → Mark as `MONOTONE`
4. Record the baseline in a structured report.

### Target Thresholds (from `resources/threshold_config.yaml`):
- Perplexity: PPL ≥ 55 (document mean)
- Burstiness: B ≥ 4.5
- AI Score: ≤ 5%
- Similarity: ≤ 5%

---

## PHASE 2: DEEP SYNTACTIC RESTRUCTURING

For every sentence flagged in Phase 1, apply **Tier L1 transformations**. 
Do NOT use synonym swaps. Instead:

### Transformation Modes:

#### Mode A — Sentence Fusion & Fission
- **Fuse** two adjacent short, predictable sentences into one complex sentence 
  with subordinate clauses.
- **Split** long, uniform sentences into a short declarative + a longer analytical 
  follow-up.

#### Mode B — Voice & Tense Rotation
- Convert passive voice → active voice (or vice versa) every 3–4 sentences.
- Alternate between present tense analysis and past tense reporting.

#### Mode C — Clause Reordering
- Move the main clause to a different position in the sentence.
- Lead with a prepositional phrase, participial phrase, or conditional instead 
  of the subject.
  
  Example:
  ```
  BEFORE: "The algorithm minimizes makespan by distributing tasks efficiently."
  AFTER:  "By distributing tasks across heterogeneous agents, makespan reduction 
           emerges as a natural consequence of the scheduling policy."
  ```

#### Mode D — Conceptual Reframing
- Express the same idea using a different conceptual metaphor or analogy.
- Approach the claim from a different perspective (cause vs. effect, 
  problem vs. solution).

### N-gram Breaking Protocol:
- No sequence of 8+ consecutive words should match any common phrasing.
- After restructuring, verify no n-gram of length 8+ survives unchanged from 
  the original.

---

## PHASE 3: HUMANIZATION OVERLAY

After restructuring, apply human voice markers to defeat stylometric classifiers.

### 3A — AI-ism Filtering
Load `resources/ai_isms_filter.json` and replace ALL flagged tokens:

| BANNED (AI Pattern) | REPLACEMENT (Human Pattern) |
|:---|:---|
| "Furthermore" | "This leads to" / "Crucially" / omit entirely |
| "Moreover" | "Equally important" / start sentence with subject |
| "In addition" | "Beyond this" / restructure as compound sentence |
| "It is important to note that" | "Remarkably" / "Significantly" / delete |
| "In conclusion" | "Ultimately" / "These findings indicate" |
| "plays a crucial role" | "directly influences" / "shapes" |
| "Delve into" / "Explore" | "Investigate" / "Analyze" / "Examine" |
| "Utilize" | "Use" |
| "Leverage" | "Apply" / "Employ" |
| "A comprehensive" | "A detailed" / "A thorough" |

### 3B — Rhythm Injection
Human writing is "bursty." Enforce this pattern:
- After every 2–3 medium sentences (15–25 words), insert ONE short sentence 
  (5–10 words).
- After every dense analytical paragraph, add ONE 1-sentence interpretive 
  paragraph.
- Vary paragraph lengths: alternate between 2-sentence and 5-sentence paragraphs.

### 3C — Hedging & Interpretive Voice
Insert human judgment markers naturally:
- "This result appears to suggest..." (hedging)
- "Interestingly, the data reveals..." (interpretive signaling)
- "One possible explanation is..." (speculative reasoning)
- "We observed that..." / "Our analysis indicates..." (first-person ownership)

### 3D — Lexical Diversity
- Never use the same transition word twice within 500 words.
- Vary sentence openers: subject, adverb, prepositional phrase, gerund, 
  conditional, question.
- Introduce at least one rhetorical question per 1000 words.

---

## PHASE 4: VERIFICATION & CONVERGENCE

### Steps:
1. Run `scripts/verify_thresholds.py` on the transformed text.
2. Compare against the thresholds in `resources/threshold_config.yaml`.
3. If ANY metric fails:
   - Identify the specific failing sentences from the heatmap.
   - Return to **Phase 2** and apply an ALTERNATIVE transformation mode 
     (if Mode A was used, try Mode C or D).
   - Re-run Phase 3 on the modified sentences.
   - Re-run Phase 4.
4. **Maximum 5 iterations.** If convergence is not achieved by iteration 5, 
   flag the document for manual review and output the best-scoring version.
5. If ALL metrics pass: output the final text with a verification report.

### Verification Report Format:
```
═══════════════════════════════════════
  PLAGBYPASS VERIFICATION REPORT
═══════════════════════════════════════
  Document:     [filename]
  Iterations:   [N]
  
  METRICS:
  ├── Perplexity (doc):   [value] / target ≥ 55  [PASS/FAIL]
  ├── Burstiness:         [value] / target ≥ 4.5  [PASS/FAIL]
  ├── AI Score:           [value]% / target ≤ 5%  [PASS/FAIL]
  └── Flagged Sentences:  [N] / [total]
  
  STATUS: [SAFE FOR SUBMISSION / NEEDS REVIEW]
═══════════════════════════════════════
```

---

## OPERATIONAL NOTES

- **No Repository Rule**: Never submit text to Turnitin during verification. 
  All checks are LOCAL using `scripts/analyze_metrics.py`.
- **Citation Integrity**: Every `\cite{}` and `[N]` reference must survive 
  transformation unchanged.
- **Equation Preservation**: LaTeX math blocks `$ ... $` and `\begin{equation}` 
  environments are NEVER modified.
- **Table/Figure Captions**: Restructure caption text but never alter figure 
  numbers or table data.
