#!/usr/bin/env python3
"""
analyze_metrics.py — Local perplexity, burstiness, and AI-detection scorer.

Computes per-sentence metrics using lightweight models that run entirely 
on-device. NO text is sent to external APIs.

Usage:
    python analyze_metrics.py <input_file> [--format json|text] [--model gpt2]
"""

import sys
import re
import json
import math
import argparse
from pathlib import Path

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# ─── Sentence Splitter ─────────────────────────────────────────────────────
def split_into_sentences(text: str) -> list[str]:
    """
    Rule-based sentence splitter that handles academic abbreviations,
    decimal numbers, and common edge cases without external dependencies.
    """
    # Protect common abbreviations
    abbreviations = [
        'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Jr.', 'Sr.',
        'Inc.', 'Ltd.', 'Corp.', 'vs.', 'etc.', 'i.e.', 'e.g.',
        'Fig.', 'Eq.', 'Ref.', 'Vol.', 'No.', 'pp.', 'ed.',
        'et al.', 'approx.', 'min.', 'max.', 'avg.',
    ]
    protected = text
    placeholders = {}
    for i, abbr in enumerate(abbreviations):
        placeholder = f"__ABBR{i}__"
        placeholders[placeholder] = abbr
        protected = protected.replace(abbr, placeholder)

    # Protect decimal numbers (e.g., 3.14)
    protected = re.sub(r'(\d)\.(\d)', r'\1__DOT__\2', protected)

    # Split on sentence-ending punctuation
    raw_sentences = re.split(r'(?<=[.!?])\s+', protected)

    # Restore placeholders
    sentences = []
    for sent in raw_sentences:
        for placeholder, original in placeholders.items():
            sent = sent.replace(placeholder, original)
        sent = sent.replace('__DOT__', '.')
        sent = sent.strip()
        if len(sent) > 10:  # Skip fragments
            sentences.append(sent)

    return sentences


# ─── Lightweight Perplexity (No GPU required) ──────────────────────────────
def compute_char_entropy(text: str) -> float:
    """
    Character-level entropy as a fast proxy for perplexity.
    Works without any ML model. Higher entropy ≈ higher perplexity.
    """
    if not text:
        return 0.0
    freq = {}
    for ch in text.lower():
        freq[ch] = freq.get(ch, 0) + 1
    total = len(text)
    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def compute_word_entropy(text: str) -> float:
    """
    Word-level entropy. Uses unigram distribution within the text itself.
    Higher values indicate more varied vocabulary (human-like).
    """
    words = re.findall(r'\b[a-z]+\b', text.lower())
    if not words:
        return 0.0
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    total = len(words)
    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def estimate_perplexity(sentence: str) -> float:
    """
    Estimate perplexity using a combination of:
    1. Character entropy (structural complexity)
    2. Word entropy (vocabulary diversity)
    3. Sentence length factor
    4. Rare word ratio
    
    This is a heuristic proxy that correlates with true model-based PPL
    but requires NO GPU or ML model download.
    """
    char_ent = compute_char_entropy(sentence)
    word_ent = compute_word_entropy(sentence)

    words = re.findall(r'\b[a-z]+\b', sentence.lower())
    word_count = len(words)

    # Longer sentences tend to have higher perplexity
    length_factor = min(word_count / 15.0, 2.0)

    # Rare words (long words) increase perplexity
    rare_ratio = sum(1 for w in words if len(w) > 8) / max(word_count, 1)

    # Composite PPL estimate (calibrated to match GPT-2 PPL scale roughly)
    ppl = (char_ent * 8.0 + word_ent * 12.0) * length_factor * (1 + rare_ratio * 2)
    return max(ppl, 5.0)


# ─── Model-Based PPL (optional, if lmppl is installed) ─────────────────────
def compute_model_perplexity(sentences: list[str], model_name: str = 'gpt2') -> list[float]:
    """
    Use the lmppl library for true model-based perplexity scoring.
    Falls back to heuristic if lmppl is not installed.
    """
    try:
        import lmppl
        scorer = lmppl.LM(model_name)
        return list(scorer.get_perplexity(sentences))
    except ImportError:
        print("[INFO] lmppl not installed. Using heuristic PPL estimator.", file=sys.stderr)
        return [estimate_perplexity(s) for s in sentences]
    except Exception as e:
        print(f"[WARN] Model loading failed ({e}). Using heuristic.", file=sys.stderr)
        return [estimate_perplexity(s) for s in sentences]


# ─── AI-ism Detection ──────────────────────────────────────────────────────
AI_ISM_PATTERNS = [
    r'\bfurthermore\b', r'\bmoreover\b', r'\bin addition\b',
    r'\bit is important to note that\b', r'\bin conclusion\b',
    r'\bto summarize\b', r'\bplays a crucial role\b',
    r'\bdelve into\b', r'\bdelve\b', r'\bexplore\b',
    r'\butilize\b', r'\bleverage\b', r'\ba comprehensive\b',
    r'\bfacilitate\b', r'\bunderscore\b', r'\bparamount\b',
    r'\bpivotal\b', r'\bseamless\b', r'\brobust\b',
    r'\bholistic\b', r'\bintricate\b', r'\bmultifaceted\b',
    r'\bin today.s .* landscape\b', r'\bin the realm of\b',
    r'\btapestry\b', r'\bunlock\b',
]

def count_ai_isms(text: str) -> dict:
    """Count known AI-associated phrases in the text."""
    results = {}
    text_lower = text.lower()
    total = 0
    for pattern in AI_ISM_PATTERNS:
        matches = re.findall(pattern, text_lower)
        if matches:
            results[pattern.replace(r'\b', '').strip()] = len(matches)
            total += len(matches)
    return {"ai_isms": results, "total_ai_isms": total}


