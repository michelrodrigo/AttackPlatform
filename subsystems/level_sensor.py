import threading
import time
from utils.simulation_params import *
from controller.events import *

class LevelSensor(threading.Thread):
    def __init__(self, stop_event,  bus, level_dynamics):
        super().__init__()
        self.stop_event = stop_event  # Stop signal
        self.name = "Level Sensor"
        self.level_dynamics = level_dynamics
        self.bus = bus
        self.level = 0

        # Thresholds in %
        self.LL = LL  # Low Level
        self.LH = LH  # High Level
        self.LHH = LHH  # Extra High Level

        # Previous states, to verify changes
        self.prev_low = None
        self.prev_high = None
        self.prev_xhigh = None
        self.prev_level = None

    def start(self):
        super().start()
        print(self.name, " thread initialized.")

    def run(self):
        while not self.stop_event.is_set():
            self.level = self.level_dynamics.level

            # Send the message if a change is detected in Level
            if self.prev_level is None or self.level != self.prev_level:
                self.bus.send_message({"source": "LevelSensor", "type": "variable_update", "data": self.level})
                self.prev_level = self.level

            # discrete sensors
            # Verify the current states of discrete sensors
            low_triggered = (self.level <= self.LL) # Falling edge
            high_triggered = (self.level >= self.LH) # rising edge
            xhigh_triggered = (self.level >= self.LHH) # rising edge

            # Send the message if a change is detected in Low Level sensor
            if self.prev_low is None or low_triggered != self.prev_low:
                ev = e_low_level_trigger if low_triggered else e_low_level_reset
                self.bus.send_message({
                    "source": "LevelSensor",
                    "type": "discrete_event",
                    "data": ev
                })
                self.prev_low = low_triggered


            # Send the message if a change is detected in High Level sensor
            if self.prev_high is None or high_triggered != self.prev_high:
                ev = e_high_level_trigger if high_triggered  else e_high_level_reset
                self.bus.send_message({
                    "source": "LevelSensor",
                    "type": "discrete_event",
                    "data": ev
                })
                self.prev_high = high_triggered

            # Send the message if a change is detected in Extra High Level sensor
            if self.prev_xhigh is None or xhigh_triggered != self.prev_xhigh:
                ev = e_extra_high_level_trigger if xhigh_triggered else e_extra_high_level_reset
                self.bus.send_message({
                    "source": "LevelSensor",
                    "type": "discrete_event",
                    "data": ev
                })
                self.prev_xhigh = xhigh_triggered

            time.sleep(1)
        print(self.name, " thread stopped.")