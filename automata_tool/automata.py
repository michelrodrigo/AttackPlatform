

from ultrades.automata import event, state, dfa #download through https://github.com/lacsed/UltraDES-Python?tab=readme-ov-file

class State:
    def __init__(self, name, marked=True):
        self.state = state(name, marked)
        self.name = name


    def __eq__(self, other):
        # Comparação baseada no nome, por exemplo
        if isinstance(other, State):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

class Event:
    def __init__(self, name, controllable=True):
        self.event = event(name, controllable)
        self.name = name  # Armazena o nome explicitamente

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

class Automaton:

    def __init__(self, transitions, initial_state, name):
        self.automaton = dfa([(s.state, e.event, d.state) for (s, e, d) in transitions], initial_state.state, name)
        self.initial_state = initial_state
        self.current_state = self.initial_state
        if isinstance(transitions, list):
            self.transitions = {(t[0], t[1]): t[2] for t in transitions}
        else:
            self.transitions = transitions
        self.name = name
        self.actions = {}

    def set_action(self, state, action_function):
        """
        Associa uma função de ação a um estado.
        :param state: Instância de State (ou nome do estado) em que a ação será executada.
        :param action_function: Função a ser executada quando o automato entrar neste estado.
        """
        self.actions[state] = action_function

    def get_current_state(self):
        """
        Gets the current state of the automaton
        :return: current state
        """
        return str(self.current_state)

    def get_feasible_events(self):
        """
        Returns all events that are defined in the current state
        :return: list of feasible events
        """
        return [str(e) for (s, e) in self.transitions.keys() if s == self.current_state]

    def is_feasible(self, e):
        """
        Checks if a given event is feasible at the current state of the automaton
        :return: True or false
        """
        for (s, evt) in self.transitions.keys():
            if s == self.current_state and evt == e:
                return True
        return False

    def trigger_event(self, e):
        """
        Checks if a given event is feasible at the current state of the automaton
        and if so, executes the transition, updating the current state
        :return: None
        """
        if self.is_feasible(e):
            self.current_state = self.transitions.get((self.current_state, e))
            if self.current_state in self.actions:
                self.actions[self.current_state]()
        else:
            raise ValueError(f"Evento {e} não é factível no estado {self.current_state}.")

    def is_defined(self, e):
        """
        Checks if a given event is defined in any of the automaton transitions, regardless if the event is
        currently feasible.
        :return: True if the event is defined, False, otherwise
        """
        return any(evt == e for (_, evt) in self.transitions.keys())

    def reset(self):
        """
        Resets the automaton to its initial state. It also calls the action function of the initial state. This avoids
        having to manually add a transition in every state with a reset event.
        :return: True if the event is defined, False, otherwise
        """
        self.current_state = self.initial_state
        self.actions[self.current_state]()
