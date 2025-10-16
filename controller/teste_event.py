# automata_plants.py
#from ultrades.automata import state, dfa #donwload through https://github.com/lacsed/UltraDES-Python?tab=readme-ov-file
#from .events import *
from automata_tool.automata import *
#from controller import *


CSUP = '\033[41m'
CEND = '\033[0m'

# Events related to the Input Valve
e_open_input_valve = Event("open_input_valve", controllable=True)
e_close_input_valve = Event("close_input_valve", controllable=True)


def create_input_valve_automaton():
    # Cria os estados da válvula de entrada
    s_input_valve_closed = State("closed", marked=True)
    s_input_valve_open = State("open", marked=False)

    # Cria o autômato e registra os estados e eventos
    a_input_valve = Automaton(
        [(s_input_valve_closed.state, e_open_input_valve.event, s_input_valve_open.state),
         (s_input_valve_open.state, e_close_input_valve.event, s_input_valve_closed.state)],
        s_input_valve_closed.state,  "Input Valve")



    return a_input_valve


def print_transitions(automaton):
    for t in automaton.transitions:
        print(f"{t[0]}->{t[1]}->{t[2]}")


def main():
    # Se o comando for "Input Valve Open" e seu valor for True:

    a = create_input_valve_automaton()

    cmd = "Input Valve Open"
    value = True

    if cmd == "Input Valve Open" and value:

        print(f"{CSUP}Automaton {a.name}{CEND}")
        print(f"Is feasible: {a.is_feasible(e_open_input_valve)}")
        print_transitions(a)
        if a.is_feasible(e_open_input_valve):
            a.trigger_event(e_open_input_valve)

if __name__ == "__main__":
    main()
