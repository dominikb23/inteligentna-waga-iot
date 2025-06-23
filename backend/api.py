from flask import Flask, jsonify, request
from flask_cors import CORS
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Konfiguracja Azure (uzupełnij swoimi danymi)
STORAGE_CONNECTION_STRING = "<twój-storage-connection-string>"
COSMOS_ENDPOINT = "<twój-cosmos-endpoint>"
COSMOS_KEY = "<twój-cosmos-key>"
DATABASE_NAME = "WeightDB"
CONTAINER_NAME = "Measurements"

# Inicjalizacja klientów
blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = cosmos_client.create_database_if_not_exists(DATABASE_NAME)
container = database.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key="/userId"
)

@app.route('/api/measurements', methods=['GET'])
def get_measurements():
    """Pobiera historię pomiarów"""
    user_id = request.args.get('userId', 'default')
    
    query = "SELECT * FROM c WHERE c.userId = @userId ORDER BY c.timestamp DESC"
    items = list(container.query_items(
        query=query,
        parameters=[{"name": "@userId", "value": user_id}],
        enable_cross_partition_query=True
    ))
    
    return jsonify(items)

@app.route('/api/measurements', methods=['POST'])
def save_measurement():
    """Zapisuje nowy pomiar"""
    data = request.json
    data['id'] = str(datetime.now().timestamp())
    data['userId'] = request.json.get('userId', 'default')
    data['timestamp'] = datetime.now().isoformat()
    
    container.create_item(body=data)
    
    # Zapisz też do Blob Storage jako backup
    blob_name = f"measurement_{data['id']}.json"
    blob_client = blob_service.get_blob_client(
        container="measurements", 
        blob=blob_name
    )
    blob_client.upload_blob(json.dumps(data))
    
    return jsonify({"status": "success", "id": data['id']})

@app.route('/api/costs', methods=['GET'])
def calculate_costs():
    """Kalkulator kosztów Azure"""
    # Przykładowe koszty (w USD/miesiąc)
    costs = {
        "IoT Hub F1": 0,  # Darmowy tier
        "Storage Account": 2.50,  # ~10GB
        "Cosmos DB": 25.00,  # Minimum
        "App Service": 0,  # Free tier
        "Total": 27.50
    }
    
    return jsonify(costs)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sprawdzenie działania API"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
