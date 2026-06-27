import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../api.dart';

class PanelsScreen extends StatefulWidget {
  final Inspection inspection;
  const PanelsScreen({super.key, required this.inspection});

  @override
  State<PanelsScreen> createState() => _PanelsScreenState();
}

class _PanelsScreenState extends State<PanelsScreen> {
  late Future<List<Panel>> _future;

  @override
  void initState() {
    super.initState();
    _future = Api.panels(widget.inspection.id);
  }

  void _reload() =>
      setState(() => _future = Api.panels(widget.inspection.id));

  Color _sevColor(String s) {
    switch (s) {
      case 'Critique':
        return Colors.red;
      case 'Eleve':
        return Colors.orange;
      case 'Modere':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  Future<void> _navigate(Panel p) async {
    if (p.lat == null || p.lon == null) return;
    final uri = Uri.parse(
        'https://www.google.com/maps/search/?api=1&query=${p.lat},${p.lon}');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  Future<void> _setStatus(Panel p, String statut) async {
    await Api.setStatus(p.id, statut);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Panneau #${p.id} → $statut')),
    );
    _reload();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.inspection.nom)),
      body: FutureBuilder<List<Panel>>(
        future: _future,
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          final panels = snap.data ?? [];
          if (panels.isEmpty) {
            return const Center(child: Text('Aucune anomalie 🎉'));
          }
          return ListView(
            children: panels.map((p) => _panelCard(p)).toList(),
          );
        },
      ),
    );
  }

  Widget _panelCard(Panel p) {
    final color = _sevColor(p.severite);
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(p.severite,
                      style: TextStyle(
                          color: color, fontWeight: FontWeight.bold)),
                ),
                const SizedBox(width: 8),
                Text(p.classe,
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                const Spacer(),
                Text('${p.perteEurAn.toStringAsFixed(0)} €/an'),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              'Panneau #${p.id} · confiance ${(p.confiance * 100).round()}% · ${p.statut}',
              style: TextStyle(color: Colors.grey[400], fontSize: 12),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              children: [
                if (p.lat != null)
                  OutlinedButton.icon(
                    onPressed: () => _navigate(p),
                    icon: const Icon(Icons.navigation, size: 16),
                    label: const Text('Naviguer'),
                  ),
                FilledButton.tonal(
                    onPressed: () => _setStatus(p, 'valide'),
                    child: const Text('Valider')),
                FilledButton.tonal(
                    onPressed: () => _setStatus(p, 'fausse_alerte'),
                    child: const Text('Fausse alerte')),
                FilledButton.tonal(
                    onPressed: () => _setStatus(p, 'repare'),
                    child: const Text('Réparé')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
