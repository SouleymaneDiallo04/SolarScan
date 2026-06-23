"""Affiche la distribution des classes du dataset (utile vu le fort déséquilibre)."""
import argparse
from collections import Counter

from dataset import load_items, CLASSES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True)
    args = parser.parse_args()

    items = load_items(args.data_dir)
    counts = Counter(lbl for _, lbl in items)
    total = len(items)

    print(f"Total images : {total}\n")
    for i, cls in enumerate(CLASSES):
        n = counts.get(i, 0)
        pct = 100 * n / total if total else 0
        print(f"  {cls:16s} : {n:6d}  ({pct:5.1f} %)")


if __name__ == "__main__":
    main()
