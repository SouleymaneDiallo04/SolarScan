"""Entraînement du classifieur d'anomalies thermiques (transfer learning ResNet-18)."""
import argparse
import json
import os

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score
from tqdm import tqdm

from dataset import InfraredSolarModules, load_items, split_items, CLASSES
from model import build_model

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_transforms():
    train_t = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    eval_t = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    return train_t, eval_t


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--output_dir", default="models")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device : {device}")

    items = load_items(args.data_dir)
    train_items, val_items, test_items = split_items(items)
    print(f"Train={len(train_items)}  Val={len(val_items)}  Test={len(test_items)}")

    # On fige le split de test pour une évaluation reproductible
    with open(os.path.join(args.output_dir, "test_split.json"), "w", encoding="utf-8") as f:
        json.dump({"test": test_items}, f)

    train_t, eval_t = get_transforms()
    train_dl = DataLoader(
        InfraredSolarModules(train_items, args.data_dir, train_t),
        batch_size=args.batch_size, shuffle=True, num_workers=2,
    )
    val_dl = DataLoader(
        InfraredSolarModules(val_items, args.data_dir, eval_t),
        batch_size=args.batch_size, shuffle=False, num_workers=2,
    )

    # Pondération des classes pour gérer le déséquilibre
    y_train = [lbl for _, lbl in train_items]
    class_weights = compute_class_weight(
        "balanced", classes=np.arange(len(CLASSES)), y=y_train
    )
    class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)

    model = build_model(len(CLASSES), pretrained=True).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, "max", patience=2)

    best_f1 = 0.0
    for epoch in range(args.epochs):
        model.train()
        for x, y in tqdm(train_dl, desc=f"Epoch {epoch + 1}/{args.epochs}"):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()

        # Validation
        model.eval()
        preds, gts = [], []
        with torch.no_grad():
            for x, y in val_dl:
                preds += model(x.to(device)).argmax(1).cpu().tolist()
                gts += y.tolist()
        val_f1 = f1_score(gts, preds, average="macro")
        scheduler.step(val_f1)
        print(f"Epoch {epoch + 1} : val macro-F1 = {val_f1:.4f}")

        if val_f1 > best_f1:
            best_f1 = val_f1
            torch.save(model.state_dict(), os.path.join(args.output_dir, "best_model.pt"))
            print(f"  -> nouveau meilleur modèle sauvegardé (F1={val_f1:.4f})")

    print(f"\nMeilleur macro-F1 (validation) : {best_f1:.4f}")
    print(f"Modèle : {os.path.join(args.output_dir, 'best_model.pt')}")


if __name__ == "__main__":
    main()
