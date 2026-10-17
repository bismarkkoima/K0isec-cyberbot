"""Measure how well the rule-based scam checker separates scams from genuine messages.

Usage:  python -m evaluation.evaluate_checker

A message counts as "flagged" when the checker rates it medium or high risk.
"""

import json
from collections import Counter
from pathlib import Path

from guardian.scam_checker import analyze

DATA = Path(__file__).with_name("messages.json")


def main():
    messages = json.loads(DATA.read_text(encoding="utf-8"))
    counts = Counter()
    levels = Counter()
    mistakes = []
    for m in messages:
        level = analyze(m["text"])["level"]
        flagged = level != "low"
        levels[(m["label"], level)] += 1
        if m["label"] == "scam":
            counts["tp" if flagged else "fn"] += 1
        else:
            counts["fp" if flagged else "tn"] += 1
        if flagged != (m["label"] == "scam"):
            mistakes.append((m["label"], level, m["text"]))

    tp, fp, tn, fn = counts["tp"], counts["fp"], counts["tn"], counts["fn"]
    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    print(f"Messages: {total} ({tp + fn} scam, {tn + fp} genuine)\n")
    print("Confusion matrix (flagged = medium or high risk)")
    print(f"                 flagged   not flagged")
    print(f"  scam           {tp:>7}   {fn:>11}")
    print(f"  genuine        {fp:>7}   {tn:>11}\n")
    print(f"Accuracy:  {(tp + tn) / total:.1%}")
    print(f"Precision: {precision:.1%}")
    print(f"Recall:    {recall:.1%}")
    print(f"F1 score:  {f1:.1%}\n")
    print("Risk levels by label")
    for label in ("scam", "genuine"):
        row = ", ".join(f"{lvl}: {levels[(label, lvl)]}" for lvl in ("high", "medium", "low"))
        print(f"  {label:<8} {row}")
    if mistakes:
        print("\nMisclassified messages")
        for label, level, text in mistakes:
            print(f"  [{label} -> {level}] {text}")


if __name__ == "__main__":
    main()
