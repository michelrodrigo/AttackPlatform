# automata_plants.py
#from ultrades.automata import state, dfa #donwload through https://github.com/lacsed/UltraDES-Python?tab=readme-ov-file
from .events import *
from automata_tool.automata import *
from controller import *
from colorama import Fore, Back, Style


class ValveAutomaton(Automaton):
    def __init__(self, controller, type): ##type: "Input" or "Output
        self.controller = controller
        self.type = type
        # Creates the states of the automaton
        s_valve_closed = State("closed", marked=True)
        s_valve_open = State("open", marked=False)

        if self.type == "Input":
            evs = [e_open_input_valve, e_close_input_valve, e_sim_reset]
            name = "Input Valve"
        else:
            evs = [e_open_output_valve, e_close_output_valve, e_sim_reset]
            name = "Output Valve"

        # Creates the automaton
        super().__init__(
            [(s_valve_closed, evs[0], s_valve_open),
             (s_valve_open, evs[1], s_valve_closed),
             (s_valve_open, evs[2], s_valve_closed),
             (s_valve_closed, evs[2], s_valve_closed)],
            s_valve_closed, name)

        self.set_action(s_valve_closed, self.close)
        self.set_action(s_valve_open, self.open)

    def open(self):
        #print("A válvula foi aberta.")
        if self.type == "Input":
            self.controller.open_input_valve()
        elif self.type == "Output":
            self.controller.open_output_valve()

    def close(self):
        #print("A válvula foi fechada.")
        if self.type == "Input":
            self.controller.close_input_valve()
        elif self.type == "Output":
            self.controller.close_output_valve()


class InputValve(ValveAutomaton):

    def __init__(self, controller):
        super().__init__(controller, "Input")
        self.name = "Input Valve"



class OutputValve(ValveAutomaton):

    def __init__(self, controller):
        super().__init__(controller, "Output")
        self.name = "Output Valve"

class OnOffAutomaton(Automaton):

    def __init__(self, controller, type): ##type: "SimControl", "Mixer"
        self.controller = controller
        self.type = type
        # Creates the states of the automaton
        s_off = State("off", marked=True)
        s_on = State("on", marked=False)

        if self.type == "SimControl":
            evs = [e_sim_running, e_sim_stop, e_sim_reset]
            name = "Simulation Control"
        elif self.type == "Mixer":
            evs = [e_mixer_on, e_mixer_off, e_sim_reset]
            name = "Mixer"
        elif self.type == "Heater":
            evs = [e_heater_on, e_heater_off, e_sim_reset]
            name = "Heater"

        # Creates the automaton
        super().__init__(
            [(s_off, evs[0], s_on),
             (s_on, evs[1], s_off),
             (s_on, evs[2], s_off),
             (s_off, evs[2], s_off)
            ],
            s_off, name)

        self.set_action(s_off, self.off)
        self.set_action(s_on, self.on)

    def on(self):
        if self.type == "SimControl":
            self.controller.start_simulation()
        elif self.type == "Mixer":
            self.controller.turn_mixer_on()

    def off(self):
        if self.type == "SimControl":
            self.controller.stop_simulation()
        elif self.type == "Mixer":
            self.controller.turn_mixer_off()

class SimulationControl(OnOffAutomaton):

    def __init__(self, controller):
        super().__init__(controller, "SimControl")
        self.name = "Simulation Control"

class Mixer(OnOffAutomaton):

    def __init__(self, controller):
        super().__init__(controller, "Mixer")
        self.name = "Mixer"


class Heater(OnOffAutomaton):

    def __init__(self, controller):
        super().__init__(controller, "Heater")
        self.name = "Heater"

class SensorAutomaton(Automaton):
    def __init__(self, controller, type):  ##type: "Low Level", "High Level", "Extra High Level", "Temperature"
        self.controller = controller
        self.type = type
        # Creates the states of the automaton
        s_sensor_off = State("off", marked=True)
        s_sensor_on = State("on", marked=False)

        if self.type == "Low Level":
            evs = [e_low_level_trigger, e_low_level_reset, e_sim_reset]
        elif self.type == "High Level":
            evs = [e_high_level_trigger, e_high_level_reset, e_sim_reset]
        elif self.type == "Extra High Level":
            evs = [e_extra_high_level_trigger, e_extra_high_level_reset, e_sim_reset]

        # Creates the automaton
        super().__init__(
            [(s_sensor_off, evs[0], s_sensor_on),
             (s_sensor_on, evs[1], s_sensor_off),
             (s_sensor_on, evs[2], s_sensor_off),
             (s_sensor_off, evs[2], s_sensor_off)
        ],
            s_sensor_off, self.type)

        self.set_action(s_sensor_off, self.reset)
        self.set_action(s_sensor_on, self.trigger)

    def trigger(self):
        if self.type == "Low Level":
            self.controller.trigger_low_level_sensor()
        elif self.type == "High Level":
            self.controller.trigger_high_level_sensor()
        elif self.type == "Extra High Level":
            self.controller.trigger_extra_high_level_sensor()

    def reset(self):
        if self.type == "Low Level":
            self.controller.reset_low_level_sensor()
        elif self.type == "High Level":
            self.controller.reset_high_level_sensor()
        elif self.type == "Extra High Level":
            self.controller.reset_extra_high_level_sensor()


class LowLevelSensor(SensorAutomaton):

    def __init__(self, controller):
        super().__init__(controller, "Low Level")
        self.name = "Low Level Sensor"

class HighLevelSensor(SensorAutomaton):

    def __init__(self, controller):
        super().__init__(controller, "High Level")
        self.name = "High Level Sensor"

class ExtraHighLevelSensor(SensorAutomaton):

    def __init__(self, controller):
        super().__init__(controller, "Extra High Level")
        self.name = "Extra High Level Sensor"


#
#def create_input_valve_automaton(controller):




#    return a_input_valve

# Define as ações para cada estado
#def action_closed(controller):
#    def inner():
#        print("A válvula de entrada foi fechada.")
#        controller.input_valve_open = False
#        controller.opc_server.variables["Input Valve"].set_value(controller.input_valve_open)
#    return inner

#def action_open(controller):
#    def inner():
#        print("A válvula de entrada foi aberta.")
#        controller.input_valve_open = True
#        controller.opc_server.variables["Input Valve"].set_value(controller.input_valve_open)
#    return inner
