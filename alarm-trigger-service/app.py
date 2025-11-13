from flask import Flask, jsonify, request
from flask_cors import CORS
import math
import requests

app = Flask(__name__)
CORS(app)

# Конфигурация
STATION_SERVICE_URL = "http://station-service:5001"

def calculate_distance(lat1, lng1, lat2, lng2):
    """
    Расчет расстояния между двумя точками в километрах
    Используем формулу гаверсинусов
    """
    R = 6371  # Радиус Земли в километрах
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lng / 2) * math.sin(delta_lng / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def get_station_info(station_id):
    """Получает информацию о станции из station-service"""
    try:
        response = requests.get(f"{STATION_SERVICE_URL}/stations/{station_id}")
        if response.status_code == 200:
            return response.json()['data']
        else:
            return None
    except requests.exceptions.RequestException:
        return None

@app.route('/check_proximity', methods=['POST'])
def check_proximity():
    """
    Проверяет, находится ли пользователь вблизи целевой станции
    Ожидает JSON: {
        "user_lat": float, 
        "user_lng": float, 
        "target_station_id": string,
        "radius_km": float (опционально, по умолчанию 0.5)
    }
    """
    data = request.get_json()
    
    if not data or 'user_lat' not in data or 'user_lng' not in data or 'target_station_id' not in data:
        return jsonify({
            "status": "error",
            "message": "Missing required fields: user_lat, user_lng, target_station_id"
        }), 400

    user_lat = data['user_lat']
    user_lng = data['user_lng']
    target_station_id = data['target_station_id']
    radius_km = data.get('radius_km', 0.5)  # Радиус срабатывания в км

    # Получаем информацию о целевой станции
    target_station = get_station_info(target_station_id)
    
    if not target_station:
        return jsonify({"status": "error", "message": "Target station not found"}), 404

    station_lat = target_station['lat']
    station_lng = target_station['lng']

    # Рассчитываем расстояние
    distance_km = calculate_distance(user_lat, user_lng, station_lat, station_lng)
    
    # Переводим в метры для удобства
    distance_m = distance_km * 1000
    
    trigger_alarm = distance_km <= radius_km

    return jsonify({
        "status": "success",
        "data": {
            "trigger_alarm": trigger_alarm,
            "distance_km": round(distance_km, 3),
            "distance_m": round(distance_m, 1),
            "radius_km": radius_km,
            "user_position": {"lat": user_lat, "lng": user_lng},
            "station_position": {"lat": station_lat, "lng": station_lng},
            "station_info": {
                "id": target_station['id'],
                "name": target_station['name'],
                "line_name": target_station['line']['name']
            }
        }
    })

@app.route('/check_multiple_stations', methods=['POST'])
def check_multiple_stations():
    """
    Проверяет приближение к нескольким станциям одновременно
    Ожидает JSON: {
        "user_lat": float,
        "user_lng": float,
        "station_ids": [string],
        "radius_km": float (опционально)
    }
    """
    data = request.get_json()
    
    if not data or 'user_lat' not in data or 'user_lng' not in data or 'station_ids' not in data:
        return jsonify({
            "status": "error",
            "message": "Missing required fields: user_lat, user_lng, station_ids"
        }), 400

    user_lat = data['user_lat']
    user_lng = data['user_lng']
    station_ids = data['station_ids']
    radius_km = data.get('radius_km', 0.5)

    results = []
    nearest_station = None
    min_distance = float('inf')

    for station_id in station_ids:
        target_station = get_station_info(station_id)
        
        if target_station:
            station_lat = target_station['lat']
            station_lng = target_station['lng']
            distance_km = calculate_distance(user_lat, user_lng, station_lat, station_lng)
            distance_m = distance_km * 1000
            
            trigger_alarm = distance_km <= radius_km
            
            station_result = {
                "station_id": station_id,
                "station_name": target_station['name'],
                "line_name": target_station['line']['name'],
                "distance_km": round(distance_km, 3),
                "distance_m": round(distance_m, 1),
                "trigger_alarm": trigger_alarm
            }
            
            results.append(station_result)
            
            # Обновляем ближайшую станцию
            if distance_km < min_distance:
                min_distance = distance_km
                nearest_station = station_result

    return jsonify({
        "status": "success",
        "data": {
            "user_position": {"lat": user_lat, "lng": user_lng},
            "radius_km": radius_km,
            "stations": results,
            "nearest_station": nearest_station,
            "any_alarm_triggered": any(result['trigger_alarm'] for result in results)
        }
    })

@app.route('/simulate_trigger', methods=['GET'])
def simulate_trigger():
    """Эндпоинт для тестирования - всегда возвращает срабатывание"""
    return jsonify({
        "status": "success",
        "data": {
            "trigger_alarm": True,
            "message": "Alarm triggered - user is near the target station",
            "distance_km": 0.2,
            "distance_m": 200,
            "radius_km": 0.5
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса"""
    # Проверяем связь с station-service
    try:
        station_health = requests.get(f"{STATION_SERVICE_URL}/health").json()
        station_status = station_health.get('status', 'unknown')
    except:
        station_status = 'unreachable'
    
    return jsonify({
        "status": "healthy", 
        "service": "alarm-trigger-service",
        "station_service": station_status
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)