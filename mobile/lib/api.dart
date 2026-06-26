import 'dart:convert';
import 'package:http/http.dart' as http;

/// URL de l'API SolarScan. Adapte selon la cible :
///  - Emulateur Android      : http://10.0.2.2:8090
///  - Flutter web (Chrome)   : http://localhost:8090
///  - Téléphone réel (Wi-Fi) : http://<IP_DU_PC>:8090
const String kApiBase = 'http://10.0.2.2:8090';

class Inspection {
  final int id;
  final String nom;
  final int nPanneaux;
  final int nAnomalies;

  Inspection.fromJson(Map<String, dynamic> j)
      : id = j['id'],
        nom = j['nom'] ?? 'Inspection',
        nPanneaux = j['n_panneaux'] ?? 0,
        nAnomalies = j['n_anomalies'] ?? 0;
}

class Panel {
  final int id;
  final String classe;
  final String severite;
  final double confiance;
  final double perteEurAn;
  final double? lat;
  final double? lon;
  final int anomalie;
  String statut;

  Panel.fromJson(Map<String, dynamic> j)
      : id = j['id'],
        classe = j['classe'] ?? '',
        severite = j['severite'] ?? 'OK',
        confiance = (j['confiance'] ?? 0).toDouble(),
        perteEurAn = (j['perte_eur_an'] ?? 0).toDouble(),
        lat = (j['lat'] as num?)?.toDouble(),
        lon = (j['lon'] as num?)?.toDouble(),
        anomalie = j['anomalie'] ?? 0,
        statut = j['statut'] ?? 'a_valider';
}

class Api {
  static Future<List<Inspection>> inspections() async {
    final r = await http.get(Uri.parse('$kApiBase/inspections'));
    final list = jsonDecode(utf8.decode(r.bodyBytes)) as List;
    return list.map((e) => Inspection.fromJson(e)).toList();
  }

  /// Anomalies d'une inspection, déjà triées par gravité côté API.
  static Future<List<Panel>> panels(int inspectionId) async {
    final r = await http.get(Uri.parse('$kApiBase/inspections/$inspectionId'));
    final data = jsonDecode(utf8.decode(r.bodyBytes)) as Map<String, dynamic>;
    return (data['panels'] as List)
        .map((e) => Panel.fromJson(e))
        .where((p) => p.anomalie == 1)
        .toList();
  }

  static Future<void> setStatus(int panelId, String statut) async {
    await http.patch(
      Uri.parse('$kApiBase/panels/$panelId'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'statut': statut}),
    );
  }
}
