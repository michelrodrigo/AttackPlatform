from .level_sensor import LevelSensor
from .temp_sensor import TempSensor
from .level_dynamics import LevelDynamics
from .temp_dynamics import TempDynamics
from .input_valve import InputValve
from .output_valve import OutputValve
from .ids import IDS

# Função para registrar subsistemas
def register_subsystems(controller, stop_event, bus):
    inputvalve = InputValve(stop_event, controller, bus)
    outputValve = OutputValve(stop_event, controller, bus)
    leveldynamics = LevelDynamics(stop_event, inputvalve, outputValve, bus)
    levelsensor = LevelSensor(stop_event, bus, leveldynamics)
    #tempsensor = TempSensor(stop_event, controller, bus)
    #temperaturedynamics = TempDynamics(stop_event, controller, bus)
    ids = IDS(stop_event, controller, bus)

    return [
        levelsensor, leveldynamics, ids, inputvalve, outputValve  #, tempsensor, temperaturedynamics
    ]

__all__ = ["register_subsystems"]