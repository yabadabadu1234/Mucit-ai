#!/usr/bin/env python3
"""
yerel_ai_dedektor.py
Evaluates text strictly locally and offline using cached transformer models:
1. roberta-base-openai-detector
2. Hello-SimpleAI/chatgpt-detector-roberta
Reports human vs AI probability per paragraph and overall.
"""

import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def get_detector():
    tok1 = AutoTokenizer.from_pretrained('roberta-base-openai-detector', local_files_only=True)
    mod1 = AutoModelForSequenceClassification.from_pretrained('roberta-base-openai-detector', local_files_only=True)
    mod1.eval()

    tok2 = AutoTokenizer.from_pretrained('Hello-SimpleAI/chatgpt-detector-roberta', local_files_only=True)
    mod2 = AutoModelForSequenceClassification.from_pretrained('Hello-SimpleAI/chatgpt-detector-roberta', local_files_only=True)
    mod2.eval()

    return (tok1, mod1), (tok2, mod2)

def evaluate_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    (tok1, mod1), (tok2, mod2) = get_detector()

    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 60 and not p.strip().startswith('#')]
    print(f"Evaluating {len(paragraphs)} substantive sections in {file_path}...\n")

    scores1, scores2 = [], []
    flagged = []

    for idx, p in enumerate(paragraphs):
        # Truncate clean text for tokenizer
        inp1 = tok1(p, return_tensors='pt', truncation=True, max_length=512)
        with torch.no_grad():
            prob1 = torch.softmax(mod1(**inp1).logits, dim=-1).squeeze().tolist()[1] # Real (Human)

        inp2 = tok2(p, return_tensors='pt', truncation=True, max_length=512)
        with torch.no_grad():
            prob2 = torch.softmax(mod2(**inp2).logits, dim=-1).squeeze().tolist()[0] # Human

        combined_human = (prob1 + prob2) / 2.0
        scores1.append(prob1)
        scores2.append(prob2)

        status = "OK (HUMAN)" if combined_human >= 0.70 else "FLAGGED (AI)"
        if combined_human < 0.70:
            flagged.append((idx + 1, combined_human, p))
            print(f"[{status}] Section {idx+1:02d}: Human Score = {combined_human*100:.1f}% (OpenAI: {prob1*100:.1f}%, ChatGPT-Det: {prob2*100:.1f}%)")
            print(f"   Excerpt: {p[:90]}...\n")

    avg_human1 = sum(scores1) / len(scores1) * 100
    avg_human2 = sum(scores2) / len(scores2) * 100
    overall = (avg_human1 + avg_human2) / 2.0

    print("=" * 60)
    print(f"OVERALL DETECTOR RESULTS:")
    print(f"OpenAI Detector Human Score:  {avg_human1:.2f}%")
    print(f"ChatGPT Detector Human Score: {avg_human2:.2f}%")
    print(f"Combined Human Authenticity:  {overall:.2f}%")
    print(f"Sections flagged as AI (<70%): {len(flagged)} / {len(paragraphs)}")
    print("=" * 60)

    return overall, flagged

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'docs/planli_eskitme_hitabet_metni_en.md'
    evaluate_file(target)
