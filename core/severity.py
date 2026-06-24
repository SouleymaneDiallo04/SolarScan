"""Sévérité et estimation de perte de puissance par type de défaut.

Barème inspiré des taxonomies d'inspection PV (Raptor Maps, IEC TS 62446-3).
`loss` = fraction de la puissance du module affecté qui est perdue (estimation).
Tous les paramètres économiques sont configurables (Wp, productible, prix).
"""

# type de défaut -> (sévérité, fraction de perte du module)
SEVERITY = {
    'No-Anomaly':     ('OK',       0.00),
    'Soiling':        ('Faible',   0.03),
    'Vegetation':     ('Faible',   0.05),
    'Cracking':       ('Modere',   0.05),
    'Cell':           ('Modere',   0.10),
    'Shadowing':      ('Modere',   0.10),
    'Cell-Multi':     ('Eleve',    0.20),
    'Hot-Spot':       ('Eleve',    0.25),
    'Hot-Spot-Multi': ('Eleve',    0.30),
    'Diode':          ('Eleve',    0.33),
    'Diode-Multi':    ('Critique', 0.66),
    'Offline-Module': ('Critique', 1.00),
}
RANK = {'OK': 0, 'Faible': 1, 'Modere': 2, 'Eleve': 3, 'Critique': 4}


def assess(classe, module_wp=400, specific_yield=1600, price_eur_kwh=0.10):
    """Évalue l'impact d'un défaut sur un module.

    module_wp      : puissance crête du module (Wc)
    specific_yield : productible annuel du site (kWh/kWc/an) — ~1600 au Maroc
    price_eur_kwh  : prix de revente / coût évité (€/kWh)
    """
    sev, loss = SEVERITY.get(classe, ('Inconnu', 0.0))
    prod_kwh_an = module_wp / 1000.0 * specific_yield       # productible annuel du module
    lost_kwh = round(prod_kwh_an * loss, 1)
    return {
        'severite': sev,
        'rang': RANK.get(sev, 0),
        'perte_pct': round(loss * 100, 1),
        'perte_kwh_an': lost_kwh,
        'perte_eur_an': round(lost_kwh * price_eur_kwh, 2),
    }
