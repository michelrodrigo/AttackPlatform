import threading
import time
import utils.simulation_params as sim_params
from controller.events import e_sim_running, e_sim_stop, e_sim_reset


class TempDynamics(threading.Thread):
    def __init__(self, stop_event, controller, heater, bus):
        super().__init__()
        self.stop_event = stop_event  # Stop signal
        self.controller = controller
        self.temperature = sim_params.tank_temperature  # Temperatura inicial
        self.name = "Temperature Dynamics"
        self.heater = heater
        self.simulation_running = False
        self.bus = bus

        self.msg_queue = self.bus.register(self.name)

    def start(self):
        super().start()
        print(self.name, " thread initialized.")

    def start_simulation(self):
        self.simulation_running = True

    def stop_simulation(self):
        self.simulation_running = False

    def reset_simulation(self):
        self.simulation_running = False
        self.temperature = sim_params.tank_temperature
        self.heater.reset()
        #self.bus.send_message({"source": "LevelSensor", "type": "variable_update", "data": self.level})


    def run(self):
        while not self.stop_event.is_set():

            if self.bus.wait_for_new_message(self.name, timeout=1):  # Timeout evita bloqueio eterno
                messages = self.bus.get_messages(self.name)
                controller_messages = [msg for msg in messages if msg.get("source") == "Controller"]
                for message in controller_messages:
                    if message.get("source") == "Controller" and message.get("type") == "command":
                        command_value = message.get("data")
                        if command_value == e_sim_running:
                            self.start_simulation()
                        elif command_value == e_sim_stop:
                            self.stop_simulation()
                        elif command_value == e_sim_reset:
                            self.reset_simulation()

            if self.simulation_running:
                potencia = self.heater.heater_power
                vazao = ...
                efeito_entrada = 0
                self.temperature += sim_params.DELTA_T * (potencia/100 - efeito_entrada)
                self.controller.data_queue.put({"dynamic": "temperature", "value": self.temperature})
                time.sleep(sim_params.DELTA_T)


        print(self.name, " thread stopped.")