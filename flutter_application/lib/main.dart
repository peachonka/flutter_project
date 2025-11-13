import 'package:flutter/material.dart';
import 'package:workmanager/workmanager.dart';
import 'screens/home_screen.dart';
import 'services/background_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Инициализация фоновой службы
  Workmanager().initialize(
    callbackDispatcher,
    isInDebugMode: true,  // Для отладки
  );
  
  runApp(const MetroAlarmApp());
}

class MetroAlarmApp extends StatelessWidget {
  const MetroAlarmApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Metro Alarm',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
