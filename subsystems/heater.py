import threading
import time
from utils.simulation_params import *
from utils.colors import *
from controller.events import *
from automata_tool.automata import *
import random

# Creates the states for the heater automaton
s_heater_off = State("heater off", marked=True)
s_heater_on = State("heater on", marked=False)


#class for the heater element
class Heater(threading.Thread):

    def __init__(self, stop_event, controller, bus):
        super().__init__()
        self.stop_event = stop_event
        self.state = "off"
        self.controller = controller
        self.name = "Heater"
        self.bus = bus
        self.last_command = None
        self.heating = False

        # Previous states, to verify changes
        self.prev_heater_power = None

        self.msg_queue = self.bus.register(self.name)

        #creates the heater automaton and registers the states and events
        self.automaton = Automaton(
            [
                (s_heater_off, e_heater_on, s_heater_on),
                (s_heater_on, e_heater_off, s_heater_off),
                (s_heater_on, e_sim_reset, s_heater_off),
                (s_heater_off, e_sim_reset, s_heater_off),
            ], s_heater_off, "Heater"
        )

        self.automaton.set_action(s_heater_off, self.stop)
        self.automaton.set_action(s_heater_on, self.heat)



    def start(self):
        super().start()
        print(f"{CSUB}{self.name} thread initialized.{CEND}")

    #while the thread is running, the heater has to keep checking if a new message arrives
    #from the bus. When a message arrives, it will verify if it is relevant to it. In
    #the positive case, it will process the event.
    def run(self):
        while not self.stop_event.is_set():
            if self.bus.wait_for_new_message(self.name, timeout=1):
                messages = self.bus.get_messages(self.name)
                controller_messages = [msg for msg in messages if msg.get("source") == "Controller"]
                for message in controller_messages:
                    if message.get("source") == "Controller" and message.get("type") == "command":
                        command_value = message.get("data")
                        if command_value != self.last_command:
                            if self.automaton.is_defined(command_value):
                                self.last_command = command_value
                                if self.automaton.is_feasible(command_value):
                                    self.automaton.trigger_event(command_value)

            if self.heating:
                #self.heater_power = round(random.uniform(0, 100), 2)
                self.heater_power = 100

                # Send the message if a change is detected in Heater power
                if self.prev_heater_power is None or self.heater_power != self.prev_heater_power:
                    self.bus.send_message({"source": "HeaterPower", "type": "variable_update", "data": self.heater_power})
                    self.prev_heater_power = self.heater_power
            time.sleep(0.5)
        if print_heater:
            print(f"{CSUB}{self.name} thread stopped.{CEND}")

    def stop(self):
            print(CSUB + "Heater stopped." + CEND)
            self.heating = False
            self.heater_power = 0
            self.bus.send_message({"source": "HeaterPower", "type": "variable_update", "data": self.heater_power})

    def heat(self):
            print(CSUB + "Heater heating" + CEND)
            self.heating = True
            #todo: make the temperature dynamics faster when the heater is on.