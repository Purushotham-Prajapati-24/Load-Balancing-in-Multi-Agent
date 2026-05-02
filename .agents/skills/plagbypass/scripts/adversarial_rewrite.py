#!/usr/bin/env python3
"""
adversarial_rewrite.py — Deep syntactic restructuring engine.

Implements Tier L1 transformations:
  Mode A: Sentence fusion & fission
  Mode B: Voice & tense rotation
  Mode C: Clause reordering
  Mode D: Conceptual reframing

Also handles AI-ism filtering and rhythm injection.

Usage:
    python adversarial_rewrite.py <input_file> <output_file> [--mode all]
"""

import sys
import re
import json
import random
import argparse
from pathlib import Path

# ─── AI-ism Replacement Map ───────────────────────────────────────────────
AI_ISM_REPLACEMENTS = {
    "furthermore": ["This leads to", "Crucially", "Building on this"],
    "moreover": ["Equally important", "In parallel", "Along similar lines"],
    "in addition": ["Beyond this", "Alongside", "Extending this idea"],
    "it is important to note that": ["Remarkably", "Significantly", "Notably"],
    "in conclusion": ["Ultimately", "These findings indicate", "Taken together"],
    "to summarize": ["In essence", "The central takeaway is", "Collectively"],
    "plays a crucial role": ["directly influences", "shapes", "governs"],
    "plays a key role": ["is central to", "underpins", "drives"],
    "plays an important role": ["contributes significantly to", "is integral to"],
    "delve into": ["investigate", "examine closely", "dissect"],
    "delve": ["examine", "probe", "scrutinize"],
    "explore": ["investigate", "analyze", "examine"],
    "utilize": ["use", "employ", "apply"],
    "leverage": ["apply", "employ", "draw on"],
    "a comprehensive": ["a detailed", "a thorough", "an extensive"],
    "facilitate": ["enable", "support", "allow"],
    "underscore": ["highlight", "emphasize", "reinforce"],
    "paramount": ["essential", "critical", "vital"],
    "pivotal": ["central", "key", "decisive"],
    "seamless": ["smooth", "uninterrupted", "fluid"],
    "robust": ["strong", "reliable", "resilient"],
    "holistic": ["integrated", "unified", "all-encompassing"],
    "intricate": ["complex", "elaborate", "detailed"],
    "multifaceted": ["complex", "layered", "many-sided"],
    "tapestry": ["landscape", "structure", "framework"],
    "unlock": ["reveal", "enable", "open up"],
}


def filter_ai_isms(text: str) -> str:
    """Replace known AI-associated phrases with human alternatives."""
    result = text
    for ai_phrase, replacements in AI_ISM_REPLACEMENTS.items():
        # Case-insensitive replacement
        pattern = re.compile(re.escape(ai_phrase), re.IGNORECASE)
        matches = list(pattern.finditer(result))
        for match in reversed(matches):
            replacement = random.choice(replacements)
            # Match original casing
            original = match.group()
            if original[0].isupper():
                replacement = replacement[0].upper() + replacement[1:]
            result = result[:match.start()] + replacement + result[match.end():]
    return result


