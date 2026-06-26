import 'package:flutter/material.dart';
import 'screens/inspections_screen.dart';

void main() => runApp(const SolarScanApp());

class SolarScanApp extends StatelessWidget {
  const SolarScanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SolarScan',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFFF59E0B),
        brightness: Brightness.dark,
        useMaterial3: true,
      ),
      home: const InspectionsScreen(),
    );
  }
}
