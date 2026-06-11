import threading
import time
import utils.simulation_params as sim_params
from controller.events import e_sim_running, e_sim_stop, e_sim_reset
from utils.simulation_params import initial_tank_level


class LevelDynamics(threading.Thread):
    def __init__(self, stop_event, input_valve, output_valve, bus):
        super().__init__()
        self.stop_event = stop_event  # Stop signal
        self._level = sim_params.initial_tank_level
        self.name = "Level Dynamics"
        self.input_valve = input_valve
        self.output_valve = output_valve
        self.simulation_running = False
        self.bus = bus


        self.msg_queue = self.bus.register(self.name)

    @property
    def level(self):
        """Returns tank level"""
        return self._level

    @level.setter
    def level(self, value):
        self._level = value


    def start(self):
        super().start()
        print(self.name, " thread initialized.")

    def start_simulation(self):
        self.simulation_running = True

    def stop_simulation(self):
        self.simulation_running = False

    def reset_simulation(self):
        self.simulation_running = False
        self.level = initial_tank_level
        self.input_valve.reset()
        self.output_valve.reset()


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
                # Simulates level dynamics
                tank_input_flow = self.input_valve.input_flow
                tank_output_flow = self.output_valve.output_flow
                self.level += sim_params.DELTA_T * (tank_input_flow - tank_output_flow) / sim_params.A_T
                self.level = max(0, self.level)  # Avoids negative level



                time.sleep(0.2)
        print(self.name, " thread stopped.")

