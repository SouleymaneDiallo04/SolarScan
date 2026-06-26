"""Démo GPS — geotague des images d'exemple (GPS de TEST dans l'EXIF).

But : valider/visualiser la chaîne RÉELLE  EXIF -> pipeline -> base -> carte,
sans attendre de vraies images drone. Les coordonnées sont des valeurs de TEST
réparties autour de Benguerir ; de vraies images drone portent déjà leur GPS
réel et passent par exactement le même code (`core/geo.py`).

    py pipeline/geotag_demo.py
    # puis envoyer le dossier de sortie a l'API :
    #   POST /inspections  (les images contiennent maintenant un GPS EXIF)
"""
import argparse
import math
from pathlib import Path

import piexif
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def _to_dms(value):
    d = int(value)
    m = int((value - d) * 60)
    s = (((value - d) * 60) - m) * 60
    return ((d, 1), (m, 1), (int(round(s * 10000)), 10000))


def geotag(src, dst, lat, lon):
    gps = {
        piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
        piexif.GPSIFD.GPSLatitude: _to_dms(abs(lat)),
        piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
        piexif.GPSIFD.GPSLongitude: _to_dms(abs(lon)),
    }
    Image.open(src).convert('RGB').save(dst, 'jpeg', exif=piexif.dump({'GPS': gps}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--images_dir', default=str(ROOT / 'data' / 'images'))
    ap.add_argument('--out', default=str(ROOT / 'data' / 'geo_demo'))
    ap.add_argument('--n', type=int, default=12)
    ap.add_argument('--rows', type=int, default=3)
    ap.add_argument('--base_lat', type=float, default=32.2230)   # Benguerir
    ap.add_argument('--base_lon', type=float, default=-7.9540)
    ap.add_argument('--spacing_m', type=float, default=3.0)
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    imgs = sorted(Path(a.images_dir).glob('*.jpg'))[:a.n]
    cols = math.ceil(len(imgs) / a.rows)
    d_lat = a.spacing_m / 111320.0
    d_lon = a.spacing_m / (111320.0 * math.cos(math.radians(a.base_lat)))

    for k, src in enumerate(imgs):
        r, c = divmod(k, cols)
        geotag(src, out / f'panel_{k:03d}.jpg',
               a.base_lat + r * d_lat, a.base_lon + c * d_lon)

    print(f'{len(imgs)} images geotaguees (GPS de TEST dans l EXIF) -> {out}')


if __name__ == '__main__':
    main()
