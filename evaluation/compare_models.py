"""Compare local Ollama models on the same safety questions.

Usage (Ollama must be running and the models pulled):
    python -m evaluation.compare_models llama3.2:3b phi3:mini gemma2:2b

Writes evaluation/model_results.csv with each answer and its response time.
Open the CSV and score each answer 1-5 for accuracy and simplicity.
"""

import csv
import sys
import time
from pathlib import Path

from guardian.assistant import Assistant
from guardian.llm import OfflineLLM

QUESTIONS = [
    "Someone phoned saying they are from my bank and asked for the code they just texted me. What should I do?",
    "I got a text saying my parcel couldn't be delivered and I need to pay a small fee. Is it real?",
    "How do I make a password I can remember?",
    "A message popped up saying my computer has a virus and to call Microsoft. Should I call?",
    "My grandson called from a strange number saying he is in jail and needs money. What do I do?",
    "Is it safe to pay for things online with my card?",
    "Somebody asked me to pay a bill with iTunes gift cards. Is that normal?",
    "What is two-step verification and should I use it?",
    "I think I gave my bank details to a scammer. What should I do now?",
    "A man I met on Facebook wants me to send money for his plane ticket. He says he loves me.",
]

OUT = Path(__file__).with_name("model_results.csv")


def main(models):
    rows = []
    for model in models:
        llm = OfflineLLM(model=model, timeout=180)
        if not llm.is_available():
            print(f"Skipping {model}: not running or not pulled (try: ollama pull {model})")
            continue
        assistant = Assistant(llm)
        for i, question in enumerate(QUESTIONS, 1):
            start = time.perf_counter()
            result = assistant.reply(question)
            seconds = time.perf_counter() - start
            words = len(result["reply"].split())
            print(f"{model} Q{i}: {seconds:.1f}s, {words} words, source={result['source']}")
            rows.append({"model": model, "question": question, "answer": result["reply"],
                         "source": result["source"], "seconds": f"{seconds:.1f}", "words": words,
                         "accuracy_1to5": "", "simplicity_1to5": ""})
    if rows:
        with OUT.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nSaved {len(rows)} answers to {OUT}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["llama3.2:3b"])
