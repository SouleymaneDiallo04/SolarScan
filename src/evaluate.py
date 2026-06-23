"""Évaluation sur le jeu de test : métriques + matrice de confusion."""
import argparse
import json
import os

import torch
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report, confusion_matrix, ConfusionMatrixDisplay,
    f1_score, accuracy_score,
)

from dataset import InfraredSolarModules, CLASSES
from model import build_model
from train import get_transforms


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True)
    parser.add_argument("--model_path", default="models/best_model.pt")
    parser.add_argument("--split_path", default="models/test_split.json")
    parser.add_argument("--output_dir", default="outputs")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    with open(args.split_path, "r", encoding="utf-8") as f:
        test_items = json.load(f)["test"]

    _, eval_t = get_transforms()
    test_dl = DataLoader(
        InfraredSolarModules(test_items, args.data_dir, eval_t),
        batch_size=64, shuffle=False, num_workers=2,
    )

    model = build_model(len(CLASSES)).to(device)
    model.load_state_dict(torch.load(args.model_path, map_location=device))
    model.eval()

    preds, gts = [], []
    with torch.no_grad():
        for x, y in test_dl:
            preds += model(x.to(device)).argmax(1).cpu().tolist()
            gts += y.tolist()

    acc = accuracy_score(gts, preds)
    macro_f1 = f1_score(gts, preds, average="macro")
    print(f"\nAccuracy (test) : {acc:.4f}")
    print(f"Macro F1-score  : {macro_f1:.4f}\n")
    print(classification_report(gts, preds, target_names=CLASSES, zero_division=0))

    cm = confusion_matrix(gts, preds)
    fig, ax = plt.subplots(figsize=(10, 10))
    ConfusionMatrixDisplay(cm, display_labels=CLASSES).plot(
        ax=ax, xticks_rotation=90, colorbar=False
    )
    plt.tight_layout()
    cm_path = os.path.join(args.output_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=150)

    with open(os.path.join(args.output_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump({"accuracy": acc, "macro_f1": macro_f1}, f, indent=2)

    print(f"Sauvegardé : {cm_path} et outputs/metrics.json")


if __name__ == "__main__":
    main()
