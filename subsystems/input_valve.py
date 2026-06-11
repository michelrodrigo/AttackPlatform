import threading
import time
from utils.simulation_params import *
from utils.colors import *
from controller.events import *
from automata_tool.automata import *

# Cria os estados da válvula de entrada
s_input_valve_closed = State("closed", marked=True)
s_input_valve_open = State("open", marked=False)




class InputValve(threading.Thread):




    def __init__(self, stop_event, controller, bus):
        super().__init__()
        self.stop_event = stop_event
        self.state = "closed"
        self.controller = controller
        self.name = "Input Valve"
        self.bus = bus
        self.input_flow = 0
        self.last_command = None

        self.msg_queue = self.bus.register(self.name)


        # Cria o autômato e registra os estados e eventos
        self.automaton = Automaton(
            [(s_input_valve_closed, e_open_input_valve, s_input_valve_open),
             (s_input_valve_open, e_close_input_valve, s_input_valve_closed),
             (s_input_valve_open, e_sim_reset, s_input_valve_closed),
             (s_input_valve_closed, e_sim_reset, s_input_valve_closed)],
            s_input_valve_closed, "Input Valve")

        self.automaton.set_action(s_input_valve_closed, self.close)
        self.automaton.set_action(s_input_valve_open, self.open)



    #@property
    #def input_flow(self):
    #    """
    #    Retorna o nível atual do tanque.
    #    """
    #    return self.input_flow

    def start(self):
        super().start()
        print(f"{CSUB}{self.name} thread initialized.{CEND}")

    def run(self):
        while not self.stop_event.is_set():
            if self.bus.wait_for_new_message(self.name, timeout=1):  # Timeout evita bloqueio eterno
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


            time.sleep(0.5)
        if print_input_valve:
            print(f"{CSUB}{self.name} thread stopped.{CEND}")

    def open(self):
        self.state = "open"
        self.input_flow = input_flow
        if print_input_valve:
            print(CSUB+"Input Valve open."+CEND)

    def close(self):
        self.state = "closed"
        self.input_flow = 0
        if print_input_valve:
            print(CSUB+"Input Valve closed."+CEND)

    def reset(self):
        self.state = "closed"
        self.input_flow = 0

