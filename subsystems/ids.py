import threading
import time
from utils.simulation_params import DELTA_T, A_T

class IDS(threading.Thread):
    def __init__(self, stop_event, controller, bus):
        super().__init__()