# ─── Mode A: Sentence Fusion & Fission ─────────────────────────────────────
def apply_fusion_fission(sentences: list[str]) -> list[str]:
    """
    Fuse short adjacent sentences; split long uniform ones.
    This breaks monotonous rhythm patterns.
    """
    result = []
    i = 0
    while i < len(sentences):
        sent = sentences[i]
        words = sent.split()

        # FISSION: Split overly long sentences (>35 words) at conjunctions
        if len(words) > 35:
            split_points = [
                m.start() for m in re.finditer(
                    r',\s*(which|where|while|although|because|since|however|but)\b',
                    sent
                )
            ]
            if split_points:
                mid = split_points[len(split_points) // 2]
                part1 = sent[:mid].rstrip(',').strip()
                part2 = sent[mid:].lstrip(', ').strip()
                if part2 and part2[0].islower():
                    part2 = part2[0].upper() + part2[1:]
                result.append(part1 + '.')
                result.append(part2)
                i += 1
                continue

        # FUSION: Merge two short sentences (<12 words each)
        if len(words) < 12 and i + 1 < len(sentences):
            next_words = sentences[i + 1].split()
            if len(next_words) < 12:
                connectors = [
                    ", and consequently ",
                    "; in effect, ",
                    "—a pattern that ",
                    ", which means that ",
                    ", thereby ",
                ]
                connector = random.choice(connectors)
                merged = sent.rstrip('.') + connector + sentences[i + 1][0].lower() + sentences[i + 1][1:]
                result.append(merged)
                i += 2
                continue

        result.append(sent)
        i += 1
    return result


# ─── Mode B: Voice & Tense Rotation ───────────────────────────────────────
PASSIVE_INDICATORS = [
    r'\bis\s+\w+ed\b', r'\bare\s+\w+ed\b', r'\bwas\s+\w+ed\b',
    r'\bwere\s+\w+ed\b', r'\bbeen\s+\w+ed\b', r'\bbe\s+\w+ed\b',
]

def detect_passive(sentence: str) -> bool:
    """Check if a sentence is likely in passive voice."""
    for pattern in PASSIVE_INDICATORS:
        if re.search(pattern, sentence, re.IGNORECASE):
            return True
    return False


def add_voice_variation(sentences: list[str]) -> list[str]:
    """
    Track voice patterns and add markers where the agent should
    consider voice transformation.
    """
    result = []
    passive_streak = 0
    active_streak = 0
    
    for sent in sentences:
        is_passive = detect_passive(sent)
        
        if is_passive:
            passive_streak += 1
            active_streak = 0
        else:
            active_streak += 1
            passive_streak = 0

        # If too many consecutive same-voice sentences, mark for transformation
        if passive_streak >= 3 or active_streak >= 4:
            # Add a brief rhythm-breaking interjection
            result.append(sent)
            if len(sent.split()) > 20:
                # Signal for the agent to vary the next sentence
                pass  # The agent uses SKILL.md instructions for this
        else:
            result.append(sent)
    
    return result


# ─── Mode C: Clause Reordering ─────────────────────────────────────────────
def reorder_clauses(sentence: str) -> str:
    """
    Move subordinate clauses to the front or back of the sentence
    to break predictable S-V-O patterns.
    """
    # Pattern: "X because/since/when/if Y" → "Because/Since/When/If Y, X"
    match = re.match(
        r'^(.+?)\s*,?\s*(because|since|when|if|although|while)\s+(.+)$',
        sentence, re.IGNORECASE
    )
    if match:
        main_clause = match.group(1).rstrip('.,')
        conjunction = match.group(2)
        subordinate = match.group(3).rstrip('.')
        # Flip the order
        reordered = f"{conjunction.capitalize()} {subordinate}, {main_clause[0].lower()}{main_clause[1:]}."
        return reordered
    
    # Pattern: "X, which Y" → keep as is (relative clauses are hard to flip)
    return sentence


# ─── Rhythm Injection ──────────────────────────────────────────────────────
RHYTHM_INJECTORS = [
    "This matters.",
    "The implications are clear.",
    "Why does this occur?",
    "The data confirms this.",
    "This warrants attention.",
    "Consider the alternative.",
    "The difference is measurable.",
    "This is a key distinction.",
]

def inject_rhythm(sentences: list[str]) -> list[str]:
    """
    Ensure human-like burstiness by inserting short sentences
    after runs of medium-length sentences.
    """
    result = []
    medium_streak = 0
    
    for sent in sentences:
        words = sent.split()
        result.append(sent)
        
        if 15 <= len(words) <= 30:
            medium_streak += 1
        else:
            medium_streak = 0
        
        # After 3 medium sentences, optionally break rhythm
        if medium_streak >= 3:
            # Don't always inject — 60% chance
            if random.random() < 0.6:
                result.append(random.choice(RHYTHM_INJECTORS))
            medium_streak = 0
    
    return result


# ─── N-gram Deduplication Check ────────────────────────────────────────────
def find_long_ngram_matches(original: str, rewritten: str, n: int = 8) -> list[str]:
    """
    Find n-gram sequences that survived the rewrite unchanged.
    These will be flagged by similarity engines.
    """
    orig_words = original.lower().split()
    new_words = rewritten.lower().split()
    
    orig_ngrams = set()
    for i in range(len(orig_words) - n + 1):
        orig_ngrams.add(' '.join(orig_words[i:i+n]))
    
    surviving = []
    for i in range(len(new_words) - n + 1):
        ngram = ' '.join(new_words[i:i+n])
        if ngram in orig_ngrams:
            surviving.append(ngram)
    
    return surviving


# ─── Main Rewrite Pipeline ─────────────────────────────────────────────────
def rewrite(text: str, mode: str = 'all') -> dict:
    """
    Apply the full adversarial rewrite pipeline.
    
    Returns:
        dict with 'rewritten_text', 'changes_made', and 'surviving_ngrams'
    """
    changes = []
    
    # Step 1: AI-ism filtering
    filtered = filter_ai_isms(text)
    if filtered != text:
        changes.append("AI-ism tokens replaced")
    
    # Step 2: Split into sentences
    from analyze_metrics import split_into_sentences
    sentences = split_into_sentences(filtered)
    
    if not sentences:
        return {"rewritten_text": text, "changes_made": [], "surviving_ngrams": []}
    
    # Step 3: Apply transformation modes
    if mode in ('all', 'fusion'):
        sentences = apply_fusion_fission(sentences)
        changes.append(f"Mode A (Fusion/Fission): {len(sentences)} sentences")
    
    if mode in ('all', 'voice'):
        sentences = add_voice_variation(sentences)
        changes.append("Mode B (Voice variation markers)")
    
    if mode in ('all', 'reorder'):
        reordered = []
        for s in sentences:
            if random.random() < 0.3:  # Reorder ~30% of sentences
                reordered.append(reorder_clauses(s))
                changes.append(f"Mode C: Reordered clause in sentence")
            else:
                reordered.append(s)
        sentences = reordered
    
    if mode in ('all', 'rhythm'):
        sentences = inject_rhythm(sentences)
        changes.append("Mode D (Rhythm injection)")
    
    # Rejoin
    rewritten = ' '.join(sentences)
    
    # Step 4: Check for surviving n-grams
    surviving = find_long_ngram_matches(text, rewritten, n=8)
    if surviving:
        changes.append(f"WARNING: {len(surviving)} 8-gram matches survive")
    
    return {
        "rewritten_text": rewritten,
        "changes_made": changes,
        "surviving_ngrams": surviving[:10],  # Top 10
    }


# ─── CLI ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Apply adversarial rewrite transformations to text."
    )
    parser.add_argument("input", help="Path to input text file")
    parser.add_argument("output", help="Path to output text file")
    parser.add_argument("--mode", default="all",
                        choices=["all", "fusion", "voice", "reorder", "rhythm"],
                        help="Transformation mode (default: all)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding='utf-8', errors='replace')
    result = rewrite(text, args.mode)

    output_path.write_text(result["rewritten_text"], encoding='utf-8')

    print(f"✅ Rewritten text saved to: {output_path}")
    print(f"   Changes: {len(result['changes_made'])}")
    for change in result['changes_made']:
        print(f"   • {change}")
    if result['surviving_ngrams']:
        print(f"   ⚠ Surviving 8-grams: {len(result['surviving_ngrams'])}")
        for ng in result['surviving_ngrams'][:3]:
            print(f"     → \"{ng}\"")


if __name__ == "__main__":
    main()
