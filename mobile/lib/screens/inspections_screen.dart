import 'package:flutter/material.dart';
import '../api.dart';
import 'panels_screen.dart';

class InspectionsScreen extends StatefulWidget {
  const InspectionsScreen({super.key});

  @override
  State<InspectionsScreen> createState() => _InspectionsScreenState();
}

class _InspectionsScreenState extends State<InspectionsScreen> {
  late Future<List<Inspection>> _future;

  @override
  void initState() {
    super.initState();
    _future = Api.inspections();
  }

  void _reload() => setState(() => _future = Api.inspections());

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('☀️ SolarScan — Inspections')),
      body: RefreshIndicator(
        onRefresh: () async => _reload(),
        child: FutureBuilder<List<Inspection>>(
          future: _future,
          builder: (context, snap) {
            if (snap.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snap.hasError) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text(
                    'Erreur de connexion à l\'API :\n${snap.error}\n\n'
                    'Vérifie kApiBase dans lib/api.dart',
                    textAlign: TextAlign.center,
                  ),
                ),
              );
            }
            final items = snap.data ?? [];
            if (items.isEmpty) {
              return const Center(child: Text('Aucune inspection'));
            }
            return ListView(
              children: items
                  .map((i) => Card(
                        margin: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 6),
                        child: ListTile(
                          leading: const Icon(Icons.solar_power),
                          title: Text(i.nom),
                          subtitle: Text(
                              '${i.nPanneaux} panneaux · ${i.nAnomalies} anomalies'),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (_) => PanelsScreen(inspection: i)),
                          ),
                        ),
                      ))
                  .toList(),
            );
          },
        ),
      ),
    );
  }
}
