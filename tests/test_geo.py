"""Test du géoréférencement EXIF (core.geo).

Valide la chaîne RÉELLE : on écrit un GPS dans l'EXIF d'une image (format
identique à celui des drones), puis on vérifie que `extract_gps` le relit bien
— signe d'hémisphère compris (Benguerir est en longitude Ouest).

    py tests/test_geo.py
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import piexif
from PIL import Image

from core.geo import extract_gps


def _to_dms(value):
    d = int(value)
    m = int((value - d) * 60)
    s = (((value - d) * 60) - m) * 60
    return ((d, 1), (m, 1), (int(round(s * 10000)), 10000))


def write_gps(src, dst, lat, lon):
    """Écrit (lat, lon) dans l'EXIF d'une copie JPEG de `src`."""
    gps = {
        piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
        piexif.GPSIFD.GPSLatitude: _to_dms(abs(lat)),
        piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
        piexif.GPSIFD.GPSLongitude: _to_dms(abs(lon)),
    }
    Image.open(src).convert('RGB').save(dst, 'jpeg', exif=piexif.dump({'GPS': gps}))


def test_extract_gps():
    src = next((ROOT / 'data' / 'images').glob('*.jpg'))
    lat, lon = 32.2230, -7.9540  # Benguerir (longitude Ouest -> teste le signe)

    with tempfile.TemporaryDirectory() as d:
        tagged = Path(d) / 'drone.jpg'
        write_gps(src, tagged, lat, lon)
        got = extract_gps(tagged)

    assert got is not None, "GPS non extrait de l'EXIF"
    assert abs(got[0] - lat) < 1e-3, f"latitude fausse : {got}"
    assert abs(got[1] - lon) < 1e-3, f"longitude fausse : {got}"
    # Une image sans GPS doit renvoyer None (comportement honnête)
    assert extract_gps(src) is None, "devrait renvoyer None sans EXIF GPS"
    print('OK — GPS extrait :', got, '| image sans EXIF -> None')


if __name__ == '__main__':
    test_extract_gps()
