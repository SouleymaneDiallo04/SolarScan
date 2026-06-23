# Détection de défauts sur panneaux solaires — Imagerie thermique (infrarouge)

Détection automatisée d'anomalies thermiques sur modules photovoltaïques à partir d'**imagerie infrarouge de drone**, par **apprentissage profond (Deep Learning)** et **transfer learning**.

Ce projet reproduit une brique clé de l'inspection automatisée de centrales solaires : à partir d'une image thermique d'un module PV, le modèle prédit s'il est sain ou affecté par l'une de **11 anomalies** (point chaud, cellule défectueuse, diode, salissure, ombrage, etc.).

---

## 🎯 Objectif

| | |
|---|---|
| **Tâche** | Classification d'images thermiques (12 classes) |
| **Modalité** | Imagerie infrarouge (thermique), 40×24 px niveaux de gris |
| **Approche** | Transfer learning (ResNet-18 pré-entraîné ImageNet) |
| **Enjeu** | Fort déséquilibre de classes (la classe *No-Anomaly* domine) |
| **Métriques** | Macro F1-score, accuracy, matrice de confusion |

---

## 📦 Dataset — InfraredSolarModules (Raptor Maps)

~20 000 images thermiques de modules PV, réparties en 12 classes.

1. Télécharger le dataset depuis le dépôt officiel : **https://github.com/RaptorMaps/InfraredSolarModules**
2. Le décompresser dans `data/` de sorte à obtenir :

```
data/
├── images/                 # sous-dossiers par classe (PNG thermiques)
└── module_metadata.json    # mapping image -> classe d'anomalie
```

> Les 12 classes : `Cell`, `Cell-Multi`, `Cracking`, `Hot-Spot`, `Hot-Spot-Multi`,
> `Shadowing`, `Diode`, `Diode-Multi`, `Vegetation`, `Soiling`, `Offline-Module`, `No-Anomaly`.

---

## 🗂️ Structure du projet

```
solar-thermal-defect-detection/
├── README.md
├── requirements.txt
├── data/                   # dataset (non versionné)
├── models/                 # poids entraînés (non versionné)
├── outputs/                # métriques, matrice de confusion, Grad-CAM
└── src/
    ├── dataset.py          # Dataset PyTorch + splits stratifiés
    ├── model.py            # ResNet-18 (transfer learning)
    ├── train.py            # entraînement + validation (gestion du déséquilibre)
    ├── evaluate.py         # métriques + matrice de confusion sur le test
    ├── gradcam.py          # explicabilité (carte de chaleur Grad-CAM)
    └── explore.py          # distribution des classes
```

---

## ⚙️ Installation

```bash
# Windows (la commande "python" est masquée -> on utilise "py")
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

---

## 🚀 Utilisation

```bash
# 1. Explorer la distribution des classes
py src/explore.py --data_dir data

# 2. Entraîner (transfer learning ResNet-18)
py src/train.py --data_dir data --epochs 15 --batch_size 64

# 3. Évaluer sur le jeu de test (métriques + matrice de confusion)
py src/evaluate.py --data_dir data

# 4. Visualiser une carte de chaleur Grad-CAM sur une image
py src/gradcam.py --image data/images/Hot-Spot/xxxx.png
```

---

## 📊 Résultats

> À compléter après l'entraînement avec **tes vrais chiffres** (`outputs/metrics.json`).

| Métrique | Score |
|---|---|
| Accuracy (test) | _à compléter_ |
| Macro F1-score | _à compléter_ |

Matrice de confusion : `outputs/confusion_matrix.png`
Exemple d'explicabilité (Grad-CAM) : `outputs/gradcam.png`

---

## 🧠 Choix techniques

- **Transfer learning** (ResNet-18 ImageNet) : images thermiques redimensionnées en 224×224 et converties en 3 canaux.
- **Déséquilibre de classes** : pondération des classes (`balanced`) dans la fonction de perte.
- **Augmentation de données** : flip horizontal + rotation légère.
- **Sélection du modèle** : meilleur **macro F1** sur la validation (et non l'accuracy, trompeuse en cas de déséquilibre).
- **Explicabilité** : Grad-CAM pour vérifier que le modèle regarde bien la zone chaude.

---

## 👤 Auteur

**Souleymane Diallo** — Élève-ingénieur IA & Data Science, ENSAM Meknès
[LinkedIn](https://www.linkedin.com/in/souleymane-diallo-51214728b/) · [Portfolio](https://jeuf-tech-portfolio.vercel.app/)
