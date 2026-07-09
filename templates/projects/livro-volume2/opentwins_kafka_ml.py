import json
import time
import random

try:
    from kafka import KafkaProducer
    HAS_KAFKA = True
except ImportError:
    HAS_KAFKA = False

class KafkaMLConnector:
    """
    Integra o OpenCode Ecosystem ao Kafka-ML do OpenTwins.
    Envia matrizes de dados de mastigação estocástica (Força, Ângulo X, Y)
    para o tópico de entrada de inferência do Kafka-ML.
    """
    def __init__(self, broker="localhost:9092", topic_in="opentwins.ml.input"):
        self.broker = broker
        self.topic_in = topic_in
        self.producer = None
        
        if HAS_KAFKA:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=[self.broker],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
            except Exception as e:
                print(f"[Kafka-ML] Erro ao conectar com Kafka broker: {e}")
                self.producer = None

    def send_raw_biomechanics(self, force_newtons, angle_x, angle_y):
        """
        Envia os inputs brutos. O modelo no Kafka-ML (TensorFlow/PyTorch)
        irá consumi-los e prever a probabilidade de reabsorção óssea.
        """
        payload = [force_newtons, angle_x, angle_y]
        
        if self.producer:
            self.producer.send(self.topic_in, payload)
            self.producer.flush()
            print(f"[Kafka-ML] Input bruto enviado para {self.topic_in}: {payload}")
        else:
            print(f"[Kafka-ML DryRun] Enviaria para o tópico '{self.topic_in}': {payload}")

if __name__ == "__main__":
    print("=== INICIANDO CONECTOR KAFKA-ML (OPENCODE PREDICTIVE) ===")
    connector = KafkaMLConnector()
    
    # Simula 5 ciclos de mordida humana para predição
    try:
        for i in range(5):
            f_n = round(random.uniform(200.0, 350.0), 2)
            a_x = round(random.uniform(-15.0, 15.0), 2)
            a_y = round(random.uniform(-15.0, 15.0), 2)
            
            connector.send_raw_biomechanics(f_n, a_x, a_y)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    print("=== CONECTOR KAFKA-ML FINALIZADO ===")
