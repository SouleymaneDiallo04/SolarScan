# SolarScan Mobile — app terrain (Flutter)

App de l'ingénieur/technicien sur site : liste des inspections, **anomalies
priorisées par gravité**, **navigation GPS** vers le panneau, et **mise à jour
du statut** (validé / fausse alerte / réparé). Elle consomme l'API SolarScan.

## Écrans
- **Inspections** — la liste, avec nombre d'anomalies.
- **Anomalies** — triées par sévérité, avec perte €/an, bouton **Naviguer**
  (ouvre Google Maps aux coordonnées GPS) et actions de **workflow**.

## Lancer
Prérequis : [Flutter SDK](https://docs.flutter.dev/get-started/install) + l'API
SolarScan qui tourne (`docker compose up -d` → port 8090).

```bash
cd mobile
flutter create .          # génère les dossiers de plateforme (android/ios/web)
flutter pub get
flutter run               # choisir un appareil / émulateur / Chrome
```

## Configurer l'URL de l'API
Dans `lib/api.dart`, ajuste `kApiBase` selon la cible :

| Cible | `kApiBase` |
|---|---|
| Émulateur Android | `http://10.0.2.2:8090` |
| Flutter web (Chrome) | `http://localhost:8090` |
| Téléphone réel (même Wi-Fi) | `http://<IP_DU_PC>:8090` |

> L'API expose **CORS** (`allow_origins=*`) pour permettre l'appel depuis le web/l'appareil.

## Dépendances
- `http` — appels à l'API REST.
- `url_launcher` — ouverture de l'app de navigation GPS.
