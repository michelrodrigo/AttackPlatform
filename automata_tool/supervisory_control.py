from .automata import Automaton


class Supervisor(Automaton):
    def __init__(self, transitions, initial_state, name):
        super().__init__(transitions, initial_state, name)
        self.name = name
        self.disabled_events = set()  # Eventos que este supervisor desabilita

    def disable_event(self, event):
        self.disabled_events.add(event)

    def enable_event(self, event):
        self.disabled_events.discard(event)

    def is_event_enabled(self, event):
        return event not in self.disabled_events


import random



class SupervisoryControl:
    def __init__(self, mode="manual"):
        """
        mode: "manual" ou "automatic"
        """
        self.mode = mode
        self.supervisors = []  # Lista de objetos Supervisor
        self.automata = {}     # Dicionário: chave = nome do subsistema, valor = autômato (ou estado) daquele subsistema

    def add_supervisor(self, supervisor):
        self.supervisors.append(supervisor)

    def add_automaton(self, subsystem, automaton):
        if subsystem in self.automata:
            raise ValueError(
                f"Automaton '{subsystem}' already exists."
            )
        self.automata[subsystem] = automaton

    def get_feasible_events(self, events):
        """
        Retorna a lista de eventos que não estão desabilitados por nenhum supervisor.
        events: lista de strings representando os eventos possíveis.
        """
        feasible = []
        for event in events:
            if all(supervisor.is_event_enabled(event) for supervisor in self.supervisors):
                feasible.append(event)
        return feasible

    def choose_event(self, events):
        """
        Em modo automático, escolhe um evento dentre os factíveis.
        """
        feasible = self.get_feasible_events(events)
        if feasible:
            return random.choice(feasible)
        return None

    def find_automata_with_event(self, event):
        """
        Retorna uma lista com os nomes dos autômatos que possuem o evento especificado em suas transições.

        :param event: Instância de Event a ser verificada
        :return: Lista dos autômatos que possuem o evento definido
        """
        automata_with_event = []

        for name, automaton in self.automata.items():
            if automaton.is_defined(event):
                automata_with_event.append(automaton)

        return automata_with_event