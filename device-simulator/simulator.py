import json
import random
import time
from datetime import datetime
from azure.iot.device import IoTHubDeviceClient, Message

# Dane połączenia (uzupełnisz później)
CONNECTION_STRING = "HostName=hub-inteligentna-waga-123.azure-devices.net;DeviceId=waga-01;SharedAccessKey=WrMi6oKtDy9D8AH1Gm8Uph4ow683yHM4H/jImL/L3Sc="

class SmartScaleSimulator:
    def __init__(self):
        self.client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        
    def generate_measurement(self):
        """Generuje losowe pomiary wagi"""
        return {
            "timestamp": datetime.now().isoformat(),
            "weight": round(random.uniform(60.0, 90.0), 1),
            "body_fat": round(random.uniform(15.0, 30.0), 1),
            "muscle_mass": round(random.uniform(25.0, 40.0), 1),
            "water_percentage": round(random.uniform(50.0, 65.0), 1),
            "bone_mass": round(random.uniform(2.0, 4.0), 1),
            "bmi": round(random.uniform(18.0, 30.0), 1)
        }
    
    def send_telemetry(self):
        """Wysyła dane do Azure IoT Hub"""
        try:
            self.client.connect()
            
            while True:
                data = self.generate_measurement()
                message = Message(json.dumps(data))
                message.content_type = "application/json"
                
                print(f"Wysyłam: {data}")
                self.client.send_message(message)
                
                time.sleep(10)  # Czeka 10 sekund między pomiarami
                
        except KeyboardInterrupt:
            print("Zatrzymano symulator")
        finally:
            self.client.disconnect()

if __name__ == "__main__":
    simulator = SmartScaleSimulator()
    simulator.send_telemetry()
