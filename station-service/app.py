from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Загружаем данные Московского метро
def load_metro_data():
    try:
        with open('moscow_metro.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Metro data file not found"}

@app.route('/stations', methods=['GET'])
def get_all_stations():
    """Возвращает список всех станций метро"""
    metro_data = load_metro_data()
    
    all_stations = []
    for line in metro_data['lines']:
        for station in line['stations']:
            station_info = {
                "id": station['id'],
                "name": station['name'],
                "lat": station['lat'],
                "lng": station['lng'],
                "line_id": line['id'],
                "line_name": line['name'],
                "line_color": line['hex_color']
            }
            all_stations.append(station_info)
    
    return jsonify({
        "status": "success",
        "data": all_stations,
        "count": len(all_stations)
    })

@app.route('/stations/<station_id>', methods=['GET'])
def get_station(station_id):
    """Возвращает информацию о конкретной станции"""
    metro_data = load_metro_data()
    
    for line in metro_data['lines']:
        for station in line['stations']:
            if station['id'] == station_id:
                station_info = {
                    "id": station['id'],
                    "name": station['name'],
                    "lat": station['lat'],
                    "lng": station['lng'],
                    "line": {
                        "id": line['id'],
                        "name": line['name'],
                        "color": line['hex_color'],
                        "index": line.get('index', '')
                    }
                }
                return jsonify({"status": "success", "data": station_info})
    
    return jsonify({"status": "error", "message": "Station not found"}), 404

@app.route('/lines', methods=['GET'])
def get_lines():
    """Возвращает список всех линий метро"""
    metro_data = load_metro_data()
    
    lines = []
    for line in metro_data['lines']:
        line_info = {
            "id": line['id'],
            "name": line['name'],
            "color": line['hex_color'],
            "index": line.get('index', ''),
            "station_count": len(line['stations'])
        }
        lines.append(line_info)
    
    return jsonify({
        "status": "success",
        "data": lines,
        "count": len(lines)
    })

@app.route('/lines/<line_id>/stations', methods=['GET'])
def get_line_stations(line_id):
    """Возвращает станции конкретной линии"""
    metro_data = load_metro_data()
    
    for line in metro_data['lines']:
        if line['id'] == line_id:
            stations = []
            for station in line['stations']:
                station_info = {
                    "id": station['id'],
                    "name": station['name'],
                    "lat": station['lat'],
                    "lng": station['lng'],
                    "order": station.get('order', 0)
                }
                stations.append(station_info)
            
            return jsonify({
                "status": "success",
                "line": {
                    "id": line['id'],
                    "name": line['name'],
                    "color": line['hex_color']
                },
                "data": stations,
                "count": len(stations)
            })
    
    return jsonify({"status": "error", "message": "Line not found"}), 404

@app.route('/search', methods=['GET'])
def search_stations():
    """Поиск станций по названию"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"status": "error", "message": "Query parameter 'q' is required"}), 400
    
    metro_data = load_metro_data()
    
    results = []
    for line in metro_data['lines']:
        for station in line['stations']:
            if query in station['name'].lower():
                station_info = {
                    "id": station['id'],
                    "name": station['name'],
                    "lat": station['lat'],
                    "lng": station['lng'],
                    "line_id": line['id'],
                    "line_name": line['name'],
                    "line_color": line['hex_color']
                }
                results.append(station_info)
    
    return jsonify({
        "status": "success",
        "query": query,
        "data": results,
        "count": len(results)
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса"""
    return jsonify({"status": "healthy", "service": "station-service"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)