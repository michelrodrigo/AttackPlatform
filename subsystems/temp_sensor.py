import threading
import time

class TempSensor(threading.Thread):
    def __init__(self, stop_event, controller, bus):
        super().__init__()
        self.stop_event = stop_event  # Stop signal
        self.controller = controller
        self.control_on = False
        self.setpoint = 60.0  # Setpoint inicial
        self.kp = 1.0
        self.ki = 0.1
        self.integral = 0.0
        self.name = "Temperature Sensor"

    def start(self):
        super().start()
        print(self.name, " thread initialized.")

    def run(self):
        while not self.stop_event.is_set():
            temperatura_atual = ...  # Obter temperatura atual
            if self.control_on:
                erro = self.setpoint - temperatura_atual
                self.integral += erro * DELTA_T
                potencia = self.kp * erro + self.ki * self.integral
                self.controller.send_command({"heater_power": potencia})
            self.controller.data_queue.put({"sensor": "temperature", "value": temperatura_atual})
            time.sleep(0.1)
        print(self.name, " thread stopped.")