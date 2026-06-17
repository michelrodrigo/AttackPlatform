import threading
import time
from utils.simulation_params import *
from utils.colors import *
from controller.events import *
from automata_tool.automata import *

# Creates the states for the mixer automaton
s_mixer_off = State("mixer off", marked=True)
s_mixer_on = State("mixer on", marked=False)


#class for the mixer element
class Mixer(threading.Thread):

    def __init__(self, stop_event, controller, bus):
        super().__init__()
        self.stop_event = stop_event
        self.state = "off"
        self.controller = controller
        self.name = "Mixer"
        self.bus = bus
        self.last_command = None

        self.msg_queue = self.bus.register(self.name)

        #creates the mixer automaton and registers the states and events
        self.automaton = Automaton(
            [
                (s_mixer_off, e_mixer_on, s_mixer_on),
                (s_mixer_on, e_mixer_off, s_mixer_off),
                (s_mixer_on, e_sim_reset, s_mixer_off),
                (s_mixer_off, e_sim_reset, s_mixer_off),
            ], s_mixer_off, "Mixer"
        )

        self.automaton.set_action(s_mixer_off, self.stop)
        self.automaton.set_action(s_mixer_on, self.agitate)

        #todo: finish implementing the mixer


    def stop(self):
            print(CSUB + "Mixer stopped." + CEND)

    def agitate(self):
            print(CSUB + "Mixer agitating" + CEND)
            #todo: make the temperature dynamics faster when the mixer is on.