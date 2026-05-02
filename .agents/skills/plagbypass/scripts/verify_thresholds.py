#!/usr/bin/env python3
"""
verify_thresholds.py — Final pass/fail gatekeeper.

Runs analyze_metrics.py on the text and compares against configurable 
institutional thresholds. Returns a structured pass/fail verdict.

Usage:
    python verify_thresholds.py <input_file> [--profile strict|lenient|ieee]
"""

import sys
import json
import argparse
from pathlib import Path

# Import the analysis engine
sys.path.insert(0, str(Path(__file__).parent))
from analyze_metrics import analyze, split_into_sentences, count_ai_isms


# ─── Institutional Profiles ───────────────────────────────────────────────
PROFILES = {
    "strict": {
        "name": "UoH / Strict University",
        "max_similarity_pct": 5,
        "max_ai_score_pct": 3,
        "min_perplexity": 55,
        "min_burstiness": 5.0,
        "max_ai_isms": 2,
        "max_flagged_pct": 5,
    },
    "lenient": {
        "name": "JNTU / Lenient University",
        "max_similarity_pct": 15,
        "max_ai_score_pct": 10,
        "min_perplexity": 45,
        "min_burstiness": 3.5,
        "max_ai_isms": 5,
        "max_flagged_pct": 15,
    },
    "ieee": {
        "name": "IEEE / Conference Submission",
        "max_similarity_pct": 8,
        "max_ai_score_pct": 5,
        "min_perplexity": 50,
        "min_burstiness": 4.0,
        "max_ai_isms": 3,
        "max_flagged_pct": 10,
    },
}


def verify(text: str, profile_name: str = "strict", model: str = "gpt2") -> dict:
    """
    Run full verification against an institutional profile.
    
    Returns:
        dict with pass/fail status, individual checks, and recommendations.
    """
    profile = PROFILES.get(profile_name, PROFILES["strict"])
    
    # Run analysis
    metrics = analyze(text, model)
    if "error" in metrics:
        return {"status": "ERROR", "message": metrics["error"]}
    
    summary = metrics["summary"]
    
    # Individual checks
    checks = {
        "perplexity": {
            "value": summary["document_perplexity"],
            "target": f"≥ {profile['min_perplexity']}",
            "pass": summary["document_perplexity"] >= profile["min_perplexity"],
        },
        "burstiness": {
            "value": summary["burstiness"],
            "target": f"≥ {profile['min_burstiness']}",
            "pass": summary["burstiness"] >= profile["min_burstiness"],
        },
        "ai_score": {
            "value": f"{summary['ai_probability_pct']}%",
            "target": f"≤ {profile['max_ai_score_pct']}%",
            "pass": summary["ai_probability_pct"] <= profile["max_ai_score_pct"],
        },
        "ai_isms": {
            "value": summary["total_ai_isms"],
            "target": f"≤ {profile['max_ai_isms']}",
            "pass": summary["total_ai_isms"] <= profile["max_ai_isms"],
        },
        "flagged_sentences": {
            "value": f"{summary['flagged_pct']}%",
            "target": f"≤ {profile['max_flagged_pct']}%",
            "pass": summary["flagged_pct"] <= profile["max_flagged_pct"],
        },
    }
    
    # Overall verdict
    all_pass = all(c["pass"] for c in checks.values())
    
    # Recommendations for failing checks
    recommendations = []
    if not checks["perplexity"]["pass"]:
        recommendations.append(
            "PERPLEXITY too low: Use more varied vocabulary, longer words, "
            "and less predictable sentence constructions."
        )
    if not checks["burstiness"]["pass"]:
        recommendations.append(
            "BURSTINESS too low: Alternate between short (5-10 word) and "
            "long (25-35 word) sentences. Add 1-sentence paragraphs."
        )
    if not checks["ai_score"]["pass"]:
        recommendations.append(
            "AI SCORE too high: Apply Mode D (conceptual reframing) to "
            "flagged sentences. Add hedging language and first-person markers."
        )
    if not checks["ai_isms"]["pass"]:
        recommendations.append(
            f"AI-ISMS detected ({summary['total_ai_isms']}): Replace "
            "'Furthermore', 'Moreover', 'utilize', 'leverage' with "
            "natural alternatives. See ai_isms_filter.json."
        )
    if not checks["flagged_sentences"]["pass"]:
        recommendations.append(
            f"Too many flagged sentences ({summary['flagged_pct']}%): "
            "Focus restructuring on sentences with PPL < 40 in the heatmap."
        )
    
    return {
        "status": "PASS" if all_pass else "FAIL",
        "profile": profile["name"],
        "checks": checks,
        "recommendations": recommendations,
        "heatmap_summary": {
            "critical": sum(1 for h in metrics["heatmap"] if h["risk"] == "CRITICAL"),
            "high": sum(1 for h in metrics["heatmap"] if h["risk"] == "HIGH"),
            "medium": sum(1 for h in metrics["heatmap"] if h["risk"] == "MEDIUM"),
            "low": sum(1 for h in metrics["heatmap"] if h["risk"] == "LOW"),
        },
    }


# ─── CLI ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Verify text against institutional plagiarism/AI thresholds."
    )
    parser.add_argument("input", help="Path to input text file")
    parser.add_argument("--profile", choices=["strict", "lenient", "ieee"],
                        default="strict", help="Institutional profile (default: strict)")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format")
    parser.add_argument("--model", default="gpt2",
                        help="Model for PPL scoring (default: gpt2)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding='utf-8', errors='replace')
    result = verify(text, args.profile, args.model)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("═" * 60)
        print("  PLAGBYPASS — VERIFICATION REPORT")
        print("═" * 60)
        print(f"  Profile:  {result['profile']}")
        print(f"  Document: {input_path.name}")
        print()
        print("  CHECKS:")
        for name, check in result["checks"].items():
            icon = "✅" if check["pass"] else "❌"
            print(f"  {icon} {name:<20} {str(check['value']):<10} (target: {check['target']})")
        print()
        
        hs = result["heatmap_summary"]
        print(f"  HEATMAP: {hs['critical']} critical, {hs['high']} high, "
              f"{hs['medium']} medium, {hs['low']} low risk")
        print()

        if result["recommendations"]:
            print("  RECOMMENDATIONS:")
            for i, rec in enumerate(result["recommendations"], 1):
                print(f"    {i}. {rec}")
            print()

        status_icon = "✅ SAFE FOR SUBMISSION" if result["status"] == "PASS" else "❌ NEEDS REMEDIATION"
        print(f"  STATUS: {status_icon}")
        print("═" * 60)
        print()


if __name__ == "__main__":
    main()
