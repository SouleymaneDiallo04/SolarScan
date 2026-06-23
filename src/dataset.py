"""Dataset PyTorch pour InfraredSolarModules (imagerie thermique PV)."""
import json
import os

from PIL import Image
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split

CLASSES = [
    "Cell", "Cell-Multi", "Cracking", "Hot-Spot", "Hot-Spot-Multi",
    "Shadowing", "Diode", "Diode-Multi", "Vegetation", "Soiling",
    "Offline-Module", "No-Anomaly",
]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}


class InfraredSolarModules(Dataset):
    """Charge les images thermiques (converties en RGB pour le transfer learning)."""

    def __init__(self, items, data_dir, transform=None):
        self.items = items
        self.data_dir = data_dir
        self.transform = transform

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        rel_path, label = self.items[idx]
        img = Image.open(os.path.join(self.data_dir, rel_path)).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


def load_items(data_dir, metadata_name="module_metadata.json"):
    """Lit module_metadata.json -> liste de (chemin_relatif, indice_classe)."""
    with open(os.path.join(data_dir, metadata_name), "r", encoding="utf-8") as f:
        meta = json.load(f)

    items = []
    for entry in meta.values():
        rel_path = entry["image_filepath"]
        cls = entry["anomaly_class"]
        if cls in CLASS_TO_IDX:
            items.append((rel_path, CLASS_TO_IDX[cls]))
    if not items:
        raise RuntimeError(
            "Aucune image trouvée. Vérifie la structure de data/ "
            "(images/ + module_metadata.json)."
        )
    return items


def split_items(items, val_size=0.15, test_size=0.15, seed=42):
    """Découpe stratifiée train / val / test."""
    labels = [lbl for _, lbl in items]
    train, temp = train_test_split(
        items, test_size=val_size + test_size, stratify=labels, random_state=seed
    )
    temp_labels = [lbl for _, lbl in temp]
    rel_test = test_size / (val_size + test_size)
    val, test = train_test_split(
        temp, test_size=rel_test, stratify=temp_labels, random_state=seed
    )
    return train, val, test
