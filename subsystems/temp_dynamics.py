import threading
import time
from utils.simulation_params import DELTA_T


class TempDynamics(threading.Thread):
    def __init__(self, stop_event, controller, bus):
        super().__init__()
        self.stop_event = stop_event  # Stop signal
        self.controller = controller
        self.temperatura = 20.0  # Temperatura inicial
        self.name = "Temperature Dynamics"

    def start(self):
        super().start()
        print(self.name, " thread initialized.")

    def run(self):
        while not self.stop_event.is_set():
            potencia = ...
            vazao = ...
            efeito_entrada = ...
            self.temperatura += DELTA_T * (potencia - efeito_entrada)
            self.controller.data_queue.put({"dynamic": "temperature", "value": self.temperatura})
            time.sleep(DELTA_T)
        print(self.name, " thread stopped.")