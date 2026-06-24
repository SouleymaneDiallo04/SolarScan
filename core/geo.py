"""Géoréférencement RÉEL à partir des métadonnées EXIF d'une image drone.

Les drones (DJI, etc.) inscrivent la position GPS dans l'EXIF de chaque cliché.
On la lit telle quelle — aucune coordonnée inventée. Si l'image n'a pas de GPS
(ex. vignette recadrée du dataset), on retourne None, honnêtement.
"""
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def _to_degrees(value) -> float:
    d, m, s = value
    return float(d) + float(m) / 60.0 + float(s) / 3600.0


def extract_gps(path):
    """Retourne (lat, lon) lus dans l'EXIF, ou None si absents."""
    try:
        exif = Image.open(path)._getexif()
    except Exception:
        return None
    if not exif:
        return None

    gps = {}
    for tag, val in exif.items():
        if TAGS.get(tag) == 'GPSInfo':
            for t, v in val.items():
                gps[GPSTAGS.get(t, t)] = v

    if 'GPSLatitude' not in gps or 'GPSLongitude' not in gps:
        return None

    lat = _to_degrees(gps['GPSLatitude'])
    if gps.get('GPSLatitudeRef') == 'S':
        lat = -lat
    lon = _to_degrees(gps['GPSLongitude'])
    if gps.get('GPSLongitudeRef') == 'W':
        lon = -lon
    return (round(lat, 7), round(lon, 7))
