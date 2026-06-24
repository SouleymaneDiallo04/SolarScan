# SolarScan 🔆 — Détection de défauts sur panneaux solaires par imagerie thermique

Détection automatisée d'anomalies thermiques sur modules photovoltaïques à partir d'**imagerie infrarouge de drone**, par **apprentissage profond (Deep Learning)** et **transfer learning**.

Ce projet reproduit une brique clé de l'inspection automatisée de centrales solaires : à partir d'une image thermique d'un module PV, le modèle prédit s'il est sain ou affecté par l'une de **11 anomalies** (point chaud, cellule défectueuse, diode, salissure, ombrage, etc.).

---

## 🎯 Objectif

| | |
|---|---|
| **Tâche** | Classification d'images thermiques (12 classes) |
| **Modalité** | Imagerie infrarouge (thermique), 40×24 px niveaux de gris |
| **Approche** | Transfer learning (ResNet-18 → EfficientNet-B0) + TTA |
| **Enjeu** | Fort déséquilibre de classes (la classe *No-Anomaly* domine) |
| **Métriques** | Macro F1-score, accuracy, matrice de confusion |

---

## 📦 Dataset — InfraredSolarModules (Raptor Maps)

~20 000 images thermiques de modules PV, réparties en 12 classes.

Le dataset est distribué en une archive **`2020-02-14_InfraredSolarModules.zip`**. Télécharge-la depuis le [dépôt officiel](https://github.com/RaptorMaps/InfraredSolarModules) et décompresse-la dans `data/` pour obtenir :

```
data/
├── images/                 # 20 000 images thermiques .jpg, nommées par numéro (ex. 0.jpg)
└── module_metadata.json    # mapping numéro d'image -> classe d'anomalie
```

> Format du JSON : `{"0": {"image_filepath": "images/0.jpg", "anomaly_class": "Cell"}, ...}`
> Les images sont **à plat** dans `images/` (pas de sous-dossiers) ; la classe vient du JSON.

> Les 12 classes : `Cell`, `Cell-Multi`, `Cracking`, `Hot-Spot`, `Hot-Spot-Multi`,
> `Shadowing`, `Diode`, `Diode-Multi`, `Vegetation`, `Soiling`, `Offline-Module`, `No-Anomaly`.

---

## 🗂️ Structure du projet

```
SolarScan/
├── README.md
├── requirements.txt
├── data/                   # dataset (non versionné)
├── splits/                 # découpages train/val/test (CSV)
├── notebooks/
│   ├── 01_eda.ipynb                    # exploration des données (EDA)
│   ├── 02_data_preparation.ipynb       # splits stratifiés
│   ├── 03_baseline.ipynb               # baseline (Dummy + Random Forest)
│   ├── 04_cnn_transfer_learning.ipynb  # ResNet-18 (transfer learning)
│   ├── 04b_cnn_improved.ipynb          # recipe amélioré
│   ├── 04c_cnn_v3.ipynb                # EfficientNet-B0 + TTA (final)
│   └── 05_gradcam.ipynb                # explicabilité (Grad-CAM)
└── src/                    # scripts CLI (alternative aux notebooks)
    ├── dataset.py · model.py · train.py · evaluate.py · gradcam.py · explore.py
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
py src/gradcam.py --image data/images/1000.jpg
```

---

## 📊 Résultats

Démarche **itérative** — chaque version corrige une faiblesse mesurée de la précédente :

| Modèle | Accuracy (test) | Macro-F1 (test) |
|---|---|---|
| ResNet-18 — transfer learning de base | 0.58 | 0.49 |
| ResNet-18 — recipe amélioré *(2 phases, LR↓ + cosine, pondération adoucie, label smoothing)* | 0.80 | 0.65 |
| **EfficientNet-B0 + TTA — modèle final** | **0.79** | **0.66** |

> Un classifieur naïf (toujours *No-Anomaly*) plafonne à ~0.06 de macro-F1 malgré ~50 % d'accuracy → d'où le choix du **macro-F1** comme métrique principale.

**Lecture par classe :** les anomalies à signature spatiale nette sont bien détectées (**Diode** F1 0.96, **No-Anomaly** 0.89) ; les classes rares et subtiles (**Soiling**, **Hot-Spot**) restent plus difficiles — limite liée au **faible nombre d'exemples** (31-37 en test), pas au modèle.

Toute la démarche (EDA → préparation → baseline → modélisation → amélioration) est détaillée dans les notebooks `notebooks/01` à `04c`.

---

## 🧠 Choix techniques

- **Transfer learning en 2 phases** : on entraîne d'abord la tête (backbone gelé), puis on fine-tune tout avec un LR faible (1e-4) + cosine — pour ne pas détruire les features pré-entraînées.
- **Déséquilibre de classes** : pondération adoucie (√) puis **sur-échantillonnage** (`WeightedRandomSampler`) des classes rares.
- **Régularisation** : AdamW + weight decay, label smoothing, augmentation (flips, rotation, translation).
- **Test-Time Augmentation (TTA)** : moyenne des prédictions sur l'image et ses miroirs (gain « gratuit »).
- **Sélection du modèle** : meilleur **macro-F1** sur la validation (et non l'accuracy, trompeuse en cas de déséquilibre).
- **Explicabilité** : Grad-CAM pour vérifier que le modèle regarde bien la zone chaude.

---

## 👤 Auteur

**Souleymane Diallo** — Élève-ingénieur IA & Data Science, ENSAM Meknès
[LinkedIn](https://www.linkedin.com/in/souleymane-diallo-51214728b/) · [Portfolio](https://jeuf-tech-portfolio.vercel.app/)
