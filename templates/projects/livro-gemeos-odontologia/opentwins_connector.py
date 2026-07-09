import json
import time
import datetime
import random
try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

class OpenTwinsConnector:
    """
    Integração do OpenCode Ecosystem com o OpenTwins via Eclipse Ditto Protocol.
    Transmite os dados biomecânicos e ZKP do SUS-Twin para o Broker MQTT.
    """
    def __init__(self, broker="localhost", port=1883, namespace="opencode", twin_name="patient_001"):
        self.broker = broker
        self.port = port
        self.namespace = namespace
        self.twin_name = twin_name
        self.topic = f"telemetry/{namespace}/{twin_name}"
        self.client = None
        
        if HAS_MQTT:
            try:
                # Utiliza versão 2 do paho-mqtt compatível com os tutoriais OpenTwins
                self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
                self.client.on_connect = self.on_connect
            except AttributeError:
                # Fallback para versões antigas do paho-mqtt
                self.client = mqtt.Client()
                self.client.on_connect = self.on_connect_old

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"[OpenTwins] Conectado com sucesso ao Broker MQTT {self.broker}:{self.port}")
        else:
            print(f"[OpenTwins] Falha na conexão. Código: {rc}")

    def on_connect_old(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[OpenTwins] Conectado com sucesso ao Broker MQTT {self.broker}:{self.port}")
        else:
            print(f"[OpenTwins] Falha na conexão. Código: {rc}")

    def start(self):
        if not HAS_MQTT:
            print("[OpenTwins] Biblioteca 'paho-mqtt' não instalada. Operando em modo de simulação (Dry Run).")
            return
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"[OpenTwins] Erro ao conectar no broker: {e}. Executando offline.")

    def stop(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

    def build_ditto_protocol_msg(self, von_mises_stress, safety_factor, approval_status, proof_hash):
        """
        Formata o payload de acordo com o Eclipse Ditto Protocol.
        """
        timestamp = datetime.datetime.now().isoformat()
        
        return {
            "topic": f"{self.namespace}/{self.twin_name}/things/twin/commands/merge",
            "headers": {
                "content-type": "application/merge-patch+json"
            },
            "path": "/features",
            "value": {
                "biomechanics": {
                    "properties": {
                        "von_mises_stress_mpa": von_mises_stress,
                        "safety_factor": safety_factor,
                        "status_approval": approval_status,
                        "time": timestamp
                    }
                },
                "zkp_audit": {
                    "properties": {
                        "proof_hash": proof_hash,
                        "is_valid": True,
                        "time": timestamp
                    }
                }
            }
        }

    def publish_telemetry(self, von_mises_stress, safety_factor, approval_status, proof_hash):
        msg = self.build_ditto_protocol_msg(von_mises_stress, safety_factor, approval_status, proof_hash)
        payload = json.dumps(msg)
        
        if self.client and self.client.is_connected():
            self.client.publish(self.topic, payload)
            print(f"[OpenTwins] Payload enviado para {self.topic}: {payload}")
        else:
            print(f"[OpenTwins DryRun] Publicaria no tópico '{self.topic}':\n{json.dumps(msg, indent=2)}")

if __name__ == "__main__":
    print("=== INICIANDO CONECTOR OPENTWINS ===")
    connector = OpenTwinsConnector()
    connector.start()
    
    # Simulando um ciclo de análise biomecânica do pipeline
    try:
        for i in range(3):
            stress = round(random.uniform(80.0, 140.0), 2)
            factor = round(130.0 / stress, 2)
            status = "APROVAÇÃO" if factor > 1.5 else "ALERTA"
            zkp_hash = f"0x{(hash(stress) & 0xffffffff):08x}abcdef"
            
            connector.publish_telemetry(stress, factor, status, zkp_hash)
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        connector.stop()
        print("=== CONECTOR OPENTWINS FINALIZADO ===")
