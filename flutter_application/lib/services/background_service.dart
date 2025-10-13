import 'package:workmanager/workmanager.dart';

@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    switch (task) {
      case 'stationProximityCheck':
        print('🚇 Проверка приближения к станции...');
        // TODO: Логика проверки геолокации
        return true;
      default:
        return false;
    }
  });
}