# ─── Sentence-Level Heatmap ───────────────────────────────────────────────
def generate_heatmap(sentences: list[str], ppl_scores: list[float]) -> list[dict]:
    """
    Generate a per-sentence risk heatmap.
    Returns list of dicts with sentence, PPL, and risk level.
    """
    heatmap = []
    for i, (sent, ppl) in enumerate(zip(sentences, ppl_scores)):
        if ppl < 25:
            risk = "CRITICAL"
        elif ppl < 40:
            risk = "HIGH"
        elif ppl < 55:
            risk = "MEDIUM"
        else:
            risk = "LOW"
        heatmap.append({
            "index": i + 1,
            "sentence": sent[:80] + ("..." if len(sent) > 80 else ""),
            "perplexity": round(ppl, 2),
            "risk": risk,
        })
    return heatmap


# ─── Main Analysis ─────────────────────────────────────────────────────────
def analyze(text: str, model: str = 'gpt2') -> dict:
    """
    Full analysis pipeline: PPL, burstiness, AI-isms, and heatmap.
    """
    sentences = split_into_sentences(text)
    if not sentences:
        return {"error": "No sentences found in input text."}

    # Compute perplexity scores
    ppl_scores = compute_model_perplexity(sentences, model)

    if HAS_NUMPY:
        doc_ppl = float(np.mean(ppl_scores))
        burstiness = float(np.std(ppl_scores))
    else:
        doc_ppl = sum(ppl_scores) / len(ppl_scores)
        variance = sum((p - doc_ppl) ** 2 for p in ppl_scores) / len(ppl_scores)
        burstiness = variance ** 0.5

    # Count flagged sentences
    flagged = sum(1 for p in ppl_scores if p < 40)
    flagged_pct = (flagged / len(sentences)) * 100

    # AI risk assessment
    if doc_ppl < 40 and burstiness < 3.0:
        ai_risk = "HIGH"
        ai_score = min(95, int(100 - doc_ppl * 1.5))
    elif doc_ppl < 55 or burstiness < 4.5:
        ai_risk = "MEDIUM"
        ai_score = min(60, int(80 - doc_ppl * 0.8))
    else:
        ai_risk = "LOW"
        ai_score = max(0, int(40 - doc_ppl * 0.3))

    ai_score = max(0, min(100, ai_score))

    # AI-ism count
    ai_ism_report = count_ai_isms(text)

    # Heatmap
    heatmap = generate_heatmap(sentences, ppl_scores)

    return {
        "summary": {
            "total_sentences": len(sentences),
            "document_perplexity": round(doc_ppl, 2),
            "burstiness": round(burstiness, 2),
            "ai_probability_pct": ai_score,
            "ai_risk_level": ai_risk,
            "flagged_sentences": flagged,
            "flagged_pct": round(flagged_pct, 1),
            "total_ai_isms": ai_ism_report["total_ai_isms"],
        },
        "thresholds": {
            "perplexity_target": "≥ 55",
            "burstiness_target": "≥ 4.5",
            "ai_score_target": "≤ 5%",
            "ppl_pass": doc_ppl >= 55,
            "burstiness_pass": burstiness >= 4.5,
            "ai_pass": ai_score <= 5,
        },
        "ai_isms_detail": ai_ism_report["ai_isms"],
        "heatmap": heatmap,
    }


# ─── CLI ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Analyze text for plagiarism/AI detection risk metrics."
    )
    parser.add_argument("input", help="Path to input text file")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--model", default="gpt2",
                        help="Model for PPL scoring (default: gpt2)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding='utf-8', errors='replace')
    results = analyze(text, args.model)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        s = results["summary"]
        t = results["thresholds"]
        print("═" * 60)
        print("  PLAGBYPASS — METRIC ANALYSIS REPORT")
        print("═" * 60)
        print(f"  Document:           {input_path.name}")
        print(f"  Total Sentences:    {s['total_sentences']}")
        print()
        print("  METRICS:")
        ppl_status = "PASS ✅" if t['ppl_pass'] else "FAIL ❌"
        burst_status = "PASS ✅" if t['burstiness_pass'] else "FAIL ❌"
        ai_status = "PASS ✅" if t['ai_pass'] else "FAIL ❌"
        print(f"  ├── Perplexity:     {s['document_perplexity']:<8} target ≥ 55   {ppl_status}")
        print(f"  ├── Burstiness:     {s['burstiness']:<8} target ≥ 4.5  {burst_status}")
        print(f"  ├── AI Score:       {s['ai_probability_pct']}%{'':<5} target ≤ 5%  {ai_status}")
        print(f"  ├── AI-isms Found:  {s['total_ai_isms']}")
        print(f"  └── Flagged Sents:  {s['flagged_sentences']}/{s['total_sentences']} ({s['flagged_pct']}%)")
        print()

        if results["ai_isms_detail"]:
            print("  AI-ISM TOKENS DETECTED:")
            for token, count in results["ai_isms_detail"].items():
                print(f"    ⚠  \"{token}\" × {count}")
            print()

        # Show top 5 riskiest sentences
        risky = [h for h in results["heatmap"] if h["risk"] in ("CRITICAL", "HIGH")]
        if risky:
            print(f"  TOP RISK SENTENCES ({len(risky)} flagged):")
            for h in risky[:5]:
                print(f"    [{h['risk']:>8}] S{h['index']:>3} (PPL={h['perplexity']}) {h['sentence']}")
            print()

        overall = "SAFE FOR SUBMISSION" if all([t['ppl_pass'], t['burstiness_pass'], t['ai_pass']]) else "NEEDS REMEDIATION"
        print(f"  STATUS: {overall}")
        print("═" * 60)


if __name__ == "__main__":
    main()
