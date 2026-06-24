"""EDA — distribution des classes du dataset InfraredSolarModules.

Script volontairement SANS dépendance lourde (bibliothèque standard uniquement) :
l'exploration des données doit pouvoir tourner immédiatement, avant même
d'installer PyTorch. On lit directement le fichier de métadonnées.
"""
import argparse
import json
import os
from collections import Counter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default="data")
    args = parser.parse_args()

    meta_path = os.path.join(args.data_dir, "module_metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    counts = Counter(entry["anomaly_class"] for entry in meta.values())
    total = sum(counts.values())

    print(f"Total images : {total}\n")
    print(f"{'Classe':18s} {'Images':>7s} {'Part':>8s}")
    print("-" * 36)
    for cls, n in counts.most_common():
        print(f"{cls:18s} {n:7d} {100 * n / total:6.1f} %")

    majority = counts.most_common(1)[0]
    minority = counts.most_common()[-1]
    print("\nIndicateurs de déséquilibre :")
    print(f"  Classe majoritaire : {majority[0]} ({majority[1]})")
    print(f"  Classe minoritaire : {minority[0]} ({minority[1]})")
    print(f"  Ratio maj / min    : {majority[1] / minority[1]:.1f} x")
    print(f"  Baseline naïve (tout en '{majority[0]}') : "
          f"{100 * majority[1] / total:.1f} % d'accuracy")


if __name__ == "__main__":
    main()
